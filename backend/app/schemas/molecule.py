from pydantic import BaseModel, Field


class MoleculeIndexRequest(BaseModel):
    smiles: str
    name: str | None = None
    lipid_class: str = "ionizable"


class MoleculeSearchRequest(BaseModel):
    smiles: str
    limit: int = Field(default=10, ge=1, le=50)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class MoleculeSearchResult(BaseModel):
    id: str
    score: float
    smiles: str | None
    name: str | None = None
    lipid_class: str | None = None


class DeduplicateResponse(BaseModel):
    smiles: str
    is_duplicate: bool
    duplicates: list[dict]
    threshold: float
