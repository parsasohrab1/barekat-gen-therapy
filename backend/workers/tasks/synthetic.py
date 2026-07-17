import logging

import uuid

from app.core.database import SessionLocal
from app.services.job_service import JobService
from app.services.synthetic_service import SyntheticDataService
from workers.celery_app import celery_app

job_service = JobService()
synthetic_service = SyntheticDataService()


@celery_app.task(name="synthetic.generate", bind=True)
def run_synthetic_generation(self, job_id: str, params: dict) -> dict:
    """تولید dataset سنتتیک CK4Gen، ذخیره در MinIO، آموزش CoxPH."""
    db = SessionLocal()
    try:
        job = job_service.get(db, uuid.UUID(job_id))
        if job is None:
            raise ValueError(f"Job {job_id} not found")

        job_service.mark_running(db, job, celery_task_id=self.request.id)
        result = synthetic_service.run_pipeline(
            db,
            job.id,
            n_patients=params.get("n_patients", 300),
            n_genes=params.get("n_genes", 25),
            seed=params.get("seed", 42),
            use_ck4gen=params.get("use_ck4gen", True),
            n_clusters=params.get("n_clusters", 5),
        )
        job_service.mark_completed(db, job, result)
        return result
    except Exception as exc:
        job = job_service.get(db, uuid.UUID(job_id))
        if job is not None:
            job_service.mark_failed(db, job, str(exc))
        raise
    finally:
        db.close()
