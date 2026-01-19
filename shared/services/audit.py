import json
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.models import AuditLog


async def log_event(
    session: AsyncSession,
    actor_telegram_id: int | None,
    event_type: str,
    payload: dict,
) -> None:
    record = AuditLog(
        actor_telegram_id=actor_telegram_id,
        event_type=event_type,
        payload_json=json.dumps(payload, ensure_ascii=True),
    )
    session.add(record)
    await session.commit()
