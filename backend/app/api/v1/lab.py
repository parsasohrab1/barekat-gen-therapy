from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_db, require_role
from app.core.security import Role
from app.schemas.lab import (
    InVitroImportRequest,
    LabSampleResponse,
    RetrainResponse,
    SynthesisDispatchRequest,
    SynthesisOrderResponse,
)
from app.services.lab_service import InVitroImporter, LimsConnector, RetrainService, RobotClient

router = APIRouter()
lims = LimsConnector()
robot = RobotClient()
importer = InVitroImporter()
retrain_service = RetrainService()


@router.post("/lims/sync", response_model=list[LabSampleResponse])
def sync_lims(
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """Sync samples from LIMS (remote URL or built-in demo mock)."""
    samples = lims.sync_samples(db)
    return [
        LabSampleResponse(
            id=str(s.id),
            external_id=s.external_id,
            source=s.source,
            sample_type=s.sample_type,
            status=s.status,
        )
        for s in samples
    ]


@router.get("/lims/mock")
def mock_lims_data():
    """Demo LIMS feed used when LIMS_BASE_URL points here or remote fetch fails."""
    from app.services.lab_service import MOCK_LIMS_SAMPLES

    return {"samples": MOCK_LIMS_SAMPLES, "mode": "demo_mock"}


@router.post("/synthesis/dispatch", response_model=SynthesisOrderResponse)
def dispatch_synthesis(
    payload: SynthesisDispatchRequest,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """Send synthesis command to lab robot via MQTT (SiLA 2 compatible payload)."""
    order = robot.dispatch_synthesis(
        db,
        lipid_smiles=payload.lipid_smiles,
        lipid_name=payload.lipid_name,
        design_job_id=payload.design_job_id,
    )
    return SynthesisOrderResponse(
        order_id=str(order.id),
        batch_id=order.batch_id,
        status=order.status,
        lipid_smiles=order.lipid_smiles,
    )


@router.post("/invitro/import")
def import_invitro(
    payload: InVitroImportRequest,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """Import in-vitro assay results for model feedback loop."""
    rows = [r.model_dump() for r in payload.results]
    imported = importer.import_results(db, rows)
    return {"imported_count": len(imported), "ids": [str(r.id) for r in imported]}


@router.post("/retrain", response_model=RetrainResponse)
def retrain_from_invitro(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """Retrain model using real in-vitro feedback data."""
    try:
        result = retrain_service.retrain_from_invitro(db, user_id=user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RetrainResponse(**result)
