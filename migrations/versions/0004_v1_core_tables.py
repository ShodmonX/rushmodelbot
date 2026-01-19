"""v1 core tables

Revision ID: 0004_v1_core_tables
Revises: 0003_add_user_leads
Create Date: 2024-01-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM

revision = "0004_v1_core_tables"
down_revision = "0003_add_user_leads"
branch_labels = None
depends_on = None


test_status_enum = ENUM("draft", "published", "closed", name="test_status", create_type=False)
attempt_status_enum = ENUM("started", "submitted", "expired", name="attempt_status", create_type=False)


def upgrade() -> None:
    test_status_enum.create(op.get_bind(), checkfirst=True)
    attempt_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "subject_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_code", sa.String(length=64), nullable=False, unique=True),
        sa.Column("subject_name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=255)),
        sa.Column("structure_json", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "tests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "subject_template_id",
            sa.Integer(),
            sa.ForeignKey("subject_templates.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", test_status_enum, nullable=False, server_default="draft"),
        sa.Column("time_limit_minutes", sa.Integer()),
        sa.Column("material_file_id", sa.String(length=255)),
        sa.Column("material_caption", sa.String(length=255)),
        sa.Column("access_code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("published_at", sa.DateTime()),
        sa.Column("closed_at", sa.DateTime()),
    )

    op.create_table(
        "test_answer_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("test_id", sa.Integer(), sa.ForeignKey("tests.id"), nullable=False),
        sa.Column("section_code", sa.String(length=8), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("test_id", "section_code", name="uq_test_key"),
    )

    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("test_id", sa.Integer(), sa.ForeignKey("tests.id"), nullable=False),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", attempt_status_enum, nullable=False, server_default="started"),
        sa.Column("started_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("submitted_at", sa.DateTime()),
        sa.Column("score_total", sa.Integer()),
        sa.Column("score_y1", sa.Integer()),
        sa.Column("score_y2", sa.Integer()),
        sa.Column("score_o", sa.Integer()),
        sa.Column("incorrect_items_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("test_id", "student_id", name="uq_attempt_test_student"),
    )

    op.create_table(
        "attempt_answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("attempts.id"), nullable=False),
        sa.Column("section_code", sa.String(length=8), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("attempt_answers")
    op.drop_table("attempts")
    op.drop_table("test_answer_keys")
    op.drop_table("tests")
    op.drop_table("subject_templates")
    attempt_status_enum.drop(op.get_bind(), checkfirst=True)
    test_status_enum.drop(op.get_bind(), checkfirst=True)
