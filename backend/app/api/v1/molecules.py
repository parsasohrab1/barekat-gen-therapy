from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_db, require_role
from app.core.security import Role
from app.schemas.molecule import (
    DeduplicateResponse,
    MoleculeIndexRequest,
    MoleculeSearchRequest,
    MoleculeSearchResult,
)
from app.services.molecule_search_service import MoleculeSearchService

router = APIRouter()
search_service = MoleculeSearchService()


@router.post("/index")
def index_molecule(
    payload: MoleculeIndexRequest,
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """Index a lipid SMILES in Qdrant vector store."""
    return search_service.index_lipid(
        db, payload.smiles, name=payload.name, lipid_class=payload.lipid_class
    )


@router.post("/search", response_model=list[MoleculeSearchResult])
def search_molecules(
    payload: MoleculeSearchRequest,
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
):
    """Find lipids similar to query SMILES."""
    hits = search_service.search_by_smiles(
        payload.smiles, limit=payload.limit, threshold=payload.threshold
    )
    return [
        MoleculeSearchResult(
            id=h["id"],
            score=h["score"],
            smiles=h.get("smiles"),
            name=h.get("name"),
            lipid_class=h.get("lipid_class"),
        )
        for h in hits
    ]


@router.post("/deduplicate", response_model=DeduplicateResponse)
def deduplicate_molecule(
    payload: MoleculeSearchRequest,
    _: CurrentUser = Depends(require_role(Role.SCIENTIST)),
):
    """Check if generated candidate is duplicate of existing library entry."""
    result = search_service.deduplicate(payload.smiles, threshold=0.95)
    return DeduplicateResponse(**result)


@router.post("/seed-library")
def seed_molecule_library(
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.ADMIN)),
):
    """Index seed lipids into vector store."""
    count = search_service.seed_library(db)
    return {"indexed_count": count}
