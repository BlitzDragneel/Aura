"""Candle memory model (E163): look-alike candles (KNN) + gradient boosting, plus a MISTAKE MODEL that learns from the
model's own past right/wrong predictions when to trust it. Shared by the live bot and the replay builder."""
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.neighbors import NearestNeighbors

from edges.memory.features import RICH

K = 200
GBM = dict(objective="binary", learning_rate=0.03, num_leaves=31, min_data_in_leaf=300, feature_fraction=0.8,
           bagging_fraction=0.8, bagging_freq=1, verbose=-1, seed=163, num_threads=2)
META = ["margin", "dist", "agree1", "agree4"]


def predict(Xm, Ym, Xq):
    """Xm/Ym: memory (past candles with known outcomes); Xq: candles to predict. Returns one row per query."""
    mu, sd = Xm[RICH].mean(), Xm[RICH].std() + 1e-9
    nn = NearestNeighbors(n_neighbors=K, algorithm="brute").fit(((Xm[RICH] - mu) / sd).values)
    d, idx = nn.kneighbors(((Xq[RICH] - mu) / sd).values)
    out = pd.DataFrame(index=Xq.index)
    out["knn"] = Ym.up1h.values[idx].mean(1)
    out["dist"] = d.mean(1)
    out["p_up1"], out["p_up4h"], out["p_big4h"] = (Ym[c].values[idx].mean(1) for c in ("up1", "up4h", "big4h"))
    out["med1h_pct"] = np.median(Ym.ret1h.values[idx], axis=1) * 100
    g = lgb.train(GBM, lgb.Dataset(Xm[RICH].values, Ym.up1h.values), num_boost_round=300)
    out["gbm"] = g.predict(Xq[RICH].values)
    out["p_up1h"] = (out.knn + out.gbm) / 2
    out["margin"] = (out.p_up1h - 0.5).abs()
    out["agree1"] = np.sign(out.p_up1 - 0.5) * np.sign(out.p_up1h - 0.5)
    out["agree4"] = np.sign(out.p_up4h - 0.5) * np.sign(out.p_up1h - 0.5)
    return pd.concat([out, Xq[RICH]], axis=1)


def mistake_model(H):
    """H: past predictions (RICH + META columns) with 'right' (1 = the call was right). None if too little history."""
    H = H.dropna(subset=RICH + META + ["right"])
    if len(H) < 3000:
        return None
    return lgb.train(GBM, lgb.Dataset(H[RICH + META].values, H.right.values), num_boost_round=200)


def p_right(mm, P):
    return mm.predict(P[RICH + META].values) if mm is not None else np.full(len(P), np.nan)


def why_wrong(row, typical_move):
    """Plain reasons a scored-wrong call went wrong, from the conditions E163 measured."""
    r = []
    if row.margin < 0.05:
        r.append("close vote (the look-alikes were split)")
    if row.get("unfamiliar"):
        r.append("unfamiliar situation (few close look-alikes)")
    if abs(row.actual_ret1h) > 2 * typical_move:
        r.append(f"shock move ({row.actual_ret1h * 100:+.2f}% in the hour, over 2x typical)")
    if np.sign(row.r96) != np.sign(row.p_up1h - 0.5):
        r.append("called against the 24h move")
    if row.volp >= 2 / 3:
        r.append("high volatility")
    if isinstance(row.get("news"), str) and row.get("news"):
        r.append(f"news: {row.news}")
    h = pd.Timestamp(row.bar).hour
    r.append("session " + ("Asia" if h < 7 else "London" if h < 13 else "New York" if h < 20 else "late"))
    return "; ".join(r)
