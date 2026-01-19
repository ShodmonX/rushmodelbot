from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def teacher_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 New Test")],
            [KeyboardButton(text="📋 My Tests")],
            [KeyboardButton(text="👥 My Students")],
            [KeyboardButton(text="ℹ️ Profile")],
            [KeyboardButton(text="🆘 Help")],
        ],
        resize_keyboard=True,
    )
