import secrets
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.models import User, UserRole, UserStatus


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_phone(session: AsyncSession, phone: str) -> User | None:
    result = await session.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def get_teacher_by_ref_token(session: AsyncSession, token: str) -> User | None:
    result = await session.execute(
        select(User).where(User.teacher_ref_token == token, User.role == UserRole.TEACHER)
    )
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    role: UserRole,
    name: str,
    phone: str,
    teacher_id: int | None = None,
    teacher_ref_token: str | None = None,
) -> User:
    user = User(
        telegram_id=telegram_id,
        role=role,
        name=name,
        phone=phone,
        teacher_id=teacher_id,
        teacher_ref_token=teacher_ref_token,
        status=UserStatus.ACTIVE,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_pending(
    session: AsyncSession,
    telegram_id: int,
    role: UserRole | None = None,
    phone: str | None = None,
    name: str | None = None,
    teacher_id: int | None = None,
    teacher_ref_token: str | None = None,
) -> User:
    user = await get_user_by_telegram_id(session, telegram_id)
    if user is None:
        user = User(
            telegram_id=telegram_id,
            role=role or UserRole.STUDENT,
            name=name or "",
            phone=phone or "",
            teacher_id=teacher_id,
            teacher_ref_token=teacher_ref_token,
            status=UserStatus.PENDING,
        )
        session.add(user)
    else:
        if role is not None:
            user.role = role
        if phone is not None:
            user.phone = phone
        if name is not None:
            user.name = name
        if teacher_id is not None:
            user.teacher_id = teacher_id
        if teacher_ref_token is not None:
            user.teacher_ref_token = teacher_ref_token
        user.status = UserStatus.PENDING

    await session.commit()
    await session.refresh(user)
    return user


async def activate_user(
    session: AsyncSession,
    telegram_id: int,
    name: str,
    phone: str,
    role: UserRole,
    teacher_id: int | None = None,
    teacher_ref_token: str | None = None,
) -> User:
    user = await get_user_by_telegram_id(session, telegram_id)
    if user is None:
        user = User(
            telegram_id=telegram_id,
            role=role,
            name=name,
            phone=phone,
            teacher_id=teacher_id,
            teacher_ref_token=teacher_ref_token,
            status=UserStatus.ACTIVE,
        )
        session.add(user)
    else:
        user.role = role
        user.name = name
        user.phone = phone
        user.teacher_id = teacher_id
        if teacher_ref_token is not None:
            user.teacher_ref_token = teacher_ref_token
        user.status = UserStatus.ACTIVE

    await session.commit()
    await session.refresh(user)
    return user


async def list_teacher_students(session: AsyncSession, teacher_id: int) -> Sequence[User]:
    result = await session.execute(
        select(User).where(User.teacher_id == teacher_id).order_by(User.created_at)
    )
    return result.scalars().all()


async def ensure_unique_teacher_token(session: AsyncSession) -> str:
    while True:
        token = secrets.token_urlsafe(8)
        existing = await get_teacher_by_ref_token(session, token)
        if existing is None:
            return token
