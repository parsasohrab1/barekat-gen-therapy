import pandas as pd

from ml.survival.coxph import predict_outcome, train_coxph
from ml.synthetic.generator import generate_gene_therapy_data


def test_train_coxph_returns_metrics():
    df = generate_gene_therapy_data(n_patients=100, n_genes=10, seed=7)
    result = train_coxph(df)

    assert result.c_index > 0.5
    assert "Age" in result.hazard_ratios
    assert result.summary["n_samples"] == 100


def test_predict_outcome_returns_valid_range():
    df = generate_gene_therapy_data(n_patients=200, seed=1)
    train_result = train_coxph(df)

    prediction = predict_outcome(
        train_result.model,
        {
            "age": 50,
            "gender": "Male",
            "disease_severity": 6.0,
            "gene_5_mutation": True,
            "gene_12_mutation": False,
            "gene_18_expression": 4.5,
        },
    )

    assert 0 < prediction["time_to_recovery_days"] <= 365
    assert 0 <= prediction["event_probability"] <= 1
    assert 0 <= prediction["toxicity_level"] <= 4
