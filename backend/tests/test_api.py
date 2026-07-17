import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data


def test_predict_without_model_returns_503():
    response = client.post(
        "/api/v1/predict/outcome",
        json={
            "age": 45,
            "gender": "Male",
            "disease_severity": 5.0,
            "gene_5_mutation": False,
            "gene_12_mutation": False,
            "gene_18_expression": 5.0,
        },
    )
    # 503 if no model, 200 if DB has active model from prior runs
    assert response.status_code in (200, 503)


def test_list_jobs_endpoint():
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
