"""Tests for molecular validity and ranking."""

from app.services.ranking_service import RankingService, RankingWeights
from ml.chemistry.validity import DesignConstraints, analyze_smiles, filter_and_score_lipids


def test_analyze_invalid_smiles():
    props = analyze_smiles("NOT_VALID_SMILES")
    assert props.valid is False
    assert props.synthesizable is False


def test_ranking_with_custom_weights():
    candidates = [
        {
            "name": "A",
            "efficacy_score": 0.9,
            "safety_score": 0.5,
            "synthesizability_score": 1.0,
            "cost_score": 0.3,
            "synthesizable": True,
        },
        {
            "name": "B",
            "efficacy_score": 0.5,
            "safety_score": 0.95,
            "synthesizability_score": 1.0,
            "cost_score": 0.8,
            "synthesizable": True,
        },
    ]
    weights = RankingWeights(efficacy=0.1, safety=0.8, synthesizability=0.05, cost=0.05)
    ranked = RankingService().rank_candidates(candidates, weights)
    assert ranked[0]["name"] == "B"


def test_filter_seed_lipids():
    constraints = DesignConstraints(max_molecular_weight=2000, min_log_p=-5, max_log_p=15)
    results = filter_and_score_lipids(constraints)
    assert len(results) >= 1
    invalid = [r for r in results if r["name"] == "Invalid-Test"]
    assert invalid and invalid[0]["valid"] is False
