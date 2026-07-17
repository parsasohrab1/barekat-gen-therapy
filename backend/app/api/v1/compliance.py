from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_db, require_role
from app.core.security import Role
from app.schemas.compliance import AuditLogResponse, GmpRecordRequest, PseudonymizeRequest
from app.services.compliance_service import ComplianceService

router = APIRouter()
compliance = ComplianceService()


@router.post("/patients/pseudonymize")
def pseudonymize_patient(
    payload: PseudonymizeRequest,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.ADMIN)),
):
    """HIPAA/GDPR — pseudonymize patient identifier."""
    try:
        return compliance.pseudonymize_patient(db, payload.patient_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/patients/{patient_id}")
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role(Role.ADMIN)),
):
    """GDPR — right to erasure."""
    try:
        return compliance.delete_patient_data(db, patient_id, user_id=user.id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/gmp/record")
def record_gmp_step(
    payload: GmpRecordRequest,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """GMP traceability — record LNP production step."""
    record = compliance.record_gmp_step(
        db,
        batch_id=payload.batch_id,
        step=payload.step,
        operator=payload.operator,
        equipment_id=payload.equipment_id,
        parameters=payload.parameters,
    )
    return {"record_id": str(record.id), "batch_id": record.batch_id, "step": record.step}


@router.get("/gmp/trace/{batch_id}")
def get_gmp_trace(
    batch_id: str,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
):
    records = compliance.get_gmp_trace(db, batch_id)
    return [
        {
            "step": r.step,
            "operator": r.operator,
            "equipment_id": r.equipment_id,
            "parameters": r.parameters,
            "recorded_at": r.recorded_at.isoformat(),
        }
        for r in records
    ]


@router.get("/audit", response_model=list[AuditLogResponse])
def get_audit_trail(
    action_prefix: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.ADMIN)),
):
    """21 CFR Part 11 — clinical decision audit trail."""
    logs = compliance.get_audit_trail(db, action_prefix=action_prefix, limit=limit)
    return [
        AuditLogResponse(
            id=str(log.id),
            action=log.action,
            model_version=log.model_version,
            input_hash=log.input_hash,
            details=log.metadata,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]
