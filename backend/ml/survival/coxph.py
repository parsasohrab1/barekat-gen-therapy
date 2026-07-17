"""Cox Proportional Hazards survival model."""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from io import BytesIO

import pandas as pd
from lifelines import CoxPHFitter

FEATURE_COLUMNS = [
    "Age",
    "Gender_Male",
    "Disease_Severity",
    "Gene_5_Mutation",
    "Gene_12_Mutation",
    "Gene_18_Expr",
]
DURATION_COL = "Time_to_Recovery_days"
EVENT_COL = "Event_Status"


@dataclass
class CoxPHTrainResult:
    model: CoxPHFitter
    c_index: float
    hazard_ratios: dict[str, float]
    summary: dict[str, float | int]


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    prepared["Gender_Male"] = (prepared["Gender"] == "Male").astype(int)
    if "Gene_18_Expr" not in prepared.columns:
        prepared["Gene_18_Expr"] = df["Gene_18_Expr"] if "Gene_18_Expr" in df.columns else 5.0
    return prepared


def train_coxph(df: pd.DataFrame) -> CoxPHTrainResult:
    prepared = prepare_features(df)

    train_df = prepared[FEATURE_COLUMNS + [DURATION_COL, EVENT_COL]].copy()
    model = CoxPHFitter()
    model.fit(train_df, duration_col=DURATION_COL, event_col=EVENT_COL)

    hazard_ratios = {k: float(v) for k, v in model.hazard_ratios_.items()}
    return CoxPHTrainResult(
        model=model,
        c_index=float(model.concordance_index_),
        hazard_ratios=hazard_ratios,
        summary={
            "n_samples": len(train_df),
            "event_rate": float(train_df[EVENT_COL].mean()),
            "mean_recovery_days": float(train_df[DURATION_COL].mean()),
        },
    )


def patient_to_dataframe(patient: dict) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Age": patient["age"],
                "Gender_Male": 1 if patient["gender"].lower() in ("male", "m") else 0,
                "Disease_Severity": patient["disease_severity"],
                "Gene_5_Mutation": int(patient.get("gene_5_mutation", False)),
                "Gene_12_Mutation": int(patient.get("gene_12_mutation", False)),
                "Gene_18_Expr": patient.get("gene_18_expression", 5.0),
            }
        ]
    )


def predict_outcome(model: CoxPHFitter, patient: dict) -> dict[str, float]:
    patient_df = patient_to_dataframe(patient)
    partial_hazard = float(model.predict_partial_hazard(patient_df).iloc[0])
    survival_fn = model.predict_survival_function(patient_df).iloc[:, 0]

    below_median = survival_fn[survival_fn <= 0.5]
    median_time = float(below_median.index[0]) if len(below_median) > 0 else float(survival_fn.index[-1])

    horizon = 180.0
    if horizon in survival_fn.index:
        survival_at_horizon = float(survival_fn.loc[horizon])
    else:
        nearest = survival_fn.index[survival_fn.index <= horizon]
        survival_at_horizon = float(survival_fn.loc[nearest[-1]]) if len(nearest) > 0 else 0.5
    event_probability = 1.0 - survival_at_horizon

    toxicity_level = 0.5 + 0.8 * int(patient.get("gene_5_mutation", False)) + 0.1 * partial_hazard

    return {
        "time_to_recovery_days": round(median_time, 1),
        "event_probability": round(min(max(event_probability, 0.0), 1.0), 3),
        "toxicity_level": round(min(toxicity_level, 4.0), 2),
        "partial_hazard": round(partial_hazard, 3),
    }


def serialize_model(model: CoxPHFitter) -> bytes:
    return pickle.dumps(model)


def deserialize_model(data: bytes) -> CoxPHFitter:
    return pickle.loads(data)


def serialize_model_to_buffer(model: CoxPHFitter) -> BytesIO:
    buffer = BytesIO()
    buffer.write(serialize_model(model))
    buffer.seek(0)
    return buffer
