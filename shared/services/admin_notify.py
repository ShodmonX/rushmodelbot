import logging
from datetime import datetime

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.models import User, UserLead
from shared.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def notify_new_lead(bot: Bot, lead: UserLead) -> None:
    if not settings.admin_ids:
        return

    message = (
        "🆕 Yangi foydalanuvchi botga kirdi (lead yaratildi)\n"
        f"TG ID: {lead.telegram_id}\n"
        f"Username: {lead.username or '-'}\n"
        f"Name: {' '.join(filter(None, [lead.first_name, lead.last_name])) or '-'}\n"
        f"Lang: {lead.language_code or '-'}\n"
        f"Ref: {lead.ref_token or '-'}\n"
        f"Time: {lead.started_at:%Y-%m-%d %H:%M:%S}"
    )

    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, message)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to notify admin %s about lead", admin_id)


def _display_role(user: User) -> str:
    if user.telegram_id in settings.admin_ids:
        return "Admin"
    if user.role.value == "teacher":
        return "Teacher"
    return "Student"


async def notify_registration_completed(bot: Bot, session: AsyncSession, user: User) -> None:
    if not settings.admin_ids:
        return
    if getattr(user, "registered_notified_at", None) is not None:
        return

    teacher_info = "-"
    if user.teacher_id:
        result = await session.execute(select(User).where(User.id == user.teacher_id))
        teacher = result.scalar_one_or_none()
        teacher_info = teacher.name if teacher else str(user.teacher_id)

    message = (
        "✅ Foydalanuvchi ro‘yxatdan o‘tdi\n"
        f"Role: {_display_role(user)}\n"
        f"Name: {user.name}\n"
        f"Phone: {user.phone}\n"
        f"TG ID: {user.telegram_id}\n"
        f"Teacher: {teacher_info}"
    )

    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, message)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to notify admin %s about registration", admin_id)

    try:
        user.registered_notified_at = datetime.utcnow()
        session.add(user)
        result = await session.execute(
            select(UserLead).where(UserLead.telegram_id == user.telegram_id)
        )
        lead = result.scalar_one_or_none()
        if lead and not lead.is_registered:
            lead.is_registered = True
            lead.registered_at = datetime.utcnow()
            session.add(lead)
        await session.commit()
    except Exception:  # noqa: BLE001
        logger.exception("Failed to mark registration notification for %s", user.telegram_id)
