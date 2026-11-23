"""Do common fingerprints distinguish a cis from a trans lipid tail? (RDKit; ethyl oleate vs ethyl elaidate)"""
from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator as G, rdMolDescriptors as D

cis = Chem.MolFromSmiles(r"CCCCCCCC/C=C\CCCCCCCC(=O)OCC")
trans = Chem.MolFromSmiles(r"CCCCCCCC/C=C/CCCCCCCC(=O)OCC")
print("isomeric SMILES differ:", Chem.MolToSmiles(cis) != Chem.MolToSmiles(trans))
print("flat SMILES identical:", Chem.MolToSmiles(cis, isomericSmiles=False) == Chem.MolToSmiles(trans, isomericSmiles=False))
for chir in (False, True):
    g = G.GetMorganGenerator(radius=2, fpSize=2048, includeChirality=chir)
    print("ECFP4 chirality", chir, DataStructs.TanimotoSimilarity(g.GetFingerprint(cis), g.GetFingerprint(trans)))
print("atom pair", DataStructs.TanimotoSimilarity(D.GetHashedAtomPairFingerprintAsBitVect(cis), D.GetHashedAtomPairFingerprintAsBitVect(trans)))
