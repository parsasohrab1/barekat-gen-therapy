import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_db, require_role
from app.core.security import Role
from app.core.storage import generate_presigned_url
from app.schemas.model import ModelVersionResponse
from app.schemas.synthetic import (
    SyntheticDatasetResponse,
    SyntheticGenerateRequest,
    SyntheticJobResponse,
    SyntheticJobStatusResponse,
)
from app.services.job_service import JobService
from app.services.synthetic_service import SyntheticDataService
from workers.tasks.synthetic import run_synthetic_generation

router = APIRouter()
job_service = JobService()
synthetic_service = SyntheticDataService()


@router.post("/generate", response_model=SyntheticJobResponse)
def generate_synthetic_data(
    payload: SyntheticGenerateRequest,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """شروع job تولید dataset سنتتیک + آموزش CoxPH."""
    job = job_service.create(db, job_type="synthetic", input_payload=payload.model_dump())
    task = run_synthetic_generation.delay(str(job.id), payload.model_dump())
    job.celery_task_id = task.id
    db.commit()
    return SyntheticJobResponse(job_id=str(job.id), status="queued", estimated_duration_seconds=30)


@router.get("/jobs/{job_id}", response_model=SyntheticJobStatusResponse)
def get_synthetic_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
):
    job = job_service.get(db, job_id)
    if job is None or job.job_type != "synthetic":
        raise HTTPException(status_code=404, detail="Synthetic job not found")
    return SyntheticJobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        result=job.result,
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@router.get("/datasets", response_model=list[SyntheticDatasetResponse])
def list_datasets(
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
):
    datasets = synthetic_service.list_datasets(db)
    return [
        SyntheticDatasetResponse(
            dataset_id=str(d.id),
            job_id=str(d.job_id),
            n_samples=d.n_samples,
            mean_recovery_days=d.mean_recovery_days,
            response_rate=d.response_rate,
            seed=d.seed,
            is_synthetic=True,
            validation_metrics=d.validation_metrics,
            download_url=generate_presigned_url(d.storage_path),
            generated_at=d.generated_at,
        )
        for d in datasets
    ]


@router.get("/datasets/{dataset_id}", response_model=SyntheticDatasetResponse)
def get_dataset(
    dataset_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
):
    dataset = synthetic_service.get_dataset(db, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return SyntheticDatasetResponse(
        dataset_id=str(dataset.id),
        job_id=str(dataset.job_id),
        n_samples=dataset.n_samples,
        mean_recovery_days=dataset.mean_recovery_days,
        response_rate=dataset.response_rate,
        seed=dataset.seed,
        is_synthetic=True,
        validation_metrics=dataset.validation_metrics,
        download_url=generate_presigned_url(dataset.storage_path),
        generated_at=dataset.generated_at,
    )
