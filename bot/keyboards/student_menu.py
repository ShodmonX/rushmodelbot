from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def student_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Join Test")],
            [KeyboardButton(text="📄 My Results")],
            [KeyboardButton(text="ℹ️ Profile")],
            [KeyboardButton(text="🆘 Help")],
        ],
        resize_keyboard=True,
    )
