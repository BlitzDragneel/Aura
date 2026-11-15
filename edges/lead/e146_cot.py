"""E146 CFTC positioning -> weekly gold/silver direction (plan md5 41f5fee7...)."""
import json
import numpy as np, pandas as pd
from edges.lib import bt

PLAN = "41f5fee70a4a487eb04402f5bd70b9d1"
PER = {"discovery": ("2006-01-01", "2016-01-01"), "validation": ("2016-01-01", "2021-01-01"), "final": ("2021-01-01", "2027-01-01")}


def z(x, n, m=None):
    return (x - x.rolling(n, min_periods=m or n // 2).mean()) / x.rolling(n, min_periods=m or n // 2).std()


def weekly(name, px):
    c = pd.read_parquet(f"/home/user/data/cot/{name}.parquet")
    p = pd.read_parquet(f"/home/user/data/metals/{px}_1d.parquet").c
    p.index = p.index.tz_localize(None).normalize()
    p = p[~p.index.duplicated()]
    S = pd.DataFrame(dict(mm=(c.mml - c.mms) / c.oi, pm=(c.pl - c.ps) / c.oi))
    S["z_mm"], S["z_pm"] = z(S.mm, 156), z(S.pm, 156)
    S["zd"] = z(S.mm - S.mm.shift(4), 52)
    # report dated Tuesday T -> acted at the close of the first trading day on/after T+6 (Monday)
    act = [p.index[p.index.searchsorted(t + pd.Timedelta(days=6))] if p.index.searchsorted(t + pd.Timedelta(days=6)) < len(p) else pd.NaT for t in S.index]
    S["act"] = act
    S = S.dropna(subset=["act"]).drop_duplicates("act").set_index("act")
    S["px"] = p.reindex(S.index)
    S["fwd"] = S.px.shift(-1) / S.px - 1          # Monday close -> next Monday close
    return S


def nw_t(x, lag=4):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    n = len(x)
    if n < 10: return np.nan
    u = x - x.mean(); v = (u @ u) / n
    for k in range(1, lag + 1):
        v += 2 * (1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n
    return float(x.mean() / np.sqrt(v / n)) if v > 0 else np.nan


def book(sig, fwd, cost, hold):
    w = sig.rolling(hold, min_periods=1).mean() if hold > 1 else sig          # overlapping tranches
    w = w.fillna(0)
    r = w * fwd - cost * w.diff().abs().fillna(w.abs())
    return r, w


def stats(r, w, a, b, fin=0.065 / 52):
    m = (r.index >= a) & (r.index < b) & r.notna()
    x, ww = r[m], w[m]
    act = x[ww != 0]
    eq = (1 + x).cumprod()
    return dict(weeks=int(len(x)), weeks_in=int((ww != 0).sum()), mean_bp_week=round(float(x.mean() * 1e4), 2), t_nw=round(nw_t(x), 2),
                ann_pct=round(float(x.mean() * 52 * 100), 2), sharpe=round(float(x.mean() / x.std() * np.sqrt(52)), 2) if x.std() > 0 else None,
                max_dd_pct=round(float((eq / eq.cummax() - 1).min() * 100), 1), ann_pct_cfd=round(float((x - fin * ww.abs()).mean() * 52 * 100), 2),
                win_weeks=round(float((act > 0).mean()), 3) if len(act) else None)


G, S = weekly("gold", "GC"), weekly("silver", "SI")
res = dict(plan="edges/plans/E146_cot_positioning.md", md5=PLAN, rules={})
sg = lambda up, dn: pd.Series(np.where(up, 1.0, np.where(dn, -1.0, 0.0)), index=up.index)
for nm, D, cost in (("gold", G, 0.0002), ("silver", S, 0.0004)):
    rules = {"C1 fade crowded funds": (sg(D.z_mm <= -1.5, D.z_mm >= 1.5), 4), "C2 follow fund flows": (sg(D.zd >= 1, D.zd <= -1), 1),
             "C3 follow producers": (sg(D.z_pm >= 1.5, D.z_pm <= -1.5), 4),
             "C4 long unless crowded": (pd.Series(np.where(D.z_mm >= 1.5, 0.0, 1.0), index=D.index).where(D.z_mm.notna()), 1),
             "buy and hold": (pd.Series(1.0, index=D.index), 1)}
    for rn, (sig, hold) in rules.items():
        r, w = book(sig, D.fwd, cost, hold)
        res["rules"][f"{nm} {rn}"] = {p: stats(r, w, pd.Timestamp(a), pd.Timestamp(b)) for p, (a, b) in PER.items()}
        for p in ("validation", "final"):
            s_ = res["rules"][f"{nm} {rn}"][p]
            bt.log_attempt(PLAN, f"E146 {nm} {rn}", p, dict(n=s_["weeks_in"], mean_bp=s_["mean_bp_week"], t_week=s_["t_nw"]))
        print(nm, rn, {p: (v["weeks_in"], v["ann_pct"], v["t_nw"], v["sharpe"], v["max_dd_pct"], v["win_weeks"]) for p, v in res["rules"][f"{nm} {rn}"].items()})
J = G.join(S, lsuffix="_g", rsuffix="_s", how="inner")
s = J.z_mm_g - J.z_mm_s
sig = sg(s >= 1, s <= -1)
r, w = book(sig, J.fwd_s - J.fwd_g, 0.0006, 4)
res["rules"]["C5 gold vs silver"] = {p: stats(r, w, pd.Timestamp(a), pd.Timestamp(b)) for p, (a, b) in PER.items()}
print("C5", {p: (v["weeks_in"], v["ann_pct"], v["t_nw"], v["sharpe"]) for p, v in res["rules"]["C5 gold vs silver"].items()})
ok = [k for k, v in res["rules"].items() if "hold" not in k and "C4" not in k and v["final"]["mean_bp_week"] > 0 and (v["final"]["t_nw"] or 0) >= 2
      and v["validation"]["mean_bp_week"] > 0 and (v["validation"]["t_nw"] or 0) >= 1.5]
for nm in ("gold", "silver"):
    c4, bh = res["rules"][f"{nm} C4 long unless crowded"], res["rules"][f"{nm} buy and hold"]
    if all(c4[p]["sharpe"] > bh[p]["sharpe"] and c4[p]["max_dd_pct"] >= bh[p]["max_dd_pct"] for p in ("validation", "final")):
        ok.append(f"{nm} C4")
res["latest"] = {nm: dict(report_acted=str(D.index[-1].date()), z_mm=round(float(D.z_mm.iloc[-1]), 2), z_pm=round(float(D.z_pm.iloc[-1]), 2), zd=round(float(D.zd.iloc[-1]), 2), mm_net_share=round(float(D.mm.iloc[-1]), 3)) for nm, D in (("gold", G), ("silver", S))}
res["verdict"] = ("PASS: " + ", ".join(ok)) if ok else "FAIL"
json.dump(res, open("edges/results/E146_result.json", "w"), indent=1, default=str)
print(res["latest"]); print(res["verdict"])
