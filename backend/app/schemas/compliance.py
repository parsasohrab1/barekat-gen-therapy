from pydantic import BaseModel, Field


class PseudonymizeRequest(BaseModel):
    patient_id: str


class GmpRecordRequest(BaseModel):
    batch_id: str
    step: str
    operator: str
    equipment_id: str | None = None
    parameters: dict = Field(default_factory=dict)


class AuditLogResponse(BaseModel):
    id: str
    action: str
    model_version: str | None
    input_hash: str | None
    details: dict
    created_at: str
