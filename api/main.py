import logging

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from api.health import router as health_router
from shared.db.session import get_async_session

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

app = FastAPI()
app.include_router(health_router)

@app.get("/internal/db-check")
async def db_check(session: AsyncSession = Depends(get_async_session)) -> dict:
    await session.execute(text("SELECT 1"))
    return {"status": "ok"}
