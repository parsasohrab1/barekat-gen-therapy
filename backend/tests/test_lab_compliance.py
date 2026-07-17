"""Lab / compliance integration tests (require PostgreSQL)."""

import json
from pathlib import Path

import pytest

from app.services.compliance_service import ComplianceService
from app.services.lab_service import InVitroImporter, LimsConnector


def test_lims_sync(db_session):
    connector = LimsConnector()
    samples = connector.sync_samples(db_session)
    assert len(samples) >= 2


def test_invitro_import(db_session):
    seed_path = Path(__file__).resolve().parents[2] / "data" / "seeds" / "invitro_results.json"
    if not seed_path.exists():
        pytest.skip("invitro seed file missing")
    rows = json.loads(seed_path.read_text(encoding="utf-8"))
    importer = InVitroImporter()
    imported = importer.import_results(db_session, rows)
    assert len(imported) == 5


def test_compliance_pseudonymize(db_session):
    from app.models import Patient

    patient_id = "GT_TEST_001"
    existing = db_session.get(Patient, patient_id)
    if existing is None:
        patient = Patient(
            id=patient_id,
            age=45,
            gender="Male",
            disease_severity=5.0,
            is_synthetic=True,
        )
        db_session.add(patient)
        db_session.commit()

    svc = ComplianceService()
    result = svc.pseudonymize_patient(db_session, patient_id)
    assert result["pseudonymized_id"].startswith("PSE_")


def test_gmp_trace(db_session):
    svc = ComplianceService()
    batch_id = "BATCH-TEST-MATURITY"
    svc.record_gmp_step(
        db_session,
        batch_id=batch_id,
        step="mixing",
        operator="qa_operator",
        equipment_id="MIX-01",
        parameters={"temp_c": 25},
    )
    trace = svc.get_gmp_trace(db_session, batch_id)
    assert len(trace) >= 1
    assert trace[-1].step == "mixing"
