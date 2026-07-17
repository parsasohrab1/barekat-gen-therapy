"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lipids",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("smiles", sa.Text(), nullable=False),
        sa.Column("molecular_weight", sa.Float(), nullable=True),
        sa.Column("log_p", sa.Float(), nullable=True),
        sa.Column("lipid_class", sa.String(50), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_lipids_lipid_class", "lipids", ["lipid_class"])

    op.create_table(
        "patients",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(20), nullable=False),
        sa.Column("disease_severity", sa.Float(), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_patients_is_synthetic", "patients", ["is_synthetic"])


def downgrade() -> None:
    op.drop_index("ix_patients_is_synthetic", table_name="patients")
    op.drop_table("patients")
    op.drop_index("ix_lipids_lipid_class", table_name="lipids")
    op.drop_table("lipids")
