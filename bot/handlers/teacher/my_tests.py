from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot import texts
from shared.db.models import UserRole, UserStatus
from shared.services.attempt_service import count_attempts_for_test
from shared.services.test_service import list_teacher_tests
from shared.services.users import get_user_by_telegram_id

router = Router()


async def _require_teacher(message: Message, session: AsyncSession):
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if not user or user.status != UserStatus.ACTIVE or user.role != UserRole.TEACHER:
        await message.answer(texts.TEACHER_ONLY)
        return None
    return user


@router.message(F.text == "📋 My Tests")
async def my_tests(message: Message, session: AsyncSession) -> None:
    user = await _require_teacher(message, session)
    if not user:
        return

    tests = await list_teacher_tests(session, user.id)
    if not tests:
        await message.answer(texts.NO_TESTS)
        return

    lines = [texts.MY_TESTS_TITLE]
    for test in tests[:10]:
        attempts = await count_attempts_for_test(session, test.id)
        lines.append(
            f"{test.title} | {test.status.value} | {test.access_code} | attempts: {attempts}"
        )
    await message.answer("\n".join(lines))
