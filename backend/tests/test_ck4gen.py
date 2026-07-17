"""Tests for CK4Gen pipeline."""

from ml.synthetic.ck4gen import CK4GenPipeline


def test_ck4gen_pipeline_runs_and_validates():
    pipeline = CK4GenPipeline(n_clusters=3, seed=42, max_retries=2)
    result = pipeline.run(n_samples=150, n_genes=10)

    assert len(result.synthetic_df) == 150
    assert result.synthetic_df["synthetic"].all()
    assert "hazard_ratios" in result.validation or "checks" in result.validation
    assert result.source_c_index > 0.5
    assert "ks_pvalue" in result.validation
