from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def template_keyboard(items: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"tpl_{tpl_id}")] for tpl_id, name in items]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def publish_keyboard(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ E’lon qilish", callback_data=f"publish_{test_id}")]
        ]
    )


def confirm_submit_keyboard(attempt_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Yuborish", callback_data=f"submit_{attempt_id}")]
        ]
    )


def summary_teacher_keyboard(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"tconfirm_{test_id}"),
                InlineKeyboardButton(text="✏️ Qayta kiritish", callback_data=f"tedit_menu_{test_id}"),
            ],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"tcancel_{test_id}")],
        ]
    )


def summary_student_keyboard(attempt_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"sconfirm_{attempt_id}"),
                InlineKeyboardButton(text="✏️ Qayta kiritish", callback_data=f"sedit_menu_{attempt_id}"),
            ],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"scancel_{attempt_id}")],
        ]
    )


def summary_teacher_sections_keyboard(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="1-32 savollar (A-D variantli)",
                    callback_data=f"tedit_y1_{test_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="33-35 savollar (A-E variantli)",
                    callback_data=f"tedit_y2_{test_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="36-45 savollar (a va b)",
                    callback_data=f"tedit_o_{test_id}",
                )
            ],
        ]
    )


def summary_student_sections_keyboard(attempt_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="1-32 savollar (A-D variantli)",
                    callback_data=f"sedit_y1_{attempt_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="33-35 savollar (A-E variantli)",
                    callback_data=f"sedit_y2_{attempt_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="36-45 savollar (a va b)",
                    callback_data=f"sedit_o_{attempt_id}",
                )
            ],
        ]
    )


def teacher_progress_keyboard(test_id: int, stage: int) -> InlineKeyboardMarkup:
    if stage == 0:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ 1-32 javoblarni kiritish",
                        callback_data=f"tedit_y1_{test_id}",
                    )
                ],
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"tcancel_{test_id}")],
            ]
        )
    if stage == 1:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ 33-35 javoblarni kiritish",
                        callback_data=f"tedit_y2_{test_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✏️ 1-32 ni o'zgartirish",
                        callback_data=f"tedit_y1_{test_id}",
                    )
                ],
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"tcancel_{test_id}")],
            ]
        )
    if stage == 2:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ 36-45 javoblarni kiritish",
                        callback_data=f"tedit_o_{test_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✏️ 33-35 ni o'zgartirish",
                        callback_data=f"tedit_y2_{test_id}",
                    )
                ],
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"tcancel_{test_id}")],
            ]
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash (Testni e'lon qilish)",
                    callback_data=f"tconfirm_{test_id}",
                )
            ],
            [InlineKeyboardButton(text="✏️ Tahrirlash (bo'lim tanlash)", callback_data=f"tedit_menu_{test_id}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"tcancel_{test_id}")],
        ]
    )


def student_progress_keyboard(attempt_id: int, stage: int) -> InlineKeyboardMarkup:
    if stage == 0:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ 1-32 javoblarni kiritish",
                        callback_data=f"sedit_y1_{attempt_id}",
                    )
                ],
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"scancel_{attempt_id}")],
            ]
        )
    if stage == 1:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ 33-35 javoblarni kiritish",
                        callback_data=f"sedit_y2_{attempt_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✏️ 1-32 ni o'zgartirish",
                        callback_data=f"sedit_y1_{attempt_id}",
                    )
                ],
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"scancel_{attempt_id}")],
            ]
        )
    if stage == 2:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ 36-45 javoblarni kiritish",
                        callback_data=f"sedit_o_{attempt_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✏️ 33-35 ni o'zgartirish",
                        callback_data=f"sedit_y2_{attempt_id}",
                    )
                ],
                [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"scancel_{attempt_id}")],
            ]
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"sconfirm_{attempt_id}")],
            [InlineKeyboardButton(text="✏️ Tahrirlash (bo'lim tanlash)", callback_data=f"sedit_menu_{attempt_id}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"scancel_{attempt_id}")],
        ]
    )


def manage_test_keyboard(test_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Natijalarni ko‘rish", callback_data=f"results_{test_id}")],
            [InlineKeyboardButton(text="👥 O‘quvchilarim", callback_data="teacher_students")],
            [InlineKeyboardButton(text="🔒 Testni yopish", callback_data=f"close_{test_id}")],
            [InlineKeyboardButton(text="➕ Yangi test", callback_data="new_test")],
        ]
    )
