from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models.subject_template import SubjectTemplate


async def list_active_templates(session: AsyncSession) -> list[SubjectTemplate]:
    result = await session.execute(
        select(SubjectTemplate).where(SubjectTemplate.is_active.is_(True))
    )
    return list(result.scalars().all())


async def get_template_by_id(
    session: AsyncSession, template_id: int
) -> SubjectTemplate | None:
    result = await session.execute(
        select(SubjectTemplate).where(SubjectTemplate.id == template_id)
    )
    return result.scalar_one_or_none()


async def get_template_by_code(
    session: AsyncSession, subject_code: str
) -> SubjectTemplate | None:
    result = await session.execute(
        select(SubjectTemplate).where(SubjectTemplate.subject_code == subject_code)
    )
    return result.scalar_one_or_none()
