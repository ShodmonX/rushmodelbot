import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.models import Base


class TestStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subject_template_id: Mapped[int] = mapped_column(
        ForeignKey("subject_templates.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TestStatus] = mapped_column(
        Enum(
            TestStatus,
            name="test_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=TestStatus.DRAFT,
    )
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer)
    material_file_id: Mapped[str | None] = mapped_column(String(255))
    material_file_type: Mapped[str | None] = mapped_column(String(32))
    material_caption: Mapped[str | None] = mapped_column(String(255))
    access_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)
