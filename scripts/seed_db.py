"""Seed database with initial synthetic patient data."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "data"))

from generators.synthetic_clinical import generate_gene_therapy_data  # noqa: E402
from sqlalchemy.dialects.postgresql import insert  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.models import Patient  # noqa: E402


def main(n_patients: int = 100) -> None:
    df = generate_gene_therapy_data(n_patients=n_patients)

    rows = [
        {
            "id": row["Patient_ID"],
            "age": int(row["Age"]),
            "gender": row["Gender"],
            "disease_severity": float(row["Disease_Severity"]),
            "is_synthetic": True,
        }
        for _, row in df.iterrows()
    ]

    with SessionLocal() as db:
        stmt = insert(Patient).values(rows)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        result = db.execute(stmt)
        db.commit()
        inserted = result.rowcount if result.rowcount is not None else len(rows)
        print(f"seed_db: inserted {inserted} synthetic patients")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    main(n_patients=count)
