"""Seed in-vitro results for retrain demo."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.database import SessionLocal
from app.services.lab_service import InVitroImporter

SAMPLE_RESULTS = [
    {
        "sample_external_id": "LIMS-2026-002",
        "lipid_smiles": "CCCCCCCCCCCCCCCC(=O)OCC(COP(=O)(O)OCCN)OC(=O)CCCCCCCCCCCCCCC",
        "transfection_efficiency": 0.72,
        "toxicity_score": 0.8,
        "cell_line": "HEPG2",
    },
    {
        "sample_external_id": "LIMS-2026-002",
        "lipid_smiles": "CCCCCCCCCCCCCCCC(=O)OC[C@H](COP(=O)(O)OCCN)OC(=O)CCCCCCCCCCCCCCC",
        "transfection_efficiency": 0.65,
        "toxicity_score": 1.1,
        "cell_line": "HEPG2",
    },
    {
        "sample_external_id": "IMP-001",
        "lipid_smiles": "CC(C)CC(=O)O",
        "transfection_efficiency": 0.41,
        "toxicity_score": 0.3,
        "cell_line": "HEPG2",
    },
    {
        "sample_external_id": "IMP-002",
        "lipid_smiles": "CCCCCCCCCCCCCCCC(=O)O",
        "transfection_efficiency": 0.55,
        "toxicity_score": 0.6,
        "cell_line": "HEPG2",
    },
    {
        "sample_external_id": "IMP-003",
        "lipid_smiles": "CCCCCCCCCCCCCCCC(=O)OC[C@H](COP(=O)([O-])OCC[N+](C)(C)C)OC(=O)CCCCCCCCCCCCCCC",
        "transfection_efficiency": 0.78,
        "toxicity_score": 0.9,
        "cell_line": "HEPG2",
    },
]


def main() -> None:
    with SessionLocal() as db:
        importer = InVitroImporter()
        imported = importer.import_results(db, SAMPLE_RESULTS)
        print(f"seed_invitro: imported {len(imported)} results")


if __name__ == "__main__":
    main()
