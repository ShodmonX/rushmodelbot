from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.models import UserLead


@dataclass
class TelegramUserInfo:
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str | None


async def create_or_update_lead(
    session: AsyncSession,
    user: TelegramUserInfo,
    ref_token: str | None,
) -> tuple[UserLead, bool]:
    result = await session.execute(
        select(UserLead).where(UserLead.telegram_id == user.telegram_id)
    )
    lead = result.scalar_one_or_none()

    now = datetime.utcnow()
    created = False
    if lead is None:
        lead = UserLead(
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            ref_token=ref_token,
            started_at=now,
            last_seen_at=now,
        )
        session.add(lead)
        created = True
    else:
        lead.username = user.username
        lead.first_name = user.first_name
        lead.last_name = user.last_name
        lead.language_code = user.language_code
        lead.ref_token = ref_token or lead.ref_token
        lead.last_seen_at = now

    await session.commit()
    await session.refresh(lead)
    return lead, created
