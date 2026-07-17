from pydantic import BaseModel, Field


class InVitroResultImport(BaseModel):
    sample_external_id: str
    lipid_smiles: str
    transfection_efficiency: float = Field(ge=0.0, le=1.0)
    toxicity_score: float = Field(ge=0.0, le=4.0)
    cell_line: str = "HEPG2"


class InVitroImportRequest(BaseModel):
    results: list[InVitroResultImport]


class SynthesisDispatchRequest(BaseModel):
    lipid_smiles: str
    lipid_name: str | None = None
    design_job_id: str | None = None


class LabSampleResponse(BaseModel):
    id: str
    external_id: str
    source: str
    sample_type: str
    status: str


class SynthesisOrderResponse(BaseModel):
    order_id: str
    batch_id: str | None
    status: str
    lipid_smiles: str


class RetrainResponse(BaseModel):
    model_id: str
    model_version: str
    c_index: float | None
    n_samples: int
