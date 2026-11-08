"""Historical, walk-forward test of UpScout / DownScout (plan edges/plans/E81_trend_scouts.md).
Train 2020-2023 -> score 2024 (validation) ; train 2020-2024 -> score 2025-26 (final). 30 liquid coins, hourly.
Reports AUC, Brier skill vs base rate, and a tradeable check: long (UpScout) / short (DownScout) for 24 h when the
probability is in the top 2% of its training-period distribution, taker costs + slippage both ways, funding ignored
(reported) - with week-clustered t.
"""
import json
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from edges.lib import bt
from edges.data.fetch import TOP
from edges.scouts.model import features, labels, fit, H

OUT = "edges/results/E81_result.json"


def build():
    btc = bt.load("BTCUSDT")
    rows = []
    for s in TOP:
        try:
            d = bt.load(s)
        except FileNotFoundError:
            continue
        d = d[d.index >= "2020-01-01"]
        F = features(d, btc)
        Lb = labels(d)
        X = F.join(Lb)
        X["sym"] = s
        X["qv24"] = d.qv.rolling(24).sum()
        rows.append(X.iloc[::3])  # every 3rd hour: less overlap, less memory
    return pd.concat(rows)


def evaluate(D, target, train_end, test_start, test_end, fcols, side):
    tr = D[(D.index < train_end)].dropna(subset=[target])
    te = D[(D.index >= test_start) & (D.index < test_end)].dropna(subset=[target])
    tr = tr[tr.index < pd.Timestamp(train_end, tz="UTC") - pd.Timedelta(hours=H)]  # no label leakage across the cut
    m = fit(tr[fcols], tr[target])
    p_tr = m.predict_proba(tr[fcols])[:, 1]
    p = m.predict_proba(te[fcols])[:, 1]
    base = tr[target].mean()
    y = te[target].values
    brier = np.mean((p - y) ** 2)
    brier0 = np.mean((base - y) ** 2)
    thr = np.quantile(p_tr, 0.98)
    pick = te[p >= thr].copy()
    cost = bt.round_trip_cost(pick.qv24.fillna(0).values)
    sgn = 1 if side == "up" else -1
    pick["net"] = sgn * (np.exp(pick.fwd) - 1) - cost
    pick["time"] = pick.index
    tstat = bt.tstat_weekly(pick.reset_index(drop=True)) if len(pick) > 10 else np.nan
    imp = sorted(zip(fcols, m.feature_importances_), key=lambda x: -x[1])[:8]
    return dict(n_test=int(len(te)), base_rate_train=round(float(base), 4), base_rate_test=round(float(y.mean()), 4),
                auc=round(float(roc_auc_score(y, p)), 4), brier_skill=round(float(1 - brier / brier0), 4),
                hit_rate_top2pct=round(float(pick[target].mean()), 4) if len(pick) else None,
                trades_top2pct=int(len(pick)), mean_net_bp=round(float(pick.net.mean() * 1e4), 1) if len(pick) else None,
                t_week=round(float(tstat), 2) if tstat == tstat else None,
                top_features=[k for k, _ in imp]), m


if __name__ == "__main__":
    D = build()
    fcols = [c for c in D.columns if c not in ("fwd", "sig24", "up_move", "down_move", "turn_up", "turn_down", "sym", "qv24")]
    res = {}
    for name, target, side in (("UpScout", "up_move", "up"), ("DownScout", "down_move", "down"),
                               ("UpScout_turn", "turn_up", "up"), ("DownScout_turn", "turn_down", "down")):
        v, _ = evaluate(D, target, "2024-01-01", "2024-01-01", "2025-01-01", fcols, side)
        f, _ = evaluate(D, target, "2025-01-01", "2025-01-01", "2100-01-01", fcols, side)
        res[name] = dict(validation_2024=v, final_2025_26=f)
        print(name, "2024 AUC", v["auc"], "BSS", v["brier_skill"], "net", v["mean_net_bp"], v["t_week"], "| 2025-26 AUC",
              f["auc"], "BSS", f["brier_skill"], "net", f["mean_net_bp"], f["t_week"], flush=True)
        bt.log_attempt("E81", name, "validation", dict(n=v["trades_top2pct"], mean_bp=v["mean_net_bp"], t_week=v["t_week"]))
        bt.log_attempt("E81", name, "final", dict(n=f["trades_top2pct"], mean_bp=f["mean_net_bp"], t_week=f["t_week"]))
    json.dump(dict(plan="edges/plans/E81_trend_scouts.md", results=res), open(OUT, "w"), indent=1)
