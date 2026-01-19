from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot import texts
from bot.keyboards.inline import (
    BACK_TO_PHONE,
    BACK_TO_ROLE,
    ROLE_STUDENT,
    ROLE_TEACHER,
    back_to_phone_keyboard,
    back_to_role_keyboard,
    role_keyboard,
)
from bot.keyboards.reply import phone_request_keyboard
from bot.states.onboarding import OnboardingStates
from shared.db.models import UserRole, UserStatus
from shared.services.admin_notify import notify_new_lead, notify_registration_completed
from shared.services.lead_service import TelegramUserInfo, create_or_update_lead
from shared.settings import get_settings
from shared.utils.validators import is_valid_name, normalize_name
from shared.services.users import (
    activate_user,
    ensure_unique_teacher_token,
    get_teacher_by_ref_token,
    get_user_by_id,
    get_user_by_phone,
    get_user_by_telegram_id,
)

router = Router()
settings = get_settings()


async def _send_phone_step(message: Message) -> None:
    await message.answer(texts.PHONE_PROMPT, reply_markup=phone_request_keyboard())
    await message.answer("⬅️ Orqaga", reply_markup=back_to_role_keyboard())


async def _send_name_step(message: Message) -> None:
    await message.answer(texts.NAME_PROMPT, reply_markup=back_to_phone_keyboard())


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    payload = ""
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) == 2:
            payload = parts[1]

    ref_token = None
    test_code = None
    if payload.startswith("ref_"):
        ref_token = payload.replace("ref_", "", 1).strip()
    if payload.startswith("test_"):
        test_code = payload.replace("test_", "", 1).strip()

    lead_user = TelegramUserInfo(
        telegram_id=message.from_user.id,
        username=f"@{message.from_user.username}" if message.from_user.username else None,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code,
    )
    lead, created = await create_or_update_lead(session, lead_user, ref_token)
    if created:
        await notify_new_lead(message.bot, lead)

    user = await get_user_by_telegram_id(session, message.from_user.id)
    if user and user.status == UserStatus.ACTIVE:
        await state.clear()
        if test_code and user.role == UserRole.STUDENT:
            from bot.handlers.student.join_test import start_join_with_code

            await start_join_with_code(message, state, session, test_code)
            return
        await message.answer(texts.WELCOME_BACK, reply_markup=_menu_keyboard_for_role(user.role))
        return

    if message.from_user.id in settings.admin_ids:
        from bot.handlers.admin_onboarding import start_admin_flow

        await start_admin_flow(message, state, session)
        return

    await state.clear()
    if test_code:
        await state.update_data(pending_test_code=test_code)

    if ref_token:
        teacher = await get_teacher_by_ref_token(session, ref_token)
        teacher_id = teacher.id if teacher else None
        if teacher is None:
            await message.answer(texts.REFERRAL_NOT_FOUND)
        await state.set_state(OnboardingStates.entering_phone)
        await state.update_data(role=UserRole.STUDENT.value, teacher_id=teacher_id)
        await _send_phone_step(message)
    else:
        await state.set_state(OnboardingStates.choosing_role)
        await state.update_data(ref_token=ref_token)
        await message.answer(texts.START_ROLE_PROMPT, reply_markup=role_keyboard())


@router.callback_query(F.data == BACK_TO_ROLE)
async def back_to_role(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(OnboardingStates.choosing_role)
    await call.message.edit_text(texts.START_ROLE_PROMPT, reply_markup=role_keyboard())
    await call.answer()


@router.callback_query(F.data.in_({ROLE_TEACHER, ROLE_STUDENT}))
async def choose_role(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    role = UserRole.TEACHER if call.data == ROLE_TEACHER else UserRole.STUDENT
    data = await state.get_data()
    teacher_id = None

    if role == UserRole.STUDENT and data.get("ref_token"):
        teacher = await get_teacher_by_ref_token(session, data["ref_token"])
        if teacher:
            teacher_id = teacher.id
        else:
            await call.message.answer(texts.REFERRAL_NOT_FOUND)

    await state.update_data(role=role.value, teacher_id=teacher_id)
    await state.set_state(OnboardingStates.entering_phone)
    await call.message.delete()
    await _send_phone_step(call.message)
    await call.answer()


@router.callback_query(F.data == BACK_TO_PHONE)
async def back_to_phone(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(OnboardingStates.entering_phone)
    await _send_phone_step(call.message)
    await call.answer()


@router.message(OnboardingStates.entering_phone, F.contact)
async def handle_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.answer(texts.PHONE_OWNERSHIP_FAIL)
        return

    phone = contact.phone_number
    existing = await get_user_by_phone(session, phone)
    if existing and existing.telegram_id != message.from_user.id:
        await message.answer(texts.PHONE_ALREADY_USED)
        return

    await state.update_data(phone=phone)
    await state.set_state(OnboardingStates.entering_name)
    await _send_name_step(message)


@router.message(OnboardingStates.entering_phone)
async def handle_phone_invalid(message: Message) -> None:
    await message.answer(texts.PHONE_TEXT_ONLY)


@router.message(OnboardingStates.entering_name, F.text)
async def handle_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    name = normalize_name(message.text or "")
    if not is_valid_name(name):
        await message.answer(texts.NAME_INVALID)
        return

    data = await state.get_data()
    role_value = data.get("role")
    phone = data.get("phone")
    teacher_id = data.get("teacher_id")
    if not role_value or not phone:
        await message.answer(texts.MISSING_ROLE_PHONE)
        return

    role = UserRole(role_value)
    teacher_ref_token = None
    if role == UserRole.TEACHER:
        teacher_ref_token = await ensure_unique_teacher_token(session)

    user = await activate_user(
        session=session,
        telegram_id=message.from_user.id,
        name=name,
        phone=phone,
        role=role,
        teacher_id=teacher_id,
        teacher_ref_token=teacher_ref_token,
    )
    pending_test_code = data.get("pending_test_code")
    await state.clear()

    if role == UserRole.TEACHER:
        await message.answer(
            texts.REGISTER_DONE_TEACHER, reply_markup=_menu_keyboard_for_role(role)
        )
    else:
        await message.answer(
            texts.REGISTER_DONE_STUDENT, reply_markup=_menu_keyboard_for_role(role)
        )

    if role == UserRole.STUDENT and teacher_id:
        teacher = await get_user_by_id(session, teacher_id)
        if teacher:
            await message.answer(texts.REFERRAL_SUCCESS.format(teacher_name=teacher.name))

    await notify_registration_completed(message.bot, session, user)

    if role == UserRole.STUDENT and pending_test_code:
        from bot.handlers.student.join_test import start_join_with_code

        await start_join_with_code(message, state, session, pending_test_code)
        return


@router.message(OnboardingStates.entering_name)
async def handle_name_invalid(message: Message) -> None:
    await message.answer(texts.NAME_TEXT_ONLY)


def _menu_keyboard_for_role(role: UserRole):
    from bot.keyboards.reply import student_menu_keyboard, teacher_menu_keyboard

    return teacher_menu_keyboard() if role == UserRole.TEACHER else student_menu_keyboard()
