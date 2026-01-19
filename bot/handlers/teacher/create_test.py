from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot import texts
from bot.keyboards.templates import (
    manage_test_keyboard,
    summary_teacher_sections_keyboard,
    teacher_progress_keyboard,
    template_keyboard,
)
from bot.states.teacher_create_test import TeacherCreateTestStates
from bot.utils.summary import build_teacher_summary, teacher_progress_stage
from shared.db.models import UserRole, UserStatus
from shared.services.answer_key_service import (
    ValidationError,
    parse_open_ab_bulk,
    parse_y1_input,
    parse_y2_choices,
    save_section_key,
)
from shared.services.template_service import get_template_by_id, list_active_templates
from shared.models.test import Test
from shared.services.test_service import (
    close_test,
    create_test,
    get_keys,
    publish_test,
    update_material,
)
from shared.services.users import get_user_by_telegram_id

router = Router()

SKIP_MATERIAL = texts.MATERIAL_SKIP_WORD


async def _update_summary(
    message: Message,
    state: FSMContext,
    instruction: str | None = None,
    error: str | None = None,
    reply_markup=None,
) -> None:
    data = await state.get_data()
    stage = teacher_progress_stage(data)
    if instruction is None:
        if stage == 0:
            instruction = texts.Y1_INSTRUCTION
        elif stage == 1:
            instruction = texts.Y2_INSTRUCTION
        elif stage == 2:
            instruction = texts.OPEN_INSTRUCTION
        else:
            instruction = texts.ALL_DONE_INSTRUCTION
    if reply_markup is None:
        test_id = data.get("test_id", 0)
        reply_markup = teacher_progress_keyboard(test_id, stage)
    text = build_teacher_summary(data, instruction=instruction, error=error)
    summary_id = data.get("summary_message_id")
    if summary_id:
        try:
            await message.bot.edit_message_text(
                text,
                chat_id=message.chat.id,
                message_id=summary_id,
                reply_markup=reply_markup,
            )
            return
        except TelegramBadRequest:
            pass
    sent = await message.answer(text, reply_markup=reply_markup)
    await state.update_data(summary_message_id=sent.message_id)


async def _delete_input(message: Message) -> None:
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def _require_teacher(message: Message, session: AsyncSession):
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if not user or user.status != UserStatus.ACTIVE or user.role != UserRole.TEACHER:
        await message.answer(texts.TEACHER_ONLY)
        return None
    return user


@router.message(F.text == "📝 New Test")
async def start_create_test(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _require_teacher(message, session)
    if not user:
        return

    templates = await list_active_templates(session)
    if not templates:
        await message.answer(texts.NO_TEMPLATES)
        return

    items = [(tpl.id, tpl.subject_name) for tpl in templates]
    await state.clear()
    await state.set_state(TeacherCreateTestStates.choose_template)
    await message.answer(texts.TEMPLATE_CHOOSE, reply_markup=template_keyboard(items))


@router.callback_query(F.data.startswith("tpl_"))
async def choose_template(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    template_id = int(call.data.replace("tpl_", ""))
    template = await get_template_by_id(session, template_id)
    if not template:
        await call.message.answer(texts.TEMPLATE_NOT_FOUND)
        await call.answer()
        return

    await state.update_data(template_id=template_id)
    await state.set_state(TeacherCreateTestStates.enter_title)
    await call.message.answer(texts.TEST_TITLE_PROMPT)
    await call.answer()


@router.message(TeacherCreateTestStates.enter_title, F.text)
async def enter_title(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await _require_teacher(message, session)
    if not user:
        return

    data = await state.get_data()
    template = await get_template_by_id(session, data["template_id"])
    if not template:
        await message.answer(texts.TEMPLATE_NOT_FOUND)
        return

    title = message.text.strip()
    test = await create_test(session, user.id, template, title)
    await state.update_data(
        test_id=test.id,
        test_title=test.title,
        template_structure=template.structure_json,
    )
    await state.set_state(TeacherCreateTestStates.upload_material)
    await message.answer(texts.MATERIAL_PROMPT)
    await message.answer(texts.MATERIAL_SKIP_HINT)


@router.message(
    TeacherCreateTestStates.upload_material, F.text.casefold() == SKIP_MATERIAL.lower()
)
async def skip_material(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    test_id = data.get("test_id")
    if test_id:
        test = await session.get(Test, test_id)
        if test:
            await update_material(session, test, None, None, None)
    await state.set_state(TeacherCreateTestStates.enter_y1_key)
    await _update_summary(
        message,
        state,
        instruction=texts.Y1_INSTRUCTION,
    )


@router.message(TeacherCreateTestStates.upload_material, F.document)
async def receive_material_document(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.get_data()
    test_id = data.get("test_id")
    if not test_id:
        await message.answer(texts.GENERAL_RETRY)
        return
    test = await session.get(Test, test_id)
    if test:
        await update_material(
            session,
            test,
            message.document.file_id,
            "document",
            message.caption,
        )
    await state.set_state(TeacherCreateTestStates.enter_y1_key)
    await _update_summary(
        message,
        state,
        instruction=texts.Y1_INSTRUCTION,
    )


@router.message(TeacherCreateTestStates.upload_material, F.photo)
async def receive_material_photo(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    data = await state.get_data()
    test_id = data.get("test_id")
    if not test_id:
        await message.answer(texts.GENERAL_RETRY)
        return
    test = await session.get(Test, test_id)
    if test:
        photo = message.photo[-1]
        await update_material(session, test, photo.file_id, "photo", message.caption)
    await state.set_state(TeacherCreateTestStates.enter_y1_key)
    await _update_summary(
        message,
        state,
        instruction=texts.Y1_INSTRUCTION,
    )


@router.message(TeacherCreateTestStates.upload_material)
async def material_invalid(message: Message) -> None:
    await message.answer(texts.MATERIAL_PROMPT)
    await message.answer(texts.MATERIAL_SKIP_HINT)


@router.message(TeacherCreateTestStates.enter_y1_key, F.text)
async def enter_y1_key(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    test_id = data.get("test_id")
    template = data.get("template_structure", {})
    y1_section = next((s for s in template.get("sections", []) if s["code"] == "Y1"), {})
    expected_len = y1_section.get("item_count", 32)

    try:
        key = parse_y1_input(message.text, expected_len=expected_len)
    except ValidationError as exc:
        await _update_summary(
            message,
            state,
            instruction=texts.Y1_INSTRUCTION,
            error=str(exc),
        )
        await _delete_input(message)
        return

    await save_section_key(session, test_id, "Y1", {"answers": key})
    await state.update_data(y1_answers={"answers": key})
    await state.set_state(TeacherCreateTestStates.enter_y2_key)
    await _update_summary(
        message,
        state,
        instruction=texts.Y2_INSTRUCTION,
    )
    await _delete_input(message)


@router.message(TeacherCreateTestStates.enter_y2_key, F.text)
async def enter_y2_key(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    template = data.get("template_structure", {})
    y2_section = next((s for s in template.get("sections", []) if s["code"] == "Y2"), {})
    item_numbers = y2_section.get("item_numbers", [33, 34, 35])

    try:
        answers = parse_y2_choices(message.text, item_numbers)
    except ValidationError as exc:
        await _update_summary(
            message,
            state,
            instruction=texts.Y2_INSTRUCTION,
            error=str(exc),
        )
        await _delete_input(message)
        return

    await save_section_key(session, data["test_id"], "Y2", {"answers": answers})
    await state.update_data(y2_answers={"answers": answers})
    await state.set_state(TeacherCreateTestStates.enter_open_bulk)
    await _update_summary(
        message,
        state,
        instruction=texts.OPEN_INSTRUCTION,
    )
    await _delete_input(message)


@router.message(TeacherCreateTestStates.enter_open_bulk, F.text)
async def enter_open_bulk(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    template = data.get("template_structure", {})
    open_section = next((s for s in template.get("sections", []) if s["code"] == "O"), {})
    item_numbers = open_section.get(
        "item_numbers", [36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
    )

    try:
        open_items = parse_open_ab_bulk(message.text, item_numbers)
    except ValidationError as exc:
        await _update_summary(
            message,
            state,
            instruction=texts.OPEN_INSTRUCTION,
            error=str(exc),
        )
        await _delete_input(message)
        return

    await state.update_data(open_items={str(k): v for k, v in open_items.items()})
    items_payload = [
        {"item_no": item_no, "a": open_items[item_no]["a"], "b": open_items[item_no]["b"]}
        for item_no in item_numbers
    ]
    await save_section_key(
        session, data["test_id"], "O", {"items": items_payload, "subparts": True}
    )
    await state.set_state(TeacherCreateTestStates.confirm_publish)
    await _update_summary(
        message,
        state,
        instruction=texts.ALL_DONE_INSTRUCTION,
    )
    await _delete_input(message)


@router.callback_query(F.data.startswith("tconfirm_"))
async def publish_test_handler(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    test_id = int(call.data.replace("tconfirm_", ""))
    test = await session.get(Test, test_id)
    if not test:
        await call.message.answer(texts.TEST_NOT_FOUND)
        await call.answer()
        return

    user = await get_user_by_telegram_id(session, call.from_user.id)
    if not user or user.id != test.teacher_id:
        await call.message.answer(texts.TEACHER_ONLY)
        await call.answer()
        return

    keys = await get_keys(session, test.id)
    key_sections = {record.section_code for record in keys}
    if not {"Y1", "Y2", "O"}.issubset(key_sections):
        await _update_summary(
            call.message,
            state,
            error=texts.TEACHER_PUBLISH_BLOCKED_MISSING_KEYS,
        )
        await call.answer()
        return

    y2_key = next((record for record in keys if record.section_code == "Y2"), None)
    if not y2_key or "answers" not in y2_key.payload_json:
        await _update_summary(
            call.message,
            state,
            error=texts.Y2_OUTDATED,
        )
        await call.answer()
        return

    open_key = next((record for record in keys if record.section_code == "O"), None)
    if not open_key or not open_key.payload_json.get("subparts"):
        await _update_summary(
            call.message,
            state,
            error=texts.OPEN_OUTDATED,
        )
        await call.answer()
        return
    open_items = open_key.payload_json.get("items", [])
    if len(open_items) != 10 or any(
        "a" not in item or "b" not in item for item in open_items
    ):
        await _update_summary(
            call.message,
            state,
            error=texts.TEACHER_PUBLISH_BLOCKED_OPEN,
        )
        await call.answer()
        return

    await publish_test(session, test)
    template = await get_template_by_id(session, test.subject_template_id)
    bot_username = (await call.bot.get_me()).username
    join_link = f"https://t.me/{bot_username}?start=test_{test.access_code}"
    material_note = texts.TEACHER_MATERIAL_NOTE if test.material_file_id else ""
    await call.message.edit_text(
        texts.TEACHER_TEST_PUBLISHED.format(
            title=test.title,
            subject=template.subject_name if template else "-",
            time_limit=test.time_limit_minutes or "-",
            code=test.access_code,
            link=join_link,
            material_note=material_note,
        ),
        reply_markup=manage_test_keyboard(test.id),
    )
    await state.clear()
    await call.answer()


@router.callback_query(F.data.startswith("tedit_menu_"))
async def edit_teacher_flow(call: CallbackQuery, state: FSMContext) -> None:
    test_id = int(call.data.replace("tedit_menu_", ""))
    await _update_summary(
        call.message,
        state,
        instruction=texts.SUMMARY_EDIT_PROMPT,
        reply_markup=summary_teacher_sections_keyboard(test_id),
    )
    await call.answer()


@router.callback_query(F.data.startswith("tedit_y1_"))
async def edit_teacher_y1(call: CallbackQuery, state: FSMContext) -> None:
    test_id = int(call.data.replace("tedit_y1_", ""))
    await state.set_state(TeacherCreateTestStates.enter_y1_key)
    await _update_summary(
        call.message,
        state,
        instruction=texts.Y1_INSTRUCTION,
    )
    await call.answer()


@router.callback_query(F.data.startswith("tedit_y2_"))
async def edit_teacher_y2(call: CallbackQuery, state: FSMContext) -> None:
    test_id = int(call.data.replace("tedit_y2_", ""))
    await state.set_state(TeacherCreateTestStates.enter_y2_key)
    await _update_summary(
        call.message,
        state,
        instruction=texts.Y2_INSTRUCTION,
    )
    await call.answer()


@router.callback_query(F.data.startswith("tedit_o_"))
async def edit_teacher_open(call: CallbackQuery, state: FSMContext) -> None:
    test_id = int(call.data.replace("tedit_o_", ""))
    await state.set_state(TeacherCreateTestStates.enter_open_bulk)
    await _update_summary(
        call.message,
        state,
        instruction=texts.OPEN_INSTRUCTION,
    )
    await call.answer()


@router.callback_query(F.data.startswith("tcancel_"))
async def cancel_teacher_flow(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(texts.SUMMARY_CANCELLED)
    await call.answer()


@router.callback_query(F.data == "new_test")
async def new_test_callback(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await call.answer()
    await start_create_test(call.message, state, session)


@router.callback_query(F.data == "teacher_students")
async def teacher_students_callback(call: CallbackQuery, session: AsyncSession) -> None:
    from bot.handlers.menu import students_list

    await call.answer()
    await students_list(call.message, session)


@router.callback_query(F.data.startswith("results_"))
async def teacher_results_callback(call: CallbackQuery, session: AsyncSession) -> None:
    from bot.handlers.teacher.my_tests import my_tests

    await call.answer()
    await my_tests(call.message, session)


@router.callback_query(F.data.startswith("close_"))
async def close_test_callback(call: CallbackQuery, session: AsyncSession) -> None:
    test_id = int(call.data.replace("close_", ""))
    test = await session.get(Test, test_id)
    if not test:
        await call.message.answer(texts.TEST_NOT_FOUND)
        await call.answer()
        return

    user = await get_user_by_telegram_id(session, call.from_user.id)
    if not user or user.id != test.teacher_id:
        await call.message.answer(texts.TEACHER_ONLY)
        await call.answer()
        return

    await close_test(session, test)
    await call.message.answer(texts.TEACHER_CLOSE_SOON)
    await call.answer()
