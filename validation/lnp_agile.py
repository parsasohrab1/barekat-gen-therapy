"""LNP product on real experimental data (AGILE fine-tuning set, 1200 ionizable lipids with measured HeLa mRNA transfection).

The product ranks candidates with RankingService (efficacy_score is an input; the repo has no structure->efficacy model for lipids).
Here an efficacy model is trained on the real data, its out-of-fold prediction is fed to the product's own RankingService
(efficacy-only weights) and the resulting ranking is compared with the measured transfection.
Baselines: random ranking, and a single descriptor (best of the 800 by training-fold Spearman).
Splits: 5-fold random CV and 5-fold scaffold-grouped CV (Bemis-Murcko scaffolds kept together).
"""
import importlib.util, json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, GroupKFold
RDLogger.DisableLog("rdApp.*")

spec = importlib.util.spec_from_file_location("rs", Path(sys.argv[1]) / "backend/app/services/ranking_service.py")
rs = importlib.util.module_from_spec(spec); sys.modules["rs"] = rs; spec.loader.exec_module(rs)

df = pd.read_csv(sys.argv[2]).drop_duplicates("smiles").reset_index(drop=True)
y = df["expt_Hela"].values
X = df[[c for c in df.columns if c.startswith("desc_")]].replace([np.inf, -np.inf], np.nan).fillna(0).values
X = X[:, X.std(0) > 0]
scaf = [MurckoScaffold.MurckoScaffoldSmiles(mol=Chem.MolFromSmiles(s)) if Chem.MolFromSmiles(s) else "" for s in df["smiles"]]
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
# lipids share only a handful of Bemis-Murcko scaffolds (6 here), so scaffold splitting is meaningless; group by structure clusters instead
groups = KMeans(10, n_init=5, random_state=0).fit_predict(StandardScaler().fit_transform(X))
svc = rs.RankingService(); W = rs.RankingWeights(efficacy=1, safety=0, synthesizability=0, cost=0)

def run(splits, name):
    pred = np.zeros(len(y)); base = np.zeros(len(y))
    for tr, te in splits:
        m = RandomForestRegressor(n_estimators=150, max_features="sqrt", random_state=0, n_jobs=-1).fit(X[tr], y[tr]); pred[te] = m.predict(X[te])
        Rx = pd.DataFrame(X[tr]).rank().values; Ry = pd.Series(y[tr]).rank().values
        Rx = Rx - Rx.mean(0); Ryc = Ry - Ry.mean()
        rho = (Rx * Ryc[:, None]).sum(0) / (np.sqrt((Rx ** 2).sum(0)) * np.sqrt((Ryc ** 2).sum()) + 1e-12)
        j = int(np.argmax(np.abs(rho))); base[te] = np.sign(rho[j]) * X[te][:, j]
    # product's own ranker, efficacy only, on the out-of-fold predictions (min-max to 0..1 as the ranker expects)
    s = (pred - pred.min()) / (pred.max() - pred.min())
    ranked = svc.rank_candidates([{"i": i, "efficacy_score": float(v)} for i, v in enumerate(s)], W, only_synthesizable=False)
    order = [c["i"] for c in ranked]; k = len(y) // 10
    top = set(np.argsort(-y)[:k])
    rng = np.random.default_rng(0)
    rnd = np.mean([len(top & set(rng.permutation(len(y))[:k])) / k for _ in range(200)])
    return {"split": name, "n": int(len(y)),
            "spearman_model": round(float(spearmanr(pred, y).correlation), 3),
            "spearman_best_single_descriptor": round(float(spearmanr(base, y).correlation), 3),
            "top10pct_recall_product_ranking": round(len(top & set(order[:k])) / k, 3),
            "top10pct_recall_random": round(float(rnd), 3)}

res = [run(KFold(5, shuffle=True, random_state=0).split(X), "random 5-fold"),
       run(GroupKFold(5).split(X, y, groups), "cluster-grouped 5-fold (10 descriptor clusters held out)")]
out = {"dataset": "AGILE fine-tuning (Zenodo 21422889)", "results": res}
Path(sys.argv[3]).write_text(json.dumps(out, indent=1), encoding="utf-8"); print(json.dumps(out, indent=1))
