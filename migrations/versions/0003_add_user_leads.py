"""add user_leads

Revision ID: 0003_add_user_leads
Revises: 0002_add_registered_notified_at
Create Date: 2024-01-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_add_user_leads"
down_revision = "0002_add_registered_notified_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("username", sa.String(length=64)),
        sa.Column("first_name", sa.String(length=64)),
        sa.Column("last_name", sa.String(length=64)),
        sa.Column("language_code", sa.String(length=16)),
        sa.Column("ref_token", sa.String(length=64)),
        sa.Column("started_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("is_registered", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("registered_at", sa.DateTime(), nullable=True),
        sa.Column("created_ip", sa.String(length=64)),
        sa.Column("user_agent", sa.String(length=255)),
        sa.Column("metadata_json", postgresql.JSONB()),
    )


def downgrade() -> None:
    op.drop_table("user_leads")
