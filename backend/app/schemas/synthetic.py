from datetime import datetime

from pydantic import BaseModel, Field


class SyntheticGenerateRequest(BaseModel):
    n_patients: int = Field(default=300, ge=10, le=10000)
    n_genes: int = Field(default=25, ge=5, le=100)
    seed: int = 42
    use_ck4gen: bool = True
    n_clusters: int = Field(default=5, ge=2, le=20)


class SyntheticJobResponse(BaseModel):
    job_id: str
    status: str
    estimated_duration_seconds: int = 30


class SyntheticJobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class SyntheticDatasetResponse(BaseModel):
    dataset_id: str
    job_id: str
    n_samples: int
    mean_recovery_days: float
    response_rate: float
    seed: int
    is_synthetic: bool = True
    validation_metrics: dict
    download_url: str | None = None
    generated_at: datetime
