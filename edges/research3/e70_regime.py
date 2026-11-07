"""E70 — hold BTC vs cash by new-data regime (plan edges/plans/E70_btc_regime_hold.md)."""
import warnings
import numpy as np
import pandas as pd
from edges.research3.common import perp, bt, MD5, write_result
from edges.research3.e68_filters import filters_raw

warnings.filterwarnings("ignore")
P = perp("BTCUSDT")
DAYS = P.index[(P.index.hour == 4)]
O = P.o.reindex(DAYS)
RET = (O.shift(-1) / O - 1)                                    # 04:00 → next 04:00
FUND = P.fund.rolling(24).sum().shift(-24).reindex(DAYS).fillna(0) + 0.0001 * P.fund_missing.rolling(24).sum().shift(-24).reindex(DAYS).fillna(0)
SWC = pd.Series(bt.TAKER + bt.slippage(P.qv24.reindex(DAYS).fillna(0).values), index=DAYS)
RAW = filters_raw()
PER = {"discovery": ("2020-01-01", "2024-01-01"), "validation": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2100-01-01")}


def regimes(shift=0):
    def sh(s, k):
        return s if not shift else pd.Series(np.roll(s.values, shift * k), index=s.index)
    st, nf, fng, dv = sh(RAW["st"], 1), sh(RAW["nf"], 1), sh(RAW["fng"], 1), sh(RAW["dv"], 24)
    def lagd(x, h):
        x = x.astype(float).copy(); x.index = x.index + pd.Timedelta(hours=h)
        return x.reindex(x.index.union(DAYS)).sort_index().ffill().reindex(DAYS).fillna(0) > 0.5
    g30 = st / st.shift(30) - 1
    R = {}
    R["R1 stable30>0"] = lagd(g30 > 0, 26)
    R["R2 stable30>med365"] = lagd(g30 > g30.rolling(365, min_periods=180).median().shift(1), 26)
    R["R3 fng7<=50"] = lagd(fng.rolling(7).mean() <= 50, 2)
    R["R4 dvol<=med365"] = lagd(dv <= dv.rolling(24 * 365, min_periods=24 * 180).median().shift(1), 1)
    R["R5 netflow30<0"] = lagd(nf.rolling(30).sum() < 0, 28)
    R["R6 R1&R5"] = R["R1 stable30>0"] & R["R5 netflow30<0"]
    return R


def strat(on, weekly):
    on = on.copy()
    if weekly:
        on = on.where(on.index.dayofweek == 0).ffill().fillna(False).astype(bool)
    pos = on.astype(float)
    sw = pos.diff().abs().fillna(pos.iloc[0])
    r = pos * (RET - FUND) - sw * SWC
    return r.dropna(), pos


def stats(r, pos=None):
    if len(r) < 10:
        return {}
    eq = (1 + r).cumprod()
    yrs = len(r) / 365.25
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    dd = float((eq / eq.cummax() - 1).min())
    out = dict(cagr=round(float(cagr), 4), max_dd=round(dd, 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(365)), 3)
               if r.std() > 0 else 0, calmar=round(float(cagr / -dd), 3) if dd < 0 else np.nan, days=len(r))
    if pos is not None:
        p = pos.reindex(r.index)
        out["in_market"] = round(float(p.mean()), 3)
        out["switches_per_year"] = round(float(p.diff().abs().sum() / yrs), 1)
    return out


def edge_t(on, weekly):
    if weekly:
        on = on.where(on.index.dayofweek == 0).ffill().fillna(False).astype(bool)
    r = (RET - FUND).dropna()
    o = on.reindex(r.index).astype(bool)
    p1 = o.mean()
    if p1 in (0, 1):
        return np.nan, np.nan
    x = r * (o / p1 - (~o) / (1 - p1))
    tr = pd.DataFrame(dict(time=x.index, net=x.values))
    return float(r[o].mean() - r[~o].mean()), bt.tstat_weekly(tr)


def per(s, p, start=None):
    a, b = PER[p]
    if start and p == "discovery":
        a = start
    return s[(s.index >= pd.Timestamp(a, tz="UTC")) & (s.index < pd.Timestamp(b, tz="UTC"))]


def grid(shift=0):
    R = regimes(shift)
    out = {}
    for k, on in R.items():
        for wk in (0, 1):
            out[f"{k} {'weekly' if wk else 'daily'}"] = (on, wk)
    return out


if __name__ == "__main__":
    md5 = MD5["E70_btc_regime_hold"]
    bh = (RET - FUND).dropna()
    bh.iloc[0] -= SWC.iloc[0]
    res = dict(plan="E70", md5=md5, bh={p: stats(per(bh, p)) for p in PER}, discovery=[], validation={}, final=None)
    G = grid()
    for name, (on, wk) in G.items():
        st0 = "2021-03-24" if "dvol" in name else None
        r, pos = strat(on, wk)
        s = stats(per(r, "discovery", st0), pos); s["label"] = name
        s["bh_sharpe"] = stats(per(bh, "discovery", st0))["sharpe"]
        d, t = edge_t(per(on, "discovery", st0), wk); s["edge_bp_day"] = round(d * 1e4, 2); s["edge_t"] = round(t, 2)
        yr = r.groupby(r.index.year).apply(lambda x: (1 + x).prod() - 1)
        res["discovery"].append(s)
        bt.log_attempt(md5, f"E70:{name}", "discovery", s)
        print(s, flush=True)
    real = max(s["sharpe"] for s in res["discovery"])
    rng = np.random.default_rng(0)
    null = []
    for _ in range(200):
        Gs = grid(int(rng.integers(60, 2000)))
        best = -9
        for name, (on, wk) in Gs.items():
            st0 = "2021-03-24" if "dvol" in name else None
            r, pos = strat(on, wk)
            best = max(best, stats(per(r, "discovery", st0)).get("sharpe", -9))
        null.append(best)
    p95 = float(np.percentile(null, 95))
    res["luck"] = dict(real_best_sharpe=real, null_p95=p95, pct=float((np.array(null) < real).mean()))
    bt.log_attempt(md5, "E70:luck_check", "discovery", res["luck"])
    cand = sorted([s for s in res["discovery"] if s["sharpe"] >= p95 and s["sharpe"] > s["bh_sharpe"]],
                  key=lambda s: -s["sharpe"])[:3]
    res["promoted"] = [s["label"] for s in cand]
    best = None
    for s in cand:
        on, wk = G[s["label"]]
        r, pos = strat(on, wk)
        v = stats(per(r, "validation"), pos); v["bh"] = res["bh"]["validation"]
        d, t = edge_t(per(on, "validation"), wk); v["edge_bp_day"] = round(d * 1e4, 2); v["edge_t"] = round(t, 2)
        res["validation"][s["label"]] = v
        bt.log_attempt(md5, f"E70:{s['label']}", "validation", v)
        if v["sharpe"] > v["bh"]["sharpe"] and t >= 1.5 and (best is None or t > best[1]):
            best = (s["label"], t)
    if best is None:
        res["verdict"] = "FAIL: " + ("nothing beat the luck check / B&H in discovery" if not cand else
                                     "no promoted regime beat B&H with edge t ≥ 1.5 in VALIDATION")
    else:
        on, wk = G[best[0]]
        r, pos = strat(on, wk)
        f = stats(per(r, "final"), pos); d, t = edge_t(per(on, "final"), wk)
        f["edge_bp_day"] = round(d * 1e4, 2); f["edge_t"] = round(t, 2); f["bh"] = res["bh"]["final"]
        res["final"] = f; res["final_variant"] = best[0]
        bt.log_attempt(md5, f"E70:{best[0]}", "final", f)
        ok = t >= 2 and f["cagr"] > 0 and f["calmar"] > f["bh"]["calmar"]
        res["verdict"] = "PASS" if ok else "FAIL at FINAL"
    write_result("E70", res)
    print(res["luck"], res["promoted"], res["validation"], res["final"], res["verdict"])
