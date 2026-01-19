"""seed math template

Revision ID: 0005_seed_math_template
Revises: 0004_v1_core_tables
Create Date: 2024-01-05 00:00:00.000000
"""

import json

from alembic import op
import sqlalchemy as sa

revision = "0005_seed_math_template"
down_revision = "0004_v1_core_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    structure = {
        "total_time_minutes": 150,
        "sections": [
            {
                "code": "Y1",
                "name": "Single choice",
                "item_count": 32,
                "answer_format": "ABCD_STRING",
                "allowed_chars": ["A", "B", "C", "D"],
            },
            {
                "code": "Y2",
                "name": "Variantli (5 ta javobli) savollar",
                "item_count": 3,
                "item_numbers": [33, 34, 35],
                "answer_format": "CHOICE_ABCDE",
                "allowed_chars": ["A", "B", "C", "D", "E"],
            },
            {
                "code": "O",
                "name": "Ochiq savollar",
                "item_count": 10,
                "item_numbers": [36, 37, 38, 39, 40, 41, 42, 43, 44, 45],
                "answer_format": "OPEN_AB",
                "subparts": ["a", "b"],
                "value_type": "number_or_fraction",
                "accept_decimal": True,
            },
        ],
    }

    payload = json.dumps(structure, ensure_ascii=True)
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO subject_templates (subject_code, subject_name, description, structure_json, is_active)
            VALUES (:code, :name, :desc, CAST(:structure AS jsonb), true)
            ON CONFLICT (subject_code) DO NOTHING
            """
        ),
        {
            "code": "math",
            "name": "Mathematics (NC)",
            "desc": "National Certificate structure",
            "structure": payload,
        },
    )
    bind.execute(
        sa.text(
            "UPDATE subject_templates SET structure_json = CAST(:structure AS jsonb) WHERE subject_code = :code"
        ),
        {"code": "math", "structure": payload},
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM subject_templates WHERE subject_code = :code").bindparams(code="math"))
