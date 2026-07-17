"""Compliance — HIPAA/GDPR anonymization, erasure, Part 11, GMP."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models import AuditLog, GmpBatchRecord, Patient
from app.services.audit_service import AuditService


class ComplianceService:
    def __init__(self) -> None:
        self.audit = AuditService()

    def pseudonymize_patient(self, db: Session, patient_id: str) -> dict:
        """HIPAA/GDPR — replace direct identifier with pseudonym."""
        patient = db.get(Patient, patient_id)
        if patient is None or patient.deleted_at:
            raise ValueError("Patient not found")

        pseudo = hashlib.sha256(f"{patient_id}:barekat".encode()).hexdigest()[:16]
        patient.pseudonymized_id = f"PSE_{pseudo}"
        db.commit()

        self.audit.log(
            db,
            action="compliance.pseudonymize",
            details={"original_id_hash": hashlib.sha256(patient_id.encode()).hexdigest(), "pseudonymized_id": patient.pseudonymized_id},
        )
        return {"patient_id": patient_id, "pseudonymized_id": patient.pseudonymized_id}

    def delete_patient_data(self, db: Session, patient_id: str, user_id: uuid.UUID | None = None) -> dict:
        """GDPR — right to erasure (soft delete + anonymize fields)."""
        patient = db.get(Patient, patient_id)
        if patient is None:
            raise ValueError("Patient not found")

        patient.age = 0
        patient.gender = "REDACTED"
        patient.disease_severity = 0.0
        patient.deleted_at = datetime.utcnow()
        patient.consent_given = False
        db.commit()

        self.audit.log(
            db,
            action="compliance.gdpr_delete",
            user_id=user_id,
            details={"patient_id_hash": hashlib.sha256(patient_id.encode()).hexdigest(), "regulatory": "GDPR"},
        )
        return {"patient_id": patient_id, "deleted_at": patient.deleted_at.isoformat()}

    def record_gmp_step(
        self,
        db: Session,
        batch_id: str,
        step: str,
        operator: str,
        equipment_id: str | None = None,
        parameters: dict | None = None,
    ) -> GmpBatchRecord:
        record = GmpBatchRecord(
            batch_id=batch_id,
            step=step,
            operator=operator,
            equipment_id=equipment_id,
            parameters=parameters or {},
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        self.audit.log_gmp_event(db, batch_id=batch_id, step=step, operator=operator, details=parameters)
        return record

    def get_audit_trail(
        self,
        db: Session,
        action_prefix: str | None = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        if action_prefix:
            stmt = stmt.where(AuditLog.action.like(f"{action_prefix}%"))
        return list(db.scalars(stmt))

    def get_gmp_trace(self, db: Session, batch_id: str) -> list[GmpBatchRecord]:
        stmt = (
            select(GmpBatchRecord)
            .where(GmpBatchRecord.batch_id == batch_id)
            .order_by(GmpBatchRecord.recorded_at)
        )
        return list(db.scalars(stmt))
