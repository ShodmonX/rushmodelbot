import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.models import Base


class AttemptStatus(str, enum.Enum):
    STARTED = "started"
    SUBMITTED = "submitted"
    EXPIRED = "expired"


class Attempt(Base):
    __tablename__ = "attempts"
    __table_args__ = (
        UniqueConstraint("test_id", "student_id", name="uq_attempt_test_student"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(
            AttemptStatus,
            name="attempt_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=AttemptStatus.STARTED,
    )
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    score_total: Mapped[int | None] = mapped_column(Integer)
    score_y1: Mapped[int | None] = mapped_column(Integer)
    score_y2: Mapped[int | None] = mapped_column(Integer)
    score_o: Mapped[int | None] = mapped_column(Integer)
    incorrect_items_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
