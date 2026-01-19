"""add test material type

Revision ID: 0006_add_test_material_type
Revises: 0005_seed_math_template
Create Date: 2024-01-06 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0006_add_test_material_type"
down_revision = "0005_seed_math_template"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tests", sa.Column("material_file_type", sa.String(length=32)))


def downgrade() -> None:
    op.drop_column("tests", "material_file_type")
