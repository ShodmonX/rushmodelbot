"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


user_role_enum = ENUM("teacher", "student", name="user_role", create_type=False)
user_status_enum = ENUM("pending", "active", "blocked", name="user_status", create_type=False)


def upgrade() -> None:
    user_role_enum.create(op.get_bind(), checkfirst=True)
    user_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False, unique=True),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("teacher_ref_token", sa.String(length=64), unique=True),
        sa.Column("status", user_status_enum, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_users_teacher_id", "users", ["teacher_id"])
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_telegram_id", sa.BigInteger()),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_index("ix_users_teacher_id", table_name="users")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
    user_status_enum.drop(op.get_bind(), checkfirst=True)
    user_role_enum.drop(op.get_bind(), checkfirst=True)
