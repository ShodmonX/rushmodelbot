from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot import texts
from bot.keyboards.student_menu import student_menu
from bot.keyboards.teacher_menu import teacher_menu


def phone_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=texts.PHONE_BUTTON, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def teacher_menu_keyboard() -> ReplyKeyboardMarkup:
    return teacher_menu()


def student_menu_keyboard() -> ReplyKeyboardMarkup:
    return student_menu()


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Profil")],
            [KeyboardButton(text="📢 Broadcast (keyinroq)")],
            [KeyboardButton(text="🧾 Loglar (keyinroq)")],
            [KeyboardButton(text="🆘 Yordam")],
        ],
        resize_keyboard=True,
    )
