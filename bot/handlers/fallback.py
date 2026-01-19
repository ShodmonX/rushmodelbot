from aiogram import Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot import texts
from shared.db.models import UserStatus
from shared.services.users import get_user_by_telegram_id

router = Router()


@router.message()
async def fallback(message: Message, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if not user or user.status != UserStatus.ACTIVE:
        await message.answer(texts.NEED_START)
        return

    await message.answer(texts.UNKNOWN_COMMAND)
