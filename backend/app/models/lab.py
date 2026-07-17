import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LabSample(Base):
    __tablename__ = "lab_samples"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # lims, import, robot
    sample_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="received")
    sample_metadata: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InVitroResult(Base):
    __tablename__ = "invitro_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    lipid_smiles: Mapped[str] = mapped_column(Text, nullable=False)
    transfection_efficiency: Mapped[float] = mapped_column(Float, nullable=False)
    toxicity_score: Mapped[float] = mapped_column(Float, nullable=False)
    cell_line: Mapped[str] = mapped_column(String(100), nullable=False)
    is_real_data: Mapped[bool] = mapped_column(Boolean, default=True)
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SynthesisOrder(Base):
    __tablename__ = "synthesis_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_job_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    lipid_smiles: Mapped[str] = mapped_column(Text, nullable=False)
    lipid_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="queued")
    mqtt_message_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    batch_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class GmpBatchRecord(Base):
    __tablename__ = "gmp_batch_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    step: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[str] = mapped_column(String(100), nullable=False)
    equipment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
