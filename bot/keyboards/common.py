from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def back_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data=callback_data)]]
    )
