from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.engine import SessionLocal


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
