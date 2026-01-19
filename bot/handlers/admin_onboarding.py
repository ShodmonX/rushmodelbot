from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot import texts
from bot.keyboards.reply import admin_menu_keyboard, phone_request_keyboard
from bot.states.admin_onboarding import AdminOnboardingStates
from shared.db.models import UserRole, UserStatus
from shared.services.admin_notify import notify_registration_completed
from shared.services.users import activate_user, get_user_by_phone, get_user_by_telegram_id
from shared.utils.validators import is_valid_name, normalize_name

router = Router()


async def start_admin_flow(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if user and user.status == UserStatus.ACTIVE:
        await state.clear()
        await message.answer(texts.WELCOME_BACK, reply_markup=admin_menu_keyboard())
        return

    await state.clear()
    await state.set_state(AdminOnboardingStates.entering_phone)
    await message.answer(texts.ADMIN_PROFILE_START)
    await message.answer(texts.PHONE_PROMPT, reply_markup=phone_request_keyboard())


@router.message(AdminOnboardingStates.entering_phone, F.contact)
async def admin_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
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
    await state.set_state(AdminOnboardingStates.entering_name)
    await message.answer(texts.NAME_PROMPT)


@router.message(AdminOnboardingStates.entering_phone)
async def admin_phone_invalid(message: Message) -> None:
    await message.answer(texts.PHONE_TEXT_ONLY)


@router.message(AdminOnboardingStates.entering_name, F.text)
async def admin_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    name = normalize_name(message.text or "")
    if not is_valid_name(name):
        await message.answer(texts.NAME_INVALID)
        return

    data = await state.get_data()
    phone = data.get("phone")
    if not phone:
        await message.answer(texts.PHONE_TEXT_ONLY)
        return

    user = await activate_user(
        session=session,
        telegram_id=message.from_user.id,
        name=name,
        phone=phone,
        role=UserRole.STUDENT,
        teacher_id=None,
        teacher_ref_token=None,
    )
    await state.clear()
    await message.answer(texts.ADMIN_DONE, reply_markup=admin_menu_keyboard())

    await notify_registration_completed(message.bot, session, user)


@router.message(AdminOnboardingStates.entering_name)
async def admin_name_invalid(message: Message) -> None:
    await message.answer(texts.NAME_TEXT_ONLY)
