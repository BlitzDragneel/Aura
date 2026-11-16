import json, sys, warnings
import numpy as np, pandas as pd
from scipy.stats import norm
from edges.lib import bt
from edges.lead.e142_movement import bars15, features, targets, fit
warnings.filterwarnings("ignore")
PLAN = sys.argv[1]


def straddle(S, K, T, s):
    if T <= 0:
        return abs(S - K)
    d1 = (np.log(S / K) + 0.5 * s * s * T) / (s * np.sqrt(T)); d2 = d1 - s * np.sqrt(T)
    c = S * norm.cdf(d1) - K * norm.cdf(d2)
    return c + (c - S + K)


fine = bt.load("BTCUSDT", "5m")[["o", "h", "l", "c", "v", "tbv"]].astype(float)
f = bars15(fine)
X, atr = features(f)
Y = targets(f, atr, ("pct", [0.005]))
a0, a1, a2, a3 = [pd.Timestamp(x, tz="UTC") for x in ("2022-01-01", "2024-01-01", "2025-01-01", "2026-11-04")]
ok = X.notna().all(axis=1) & Y.big_4h.notna()
tr, va = ok & (f.index >= a0) & (f.index < a1), ok & (f.index >= a1) & (f.index < a2)
p = fit(X[tr], Y.big_4h[tr], X[va], Y.big_4h[va], True)
pa = pd.Series(p(X[ok]), index=X.index[ok])
thr = np.quantile(pa[va[ok].values], 0.75)
dv = pd.read_parquet("/home/user/data/deribit_dvol/BTC.parquet")
dv = pd.Series(dv.c.values / 100, index=pd.to_datetime(dv.ts, unit="ms", utc=True) + pd.Timedelta("1h"))  # known at the close of its hour
c15 = f.c
lr = np.log(c15).diff()


def book(times):
    rows, last = [], pd.Timestamp("2000-01-01", tz="UTC")
    for t in times:
        if t < last + pd.Timedelta("4h"):
            continue
        t_in = t + pd.Timedelta("15min")
        if t_in not in c15.index or t_in + pd.Timedelta("4h") not in c15.index:
            continue
        iv0 = dv[dv.index <= t_in]; iv1 = dv[dv.index <= t_in + pd.Timedelta("4h")]
        if not len(iv0) or (t_in - iv0.index[-1]) > pd.Timedelta("3h"):
            continue
        S0, S1 = c15[t_in], c15[t_in + pd.Timedelta("4h")]
        rv = lr[t_in + pd.Timedelta("15min"): t_in + pd.Timedelta("4h")].std() * np.sqrt(4 * 24 * 365)
        r = dict(time=t_in, rv_over_iv=rv / iv0.iloc[-1])
        for m in (1.0, 1.2, 1.4):
            prem = straddle(S0, S0, 1 / 365, m * iv0.iloc[-1])
            val = straddle(S1, S0, 20 / 24 / 365, m * iv1.iloc[-1])
            r[f"pnl_{m}"] = (val - prem) / prem - 0.03          # return on premium after 3% round-trip cost
            r[f"pnl_{m}_stress"] = (val - prem) / prem - 0.06
        rows.append(r); last = t
    return pd.DataFrame(rows)


watch_t = pa.index[(pa >= thr).values]
ctrl_t = pa.index[(pa.index.minute == 0) & (pa.index.hour % 4 == 0)]
res = dict(plan="edges/plans/E156_watch_straddle.md", md5=PLAN, cells={})
for name, ts in (("WATCH", watch_t), ("control", ctrl_t)):
    T = book(ts)
    res["cells"][name] = {}
    for per, (a, b) in (("val", (a1, a2)), ("final", (a2, a3))):
        x = T[(T.time >= a) & (T.time < b)]
        cell = dict(n=int(len(x)), rv_over_iv_median=round(float(x.rv_over_iv.median()), 3))
        for k in [c for c in x.columns if c.startswith("pnl")]:
            cell[k] = round(float(x[k].mean() * 100), 2)
            cell["t_" + k] = round(bt.tstat_weekly(x.assign(net=x[k])), 2)
        res["cells"][name][per] = cell
        if name == "WATCH":
            bt.log_attempt(PLAN, "E156 WATCH straddle m1.4", per, dict(n=cell["n"], mean_bp=cell["pnl_1.4"], t_week=cell["t_pnl_1.4"]))
        print(name, per, cell, flush=True)
W = res["cells"]["WATCH"]
ok_ = W["final"]["pnl_1.4"] > 0 and W["final"]["t_pnl_1.4"] >= 2 and W["val"]["pnl_1.4"] > 0 and W["final"]["pnl_1.4"] > res["cells"]["control"]["final"]["pnl_1.4"]
res["verdict"] = "PASS (research candidate: paper-track real option quotes)" if ok_ else "FAIL"
json.dump(res, open("edges/results/E156_result.json", "w"), indent=1, default=str); print(res["verdict"])
