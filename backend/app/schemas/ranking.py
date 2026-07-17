from pydantic import BaseModel, Field


class RankingWeightsSchema(BaseModel):
    efficacy: float = Field(default=0.4, ge=0.0, le=1.0)
    safety: float = Field(default=0.3, ge=0.0, le=1.0)
    synthesizability: float = Field(default=0.2, ge=0.0, le=1.0)
    cost: float = Field(default=0.1, ge=0.0, le=1.0)


class RankCandidatesRequest(BaseModel):
    weights: RankingWeightsSchema = Field(default_factory=RankingWeightsSchema)
    only_synthesizable: bool = True


class RankCandidatesResponse(BaseModel):
    job_id: str
    ranked_candidates: list[dict]
    weights_used: dict[str, float]
