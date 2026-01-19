from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot import texts
from bot.keyboards.reply import admin_menu_keyboard
from shared.db.models import UserRole, UserStatus
from shared.settings import get_settings
from shared.services.users import get_user_by_telegram_id, list_teacher_students

router = Router()
settings = get_settings()


async def _require_active_user(message: Message, session: AsyncSession):
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if not user or user.status != UserStatus.ACTIVE:
        await message.answer(texts.NEED_START)
        return None
    return user


@router.message(F.text.in_({"ℹ️ Profil", "👤 Profil", "ℹ️ Profile"}))
async def profile(message: Message, session: AsyncSession) -> None:
    user = await _require_active_user(message, session)
    if not user:
        return

    if user.telegram_id in settings.admin_ids:
        role_label = "Admin"
    elif user.role == UserRole.TEACHER:
        role_label = texts.ROLE_TEACHER
    else:
        role_label = texts.ROLE_STUDENT
    lines = [
        texts.PROFILE_TITLE,
        f"Ism: {user.name}",
        f"Telefon: {user.phone}",
        f"Rol: {role_label}",
    ]
    if user.role == UserRole.TEACHER and user.teacher_ref_token:
        bot_username = (await message.bot.get_me()).username
        lines.append(
            f"Referral link: https://t.me/{bot_username}?start=ref_{user.teacher_ref_token}"
        )
    await message.answer("\n".join(lines))


@router.message(F.text.in_({"🆘 Yordam", "🆘 Help"}))
async def help_message(message: Message) -> None:
    await message.answer(texts.HELP_TEXT)


@router.message(F.text.in_({"📢 Broadcast (keyinroq)", "🧾 Loglar (keyinroq)"}))
async def admin_placeholders(message: Message) -> None:
    await message.answer(texts.ADMIN_SOON)


@router.message(F.text.in_({"👥 O‘quvchilarim", "👥 My Students"}))
async def students_list(message: Message, session: AsyncSession) -> None:
    user = await _require_active_user(message, session)
    if not user:
        return
    if user.telegram_id in settings.admin_ids:
        await message.answer(texts.TEACHER_ONLY, reply_markup=admin_menu_keyboard())
        return
    if user.role != UserRole.TEACHER:
        await message.answer(texts.TEACHER_ONLY)
        return

    students = await list_teacher_students(session, user.id)
    if not students:
        await message.answer(texts.NO_STUDENTS)
        return

    lines = [texts.STUDENTS_LIST_TITLE]
    for idx, student in enumerate(students, start=1):
        lines.append(
            f"{idx}. {student.name} | {student.phone} | {student.created_at:%Y-%m-%d}"
        )
    await message.answer("\n".join(lines))
