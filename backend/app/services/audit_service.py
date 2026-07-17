import hashlib
import json
import uuid

from sqlalchemy.orm import Session

from app.models import AuditLog


class AuditService:
    def log(
        self,
        db: Session,
        action: str,
        user_id: uuid.UUID | None = None,
        model_version: str | None = None,
        input_payload: dict | None = None,
        details: dict | None = None,
    ) -> AuditLog:
        input_hash = None
        if input_payload is not None:
            normalized = json.dumps(input_payload, sort_keys=True, default=str)
            input_hash = hashlib.sha256(normalized.encode()).hexdigest()

        entry = AuditLog(
            user_id=user_id,
            action=action,
            model_version=model_version,
            input_hash=input_hash,
            metadata=details or {},
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def log_clinical_decision(
        self,
        db: Session,
        user_id: uuid.UUID | None,
        decision_type: str,
        model_version: str,
        input_payload: dict,
        outcome: dict,
    ) -> AuditLog:
        return self.log(
            db,
            action=f"clinical.{decision_type}",
            user_id=user_id,
            model_version=model_version,
            input_payload=input_payload,
            details={
                "regulatory": "21_cfr_part_11",
                "outcome": outcome,
                "immutable": True,
            },
        )

    def log_gmp_event(
        self,
        db: Session,
        batch_id: str,
        step: str,
        operator: str,
        details: dict | None = None,
    ) -> AuditLog:
        return self.log(
            db,
            action=f"gmp.{step}",
            details={
                "regulatory": "gmp_traceability",
                "batch_id": batch_id,
                "operator": operator,
                **(details or {}),
            },
        )
