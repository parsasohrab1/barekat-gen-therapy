import logging
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Job

logger = logging.getLogger(__name__)


class JobService:
    def create(self, db: Session, job_type: str, input_payload: dict) -> Job:
        job = Job(job_type=job_type, status="queued", input_payload=input_payload)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def get(self, db: Session, job_id: uuid.UUID) -> Job | None:
        return db.get(Job, job_id)

    def list_jobs(self, db: Session, job_type: str | None = None, limit: int = 50) -> list[Job]:
        stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
        if job_type:
            stmt = stmt.where(Job.job_type == job_type)
        return list(db.scalars(stmt))

    def mark_running(self, db: Session, job: Job, celery_task_id: str | None = None) -> Job:
        job.status = "running"
        job.updated_at = datetime.utcnow()
        if celery_task_id:
            job.celery_task_id = celery_task_id
        db.commit()
        db.refresh(job)
        return job

    def mark_completed(self, db: Session, job: Job, result: dict) -> Job:
        import logging

        job.status = "completed"
        job.result = result
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        logging.getLogger(__name__).info(
            "Job completed",
            extra={"job_id": str(job.id), "action": f"job.{job.job_type}.completed"},
        )
        return job

    def mark_failed(self, db: Session, job: Job, error: str) -> Job:
        job.status = "failed"
        job.error_message = error
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return job
