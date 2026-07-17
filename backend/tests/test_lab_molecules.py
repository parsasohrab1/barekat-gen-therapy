"""Lab, molecule search, and compliance tests."""

from ml.chemistry.fingerprint import smiles_fingerprint, tanimoto_similarity


def test_fingerprint_similarity():
    fp1 = smiles_fingerprint("CCO")
    fp2 = smiles_fingerprint("CCO")
    fp3 = smiles_fingerprint("CCCCCCCC")
    assert tanimoto_similarity(fp1, fp2) == 1.0
    assert tanimoto_similarity(fp1, fp3) < 0.5


def test_deduplicate_logic():
    import pytest

    pytest.importorskip("psycopg")
    from app.services.molecule_search_service import MoleculeSearchService

    service = MoleculeSearchService()
    result = service.deduplicate("CCO")
    assert result["smiles"] == "CCO"
    assert "is_duplicate" in result
