import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_db, require_role
from app.core.security import Role
from app.schemas.job import JobResponse
from app.services.job_service import JobService

router = APIRouter()
job_service = JobService()


def _to_response(job) -> JobResponse:
    return JobResponse(
        job_id=str(job.id),
        job_type=job.job_type,
        status=job.status,
        input_payload=job.input_payload,
        result=job.result,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
    )


@router.get("", response_model=list[JobResponse])
def list_jobs(
    job_type: str | None = None,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
):
    """لیست jobها — برای داشبورد."""
    jobs = job_service.list_jobs(db, job_type=job_type)
    return [_to_response(j) for j in jobs]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
):
    job = job_service.get(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_response(job)
