"""E143 direction from positioning (plan edges/plans/E143_positioning_direction.md, md5 2a8b2b87...).
Usage: python3 -m edges.lead.e143_positioning <XAU_perp_1m.parquet>"""
import json
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from edges.lib import bt
from edges.lead.e142_movement import bars15, features, fit, simulate

warnings.filterwarnings("ignore")
PLAN = "2a8b2b878acee7ea8bcbdb42cb3a2494"
M = "/home/user/data/metrics/"
SETS = {"BTC": dict(per=("2022-01-01", "2024-01-01", "2025-01-01", "2026-11-04"), costs={"base": 0.0007}),
        "GOLD": dict(per=("2025-12-11", "2026-06-01", "2026-09-01", "2026-11-14"), costs={"base": 0.0002, "tight": 0.000025})}


def z(x, n=672):
    return (x - x.rolling(n, min_periods=n // 2).mean()) / x.rolling(n, min_periods=n // 2).std()


def positioning(met, idx):
    m = met.copy()
    m.index = m.index + pd.Timedelta("5min")            # known 5 minutes after its stamp
    m = m.resample("15min", label="left", closed="left").last()   # last value known inside bar [T, T+15m)
    m = m.reindex(idx)
    P = pd.DataFrame(index=idx)
    lt, la, lc, lk, lo = np.log(m.top_pos), np.log(m.top_acct), np.log(m.crowd), np.log(m.taker.clip(lower=1e-3)), np.log(m.oi)
    P["div"] = lt - lc
    for n, s in (("tp", lt), ("ta", la), ("cr", lc), ("tk", lk), ("dv", P["div"])):
        P[f"z_{n}"] = z(s)
        for k, lab in ((4, "1h"), (16, "4h"), (96, "24h")):
            P[f"d_{n}_{lab}"] = s - s.shift(k)
    for k, lab in ((4, "1h"), (16, "4h"), (96, "24h")):
        P[f"doi_{lab}"] = lo - lo.shift(k)
    P["z_doi4"] = z(P.doi_4h)
    P["z_dtp4"] = z(P.d_tp_4h)
    return P.drop(columns="div")


def fund_cost(t, fund):
    if fund is None or not len(t):
        return np.zeros(len(t))
    cs = fund.cumsum()
    a = cs.reindex(t.time, method="ffill").fillna(0).values
    b = cs.reindex(t.exit, method="ffill").fillna(0).values
    return (b - a) * t.d.values   # longs pay positive funding


def tstats(t, cost, a, b, fund=None):
    s = t[(t.time >= a) & (t.time < b)].copy()
    if len(s) < 5:
        return dict(n=int(len(s)))
    s["net"] = s.gross - 2 * cost - fund_cost(s, fund)
    return dict(n=int(len(s)), gross_bp=round(float(s.gross.mean() * 1e4), 2), mean_bp=round(float(s.net.mean() * 1e4), 2),
                t_week=round(bt.tstat_weekly(s), 2), win=round(float((s.net > 0).mean()), 3))


def run(name, fine, met, fund, cfg, res):
    f = bars15(fine)
    X, atr = features(f)
    P = positioning(met, f.index)
    a0, a1, a2, a3 = [pd.Timestamp(x, tz="UTC") for x in cfg["per"]]
    ok = X.notna().all(axis=1) & (f.index >= a0) & (f.index < a3)
    idx = X.index[ok]
    step = int(round(pd.Timedelta("15min") / (fine.index[1] - fine.index[0])))
    pos = fine.index.searchsorted(idx + pd.Timedelta("15min"))
    A = atr.reindex(idx).values
    r4 = (f.c / f.c.shift(16) - 1).reindex(idx).values
    a14 = (atr / f.c).reindex(idx).values
    Pi = P.reindex(idx)
    sg = lambda up, dn: np.where(up, 1, np.where(dn, -1, 0))
    rules = {
        "P1 follow smart vs crowd": sg(Pi.z_dv >= 1.5, Pi.z_dv <= -1.5),
        "P2 fade the crowd": sg(Pi.z_cr <= -2, Pi.z_cr >= 2),
        "P3 follow top traders' change": sg(Pi.z_dtp4 >= 2, Pi.z_dtp4 <= -2),
        "P4 OI-confirmed move": np.where((Pi.z_doi4 >= 2) & (np.abs(r4) >= 2 * a14), np.sign(r4), 0),
        "P5 OI flush fade": np.where((Pi.z_doi4 <= -2) & (np.abs(r4) >= 2 * a14), -np.sign(r4), 0),
    }
    R = dict(trades={}, model={})
    # model
    fwd = {"4h": 16, "24h": 96}
    XP = pd.concat([X, P], axis=1)
    for hz, n in fwd.items():
        y = (f.c.shift(-n) / f.c - 1)
        yb = (y > 0).astype(float).where(y.notna())
        seg = {k: ok & yb.notna() & (f.index >= lo) & (f.index < hi) for k, (lo, hi) in (("train", (a0, a1 - pd.Timedelta(hours=24))), ("val", (a1, a2 - pd.Timedelta(hours=24))), ("final", (a2, a3)))}
        row = {}
        for lab, cols in (("price_only", list(X.columns)), ("with_positioning", list(XP.columns))):
            p = fit(XP.loc[seg["train"], cols], yb[seg["train"]], XP.loc[seg["val"], cols], yb[seg["val"]], True)
            pf, pv = p(XP.loc[seg["final"], cols]), p(XP.loc[seg["val"], cols])
            row[f"auc_{lab}"] = round(float(roc_auc_score(yb[seg["final"]], pf)), 4)
            row[f"auc_val_{lab}"] = round(float(roc_auc_score(yb[seg["val"]], pv)), 4)
            if lab == "with_positioning":
                thr = np.quantile(np.abs(pv - 0.5), 0.75)
                pa = p(XP.loc[ok, cols])
                rules[f"P6 model {hz}"] = np.where(np.abs(pa - 0.5) >= thr, np.sign(pa - 0.5), 0)
                yf = yb[seg["final"]]
                conf = np.abs(pf - 0.5) >= thr
                row["top25_accuracy"] = round(float(((pf[conf] > 0.5) == (yf[conf] > 0.5)).mean()), 4) if conf.sum() else None
                row["top25_share"] = round(float(conf.mean()), 3)
        R["model"][hz] = row
        print(name, "model", hz, row, flush=True)
    rng = np.random.default_rng(143)
    per = [("train", (a0, a1)), ("val", (a1, a2)), ("final", (a2, a3))]
    for rn, d in rules.items():
        d = np.nan_to_num(np.asarray(d, float)).astype(int)
        holds = [("24h", 96, 3.0, None)] if rn == "P6 model 24h" else ([("4h", 16, 1.5, 3.0)] if rn == "P6 model 4h" else [("4h", 16, 1.5, 3.0), ("24h", 96, 3.0, None)])
        for hl, hb, sk, tk in holds:
            s = d != 0
            t, _ = simulate(fine, pos[s], A[s], dirs=d[s], arm=4 * step, hold=hb * step, stop_k=sk, tgt_k=tk)
            # control: same count per month, random bars and sides
            mon = pd.Series(t.time.dt.strftime("%Y-%m")).value_counts()
            im = pd.Series(idx.strftime("%Y-%m"))
            pick = np.sort(np.concatenate([rng.choice(np.flatnonzero((im == m).values), size=min(c * 3, int((im == m).sum())), replace=False) for m, c in mon.items()])) if len(mon) else np.array([], int)
            tc, _ = simulate(fine, pos[pick], A[pick], dirs=rng.choice([-1, 1], len(pick)), arm=4 * step, hold=hb * step, stop_k=sk, tgt_k=tk)
            key = f"{rn} [{hl}]"
            R["trades"][key] = {}
            for cn, cst in cfg["costs"].items():
                fu = fund if hl == "24h" else None
                R["trades"][key][cn] = {p: tstats(t, cst, x, y_, fu) for p, (x, y_) in per}
                R["trades"][key][cn]["control_final"] = tstats(tc, cst, a2, a3, fu)
                for p in ("val", "final"):
                    st = R["trades"][key][cn][p]
                    bt.log_attempt(PLAN, f"E143 {name} {key} {cn}", p, dict(n=st.get("n"), mean_bp=st.get("mean_bp"), t_week=st.get("t_week")))
            b = R["trades"][key]["base"]
            print(name, key, {p: (v.get("n"), v.get("gross_bp"), v.get("mean_bp"), v.get("t_week"), v.get("win")) for p, v in b.items()}, flush=True)
    res[name] = R


def main(xau):
    res = dict(plan="edges/plans/E143_positioning_direction.md", md5=PLAN)
    btc = bt.load("BTCUSDT", "5m")[["o", "h", "l", "c", "v", "tbv"]].astype(float)
    run("BTC", btc, pd.read_parquet(M + "BTCUSDT_metrics_5m.parquet"), bt.funding("BTCUSDT"), SETS["BTC"], res)
    gf = pd.read_parquet("/home/user/data/metals/XAUUSDT_funding.parquet").rate
    run("GOLD", pd.read_parquet(xau)[["o", "h", "l", "c", "v"]].astype(float), pd.read_parquet(M + "XAUUSDT_metrics_5m.parquet"), gf, SETS["GOLD"], res)
    v = []
    for n in ("BTC", "GOLD"):
        T = res[n]["trades"]
        best = [k for k in T if (T[k]["base"]["final"].get("mean_bp") or -1) > 0 and (T[k]["base"]["final"].get("t_week") or 0) >= 2
                and (T[k]["base"]["val"].get("mean_bp") or -1) > 0 and (T[k]["base"]["val"].get("t_week") or 0) >= 1.5
                and T[k]["base"]["final"]["mean_bp"] > (T[k]["base"]["control_final"].get("mean_bp") or -99)]
        v.append(f"{n}: {'PASS ' + ', '.join(best) if best else 'FAIL'}")
    res["verdict"] = "; ".join(v)
    json.dump(res, open("edges/results/E143_result.json", "w"), indent=1, default=str)
    print(res["verdict"])


if __name__ == "__main__":
    main(sys.argv[1])
