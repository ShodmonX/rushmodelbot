import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"


class UserStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    BLOCKED = "blocked"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda enum: [e.value for e in enum])
    )
    name: Mapped[str] = mapped_column(String(80))
    phone: Mapped[str] = mapped_column(String(32), unique=True)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    teacher_ref_token: Mapped[str | None] = mapped_column(String(64), unique=True)
    status: Mapped[UserStatus] = mapped_column(
        Enum(
            UserStatus,
            name="user_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=UserStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    registered_notified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    teacher: Mapped["User"] = relationship(remote_side=[id], foreign_keys=[teacher_id])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_telegram_id: Mapped[int | None] = mapped_column(BigInteger)
    event_type: Mapped[str] = mapped_column(String(64))
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


Index("ix_users_teacher_id", User.teacher_id)


class UserLead(Base):
    __tablename__ = "user_leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64))
    first_name: Mapped[str | None] = mapped_column(String(64))
    last_name: Mapped[str | None] = mapped_column(String(64))
    language_code: Mapped[str | None] = mapped_column(String(16))
    ref_token: Mapped[str | None] = mapped_column(String(64))
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    is_registered: Mapped[bool] = mapped_column(default=False)
    registered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_ip: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[dict | None] = mapped_column(JSONB)
