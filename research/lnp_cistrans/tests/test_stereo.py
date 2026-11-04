"""Unit tests on toy molecules written in the tests (synthetic, not results)."""

import pandas as pd

from research.lnp_cistrans.stereo import (
    bond_stereo_counts,
    find_pairs,
    is_cis_trans_pair,
    morgan_counts,
    stereo_features,
)

CIS = "CCCC/C=C\\CCCC(=O)OC"
TRANS = "CCCC/C=C/CCCC(=O)OC"
COND = {
    "Experiment_Type": "in vitro", "Cell_or_Organ_Target": "HeLa", "Gene": "FFL",
    "Cargo_Type": "mRNA", "Lipid_to_mRNA_Weight_Ratio": 10.0, "Cationic_Lipid_Mol_Ratio": 35.0,
    "Phospholipid_Mol_Ratio": 16.0, "Cholesterol_Mol_Ratio": 46.5, "PEG_Lipid_Mol_Ratio": 2.5,
    "Dataset": "toy",
}


def test_counts():
    assert bond_stereo_counts(CIS) == (1, 0)
    assert bond_stereo_counts(TRANS) == (0, 1)


def test_morgan_without_chirality_is_blind_to_double_bond_stereo():
    a, b = morgan_counts([CIS, TRANS], chirality=False)
    assert (a == b).all()


def test_morgan_with_chirality_sees_double_bond_stereo():
    a, b = morgan_counts([CIS, TRANS], chirality=True)
    assert (a != b).any()


def test_stereo_features_differ():
    f = stereo_features([CIS, TRANS])
    assert (f[0] != f[1]).any()


def test_pair_detection_and_orientation():
    assert is_cis_trans_pair(CIS, TRANS)
    assert not is_cis_trans_pair(CIS, CIS)
    cond = COND
    df = pd.DataFrame([{**cond, "SMILES": TRANS, "y": 1.0}, {**cond, "SMILES": CIS, "y": 3.0}])
    p = find_pairs(df, "y")
    assert len(p) == 1 and p.loc[0, "y_cis"] == 3.0 and p.loc[0, "y_trans"] == 1.0


def test_different_conditions_not_paired():
    base = COND
    df = pd.DataFrame([{**base, "SMILES": TRANS, "y": 1.0},
                       {**base, "SMILES": CIS, "y": 3.0, "Lipid_to_mRNA_Weight_Ratio": 20.0}])
    assert len(find_pairs(df, "y")) == 0
