"""Daily grid evaluator shared by E124/E125 (methods E120)."""
import numpy as np
import pandas as pd

from edges.lib import bt
from edges.research_xag import xlib as X


def market():
    si, gc = X.daily("SI"), X.daily("GC")
    df = pd.concat([si.rename("SI"), gc.rename("GC")], axis=1, join="inner").dropna()
    df = df[(df > 0).all(axis=1)]
    rets = df.shift(-1) / df - 1
    gap = pd.Series(np.r_[np.diff(df.index.values).astype("timedelta64[D]").astype(int), 1], index=df.index)
    return df, rets, gap


def evaluate(W, rets, gap, stress=1.0, delay=0):
    W = W.reindex(rets.index).fillna(0.0)
    if delay:
        W = W.shift(delay).fillna(0.0)
    cols = [c for c in W.columns if (W[c] != 0).any()]
    if not cols:
        cols = list(W.columns[:1])
    return X.book(W[cols], rets[cols], gap, {c: X.SPREAD[c] for c in cols}, fin=True, stress=stress)


def trade_list(W, pnl):
    lead = W["SI"] if (W["SI"] != 0).any() else W["GC"]
    rr = X.runs(lead.reindex(pnl.index).fillna(0))
    out = []
    v = pnl.values
    for a, b, s in rr:
        out.append(dict(time=pnl.index[a], start=a, length=b - a + 1, side=s, net=float(v[a:b + 1].sum())))
    return pd.DataFrame(out)


def period_stats(W, rets, gap):
    pnl = evaluate(W, rets, gap)
    pnl_s = evaluate(W, rets, gap, stress=2.0)
    pnl_d = evaluate(W, rets, gap, delay=1)
    tl = trade_list(W, pnl)
    res = {}
    for p, (a, b) in X.DPER.items():
        m = (pnl.index >= a) & (pnl.index < b)
        n_tr = int(((tl.time >= a) & (tl.time < b)).sum()) if len(tl) else 0
        s = X.dstats(pnl[m], trades=n_tr)
        s["stress_mean_bp"] = round(pnl_s[m].mean() * 1e4, 3)
        s["delay1_mean_bp"] = round(pnl_d[m].mean() * 1e4, 3)
        s["delay1_t"] = round(X.nw_t(pnl_d[m]), 2)
        if len(tl):
            tt = tl[(tl.time >= a) & (tl.time < b)]
            if len(tt):
                k = max(1, int(len(tt) * 0.05))
                s["trade_mean_bp"] = round(tt.net.mean() * 1e4, 2)
                s["trade_ex_top5pct_bp"] = round(tt.net.sort_values().iloc[:-k].mean() * 1e4, 2)
        res[p] = s
    yr = pnl.groupby(pnl.index.year).sum()
    res["all_years_pos"], res["all_years"] = int((yr > 0).sum()), int(len(yr))
    return res, pnl, tl


def run_grid(V, rets, gap, plan, tag, min_trades=0, nshift=200, seed=5):
    """V: {name: (W DataFrame [SI, GC], min_trades)}."""
    R, P, T = {}, {}, {}
    for name, W in V.items():
        res, pnl, tl = period_stats(W, rets, gap)
        R[name], P[name], T[name] = res, pnl, tl
        bt.log_attempt(plan, f"{tag} {name}", "discovery", dict(n=res["discovery"].get("trades"), mean_bp=res["discovery"].get("mean_bp"),
                                                               t_week=res["discovery"].get("t_nw")))
    cand = {k: v["discovery"] for k, v in R.items() if v["discovery"].get("trades", 0) >= min_trades.get(k, 0)}
    best = max(cand, key=lambda k: cand[k]["t_nw"] if cand[k]["t_nw"] == cand[k]["t_nw"] else -9)
    d = cand[best]
    a, b = X.DPER["discovery"]
    m = (rets.index >= a) & (rets.index < b)
    idx = rets.index[m]
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(nshift):
        off = int(rng.integers(60, len(idx) - 60))
        bt_ = -9
        for k, W in V.items():
            Wd = W.reindex(idx).fillna(0.0)
            Ws = pd.DataFrame(np.roll(Wd.values, off, axis=0), index=idx, columns=Wd.columns)
            p = evaluate(Ws, rets[m], gap[m])
            t = X.nw_t(p)
            if t == t:
                bt_ = max(bt_, t)
        null.append(bt_)
    p95t = float(np.percentile(null, 95))
    # random-entry control: same trade lengths and sides, random starts, discovery
    tl = T[best]
    td = tl[(tl.time >= a) & (tl.time < b)]
    W = V[best].reindex(rets.index).fillna(0.0)
    unit = {c: (W[c][W[c] != 0].abs().median() if (W[c] != 0).any() else 0) for c in W.columns}
    sgn = {c: np.sign(W[c][W["SI" if (W["SI"] != 0).any() else "GC"] != 0].iloc[0]) if (W[c] != 0).any() else 0 for c in W.columns}
    lead = "SI" if (W["SI"] != 0).any() else "GC"
    rand_means = []
    nidx = len(idx)
    for _ in range(200):
        nets = []
        for _, r in td.iterrows():
            s0 = int(rng.integers(0, max(1, nidx - r.length)))
            Wr = pd.DataFrame(0.0, index=idx[s0:s0 + int(r.length)], columns=W.columns)
            for c in W.columns:
                if unit[c]:
                    Wr[c] = r.side * unit[c] * (1 if c == lead else sgn[c] * sgn[lead])
            pr = evaluate(Wr, rets.loc[Wr.index], gap.loc[Wr.index])
            nets.append(pr.sum() - sum(X.SPREAD[c] * abs(Wr[c].iloc[-1]) for c in W.columns))
        rand_means.append(np.mean(nets) if nets else np.nan)
    p95r = float(np.nanpercentile(rand_means, 95)) * 1e4
    real_tr = float(td.net.mean() * 1e4) if len(td) else np.nan
    promoted = d["t_nw"] >= 2 and d["t_nw"] >= p95t and real_tr > p95r
    sel = dict(best=best, discovery=d, shifted_grid_best_t_p95=round(p95t, 2), random_entry_trade_p95_bp=round(p95r, 2),
               real_trade_mean_bp=round(real_tr, 2), promoted=bool(promoted))
    v, f = R[best]["validation"], R[best]["final"]
    if promoted:
        bt.log_attempt(plan, f"{tag} {best}", "validation", dict(n=v.get("trades"), mean_bp=v.get("mean_bp"), t_week=v.get("t_nw")))
    vpass = promoted and v["mean_bp"] > 0 and v["t_nw"] >= 1.5
    if vpass:
        bt.log_attempt(plan, f"{tag} {best}", "final", dict(n=f.get("trades"), mean_bp=f.get("mean_bp"), t_week=f.get("t_nw")))
        yrs = R[best]["all_years_pos"] / R[best]["all_years"]
        ok = f["mean_bp"] > 0 and f["t_nw"] >= 2 and yrs >= 0.6 and (f["trades"] >= 100 or (f["trades"] >= 50 and f["t_nw"] >= 3))
        verdict = f"{'PASS' if ok else 'FAIL'} (FINAL judged) best={best} final=({f.get('trades')},{f['mean_bp']},{f['t_nw']}) years_pos={yrs:.2f}"
    else:
        verdict = f"FAIL before FINAL best={best} promoted={promoted} val=({v.get('trades')},{v.get('mean_bp')},{v.get('t_nw')}) " \
                  f"final_info=({f.get('trades')},{f.get('mean_bp')},{f.get('t_nw')})"
    return dict(variants=R, selection=sel, verdict=verdict), P, T
