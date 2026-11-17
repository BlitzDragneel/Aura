import json, sys, warnings
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
from edges.lib import bt
from edges.memory.features import FEATS, describe, outcomes
warnings.filterwarnings("ignore")
PLAN, XAU = sys.argv[1], sys.argv[2]
agg = dict(o="first", h="max", l="min", c="last")
K = 200


def bars(fine):
    return fine.resample("15min").agg(agg).dropna()


def run(name, f, start_mem, per, cost, rng):
    X, Y = describe(f), outcomes(f)
    ok = X.notna().all(axis=1) & Y.up1h.notna()
    X, Y = X[ok], Y[ok]
    months = pd.date_range(per["val"][0], per["final"][1], freq="MS", tz="UTC")
    P = []
    for i, m in enumerate(months[:-1]):
        mem = (X.index >= pd.Timestamp(start_mem, tz="UTC")) & (X.index < m - pd.Timedelta("5h"))   # past only (outcomes up to 4h ahead)
        q = (X.index >= m) & (X.index < months[i + 1])
        if mem.sum() < 5000 or q.sum() == 0:
            continue
        mu, sd = X[mem].mean(), X[mem].std() + 1e-9
        Z = ((X[mem] - mu) / sd).values
        nn = NearestNeighbors(n_neighbors=K).fit(Z)
        _, idx = nn.kneighbors(((X[q] - mu) / sd).values)
        Ym = Y[mem]
        shuf = Ym.up1h.values.copy(); rng.shuffle(shuf)
        out = pd.DataFrame(index=X.index[q])
        for col in ("up1", "up1h", "up4h", "big4h"):
            out["p_" + col] = Ym[col].values[idx].mean(1)
        out["p_up1h_shuf"] = shuf[idx].mean(1)
        out["med1h"] = np.median(Ym.ret1h.values[idx], axis=1)
        P.append(out.join(Y))
    P = pd.concat(P)
    R = {}
    for p, (a, b) in per.items():
        S = P[(P.index >= pd.Timestamp(a, tz="UTC")) & (P.index < pd.Timestamp(b, tz="UTC"))]
        if len(S) < 500:
            continue
        r = {f"auc_{c}": round(float(roc_auc_score(S[c], S["p_" + c])), 4) for c in ("up1", "up1h", "up4h", "big4h")}
        r["auc_up1h_shuffled_memory"] = round(float(roc_auc_score(S.up1h, S.p_up1h_shuf)), 4)
        conf = (S.p_up1h - 0.5).abs(); top = S[conf >= conf.quantile(0.9)]
        r["confident10_accuracy"] = round(float(((top.p_up1h > 0.5) == (top.up1h > 0.5)).mean()), 3)
        r["base_rate_up1h"] = round(float(S.up1h.mean()), 3)
        tr = S[(S.p_up1h >= 0.6) | (S.p_up1h <= 0.4)]
        tr = tr.iloc[::4] if len(tr) else tr                       # no overlapping 1h trades (approx.)
        net = np.sign(tr.p_up1h - 0.5) * tr.ret1h - 2 * cost
        T = pd.DataFrame(dict(time=tr.index, net=net.values))
        r["trades"] = int(len(T)); r["trade_net_bp"] = round(float(T.net.mean() * 1e4), 2) if len(T) else None
        r["trade_t"] = round(bt.tstat_weekly(T), 2) if len(T) > 10 else None
        R[p] = r
        bt.log_attempt(PLAN, f"E162 {name}", p, dict(n=r["trades"], mean_bp=r["trade_net_bp"], t_week=r["trade_t"]))
    print(name, json.dumps(R), flush=True)
    return R


rng = np.random.default_rng(162)
D = "/home/user/data/metrics/"
res = dict(plan="edges/plans/E162_candle_memory.md", md5=PLAN, assets={})
res["assets"]["BTC"] = run("BTC", bars(bt.load("BTCUSDT", "5m")[["o", "h", "l", "c"]].astype(float)["2022-01-01":]), "2022-01-01",
                           {"val": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2026-11-04")}, 0.0007, rng)
res["assets"]["PAXG"] = run("PAXG", bars(pd.read_parquet("/tmp/claude-0/-home-user/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/e140/dl/PAXG_1m.parquet")[["o", "h", "l", "c"]].astype(float)),
                            "2021-01-01", {"val": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2025-12-01")}, 0.0002, rng)
res["assets"]["XAU"] = run("XAU", bars(pd.read_parquet(XAU)[["o", "h", "l", "c"]].astype(float)), "2025-12-11",
                           {"val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-11-14")}, 0.0002, rng)
res["assets"]["XAG"] = run("XAG", bars(pd.read_parquet(D + "XAG_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float)), "2026-01-07",
                           {"val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-11-14")}, 0.0004, rng)
F = {k: v.get("final", {}) for k, v in res["assets"].items()}
good = [k for k, v in F.items() if v.get("auc_up1h", 0) >= 0.53]
trade_ok = [k for k, v in res["assets"].items() if (v.get("final", {}).get("trade_net_bp") or -1) > 0 and (v.get("final", {}).get("trade_t") or 0) >= 2 and (v.get("val", {}).get("trade_net_bp") or -1) > 0]
res["verdict"] = "PASS" if len(good) >= 2 and trade_ok else f"FAIL (direction AUC >= 0.53 on {good}; trade test passes on {trade_ok})"
json.dump(res, open("edges/results/E162_result.json", "w"), indent=1); print(res["verdict"])
