from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot import texts
from shared.db.models import UserRole, UserStatus
from shared.models.attempt import Attempt
from shared.models.test import Test
from shared.services.users import get_user_by_telegram_id

router = Router()


async def _require_student(message: Message, session: AsyncSession):
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if not user or user.status != UserStatus.ACTIVE or user.role != UserRole.STUDENT:
        await message.answer(texts.STUDENT_ONLY)
        return None
    return user


@router.message(F.text == "📄 My Results")
async def my_results(message: Message, session: AsyncSession) -> None:
    user = await _require_student(message, session)
    if not user:
        return

    result = await session.execute(
        select(Attempt, Test)
        .join(Test, Attempt.test_id == Test.id)
        .where(Attempt.student_id == user.id)
        .order_by(Attempt.created_at.desc())
    )

    rows = result.all()
    if not rows:
        await message.answer(texts.NO_RESULTS)
        return

    lines = [texts.RESULTS_TITLE]
    for attempt, test in rows[:10]:
        lines.append(
            f"{test.title} | {attempt.score_total or 0} | {attempt.status.value}"
        )
    await message.answer("\n".join(lines))
