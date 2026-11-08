"""Fast scouts on 15-minute candles (plan edges/plans/E82_fast_scouts.md).
Same features and labels as the hourly scouts, counted in 15m bars; horizon 16 bars = 4 hours.
  python -m edges.scouts.fast test     walk-forward: train 2022-23 -> 2024 ; train 2022-24 -> 2025-26
  python -m edges.scouts.fast train    fit on all 15m history, save to edges/scouts/models15/
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from edges.lib import bt
from edges.data.fetch import TOP
from edges.scouts.model import features, labels, fit

HB = 16          # horizon in 15m bars (4 h)
TARGETS = ("up_move", "down_move", "turn_up", "turn_down")
MODELS = os.environ.get("SCOUT_MODELS15") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "models15")


def to15(d):
    r = d.resample("15min", label="left", closed="left")
    out = pd.DataFrame(dict(o=r.o.first(), h=r.h.max(), l=r.l.min(), c=r.c.last(), v=r.v.sum(), qv=r.qv.sum()))
    return out.dropna(subset=["c"])


def dataset(step=4):
    btc = to15(bt.load("BTCUSDT", "5m"))
    rows = []
    for s in TOP:
        try:
            d = to15(bt.load(s, "5m"))
        except FileNotFoundError:
            continue
        X = features(d, btc).join(labels(d, HB))
        X["qv24"] = d.qv.rolling(96).sum()
        rows.append(X.iloc[::step])
    D = pd.concat(rows)
    lab = ("fwd", "sig24", "up_move", "down_move", "turn_up", "turn_down", "qv24")
    return D, [c for c in D.columns if c not in lab]


def score(D, fcols, target, side, train_end, a, b):
    cut = pd.Timestamp(train_end, tz="UTC") - pd.Timedelta(minutes=15 * HB)
    tr = D[D.index < cut].dropna(subset=[target])
    te = D[(D.index >= a) & (D.index < b)].dropna(subset=[target])
    m = fit(tr[fcols], tr[target])
    p_tr, p = m.predict_proba(tr[fcols])[:, 1], m.predict_proba(te[fcols])[:, 1]
    y, base = te[target].values, tr[target].mean()
    pick = te[p >= np.quantile(p_tr, 0.98)].copy()
    sgn = 1 if side == "up" else -1
    pick["net"] = sgn * (np.exp(pick.fwd) - 1) - bt.round_trip_cost(pick.qv24.fillna(0).values)
    pick["time"] = pick.index
    t = bt.tstat_weekly(pick.reset_index(drop=True)) if len(pick) > 10 else np.nan
    return dict(n_test=int(len(te)), auc=round(float(roc_auc_score(y, p)), 4),
                brier_skill=round(float(1 - np.mean((p - y) ** 2) / np.mean((base - y) ** 2)), 4),
                trades=int(len(pick)), mean_net_bp=round(float(pick.net.mean() * 1e4), 1) if len(pick) else None,
                t_week=round(float(t), 2) if t == t else None)


def test():
    D, fcols = dataset()
    res = {}
    for name, tgt, side in (("FastUp", "up_move", "up"), ("FastDown", "down_move", "down"),
                            ("FastTurnUp", "turn_up", "up"), ("FastTurnDown", "turn_down", "down")):
        v = score(D, fcols, tgt, side, "2024-01-01", "2024-01-01", "2025-01-01")
        f = score(D, fcols, tgt, side, "2025-01-01", "2025-01-01", "2100-01-01")
        res[name] = dict(validation_2024=v, final_2025_26=f)
        bt.log_attempt("E82", name, "validation", dict(n=v["trades"], mean_bp=v["mean_net_bp"], t_week=v["t_week"]))
        bt.log_attempt("E82", name, "final", dict(n=f["trades"], mean_bp=f["mean_net_bp"], t_week=f["t_week"]))
        print(name, "2024 AUC", v["auc"], "net", v["mean_net_bp"], v["t_week"], "| 2025-26 AUC", f["auc"], "BSS",
              f["brier_skill"], "net", f["mean_net_bp"], f["t_week"], "n", f["trades"], flush=True)
    json.dump(dict(plan="edges/plans/E82_fast_scouts.md", horizon="4h on 15m bars", results=res),
              open("edges/results/E82_result.json", "w"), indent=1)


def train():
    os.makedirs(MODELS, exist_ok=True)
    D, fcols = dataset(step=2)
    meta = dict(features=fcols, tf="15m", horizon_bars=HB, trained_to=str(D.index.max()), coins=TOP, thresholds={})
    for t in TARGETS:
        tr = D.dropna(subset=[t])
        m = fit(tr[fcols], tr[t])
        m.booster_.save_model(os.path.join(MODELS, f"{t}.txt"))
        meta["thresholds"][t] = float(np.quantile(m.predict_proba(tr[fcols])[:, 1], 0.98))
        print(t, len(tr), flush=True)
    json.dump(meta, open(os.path.join(MODELS, "meta.json"), "w"), indent=1)


if __name__ == "__main__":
    {"test": test, "train": train}[sys.argv[1]]()
