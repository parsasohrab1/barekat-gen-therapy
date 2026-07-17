from pydantic import BaseModel, Field


class PredictOutcomeRequest(BaseModel):
    age: int = Field(ge=10, le=80)
    gender: str
    disease_severity: float = Field(ge=1.0, le=10.0)
    gene_5_mutation: bool = False
    gene_12_mutation: bool = False
    gene_18_expression: float = Field(default=5.0, ge=0.0, le=15.0)


class PredictOutcomeResponse(BaseModel):
    time_to_recovery_days: float
    event_probability: float
    toxicity_level: float
    model_version: str | None = None
    partial_hazard: float | None = None
    is_research_prediction: bool = True
    is_research_prediction: bool = True
    is_research_prediction: bool = True
    is_research_prediction: bool = True
