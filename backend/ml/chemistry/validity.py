"""Molecular validity and property filtering using RDKit."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SEED_LIPIDS_PATH = ROOT / "data" / "seeds" / "lipids.json"

try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski

    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


@dataclass
class MolecularProperties:
    smiles: str
    valid: bool
    molecular_weight: float | None
    log_p: float | None
    tpsa: float | None
    synthesizable: bool
    rejection_reason: str | None = None


@dataclass
class DesignConstraints:
    max_molecular_weight: float = 800.0
    min_log_p: float = 2.0
    max_log_p: float = 8.0
    lipid_class: str | None = None


def analyze_smiles(smiles: str) -> MolecularProperties:
    if not RDKIT_AVAILABLE:
        basic_valid = bool(smiles) and "(" in smiles or smiles.isalnum()
        return MolecularProperties(
            smiles=smiles,
            valid=basic_valid and "NOT" not in smiles.upper(),
            molecular_weight=400.0 if basic_valid else None,
            log_p=4.0 if basic_valid else None,
            tpsa=40.0 if basic_valid else None,
            synthesizable=basic_valid and "NOT" not in smiles.upper() and "INVALID" not in smiles.upper(),
            rejection_reason=None if basic_valid else "RDKit not installed",
        )

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return MolecularProperties(
            smiles=smiles,
            valid=False,
            molecular_weight=None,
            log_p=None,
            tpsa=None,
            synthesizable=False,
            rejection_reason="Invalid SMILES",
        )

    mw = float(Descriptors.MolWt(mol))
    log_p = float(Descriptors.MolLogP(mol))
    tpsa = float(Descriptors.TPSA(mol))

    reasons: list[str] = []
    if mw > 2000:
        reasons.append("Molecular weight too high")
    if log_p < -2 or log_p > 15:
        reasons.append("logP out of drug-like range")
    if Lipinski.NumHDonors(mol) > 10:
        reasons.append("Too many H-bond donors")

    synthesizable = len(reasons) == 0
    return MolecularProperties(
        smiles=smiles,
        valid=True,
        molecular_weight=round(mw, 2),
        log_p=round(log_p, 2),
        tpsa=round(tpsa, 2),
        synthesizable=synthesizable,
        rejection_reason="; ".join(reasons) if reasons else None,
    )


def passes_constraints(props: MolecularProperties, constraints: DesignConstraints) -> bool:
    if not props.valid or not props.synthesizable:
        return False
    if props.molecular_weight is None or props.log_p is None:
        return False
    if props.molecular_weight > constraints.max_molecular_weight:
        return False
    if not (constraints.min_log_p <= props.log_p <= constraints.max_log_p):
        return False
    return True


def load_seed_lipids() -> list[dict]:
    if not SEED_LIPIDS_PATH.exists():
        return []
    return json.loads(SEED_LIPIDS_PATH.read_text(encoding="utf-8"))


def filter_and_score_lipids(
    constraints: DesignConstraints,
    lipid_class: str | None = None,
) -> list[dict]:
    results: list[dict] = []
    for entry in load_seed_lipids():
        if lipid_class and entry.get("lipid_class") != lipid_class:
            continue
        props = analyze_smiles(entry["smiles"])
        accepted = passes_constraints(props, constraints)
        results.append(
            {
                "name": entry["name"],
                "smiles": entry["smiles"],
                "lipid_class": entry.get("lipid_class", "ionizable"),
                "source": entry.get("source", "seed"),
                "valid": props.valid,
                "synthesizable": props.synthesizable and accepted,
                "molecular_weight": props.molecular_weight,
                "log_p": props.log_p,
                "tpsa": props.tpsa,
                "rejection_reason": props.rejection_reason,
                "efficacy_score": _estimate_efficacy(props),
                "safety_score": _estimate_safety(props),
                "synthesizability_score": 1.0 if props.synthesizable and accepted else 0.0,
                "cost_score": _estimate_cost(entry.get("lipid_class")),
            }
        )
    return results


def _estimate_efficacy(props: MolecularProperties) -> float:
    if not props.valid or props.log_p is None:
        return 0.0
    # Ionizable lipids with moderate logP tend to perform better for LNP
    optimal = 4.5
    return float(max(0.0, 1.0 - abs(props.log_p - optimal) / 5.0))


def _estimate_safety(props: MolecularProperties) -> float:
    if not props.valid:
        return 0.0
    tpsa = props.tpsa or 20.0
    return float(min(1.0, max(0.2, 1.0 - tpsa / 200.0)))


def _estimate_cost(lipid_class: str | None) -> float:
    costs = {"ionizable": 0.4, "helper": 0.7, "sterol": 0.8, "peg": 0.5}
    return costs.get(lipid_class or "ionizable", 0.5)
