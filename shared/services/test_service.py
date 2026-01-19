import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.test import Test, TestStatus
from shared.models.test_answer_key import TestAnswerKey
from shared.models.subject_template import SubjectTemplate


async def _generate_access_code(
    session: AsyncSession, subject_code: str
) -> str:
    prefix = subject_code.upper()
    while True:
        suffix = secrets.token_hex(2).upper()
        code = f"{prefix}-{suffix}"
        result = await session.execute(select(Test.id).where(Test.access_code == code))
        if result.scalar_one_or_none() is None:
            return code


async def create_test(
    session: AsyncSession,
    teacher_id: int,
    template: SubjectTemplate,
    title: str,
) -> Test:
    access_code = await _generate_access_code(session, template.subject_code)
    test = Test(
        teacher_id=teacher_id,
        subject_template_id=template.id,
        title=title,
        status=TestStatus.DRAFT,
        time_limit_minutes=template.structure_json.get("total_time_minutes"),
        access_code=access_code,
    )
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return test


async def update_material(
    session: AsyncSession,
    test: Test,
    file_id: str | None,
    file_type: str | None = None,
    caption: str | None = None,
) -> Test:
    test.material_file_id = file_id
    test.material_file_type = file_type
    test.material_caption = caption
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return test


async def publish_test(session: AsyncSession, test: Test) -> Test:
    test.status = TestStatus.PUBLISHED
    test.published_at = datetime.utcnow()
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return test


async def close_test(session: AsyncSession, test: Test) -> Test:
    test.status = TestStatus.CLOSED
    test.closed_at = datetime.utcnow()
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return test


async def get_test_by_id(session: AsyncSession, test_id: int) -> Test | None:
    result = await session.execute(select(Test).where(Test.id == test_id))
    return result.scalar_one_or_none()


async def get_test_by_code(session: AsyncSession, code: str) -> Test | None:
    result = await session.execute(select(Test).where(Test.access_code == code))
    return result.scalar_one_or_none()


async def list_teacher_tests(session: AsyncSession, teacher_id: int) -> list[Test]:
    result = await session.execute(
        select(Test)
        .where(Test.teacher_id == teacher_id)
        .order_by(Test.created_at.desc())
    )
    return list(result.scalars().all())


async def count_keys(session: AsyncSession, test_id: int) -> int:
    result = await session.execute(
        select(TestAnswerKey.id).where(TestAnswerKey.test_id == test_id)
    )
    return len(result.scalars().all())


async def get_keys(session: AsyncSession, test_id: int) -> list[TestAnswerKey]:
    result = await session.execute(
        select(TestAnswerKey).where(TestAnswerKey.test_id == test_id)
    )
    return list(result.scalars().all())
