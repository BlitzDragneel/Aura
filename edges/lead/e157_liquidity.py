import json, sys, warnings
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from edges.lib import bt
from edges.lead.e142_movement import bars15
warnings.filterwarnings("ignore")
PLAN = sys.argv[2]


def prep(fine, depth):
    f = bars15(fine)
    d = depth.copy(); d.index = d.index + pd.Timedelta("5min")             # row stamped T is known at T+5m
    d = d.resample("15min", label="left", closed="left").last().reindex(f.index)
    X = pd.DataFrame(index=f.index)
    for k in ("0.2", "1", "5"):
        b, a = d[f"b{k}"], d[f"a{k}"]
        X[f"imb{k}"] = (b - a) / (b + a)
        X[f"z{k}"] = (X[f"imb{k}"] - X[f"imb{k}"].rolling(672, min_periods=200).mean()) / X[f"imb{k}"].rolling(672, min_periods=200).std()
    tot = d["b1"] + d["a1"]
    X["thin"] = tot / tot.rolling(672, min_periods=200).median()
    di = X.imb1 - X.imb1.shift(4)
    X["zd"] = (di - di.rolling(672, min_periods=200).mean()) / di.rolling(672, min_periods=200).std()
    o = f.o.shift(-1)
    for h, n in (("1h", 4), ("4h", 16)):
        X[f"r{h}"] = f.c.shift(-n) / o - 1 if False else o.shift(-n) / o - 1
        X[f"rng{h}"] = (f.h[::-1].rolling(n).max()[::-1].shift(-1) - f.l[::-1].rolling(n).min()[::-1].shift(-1)) / f.c
    return X


def rule_trades(X, z, sgn, h):
    n = {"1h": 4, "4h": 16}[h]
    out, busy = [], -1
    zz, rr, idx = X[z].values, X[f"r{h}"].values, X.index
    for i in range(len(X)):
        if i <= busy or not np.isfinite(zz[i]) or not np.isfinite(rr[i]):
            continue
        d = 1 if zz[i] >= 2 else (-1 if zz[i] <= -2 else 0)
        if d:
            out.append((idx[i], sgn * d * rr[i])); busy = i + n
    return pd.DataFrame(out, columns=["time", "gross"])


sets = [("BTC", bt.load("BTCUSDT", "5m")[["o", "h", "l", "c", "v"]].astype(float)["2023-01-01":], pd.read_parquet("/home/user/data/depth/BTCUSDT_5m.parquet"), 0.0007,
         {"train": ("2023-01-01", "2024-01-01"), "val": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2026-11-04")}),
        ("GOLD", pd.read_parquet(sys.argv[1])[["o", "h", "l", "c", "v"]].astype(float), pd.read_parquet("/home/user/data/depth/XAUUSDT_5m.parquet"), 0.0002,
         {"train": ("2025-12-11", "2026-06-01"), "val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-11-14")})]
res = dict(plan="edges/plans/E157_liquidity.md", md5=PLAN, assets={})
passed = []
for name, fine, depth, cost, per in sets:
    X = prep(fine, depth)
    R = dict(size={}, ic={}, rules={})
    a, b = [pd.Timestamp(x, tz="UTC") for x in per["final"]]
    F = X[(X.index >= a) & (X.index < b)].dropna(subset=["thin", "rng4h"])
    q = F.thin.rank(pct=True)
    R["size"] = dict(thinnest_fifth=round(float(F.rng4h[q <= 0.2].median() * 100), 3), middle=round(float(F.rng4h[(q > 0.4) & (q <= 0.6)].median() * 100), 3),
                     thickest_fifth=round(float(F.rng4h[q > 0.8].median() * 100), 3), n=int(len(F)))
    for p, (a_, b_) in per.items():
        S = X[(X.index >= pd.Timestamp(a_, tz="UTC")) & (X.index < pd.Timestamp(b_, tz="UTC"))]
        R["ic"][p] = {f"{z}->{h}": round(float(spearmanr(S[z], S[f"r{h}"], nan_policy="omit").correlation), 4) for z in ("z0.2", "z1", "z5", "zd") for h in ("1h", "4h")}
    for z in ("z1", "z5", "zd"):
        for rule, sgn in (("FOLLOW", 1), ("MAGNET", -1)):
            for h in ("1h", "4h"):
                T = rule_trades(X, z, sgn, h)
                key = f"{z} {rule} {h}"
                R["rules"][key] = {}
                for p, (a_, b_) in per.items():
                    s = T[(T.time >= pd.Timestamp(a_, tz="UTC")) & (T.time < pd.Timestamp(b_, tz="UTC"))]
                    s = s.assign(net=s.gross - 2 * cost)
                    R["rules"][key][p] = dict(n=int(len(s)), gross_bp=round(float(s.gross.mean() * 1e4), 1) if len(s) else None,
                                              net_bp=round(float(s.net.mean() * 1e4), 1) if len(s) else None, t=round(bt.tstat_weekly(s), 2) if len(s) > 5 else None,
                                              right=round(float((s.gross > 0).mean()), 3) if len(s) else None)
                    if p != "train":
                        bt.log_attempt(PLAN, f"E157 {name} {key}", p, dict(n=R["rules"][key][p]["n"], mean_bp=R["rules"][key][p]["net_bp"], t_week=R["rules"][key][p]["t"]))
                v, f_ = R["rules"][key]["val"], R["rules"][key]["final"]
                if (f_.get("net_bp") or -1) > 0 and (f_.get("t") or 0) >= 2 and (v.get("net_bp") or -1) > 0 and (v.get("t") or 0) >= 1.5:
                    passed.append(f"{name} {key}")
                print(name, key, {p: (c["n"], c["gross_bp"], c["net_bp"], c["t"], c["right"]) for p, c in R["rules"][key].items()}, flush=True)
    print(name, "SIZE", R["size"], "\nIC", R["ic"], flush=True)
    res["assets"][name] = R
res["verdict"] = ("PASS " + ", ".join(passed)) if passed else "FAIL (direction); see size"
json.dump(res, open("edges/results/E157_result.json", "w"), indent=1, default=str); print(res["verdict"])
