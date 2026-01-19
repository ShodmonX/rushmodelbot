from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot import texts
from bot.keyboards.templates import student_progress_keyboard, summary_student_sections_keyboard
from bot.states.student_join_test import StudentJoinTestStates
from bot.utils.summary import build_student_summary, student_progress_stage
from shared.db.models import UserRole, UserStatus
from shared.models.attempt import AttemptStatus
from shared.models.subject_template import SubjectTemplate
from shared.models.test import TestStatus
from shared.services.answer_key_service import (
    ValidationError,
    parse_open_ab_bulk,
    parse_y1_input,
    parse_y2_choices,
)
from shared.services.attempt_service import (
    AttemptError,
    get_attempt,
    start_attempt,
    submit_attempt,
)
from shared.services.template_service import get_template_by_id
from shared.services.test_service import get_test_by_code
from shared.services.users import get_user_by_telegram_id

router = Router()


async def _update_summary(
    message: Message,
    state: FSMContext,
    instruction: str | None = None,
    error: str | None = None,
    reply_markup=None,
) -> None:
    data = await state.get_data()
    stage = student_progress_stage(data)
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
        attempt_id = data.get("attempt_id", 0)
        reply_markup = student_progress_keyboard(attempt_id, stage)
    text = build_student_summary(data, instruction=instruction, error=error)
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


async def _require_student(message: Message, session: AsyncSession):
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if not user or user.status != UserStatus.ACTIVE or user.role != UserRole.STUDENT:
        await message.answer(texts.STUDENT_ONLY)
        return None
    return user


@router.message(F.text == "✅ Join Test")
async def start_join(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(StudentJoinTestStates.enter_code)
    await message.answer(texts.ENTER_TEST_CODE)


async def start_join_with_code(
    message: Message, state: FSMContext, session: AsyncSession, code: str
) -> None:
    await state.clear()
    await _handle_code(message, state, session, code)


@router.message(StudentJoinTestStates.enter_code, F.text)
async def handle_code(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await _handle_code(message, state, session, message.text.strip())


async def _handle_code(
    message: Message, state: FSMContext, session: AsyncSession, code: str
) -> None:
    user = await _require_student(message, session)
    if not user:
        return

    test = await get_test_by_code(session, code)
    if not test:
        await message.answer(texts.TEST_CODE_NOT_FOUND)
        return
    if test.status != TestStatus.PUBLISHED:
        await message.answer(texts.TEST_NOT_PUBLISHED)
        return

    attempt = await get_attempt(session, test.id, user.id)
    if attempt and attempt.status == AttemptStatus.SUBMITTED:
        await message.answer(texts.ALREADY_SUBMITTED)
        return

    try:
        attempt = await start_attempt(session, test, user.id)
    except AttemptError:
        await message.answer(texts.TEST_NOT_PUBLISHED)
        return

    template: SubjectTemplate | None = await get_template_by_id(
        session, test.subject_template_id
    )
    if template and test.material_file_id:
        if test.material_file_type == "photo":
            await message.answer_photo(test.material_file_id, caption=test.material_caption)
        else:
            await message.answer_document(test.material_file_id, caption=test.material_caption)

    await state.update_data(
        test_id=test.id,
        template_structure=template.structure_json if template else {},
        attempt_id=attempt.id,
        access_code=code,
    )
    await state.set_state(StudentJoinTestStates.y1_answers)
    await _update_summary(
        message,
        state,
        instruction=texts.Y1_INSTRUCTION,
    )


@router.message(StudentJoinTestStates.y1_answers, F.text)
async def student_y1(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    template = data.get("template_structure", {})
    y1_section = next((s for s in template.get("sections", []) if s["code"] == "Y1"), {})
    expected_len = y1_section.get("item_count", 32)
    try:
        answers = parse_y1_input(message.text, expected_len=expected_len)
    except ValidationError as exc:
        await _update_summary(
            message,
            state,
            instruction=texts.Y1_INSTRUCTION,
            error=str(exc),
        )
        await _delete_input(message)
        return

    await state.update_data(y1_answers={"answers": answers})
    await state.set_state(StudentJoinTestStates.y2_answers)
    await _update_summary(
        message,
        state,
        instruction=texts.Y2_INSTRUCTION,
    )
    await _delete_input(message)


@router.message(StudentJoinTestStates.y2_answers, F.text)
async def student_y2_answers(message: Message, state: FSMContext) -> None:
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

    await state.update_data(y2_answers={"answers": answers})
    await state.set_state(StudentJoinTestStates.open_bulk)
    await _update_summary(
        message,
        state,
        instruction=texts.OPEN_INSTRUCTION,
    )
    await _delete_input(message)


@router.message(StudentJoinTestStates.open_bulk, F.text)
async def student_open_bulk(message: Message, state: FSMContext) -> None:
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
    await state.set_state(StudentJoinTestStates.confirm_submit)
    await _update_summary(
        message,
        state,
        instruction="Hammasi tayyor. Tasdiqlaysizmi?",
    )
    await _delete_input(message)


@router.callback_query(F.data.startswith("sconfirm_"))
async def submit_answers(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    attempt_id = int(call.data.replace("sconfirm_", ""))
    data = await state.get_data()
    if data.get("attempt_id") != attempt_id:
        await call.message.answer(texts.GENERAL_RETRY)
        await call.answer()
        return

    template = data.get("template_structure", {})
    y1_section = next((s for s in template.get("sections", []) if s["code"] == "Y1"), {})
    y2_section = next((s for s in template.get("sections", []) if s["code"] == "Y2"), {})
    o_section = next((s for s in template.get("sections", []) if s["code"] == "O"), {})
    y1_expected = y1_section.get("item_count", 32)
    y1_answers = data.get("y1_answers", {}).get("answers", "")
    y2_answers = data.get("y2_answers", {}).get("answers", {})
    y2_items = y2_section.get("item_numbers", [33, 34, 35])
    open_items = data.get("open_items", {})
    open_numbers = o_section.get(
        "item_numbers", [36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
    )

    y1_ok = len(y1_answers) == y1_expected
    y2_ok = all(str(num) in y2_answers for num in y2_items)
    open_ok = all(
        "a" in open_items.get(str(num), {}) and "b" in open_items.get(str(num), {})
        for num in open_numbers
    )
    if not (y1_ok and y2_ok and open_ok):
        await _update_summary(
            call.message,
            state,
            error=texts.SUMMARY_INCOMPLETE,
        )
        await call.answer()
        return

    from shared.models.attempt import Attempt

    attempt = await session.get(Attempt, attempt_id)
    if not attempt:
        await call.message.answer(texts.GENERAL_RETRY)
        await call.answer()
        return

    answers = {
        "Y1": data.get("y1_answers"),
        "Y2": data.get("y2_answers"),
        "O": {"items": [], "subparts": True},
    }
    for item_no in open_numbers:
        entry = open_items.get(str(item_no))
        if not entry:
            continue
        answers["O"]["items"].append(
            {"item_no": item_no, "a": entry.get("a", ""), "b": entry.get("b", "")}
        )

    try:
        attempt = await submit_attempt(session, attempt, answers)
    except AttemptError:
        await call.message.answer(texts.GENERAL_RETRY)
        await call.answer()
        return

    await state.clear()
    wrong_items = attempt.incorrect_items_json or {}
    wrong_list: list[int] = []
    wrong_list.extend(wrong_items.get("Y1", []))
    wrong_list.extend(wrong_items.get("Y2", []))
    wrong_list.extend(wrong_items.get("O", []))
    wrong_list = [int(x) for x in wrong_list if x]
    wrong_list = sorted(set(wrong_list))

    if wrong_list:
        display = ", ".join(str(x) for x in wrong_list[:10])
        if len(wrong_list) > 10:
            display += ", ..."
        wrong_line = f"❗ Xato savollar: {display}"
    else:
        wrong_line = texts.STUDENT_SUBMITTED_RESULT_NO_WRONGS

    total = attempt.score_total or 0
    if total >= 40:
        feedback_line = "🔥 Juda yaxshi! Shu tempda davom eting."
    elif total >= 30:
        feedback_line = "👍 Yaxshi natija. Bir-ikki mavzuni mustahkamlab oling."
    else:
        feedback_line = "💪 Boshlanishi yaxshi. Xatolarni tahlil qilib, yana urinib ko‘ring."

    await call.message.edit_text(
        texts.STUDENT_SUBMITTED_RESULT.format(
            y1=attempt.score_y1 or 0,
            y2=attempt.score_y2 or 0,
            o=attempt.score_o or 0,
            total=total,
            feedback_line=feedback_line,
            wrong_line=wrong_line,
        )
    )
    await call.answer()


@router.callback_query(F.data.startswith("sedit_menu_"))
async def edit_student_flow(call: CallbackQuery, state: FSMContext) -> None:
    attempt_id = int(call.data.replace("sedit_menu_", ""))
    await _update_summary(
        call.message,
        state,
        instruction=texts.SUMMARY_EDIT_PROMPT,
        reply_markup=summary_student_sections_keyboard(attempt_id),
    )
    await call.answer()


@router.callback_query(F.data.startswith("sedit_y1_"))
async def edit_student_y1(call: CallbackQuery, state: FSMContext) -> None:
    attempt_id = int(call.data.replace("sedit_y1_", ""))
    await state.set_state(StudentJoinTestStates.y1_answers)
    await _update_summary(
        call.message,
        state,
        instruction=texts.Y1_INSTRUCTION,
    )
    await call.answer()


@router.callback_query(F.data.startswith("sedit_y2_"))
async def edit_student_y2(call: CallbackQuery, state: FSMContext) -> None:
    attempt_id = int(call.data.replace("sedit_y2_", ""))
    await state.set_state(StudentJoinTestStates.y2_answers)
    await _update_summary(
        call.message,
        state,
        instruction=texts.Y2_INSTRUCTION,
    )
    await call.answer()


@router.callback_query(F.data.startswith("sedit_o_"))
async def edit_student_open(call: CallbackQuery, state: FSMContext) -> None:
    attempt_id = int(call.data.replace("sedit_o_", ""))
    await state.set_state(StudentJoinTestStates.open_bulk)
    await _update_summary(
        call.message,
        state,
        instruction=texts.OPEN_INSTRUCTION,
    )
    await call.answer()


@router.callback_query(F.data.startswith("scancel_"))
async def cancel_student_flow(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(texts.SUMMARY_CANCELLED)
    await call.answer()
