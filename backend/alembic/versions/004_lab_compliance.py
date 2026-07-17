"""lab integration, gmp, invitro tables

Revision ID: 004
Revises: 003
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lab_samples",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(100), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("sample_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="received"),
        sa.Column("metadata", JSONB, nullable=False, server_default="{}"),
        sa.Column("received_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_lab_samples_external_id", "lab_samples", ["external_id"])

    op.create_table(
        "invitro_results",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("sample_id", UUID(as_uuid=True), nullable=False),
        sa.Column("lipid_smiles", sa.Text(), nullable=False),
        sa.Column("transfection_efficiency", sa.Float(), nullable=False),
        sa.Column("toxicity_score", sa.Float(), nullable=False),
        sa.Column("cell_line", sa.String(100), nullable=False),
        sa.Column("is_real_data", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("imported_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_invitro_results_sample_id", "invitro_results", ["sample_id"])

    op.create_table(
        "synthesis_orders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("design_job_id", sa.String(36), nullable=True),
        sa.Column("lipid_smiles", sa.Text(), nullable=False),
        sa.Column("lipid_name", sa.String(255), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="queued"),
        sa.Column("mqtt_message_id", sa.String(100), nullable=True),
        sa.Column("batch_id", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_synthesis_orders_batch_id", "synthesis_orders", ["batch_id"])

    op.create_table(
        "gmp_batch_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_id", sa.String(50), nullable=False),
        sa.Column("step", sa.String(100), nullable=False),
        sa.Column("operator", sa.String(100), nullable=False),
        sa.Column("equipment_id", sa.String(100), nullable=True),
        sa.Column("parameters", JSONB, nullable=False, server_default="{}"),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_gmp_batch_records_batch_id", "gmp_batch_records", ["batch_id"])

    op.add_column("patients", sa.Column("pseudonymized_id", sa.String(64), nullable=True))
    op.add_column("patients", sa.Column("consent_given", sa.Boolean(), server_default=sa.true()))
    op.add_column("patients", sa.Column("deleted_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("patients", "deleted_at")
    op.drop_column("patients", "consent_given")
    op.drop_column("patients", "pseudonymized_id")
    op.drop_index("ix_gmp_batch_records_batch_id", table_name="gmp_batch_records")
    op.drop_table("gmp_batch_records")
    op.drop_index("ix_synthesis_orders_batch_id", table_name="synthesis_orders")
    op.drop_table("synthesis_orders")
    op.drop_index("ix_invitro_results_sample_id", table_name="invitro_results")
    op.drop_table("invitro_results")
    op.drop_index("ix_lab_samples_external_id", table_name="lab_samples")
    op.drop_table("lab_samples")
