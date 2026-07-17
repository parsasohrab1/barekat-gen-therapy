import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_db, require_role
from app.core.security import Role
from app.schemas.design import DesignJobCreate, DesignJobResponse, DesignJobStatusResponse
from app.schemas.ranking import RankCandidatesRequest, RankCandidatesResponse
from app.services.job_service import JobService
from app.services.ranking_service import RankingService, RankingWeights
from workers.tasks.design import run_design_job

router = APIRouter()
job_service = JobService()
ranking_service = RankingService()


@router.post("/jobs", response_model=DesignJobResponse)
def create_design_job(
    payload: DesignJobCreate,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """ایجاد job طراحی لیپید — اجرای ناهمزمان."""
    job = job_service.create(db, job_type="design", input_payload=payload.model_dump(mode="json"))
    task = run_design_job.delay(str(job.id), payload.model_dump(mode="json"))
    job.celery_task_id = task.id
    db.commit()
    return DesignJobResponse(
        job_id=str(job.id),
        status="queued",
        estimated_duration_seconds=120,
    )


@router.get("/jobs/{job_id}", response_model=DesignJobStatusResponse)
def get_design_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
):
    job = job_service.get(db, job_id)
    if job is None or job.job_type != "design":
        raise HTTPException(status_code=404, detail="Design job not found")
    return DesignJobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        result=job.result,
        error_message=job.error_message,
    )


@router.post("/jobs/{job_id}/rank", response_model=RankCandidatesResponse)
def rank_design_candidates(
    job_id: uuid.UUID,
    payload: RankCandidatesRequest,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """رتبه‌بندی مجدد کاندیداها با وزن‌های قابل تنظیم."""
    job = job_service.get(db, job_id)
    if job is None or job.job_type != "design":
        raise HTTPException(status_code=404, detail="Design job not found")
    if job.status != "completed" or not job.result:
        raise HTTPException(status_code=400, detail="Design job not completed yet")

    candidates = job.result.get("candidates", [])
    weights = RankingWeights(
        efficacy=payload.weights.efficacy,
        safety=payload.weights.safety,
        synthesizability=payload.weights.synthesizability,
        cost=payload.weights.cost,
    )
    ranked = ranking_service.rank_candidates(
        candidates, weights, only_synthesizable=payload.only_synthesizable
    )
    normalized = weights.normalized()

    job.result = {**job.result, "candidates": ranked, "ranking_weights": normalized.__dict__}
    db.commit()

    return RankCandidatesResponse(
        job_id=str(job.id),
        ranked_candidates=ranked,
        weights_used=normalized.__dict__,
    )
