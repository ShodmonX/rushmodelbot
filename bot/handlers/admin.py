from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot import texts
from bot.keyboards.reply import admin_menu_keyboard
from shared.settings import get_settings

router = Router()
settings = get_settings()


@router.message(Command("admin"))
async def admin_entry(message: Message) -> None:
    if message.from_user.id not in settings.admin_ids:
        await message.answer(texts.ADMIN_ONLY)
        return

    await message.answer(texts.ADMIN_DONE, reply_markup=admin_menu_keyboard())
