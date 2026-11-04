"""Cis/trans (E/Z) isomer pairs of lipids and a stereo-aware feature set.

RDKit Morgan fingerprints without includeChirality give identical vectors for cis/trans isomers
(checked on the 21 real pairs in the test of research/lnp_cistrans/run.py); with
includeChirality=True they differ. Explicit counts of Z and E double bonds are a third,
low-dimensional way to give a model the stereo information.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator

RDLogger.DisableLog("rdApp.*")

CONDITION_COLUMNS = [
    "Dataset", "Experiment_Type", "Cell_or_Organ_Target", "Gene", "Cargo_Type",
    "Lipid_to_mRNA_Weight_Ratio", "Cationic_Lipid_Mol_Ratio", "Phospholipid_Mol_Ratio",
    "Cholesterol_Mol_Ratio", "PEG_Lipid_Mol_Ratio",
]


def canonical(smiles: str, isomeric: bool) -> str:
    return Chem.MolToSmiles(Chem.MolFromSmiles(smiles), isomericSmiles=isomeric)


def bond_stereo_counts(smiles: str) -> tuple[int, int]:
    """Number of Z and of E double bonds."""
    m = Chem.MolFromSmiles(smiles)
    z = sum(b.GetStereo() == Chem.BondStereo.STEREOZ for b in m.GetBonds())
    e = sum(b.GetStereo() == Chem.BondStereo.STEREOE for b in m.GetBonds())
    return z, e


def assigned_centres(smiles: str) -> tuple:
    return tuple(sorted(Chem.FindMolChiralCenters(Chem.MolFromSmiles(smiles), includeUnassigned=False)))


def is_cis_trans_pair(iso_a: str, iso_b: str) -> bool:
    """Same constitution, same assigned tetrahedral centres, same number of stereo double bonds,
    different E/Z pattern."""
    za, ea = bond_stereo_counts(iso_a)
    zb, eb = bond_stereo_counts(iso_b)
    return (
        iso_a != iso_b
        and assigned_centres(iso_a) == assigned_centres(iso_b)
        and za + ea == zb + eb > 0
        and (za, ea) != (zb, eb)
    )


def add_structure_columns(df: pd.DataFrame, smiles_col: str = "SMILES") -> pd.DataFrame:
    uniq = {s: (canonical(s, False), canonical(s, True)) for s in df[smiles_col].unique()}
    out = df.copy()
    out["flat"] = out[smiles_col].map(lambda s: uniq[s][0])
    out["iso"] = out[smiles_col].map(lambda s: uniq[s][1])
    zc = {s: bond_stereo_counts(s) for s in out["iso"].unique()}
    out["nZ"] = out["iso"].map(lambda s: zc[s][0])
    out["nE"] = out["iso"].map(lambda s: zc[s][1])
    return out


def find_pairs(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Rows = (cis, trans) lipid pairs measured under identical conditions.
    The 'cis' member is the one with more Z bonds."""
    d = add_structure_columns(df)
    rows = []
    for flat, g in d.groupby("flat"):
        isos = sorted(g["iso"].unique())
        for i in range(len(isos)):
            for j in range(i + 1, len(isos)):
                if not is_cis_trans_pair(isos[i], isos[j]):
                    continue
                zi, zj = bond_stereo_counts(isos[i])[0], bond_stereo_counts(isos[j])[0]
                cis, trans = (isos[i], isos[j]) if zi > zj else (isos[j], isos[i])
                a = g[g["iso"] == cis].drop_duplicates(CONDITION_COLUMNS)
                b = g[g["iso"] == trans].drop_duplicates(CONDITION_COLUMNS)
                for _, r in a.merge(b, on=CONDITION_COLUMNS, suffixes=("_cis", "_trans")).iterrows():
                    rows.append({
                        "flat": flat, "cis": cis, "trans": trans, "Dataset": r["Dataset"],
                        "y_cis": r[value_col + "_cis"], "y_trans": r[value_col + "_trans"],
                    })
    return pd.DataFrame(rows)


def morgan_counts(
    smiles: list[str], radius: int = 2, n_bits: int = 1024, chirality: bool = False
) -> np.ndarray:
    gen = rdkit_gen(radius, n_bits, chirality)
    return np.vstack([gen.GetCountFingerprintAsNumPy(Chem.MolFromSmiles(s)) for s in smiles]).astype(float)


def rdkit_gen(radius: int, n_bits: int, chirality: bool):
    return rdFingerprintGenerator.GetMorganGenerator(
        radius=radius, fpSize=n_bits, includeChirality=chirality
    )


def stereo_features(isos: list[str]) -> np.ndarray:
    out = []
    for s in isos:
        z, e = bond_stereo_counts(s)
        out.append([z, e, z / (z + e) if z + e else 0.0])
    return np.array(out, dtype=float)
