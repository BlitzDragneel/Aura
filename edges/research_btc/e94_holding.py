"""E94 BTC holding combinations vs buy-and-hold (plans/E94_btc_holding.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from libbtc import *  # noqa
from e93_btc_gold import paxg_daily
from e92_mom_rev import daily_funding
MD5 = "862939761a6db9d8a1d58f6a43cb47bd"
PH = {"discovery": ("2020-09-01", "2024-01-01"), "validation": ("2024-01-01", "2025-01-01"),
      "final": ("2025-01-01", "2026-11-01")}


def run(wB, wG, rB, rG, fd):
    """weights decided at close d, applied to d+1; daily rebalance to target; costs 0.10% per unit turnover each leg."""
    b = wB.shift(1).fillna(0); g = wG.shift(1).fillna(0)
    tb = b.diff().abs().fillna(b.abs()); tg = g.diff().abs().fillna(g.abs())
    return b * rB + g * rG - 0.001 * (tb + tg) - b * fd


def monthly(x):
    """hold the value set on the first day of each month."""
    m = x.index.to_period("M")
    return x.groupby(m).transform("first")


def build(d, pg, fd, sma_state=None):
    rB = d.c.pct_change().fillna(0); rG = pg.pct_change().fillna(0)
    lB = np.log(d.c).diff(); lG = np.log(pg).diff()
    v20 = lB.rolling(20, min_periods=15).std() * np.sqrt(365)
    v60 = lB.rolling(60, min_periods=40).std() * np.sqrt(365)
    vg60 = lG.rolling(60, min_periods=40).std() * np.sqrt(365)
    above = (d.c > d.c.rolling(200, min_periods=200).mean()).astype(float) if sma_state is None else sma_state
    part = sum((d.c / d.c.shift(n) - 1 > 0).astype(float) for n in (20, 60, 120)) / 3
    zero = pd.Series(0.0, index=d.index); one = pd.Series(1.0, index=d.index)
    W = {}
    W["H1 buy&hold"] = (one, zero)
    W["H2 E85 controller"] = (part * np.minimum(1, 0.10 / np.maximum(v20, v60)).fillna(0), zero)
    W["H3 SMA200"] = (above, zero)
    W["H4 SMA200 x vol40"] = (above * np.minimum(1, 0.40 / v20).fillna(0), zero)
    W["H5 50/50 BTC/gold"] = (0.5 * one, 0.5 * one)
    ib = (1 / v60) / (1 / v60 + 1 / vg60)
    ibm = monthly(ib.ffill().fillna(0.5))
    W["H6 inv-vol BTC/gold"] = (ibm, 1 - ibm)
    W["H7 H6 + BTC leg->gold below SMA200"] = (ibm * above, 1 - ibm * above)
    # H8: portfolio vol scaling of H7
    wb7, wg7 = W["H7 H6 + BTC leg->gold below SMA200"]
    pr = (wb7.shift(1) * rB + wg7.shift(1) * rG)
    pv = pr.rolling(60, min_periods=40).std() * np.sqrt(365)
    sc = np.minimum(1, 0.20 / pv).fillna(0)
    W["H8 H7 x port-vol20"] = (wb7 * sc, wg7 * sc)
    return {k: run(b, g, rB, rG, fd) for k, (b, g) in W.items()}


def stats(r):
    out = {}
    for p, (a, b) in PH.items():
        x = r[(r.index >= a) & (r.index < b)]
        out[p] = curve_stats(x)
        out[p]["total_return"] = round(float((1 + x).prod() - 1), 4)
    return out


def main():
    d = bars("1d")
    pg = paxg_daily().reindex(d.index).ffill(limit=3)
    fd = daily_funding(d)
    R = build(d, pg, fd)
    S = {k: stats(r) for k, r in R.items()}
    for k, s in S.items():
        bt.log_attempt(MD5, k, "discovery", s["discovery"])
    h1 = S["H1 buy&hold"]
    elig = [k for k in S if k != "H1 buy&hold" and S[k]["discovery"]["maxdd"] >= 0.6 * h1["discovery"]["maxdd"]]
    chosen = max(elig, key=lambda k: S[k]["discovery"]["sharpe"]) if elig else None
    out = dict(plan="E94", md5=MD5, stats=S, eligible=elig, chosen=chosen)
    # luck/timing check: shifted SMA state (affects H3, H4, H7, H8)
    above = (d.c > d.c.rolling(200, min_periods=200).mean()).astype(float)
    rng = np.random.default_rng(94)
    nulls = {k: [] for k in ("H3 SMA200", "H4 SMA200 x vol40", "H7 H6 + BTC leg->gold below SMA200", "H8 H7 x port-vol20")}
    for _ in range(200):
        sh = int(rng.integers(180, len(d) - 180))
        st = pd.Series(np.roll(above.values, sh), index=d.index)
        Rn = build(d, pg, fd, sma_state=st)
        for k in nulls:
            x = Rn[k][(Rn[k].index >= PH["discovery"][0]) & (Rn[k].index < PH["discovery"][1])]
            nulls[k].append(curve_stats(x)["sharpe"])
    out["timing_null_p95_sharpe_discovery"] = {k: round(float(np.percentile(v, 95)), 3) for k, v in nulls.items()}
    out["timing_luck_pass"] = {k: bool(S[k]["discovery"]["sharpe"] >= out["timing_null_p95_sharpe_discovery"][k]) for k in nulls}
    if chosen:
        c = S[chosen]
        for p in ("validation", "final"):
            bt.log_attempt(MD5, chosen, p, c[p])
        okp = {p: bool(c[p]["sharpe"] > h1[p]["sharpe"] and c[p]["maxdd"] >= 0.75 * h1[p]["maxdd"]) for p in ("validation", "final")}
        okp["final_positive"] = c["final"]["total_return"] > 0
        out["checks"] = okp
        timing = chosen in nulls
        out["verdict"] = ("PASS" if all(okp.values()) and (not timing or out["timing_luck_pass"][chosen]) else "FAIL")
        if not timing:
            out["verdict"] += " (allocation, no timing claim)"
    json.dump(out, open(f"{ROOT}/edges/results/E94_result.json", "w"), indent=1, default=str)
    for k, s in S.items():
        print(f"{k:38s}", " | ".join(f"{p[:4]} Sh {s[p]['sharpe']:5.2f} CAGR {s[p]['cagr']*100:6.1f}% DD {s[p]['maxdd']*100:5.1f}%" for p in PH))
    print({k: v for k, v in out.items() if k != "stats"})


if __name__ == "__main__":
    main()
