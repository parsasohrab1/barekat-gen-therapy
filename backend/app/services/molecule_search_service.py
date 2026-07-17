"""Molecular similarity search and deduplication."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.vector_store import VectorStore
from app.models import Lipid
from ml.chemistry.fingerprint import smiles_fingerprint, tanimoto_similarity
from ml.chemistry.validity import analyze_smiles


class MoleculeSearchService:
    def __init__(self) -> None:
        self.store = VectorStore()

    def index_lipid(
        self,
        db: Session,
        smiles: str,
        name: str | None = None,
        lipid_class: str = "ionizable",
        source: str = "internal",
    ) -> dict:
        props = analyze_smiles(smiles)
        vector = smiles_fingerprint(smiles)

        lipid = Lipid(
            id=str(uuid.uuid4()),
            name=name,
            smiles=smiles,
            molecular_weight=props.molecular_weight,
            log_p=props.log_p,
            lipid_class=lipid_class,
            is_synthetic=False,
        )
        db.add(lipid)
        db.commit()

        point_id = self.store.upsert_molecule(
            smiles=smiles,
            vector=vector,
            payload={
                "lipid_id": lipid.id,
                "name": name,
                "lipid_class": lipid_class,
                "source": source,
                "valid": props.valid,
            },
        )

        return {
            "lipid_id": lipid.id,
            "vector_id": point_id,
            "smiles": smiles,
            "indexed": True,
        }

    def search_by_smiles(self, smiles: str, limit: int = 10, threshold: float = 0.7) -> list[dict]:
        vector = smiles_fingerprint(smiles)
        return self.store.search_similar(vector, limit=limit, threshold=threshold)

    def deduplicate(self, smiles: str, threshold: float = 0.95) -> dict:
        vector = smiles_fingerprint(smiles)
        duplicates = self.store.find_duplicates(vector, threshold=threshold)
        is_duplicate = len(duplicates) > 0
        return {
            "smiles": smiles,
            "is_duplicate": is_duplicate,
            "duplicates": duplicates,
            "threshold": threshold,
        }

    def seed_library(self, db: Session) -> int:
        from ml.chemistry.validity import load_seed_lipids

        count = 0
        for entry in load_seed_lipids():
            if entry.get("name") == "Invalid-Test":
                continue
            self.index_lipid(
                db,
                smiles=entry["smiles"],
                name=entry["name"],
                lipid_class=entry.get("lipid_class", "ionizable"),
                source="seed",
            )
            count += 1
        return count
