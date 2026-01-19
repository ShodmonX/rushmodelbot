from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import texts

ROLE_TEACHER = "role_teacher"
ROLE_STUDENT = "role_student"
BACK_TO_ROLE = "back_to_role"
BACK_TO_PHONE = "back_to_phone"


def role_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=texts.ROLE_TEACHER, callback_data=ROLE_TEACHER)],
            [InlineKeyboardButton(text=texts.ROLE_STUDENT, callback_data=ROLE_STUDENT)],
        ]
    )


def back_to_role_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data=BACK_TO_ROLE)]]
    )


def back_to_phone_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⬅️ Orqaga", callback_data=BACK_TO_PHONE)]]
    )
