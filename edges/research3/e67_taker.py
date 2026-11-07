"""E67 — taker buy/sell imbalance (plan edges/plans/E67_taker_flow.md). Universe: monthly top-100 by trailing 30d qv."""
import json, os, warnings
import numpy as np
import pandas as pd
from edges.research3.common import perp, DATA, bt
from edges.research3.driver import run_plan

warnings.filterwarnings("ignore")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "e67_universe.json")
EXCL = ("USDC", "FDUSD", "TUSD", "BUSD", "USDP", "USDE", "BTCDOM", "DEFI", "XAU", "XAG", "PAXG")


def universe():
    if os.path.exists(CACHE):
        return json.load(open(CACHE))
    months = pd.date_range("2020-01-01", "2026-12-01", freq="MS", tz="UTC")
    qv = {}
    for s in bt.universe("1h"):
        if any(x in s for x in EXCL):
            continue
        try:
            d = bt.load(s)
        except Exception:
            continue
        q = d.qv.fillna(0)
        cs = q.cumsum()
        row = {}
        for m in months:
            a = cs[cs.index < m]
            b = cs[cs.index < m - pd.Timedelta(days=30)]
            if len(a) and len(d[d.index < m]) >= 60 * 24:
                row[str(m.date())] = float(a.iloc[-1] - (b.iloc[-1] if len(b) else 0))
        qv[s] = row
    Q = pd.DataFrame(qv)
    top = {m: list(Q.loc[m].dropna().sort_values(ascending=False).index[:100]) for m in Q.index}
    json.dump(top, open(CACHE, "w"))
    return top


TOP = universe()
COINS = sorted({c for v in TOP.values() for c in v})
PERPS, RAW = {}, {}
for c in COINS:
    df = perp(c)
    v = df.v.values
    r = np.where(v > 0, df.tbv.values / np.where(v > 0, v, 1), np.nan)
    lr = np.log(df.c / df.c.shift(1))
    sig = lr.rolling(168, min_periods=120).std().shift(1)
    mon = df.index.tz_localize(None).to_period("M").astype(str) + "-01"
    inu = np.array([c in TOP.get(m, ()) for m in mon])
    RAW[c] = dict(r=r, m=(lr / sig).values, inu=inu)
    PERPS[c] = df[["o", "h", "l", "qv24", "rtc", "fund", "fund_missing"]].copy()


def lag1(x):
    y = np.empty_like(x); y[0] = np.nan; y[1:] = x[:-1]; return y


def feats(c, shift):
    R = RAW[c]
    r = R["r"] if not shift else np.roll(R["r"], shift % len(R["r"]))
    rs = pd.Series(r)
    z = ((rs - rs.rolling(168, min_periods=120).mean().shift(1)) / rs.rolling(168, min_periods=120).std().shift(1)).values
    return PERPS[c], dict(z=lag1(z), m=lag1(R["m"]), inu=lag1(R["inu"].astype(float)) > 0)


V = []
for k in (2, 3):
    for pf in ("none", "m<=-2"):
        for H in (4, 12, 24):
            V.append((f"X z<=-{k} {pf} H{H}", lambda F, k=k, pf=pf: (
                F["inu"] & (F["z"] <= -k) & ((F["m"] <= -2) if pf != "none" else True), 1), H))
    for H in (4, 12, 24):
        V.append((f"M |z|>={k} H{H}", lambda F, k=k: (F["inu"] & (np.abs(np.nan_to_num(F["z"])) >= k),
                                                     np.sign(np.nan_to_num(F["z"])).astype(int)), H))

if __name__ == "__main__":
    print(len(COINS), "coins", flush=True)
    out, R = run_plan("E67", "E67_taker_flow", COINS, feats, V, n_null=100, shift_range=(60 * 24, 20000))
    print({k: out[k] for k in ("luck", "promoted", "validation", "final", "verdict")})
    for r in sorted(out["discovery"], key=lambda r: -(r["t"] if r["t"] == r["t"] else -9))[:8]:
        print(r["label"], r["n"], r.get("mean_bp"), round(r["t"], 2), r.get("per_day"), r.get("years"))
