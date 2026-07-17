from enum import Enum

from pydantic import BaseModel, Field


class LipidClass(str, Enum):
    ionizable = "ionizable"
    helper = "helper"
    sterol = "sterol"
    peg = "peg"


class DesignConstraints(BaseModel):
    max_molecular_weight: float = 800
    min_logP: float = 2.0
    max_logP: float = 8.0
    lipid_class: LipidClass = LipidClass.ionizable


class DesignJobCreate(BaseModel):
    target_tissue: str
    cargo_type: str
    constraints: DesignConstraints
    n_candidates: int = Field(default=100, ge=1, le=1000)
    optimization_objectives: list[str] = ["efficacy", "safety", "synthesizability"]


class DesignJobResponse(BaseModel):
    job_id: str
    status: str
    estimated_duration_seconds: int


class DesignJobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None
    error_message: str | None = None
