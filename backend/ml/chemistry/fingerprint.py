"""Molecular fingerprinting for vector similarity search."""

from __future__ import annotations

import hashlib

import numpy as np

try:
    from rdkit import Chem, DataStructs
    from rdkit.Chem import AllChem

    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False


def smiles_fingerprint(smiles: str, n_bits: int = 2048) -> list[float]:
    if not RDKIT_AVAILABLE:
        digest = hashlib.sha256(smiles.encode()).digest()
        arr = np.frombuffer(digest, dtype=np.uint8).astype(np.float32)
        padded = np.zeros(n_bits, dtype=np.float32)
        padded[: min(len(arr), n_bits)] = arr[:n_bits]
        return padded.tolist()

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return [0.0] * n_bits

    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    arr = np.zeros((n_bits,), dtype=np.float32)
    DataStructs.ConvertToNumpyArray(fp, arr)
    return arr.tolist()


def tanimoto_similarity(fp1: list[float], fp2: list[float]) -> float:
    a = np.array(fp1, dtype=np.float32)
    b = np.array(fp2, dtype=np.float32)
    intersection = float(np.sum(a * b))
    union = float(np.sum(a) + np.sum(b) - intersection)
    return intersection / union if union > 0 else 0.0
