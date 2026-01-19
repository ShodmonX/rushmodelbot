"""add registered_notified_at

Revision ID: 0002_add_registered_notified_at
Revises: 0001_initial
Create Date: 2024-01-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_registered_notified_at"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("registered_notified_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "registered_notified_at")
