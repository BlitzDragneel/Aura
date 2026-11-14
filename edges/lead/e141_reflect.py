"""E141 learn-from-losses cycle on E140 (plan edges/plans/E141_gold_pyramid_reflect.md, md5 d32d08c1...)."""
import json
import sys

import numpy as np
import pandas as pd

from edges.lib import bt
from edges.lib.reflect import buckets, plain, reflect
from edges.lead.e140_pyramid import PER, account, prep, run, stats

PLAN = "d32d08c1e3e9be59323a61390176f1a9"
K, N = 0.5, 6
FEATS = ["hour", "weekday", "eff24", "volpct", "trend_agree"]


def features(f, ents):
    c = f.c
    eff = (c - c.shift(288)).abs() / c.diff().abs().rolling(288).sum()
    volp = (f.atr / c).rolling(288 * 30, min_periods=288 * 5).rank(pct=True)
    d = c.resample("1D").last()
    sma = d.rolling(20).mean().shift(1).reindex(c.index, method="ffill")
    rows = []
    for t, dr in ents:
        rows.append(dict(t=t, d=dr, hour=t.hour, weekday=t.weekday(), eff24=eff.get(t, np.nan), volpct=volp.get(t, np.nan),
                         trend_agree=int(np.sign(c.at[t] - sma.get(t, np.nan)) == dr) if pd.notna(sma.get(t)) else -1))
    return pd.DataFrame(rows).set_index("t")


def main(xau_path, paxg_path):
    rng = np.random.default_rng(141)
    data, disc = {}, []
    for asset, path, cost in (("XAU", xau_path, lambda p: 0.20), ("PAXG", paxg_path, lambda p: 0.001 * p)):
        m, f = prep(path)
        mom = [(t, int(s)) for t, s in f.sig[f.sig != 0].items()]
        months = pd.Series([t for t, _ in mom]).dt.to_period("M").value_counts()
        rnd = []
        for per, n in months.items():
            pool = f.index[(f.index.to_period("M") == per) & f.atr.notna().values]
            if len(pool):
                rnd += [(t, int(rng.choice([-1, 1]))) for t in rng.choice(pool, size=min(n, len(pool)), replace=False)]
        rnd.sort()
        F = {"M": features(f, mom), "R": features(f, rnd)}
        tr = run(m, f, K, N, cost, mom)
        # attach features by the signal bar (fill time - 5 min, nearest previous 5m bar)
        sig_t = tr.time.dt.floor("5min") - pd.Timedelta(minutes=5)
        tr = pd.concat([tr.reset_index(drop=True), F["M"][~F["M"].index.duplicated()].reindex(pd.DatetimeIndex(sig_t)).reset_index(drop=True)[FEATS]], axis=1)
        a, b = PER[asset]["discovery"]
        d = tr[(tr.time >= a) & (tr.time < b)].dropna(subset=FEATS).copy()
        d["asset"] = asset
        disc.append(d)
        data[asset] = (m, f, cost, mom, rnd, F)
    # reflection on DISCOVERY only, pooled by rank within asset (buckets are per-asset terciles)
    tabs, n_looked = [], 0
    for d in disc:
        t, n = reflect(d, FEATS)
        t["asset"] = d.asset.iloc[0]
        tabs.append(t)
        n_looked += n
    T = pd.concat(tabs)
    T["rank"] = T.groupby("asset").mean_R.rank(ascending=False)
    pooled = T.groupby(["feature", "bucket"]).agg(rank=("rank", "mean"), n_assets=("asset", "nunique")).reset_index()
    pooled = pooled[pooled.n_assets == 2].sort_values("rank")
    best = pooled.iloc[0]
    print("Reflection (discovery only):")
    for t in tabs:
        print(t.asset.iloc[0], "\n" + plain(t))
    print("chosen filter:", best.feature, "=", best.bucket, "| buckets examined:", n_looked, flush=True)
    bt.log_attempt(PLAN, "E141 reflection buckets", "discovery", dict(n=n_looked, mean_bp=None, t_week=None))

    res = dict(plan="edges/plans/E141_gold_pyramid_reflect.md", md5=PLAN, filter=f"{best.feature}={best.bucket}",
               buckets_examined=n_looked, reflection={t.asset.iloc[0]: t.head(5).to_dict("records") + t.tail(5).to_dict("records") for t in tabs},
               assets={})
    verdicts = []
    for asset, (m, f, cost, mom, rnd, F) in data.items():
        A = {}
        for fam, ents in (("M", mom), ("R", rnd)):
            X = F[fam]
            # filter buckets are defined with discovery cut-points of THIS asset (no peeking at later periods)
            a, b = PER[asset]["discovery"]
            Xd = X[(X.index >= a) & (X.index < b)][best.feature].dropna()
            if best.feature in ("hour", "weekday", "trend_agree"):
                keep = X[best.feature].astype(str) == str(best.bucket)
            else:
                lo, hi = {"low": (0, 1 / 3), "mid": (1 / 3, 2 / 3), "high": (2 / 3, 1.0)}[best.bucket]
                ql, qh = Xd.quantile(lo), Xd.quantile(hi)
                keep = (X[best.feature] >= ql) & (X[best.feature] <= qh)
            sel = [(t, dr) for (t, dr), k in zip(ents, keep.values) if k]
            for name, k_, n_ in (("SINGLE", 0, 0), ("PYR", K, N)):
                tr = run(m, f, k_, n_, cost, sel)
                key = f"{fam} {name} filtered"
                A[key] = {}
                for p, (a, b) in PER[asset].items():
                    seg = tr[(tr.time >= a) & (tr.time < b)]
                    st = stats(seg)
                    if asset == "XAU":
                        st["stress_mean_R"] = round(float(((seg.pnl - seg.units * 0.20) / seg.S).mean()), 3) if len(seg) else None
                        if fam == "M":
                            st["account_560"] = account(seg)
                    A[key][p] = st
                    bt.log_attempt(PLAN, f"E141 {asset} {key}", p, dict(n=st.get("n"), mean_bp=None, t_week=st.get("t_week")))
                print(asset, key, {p: (v.get("n"), v.get("mean_R"), v.get("t_week"), v.get("stress_mean_R")) for p, v in A[key].items()}, flush=True)
        ok = all(A["M PYR filtered"][p].get("mean_R", -9) > max(A["M SINGLE filtered"][p].get("mean_R", -9), A["R PYR filtered"][p].get("mean_R", -9))
                 for p in ("validation", "final")) and A["M PYR filtered"]["final"].get("mean_R", -9) > 0 \
            and (A["M PYR filtered"]["final"].get("t_week") or 0) >= 2 and A["M PYR filtered"]["validation"].get("mean_R", -9) > 0 \
            and (A["M PYR filtered"]["validation"].get("t_week") or 0) >= 1.5
        verdicts.append(f"{asset}: {'PASS (grade B max, contaminated)' if ok else 'FAIL'}")
        res["assets"][asset] = A
    res["verdict"] = "; ".join(verdicts)
    json.dump(res, open("edges/results/E141_result.json", "w"), indent=1, default=str)
    print(res["verdict"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
