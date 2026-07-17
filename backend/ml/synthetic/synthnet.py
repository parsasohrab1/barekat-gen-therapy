"""SynthNet — cluster-conditional generator distilled from CoxPH knowledge."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.stats import weibull_min

from ml.survival.coxph import FEATURE_COLUMNS, prepare_features, train_coxph


@dataclass
class ClusterProfile:
    label: int
    size: int
    means: dict[str, float]
    stds: dict[str, float]
    mutation_rates: dict[str, float]
    hazard_scale: float


@dataclass
class SynthNetModel:
    cluster_profiles: list[ClusterProfile] = field(default_factory=list)
    cluster_weights: list[float] = field(default_factory=list)
    hazard_ratios: dict[str, float] = field(default_factory=dict)
    column_template: list[str] = field(default_factory=list)


class SynthNet:
    """Generates synthetic patients preserving cluster-specific risk profiles."""

    CONTINUOUS = ["Age", "Disease_Severity", "Gene_18_Expr"]
    BINARY = ["Gene_5_Mutation", "Gene_12_Mutation"]

    def fit(
        self,
        source_df: pd.DataFrame,
        cluster_labels: np.ndarray,
        hazard_ratios: dict[str, float],
    ) -> SynthNetModel:
        prepared = prepare_features(source_df)
        profiles: list[ClusterProfile] = []
        weights: list[float] = []

        for label in sorted(np.unique(cluster_labels)):
            mask = cluster_labels == label
            cluster_df = prepared.loc[mask]
            if len(cluster_df) == 0:
                continue

            means = {col: float(cluster_df[col].mean()) for col in self.CONTINUOUS}
            stds = {
                col: max(float(cluster_df[col].std(ddof=0)), 0.5) for col in self.CONTINUOUS
            }
            mutation_rates = {col: float(cluster_df[col].mean()) for col in self.BINARY}

            patient_df = cluster_df[self.CONTINUOUS + self.BINARY].mean().to_frame().T
            # Approximate hazard scale from cluster centroid
            hazard_scale = 1.0
            for feature, hr in hazard_ratios.items():
                if feature in patient_df.columns:
                    hazard_scale *= hr ** float(patient_df[feature].iloc[0])

            profiles.append(
                ClusterProfile(
                    label=int(label),
                    size=int(mask.sum()),
                    means=means,
                    stds=stds,
                    mutation_rates=mutation_rates,
                    hazard_scale=max(hazard_scale, 0.1),
                )
            )
            weights.append(float(mask.sum()))

        total = sum(weights) or 1.0
        weights = [w / total for w in weights]

        return SynthNetModel(
            cluster_profiles=profiles,
            cluster_weights=weights,
            hazard_ratios=hazard_ratios,
            column_template=list(source_df.columns),
        )

    def generate(self, model: SynthNetModel, n_samples: int, seed: int = 42) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        rows: list[dict] = []

        for i in range(n_samples):
            profile = self._sample_profile(model, rng)
            row = self._generate_patient(profile, rng, i)
            rows.append(row)

        df = pd.DataFrame(rows)

        # Preserve gene expression columns from template with cluster-perturbed noise
        for col in model.column_template:
            if col.startswith("Gene_") and col.endswith("_Expr") and col not in df.columns:
                base = df["Gene_18_Expr"] if "Gene_18_Expr" in df.columns else 5.0
                df[col] = np.clip(rng.normal(base, 1.5, len(df)), 0, 15).round(3)

        df["synthetic"] = True
        return df

    def _sample_profile(self, model: SynthNetModel, rng: np.random.Generator) -> ClusterProfile:
        idx = rng.choice(len(model.cluster_profiles), p=model.cluster_weights)
        return model.cluster_profiles[idx]

    def _generate_patient(
        self, profile: ClusterProfile, rng: np.random.Generator, index: int
    ) -> dict:
        age = int(np.clip(rng.normal(profile.means["Age"], profile.stds["Age"]), 10, 80))
        severity = float(
            np.clip(rng.normal(profile.means["Disease_Severity"], profile.stds["Disease_Severity"]), 1, 10)
        )
        gene18 = float(
            np.clip(rng.normal(profile.means["Gene_18_Expr"], profile.stds["Gene_18_Expr"]), 0, 15)
        )
        g5 = int(rng.random() < profile.mutation_rates["Gene_5_Mutation"])
        g12 = int(rng.random() < profile.mutation_rates["Gene_12_Mutation"])

        hazard = profile.hazard_scale
        hazard *= 1 + 0.05 * (age - 45) / 15
        hazard *= severity / 5
        hazard *= 1 + 0.3 * g5
        hazard *= 1 + 0.2 * g12
        hazard *= 1 - 0.3 * (gene18 / 8)
        hazard = max(hazard, 0.1)

        recovery = float(weibull_min.rvs(1.5, scale=30 / hazard, random_state=rng))
        recovery = float(np.clip(recovery, 0.1, 365))
        event = int(recovery < 180)
        toxicity = float(np.clip(rng.gamma(2, 0.3) * g5, 0, 4))
        cytokine = int(rng.random() < (0.1 + 0.05 * toxicity))

        gender = "Male" if rng.random() < 0.5 else "Female"

        return {
            "Patient_ID": f"SYN_{str(index).zfill(5)}",
            "Age": age,
            "Gender": gender,
            "Disease_Severity": round(severity, 2),
            "Gene_5_Mutation": g5,
            "Gene_12_Mutation": g12,
            "Gene_18_Mutation": int(rng.random() < 0.2),
            "Gene_18_Expr": round(gene18, 3),
            "Time_to_Recovery_days": round(recovery, 1),
            "Event_Status": event,
            "Treatment_Response": event,
            "Toxicity_Level": round(toxicity, 2),
            "Cytokine_Storm": cytokine,
            "synthetic": True,
        }


def cluster_risk_profiles(
    df: pd.DataFrame,
    cox_model,
    n_clusters: int = 5,
    seed: int = 42,
) -> np.ndarray:
    from sklearn.cluster import KMeans

    prepared = prepare_features(df)
    features = prepared[FEATURE_COLUMNS].copy()
    features["partial_hazard"] = cox_model.predict_partial_hazard(features).values

    n_clusters = min(n_clusters, len(df) // 10, len(df))
    n_clusters = max(n_clusters, 2)

    kmeans = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    return kmeans.fit_predict(features)
