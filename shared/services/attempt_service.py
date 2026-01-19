from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.attempt import Attempt, AttemptStatus
from shared.models.attempt_answer import AttemptAnswer
from shared.models.test import Test, TestStatus
from shared.models.test_answer_key import TestAnswerKey
from shared.services.scoring_service import compute_scores


class AttemptError(ValueError):
    pass


async def get_attempt(
    session: AsyncSession, test_id: int, student_id: int
) -> Attempt | None:
    result = await session.execute(
        select(Attempt).where(
            Attempt.test_id == test_id, Attempt.student_id == student_id
        )
    )
    return result.scalar_one_or_none()


async def start_attempt(
    session: AsyncSession, test: Test, student_id: int
) -> Attempt:
    if test.status != TestStatus.PUBLISHED:
        raise AttemptError("Test is not published")

    existing = await get_attempt(session, test.id, student_id)
    if existing:
        return existing

    attempt = Attempt(test_id=test.id, student_id=student_id, status=AttemptStatus.STARTED)
    session.add(attempt)
    await session.commit()
    await session.refresh(attempt)
    return attempt


async def submit_attempt(
    session: AsyncSession,
    attempt: Attempt,
    answers: dict,
) -> Attempt:
    result = await session.execute(
        select(TestAnswerKey).where(TestAnswerKey.test_id == attempt.test_id)
    )
    keys = {record.section_code: record.payload_json for record in result.scalars().all()}
    if not all(code in keys for code in ("Y1", "Y2", "O")):
        raise AttemptError("Answer key missing")

    scores = compute_scores(keys, answers)

    attempt.status = AttemptStatus.SUBMITTED
    attempt.submitted_at = datetime.utcnow()
    attempt.score_total = scores["score_total"]
    attempt.score_y1 = scores["score_y1"]
    attempt.score_y2 = scores["score_y2"]
    attempt.score_o = scores["score_o"]
    attempt.incorrect_items_json = scores["incorrect_items"]
    session.add(attempt)

    for code, payload in answers.items():
        record = AttemptAnswer(attempt_id=attempt.id, section_code=code, payload_json=payload)
        session.add(record)

    await session.commit()
    await session.refresh(attempt)
    return attempt


async def count_attempts_for_test(session: AsyncSession, test_id: int) -> int:
    result = await session.execute(
        select(Attempt.id).where(Attempt.test_id == test_id)
    )
    return len(result.scalars().all())
