from datetime import datetime

from pydantic import BaseModel


class ModelVersionResponse(BaseModel):
    model_id: str
    name: str
    version: str
    model_type: str
    metrics: dict
    is_active: bool
    dataset_id: str | None = None
    trained_at: datetime
