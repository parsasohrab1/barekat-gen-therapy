from datetime import datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    job_id: str
    job_type: str
    status: str
    input_payload: dict
    result: dict | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
