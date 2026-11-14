"""E126 silver holding: E85 as written, pre-registered improvements, silver/gold rotation (plan E126_xag_hold_controller.md)."""
import numpy as np
import pandas as pd

from edges.lib import bt
from edges.research_xag import xlib as X
from edges.research_xag.dgrid import market

PLAN = "13cd962ba99baa23f1f19774281d6995"
COST = 0.0005


def pnl(w, rets, gap, stress=1.0, fin=False, cost=COST):
    """w: DataFrame exposures [SI, GC] decided at close t."""
    w = w.reindex(rets.index).fillna(0.0)
    p = pd.Series(0.0, index=rets.index)
    for c in w.columns:
        turn = w[c].diff().abs().fillna(w[c].abs())
        p += w[c] * rets[c] - stress * cost * turn
        if fin:
            p -= X.FIN_NIGHT * gap * w[c].abs()
    return p.iloc[:-1]


def controller(c, tau, lbs):
    lr = np.log(c).diff()
    part = sum((c / c.shift(k) - 1 > 0).astype(float) for k in lbs) / 3
    v20, v60 = lr.rolling(20).std() * np.sqrt(252), lr.rolling(60).std() * np.sqrt(252)
    scale = (tau / np.maximum(v20, v60)).clip(upper=1.0)
    return (part * scale).fillna(0.0), scale.fillna(0.0)


def rotation(df, L, cash):
    mom = df / df.shift(L) - 1
    fri = df.index.to_series().groupby(df.index.to_period("W")).transform("max") == df.index.to_series()
    w = pd.DataFrame(np.nan, index=df.index, columns=["SI", "GC"])
    for t in df.index[fri.values]:
        m = mom.loc[t]
        if m.isna().any():
            continue
        win = m.idxmax()
        row = {"SI": 0.0, "GC": 0.0}
        if not (cash and m[win] <= 0):
            row[win] = 1.0
        w.loc[t] = row
    return w.ffill().fillna(0.0)


def fifty(df):
    # monthly-rebalanced 50/50: weights drift within the month
    w = pd.DataFrame(index=df.index, columns=["SI", "GC"], dtype=float)
    month = df.index.to_period("M")
    for m, idx in df.groupby(month).groups.items():
        base = df.loc[idx].iloc[0]
        val = 0.5 * df.loc[idx] / base
        w.loc[idx] = (val.div(val.sum(axis=1), axis=0)).values
    return w


def stats_all(series):
    out = {}
    for p, (a, b) in X.DPER.items():
        s = series[(series.index >= a) & (series.index < b)]
        out[p] = X.dstats(s)
    return out


def main():
    df, rets, gap = market()
    si = df.SI
    one = pd.DataFrame({"SI": 1.0, "GC": 0.0}, index=df.index)
    books = {"buy_hold_SI": one, "buy_hold_GC": pd.DataFrame({"SI": 0.0, "GC": 1.0}, index=df.index), "fifty_fifty": fifty(df)}
    e85, vol10 = controller(si, 0.10, (20, 60, 120))
    books["A_E85_as_written"] = pd.DataFrame({"SI": e85, "GC": 0.0})
    books["vol_only_t10"] = pd.DataFrame({"SI": vol10, "GC": 0.0})
    grid_B, grid_C = [], []
    for tau in (0.15, 0.20, 0.25):
        for lbs in ((20, 60, 120), (50, 100, 200)):
            w, vo = controller(si, tau, lbs)
            n = f"B_tau{int(tau*100)}_lb{lbs[0]}"
            books[n] = pd.DataFrame({"SI": w, "GC": 0.0})
            books[f"vol_only_t{int(tau*100)}"] = pd.DataFrame({"SI": vo, "GC": 0.0})
            grid_B.append(n)
    for L in (60, 120, 250):
        for cash in (True, False):
            n = f"C_rot_L{L}_{'CASH' if cash else 'ALWAYS'}"
            books[n] = rotation(df, L, cash)
            grid_C.append(n)
    S, Sfin, Sstr = {}, {}, {}
    P = {}
    for n, w in books.items():
        P[n] = pnl(w, rets, gap)
        S[n] = stats_all(P[n])
        Sfin[n] = stats_all(pnl(w, rets, gap, fin=True))
        Sstr[n] = stats_all(pnl(w, rets, gap, stress=2.0))
        if n.startswith(("A_", "B_", "C_")):
            bt.log_attempt(PLAN, f"E126 {n}", "discovery", dict(n=S[n]["discovery"]["days"], mean_bp=S[n]["discovery"]["mean_bp"],
                                                               t_week=S[n]["discovery"]["t_nw"], sharpe=S[n]["discovery"]["sharpe"]))

    def judge(n, ctrl):
        ok, why = True, []
        for p in ("validation", "final"):
            s, bh, c = S[n][p], S["buy_hold_SI"][p], S[ctrl][p]
            conds = dict(sharpe_gt_bh=s["sharpe"] > bh["sharpe"], sharpe_gt_ctrl=s["sharpe"] > c["sharpe"],
                         dd_le_075bh=s["max_dd"] >= 0.75 * bh["max_dd"], t_ok=s["mean_bp"] > 0 and s["t_nw"] >= (2 if p == "final" else 1.5))
            why.append({p: conds})
            ok = ok and all(conds.values())
        return ok, why

    # luck check: best discovery Sharpe over a grid vs circularly shifted exposures
    a, b = X.DPER["discovery"]
    m = (rets.index >= a) & (rets.index < b)
    idx = rets.index[m]
    rng = np.random.default_rng(3)

    def null_best(grid):
        out = []
        for _ in range(200):
            off = int(rng.integers(120, len(idx) - 120))
            best = -9
            for n in grid:
                w = books[n].reindex(idx).fillna(0.0)
                ws = pd.DataFrame(np.roll(w.values, off, axis=0), index=idx, columns=w.columns)
                s = pnl(ws, rets[m].iloc[:], gap[m])
                sh = s.mean() / s.std() * np.sqrt(252) if s.std() > 0 else -9
                best = max(best, sh)
            out.append(best)
        return float(np.percentile(out, 95))

    res = dict(plan="edges/plans/E126_xag_hold_controller.md", md5=PLAN, stats=S, stats_cfd_financing=Sfin, stats_stress=Sstr)
    okA, whyA = judge("A_E85_as_written", "vol_only_t10")
    for p in ("validation", "final"):
        bt.log_attempt(PLAN, "E126 A_E85_as_written", p, dict(n=S["A_E85_as_written"][p]["days"], mean_bp=S["A_E85_as_written"][p]["mean_bp"],
                                                             t_week=S["A_E85_as_written"][p]["t_nw"]))
    res["A"] = dict(verdict="PASS" if okA else "FAIL", checks=whyA)
    for tag, grid, ctrlf in (("B", grid_B, lambda n: "vol_only_t" + n.split("_tau")[1].split("_")[0]), ("C", grid_C, lambda n: "fifty_fifty")):
        best = max(grid, key=lambda n: S[n]["discovery"]["sharpe"])
        p95 = null_best(grid)
        d = S[best]["discovery"]
        ctrl = ctrlf(best)
        disc_ok = d["sharpe"] > S["buy_hold_SI"]["discovery"]["sharpe"] and d["sharpe"] > S[ctrl]["discovery"]["sharpe"] and d["sharpe"] >= p95
        sel = dict(best=best, control=ctrl, discovery_sharpe=d["sharpe"], bh_sharpe=S["buy_hold_SI"]["discovery"]["sharpe"],
                   ctrl_sharpe=S[ctrl]["discovery"]["sharpe"], shifted_best_sharpe_p95=round(p95, 2), promoted=bool(disc_ok))
        if disc_ok:
            ok, why = judge(best, ctrl)
            for p in ("validation", "final"):
                bt.log_attempt(PLAN, f"E126 {best}", p, dict(n=S[best][p]["days"], mean_bp=S[best][p]["mean_bp"], t_week=S[best][p]["t_nw"]))
            sel.update(verdict="PASS" if ok else "FAIL (judged)", checks=why)
        else:
            sel.update(verdict="FAIL before validation (discovery/luck)", checks_info=judge(best, ctrl)[1])
        res[tag] = sel
    for n in books:
        print(n, {p: (S[n][p]["sharpe"], S[n][p]["cagr"], S[n][p]["max_dd"], S[n][p]["t_nw"]) for p in X.DPER})
    print("A", res["A"]["verdict"], "\nB", {k: v for k, v in res["B"].items() if k not in ("checks", "checks_info")},
          "\nC", {k: v for k, v in res["C"].items() if k not in ("checks", "checks_info")})
    X.save("E126", res)


if __name__ == "__main__":
    main()
