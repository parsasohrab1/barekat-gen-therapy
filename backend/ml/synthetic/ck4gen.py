"""CK4Gen pipeline — distill CoxPH knowledge into SynthNet synthetic data."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ml.evaluation.ck4gen_validation import validate_ck4gen
from ml.survival.coxph import train_coxph
from ml.synthetic.generator import generate_gene_therapy_data
from ml.synthetic.synthnet import SynthNet, cluster_risk_profiles


@dataclass
class CK4GenResult:
    source_df: pd.DataFrame
    synthetic_df: pd.DataFrame
    hazard_ratios: dict[str, float]
    n_clusters: int
    validation: dict
    source_c_index: float
    synthetic_c_index: float


class CK4GenPipeline:
    """CoxPH → hazard ratios → risk clustering → SynthNet → validation."""

    def __init__(self, n_clusters: int = 5, seed: int = 42, max_retries: int = 3):
        self.n_clusters = n_clusters
        self.seed = seed
        self.max_retries = max_retries
        self.synthnet = SynthNet()

    def run(
        self,
        n_samples: int,
        source_df: pd.DataFrame | None = None,
        n_genes: int = 25,
    ) -> CK4GenResult:
        if source_df is None:
            # Simulate limited real-world data as CK4Gen input
            source_df = generate_gene_therapy_data(
                n_patients=max(n_samples // 3, 80),
                n_genes=n_genes,
                seed=self.seed,
            )
            source_df["synthetic"] = False

        cox_result = train_coxph(source_df)
        labels = cluster_risk_profiles(
            source_df, cox_result.model, self.n_clusters, self.seed
        )
        cox_model = cox_result.model

        synth_model = self.synthnet.fit(source_df, labels, cox_result.hazard_ratios)

        synthetic_df = None
        validation = {}
        for attempt in range(self.max_retries):
            synthetic_df = self.synthnet.generate(
                synth_model, n_samples=n_samples, seed=self.seed + attempt
            )
            validation = validate_ck4gen(
                source_df, synthetic_df, cox_model, cox_result.c_index
            )
            if validation["accepted"]:
                break

        assert synthetic_df is not None
        return CK4GenResult(
            source_df=source_df,
            synthetic_df=synthetic_df,
            hazard_ratios=cox_result.hazard_ratios,
            n_clusters=len(set(labels)),
            validation=validation,
            source_c_index=cox_result.c_index,
            synthetic_c_index=validation["synthetic_c_index"],
        )
