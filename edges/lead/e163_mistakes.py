"""E163 candle memory that learns from its mistakes (plan edges/plans/E163_memory_learns_from_mistakes.md)."""
import json, sys, warnings
import numpy as np, pandas as pd
import lightgbm as lgb
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
from edges.lib import bt
from edges.memory.features import FEATS, RICH, describe_rich, outcomes
warnings.filterwarnings("ignore")
PLAN = "3d56d65d223deaa953003b7da4a28856"
agg = dict(o="first", h="max", l="min", c="last")
K = 200
GBM = dict(objective="binary", learning_rate=0.03, num_leaves=31, min_data_in_leaf=300, feature_fraction=0.8,
           bagging_fraction=0.8, bagging_freq=1, verbose=-1, seed=163, num_threads=4)
META = ["margin", "dist", "agree1", "agree4"]


def knn(Xm, Ym, Xq, cols):
    mu, sd = Xm[cols].mean(), Xm[cols].std() + 1e-9
    nn = NearestNeighbors(n_neighbors=K, algorithm="brute").fit(((Xm[cols] - mu) / sd).values)
    d, idx = nn.kneighbors(((Xq[cols] - mu) / sd).values)
    return idx, d.mean(1)


def predictions(name, fine, start_mem, warm, per):
    """Walk-forward predictions of A-D plus the mistake model (E_pright). Used by E163 and E164."""
    f = fine.resample("15min").agg(agg).dropna()
    X, Y = describe_rich(f), outcomes(f)
    ok = X.notna().all(axis=1) & Y.up1h.notna()
    X, Y = X[ok], Y[ok]
    months = pd.date_range(warm, per["final"][1], freq="MS", tz="UTC")
    P = []
    for i, m in enumerate(months[:-1]):
        mem = (X.index >= pd.Timestamp(start_mem, tz="UTC")) & (X.index < m - pd.Timedelta("5h"))
        q = (X.index >= m) & (X.index < months[i + 1])
        if mem.sum() < 5000 or q.sum() == 0:
            continue
        Xm, Ym, Xq = X[mem], Y[mem], X[q]
        out = pd.DataFrame(index=Xq.index)
        ia, _ = knn(Xm, Ym, Xq, FEATS)
        out["A"] = Ym.up1h.values[ia].mean(1)
        ib, dist = knn(Xm, Ym, Xq, RICH)
        out["B"] = Ym.up1h.values[ib].mean(1)
        out["dist"] = dist
        out["nb_up1"], out["nb_up4"] = Ym.up1.values[ib].mean(1), Ym.up4h.values[ib].mean(1)
        out["nb_big4"] = Ym.big4h.values[ib].mean(1)
        gbm = lgb.train(GBM, lgb.Dataset(Xm[RICH].values, Ym.up1h.values), num_boost_round=300)
        out["C"] = gbm.predict(Xq[RICH].values)
        out["D"] = (out.B + out.C) / 2
        P.append(pd.concat([out, Xq[RICH]], axis=1).join(Y))
        print(name, m.date(), len(out), flush=True)
    P = pd.concat(P)
    P["margin"] = (P.D - 0.5).abs()
    P["agree1"] = np.sign(P.nb_up1 - 0.5) * np.sign(P.D - 0.5)
    P["agree4"] = np.sign(P.nb_up4 - 0.5) * np.sign(P.D - 0.5)
    P["right"] = ((P.D > 0.5) == (P.up1h > 0.5)).astype(float)
    # E: mistake model trained on D's earlier out-of-sample predictions only
    P["E_pright"] = np.nan
    pm = P.index.to_period("M")
    for m in pm.unique():
        past = P[(pm < m)]
        past = past[past.index < m.start_time.tz_localize("UTC") - pd.Timedelta("5h")]
        if len(past) < 3000:
            continue
        cols = RICH + META
        mm = lgb.train(GBM, lgb.Dataset(past[cols].values, past.right.values), num_boost_round=200)
        P.loc[pm == m, "E_pright"] = mm.predict(P.loc[pm == m, cols].values)
    P["ret4h"] = (f.c.shift(-16) / f.o.shift(-1) - 1).reindex(P.index)
    return P


def run(name, fine, start_mem, warm, per, cost):
    P = predictions(name, fine, start_mem, warm, per)
    R = {}
    for p, (a, b) in per.items():
        S = P[(P.index >= pd.Timestamp(a, tz="UTC")) & (P.index < pd.Timestamp(b, tz="UTC"))]
        r = {}
        for v in "ABCD":
            x = dict(auc=round(float(roc_auc_score(S.up1h, S[v])), 4))
            conf = (S[v] - 0.5).abs(); top = S[conf >= conf.quantile(0.9)]
            x["conf10_acc"] = round(float(((top[v] > 0.5) == (top.up1h > 0.5)).mean()), 3)
            tr = S[(S[v] >= 0.6) | (S[v] <= 0.4)].iloc[::4]
            x.update(trade(tr, np.sign(tr[v] - 0.5), cost))
            r[v] = x
            bt.log_attempt(PLAN, f"E163 {name} {v}", p, dict(n=x["trades"], mean_bp=x["net_bp"], t_week=x["t"]))
        Se = S[S.E_pright.notna()]
        calls = Se[Se.E_pright >= 0.55]
        x = dict(coverage=round(len(calls) / max(len(Se), 1), 3), calls=int(len(calls)),
                 acc=round(float(calls.right.mean()), 3) if len(calls) else None,
                 D_acc_same_period=round(float(Se.right.mean()), 3) if len(Se) else None,
                 mistake_model_auc=round(float(roc_auc_score(Se.right, Se.E_pright)), 4) if len(Se) > 100 and Se.right.nunique() == 2 else None)
        tr = calls.iloc[::4]
        x.update(trade(tr, np.sign(tr.D - 0.5), cost))
        r["E"] = x
        bt.log_attempt(PLAN, f"E163 {name} E", p, dict(n=x["trades"], mean_bp=x["net_bp"], t_week=x["t"]))
        R[p] = r
    # why it was wrong: D's accuracy by condition (VAL + FINAL)
    S = P[P.index >= pd.Timestamp(per["val"][0], tz="UTC")].copy()
    hr = S.index.hour
    S["session"] = np.select([hr < 7, hr < 13, hr < 20], ["Asia 00-07", "London 07-13", "New York 13-20"], "late 20-24")
    S["unfamiliar"] = S.dist >= S.dist.quantile(0.8)
    S["close_vote"] = S.margin < 0.05
    S["vol"] = pd.qcut(S.volp, 3, labels=["low vol", "mid vol", "high vol"])
    S["with_24h_move"] = np.sign(S.r96) == np.sign(S.D - 0.5)
    S["weekend"] = S.wkend > 0
    why = {}
    for c in ("session", "unfamiliar", "close_vote", "vol", "with_24h_move", "weekend"):
        g = S.groupby(c).right.agg(["mean", "size"])
        why[c] = {str(k): [round(float(v["mean"]), 3), int(v["size"])] for k, v in g.iterrows()}
    R["why_wrong"] = why
    R["overall_D_acc"] = round(float(S.right.mean()), 3)
    print(name, json.dumps(R), flush=True)
    return R


def trade(tr, side, cost):
    if not len(tr):
        return dict(trades=0, net_bp=None, t=None)
    net = side * tr.ret1h - 2 * cost
    T = pd.DataFrame(dict(time=tr.index, net=net.values))
    return dict(trades=int(len(T)), net_bp=round(float(T.net.mean() * 1e4), 2),
                t=round(float(bt.tstat_weekly(T)), 2) if len(T) > 10 else None)


SP = "/tmp/claude-0/-home-user/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/e140/dl/"
CFG = {"BTC": (lambda: bt.load("BTCUSDT", "5m")[["o", "h", "l", "c"]].astype(float)["2021-01-01":], "2021-01-01", "2023-01-01",
               {"val": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2026-11-04")}, 0.0007),
       "PAXG": (lambda: pd.read_parquet(SP + "PAXG_1m.parquet")[["o", "h", "l", "c"]].astype(float), "2021-01-01", "2023-01-01",
                {"val": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2025-12-01")}, 0.0002),
       "XAU": (lambda: pd.read_parquet(SP + "XAU_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float), "2025-12-11", "2026-03-01",
               {"val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-11-14")}, 0.0002),
       "XAG": (lambda: pd.read_parquet("/home/user/data/metrics/XAG_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float), "2026-01-07", "2026-03-01",
               {"val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-11-14")}, 0.0004)}


if __name__ == "__main__":
    which = sys.argv[1:] or ["BTC", "PAXG", "XAU", "XAG"]
    for a in which:
        load, sm, warm, per, cost = CFG[a]
        res = run(a, load(), sm, warm, per, cost)
        json.dump(res, open(f"edges/results/E163_{a}.json", "w"), indent=1)
