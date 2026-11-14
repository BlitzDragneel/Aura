"""E128 silver holding with MA trend gates incl. gold-gated silver (plan E128_xag_hold_gates.md)."""
import numpy as np
import pandas as pd

from edges.lib import bt
from edges.research_xag import xlib as X
from edges.research_xag.dgrid import market
from edges.research_xag.e126_hold import pnl, stats_all

PLAN = "349a4ae40c5cf451f8f58e7ba6b08d1f"


def main():
    df, rets, gap = market()
    lr = np.log(df.SI).diff()
    volsz = (0.20 / (lr.rolling(60).std() * np.sqrt(252))).clip(upper=1.0).fillna(0.0)
    books = {"buy_hold_SI": pd.DataFrame({"SI": 1.0, "GC": 0.0}, index=df.index),
             "vol_only_VOL": pd.DataFrame({"SI": volsz, "GC": 0.0})}
    gates, grid = {}, []
    for ma in (100, 200):
        gs = (df.SI > df.SI.rolling(ma).mean()).astype(float)
        gg = (df.GC > df.GC.rolling(ma).mean()).astype(float)
        for src, g in (("SILVER", gs), ("GOLD", gg), ("BOTH", gs * gg)):
            for size in ("FULL", "VOL"):
                n = f"G_{src}_MA{ma}_{size}"
                w = g * (1.0 if size == "FULL" else volsz)
                books[n] = pd.DataFrame({"SI": w.fillna(0.0), "GC": 0.0})
                gates[n] = (g, size)
                grid.append(n)
    S, Sf, Ss = {}, {}, {}
    for n, w in books.items():
        S[n], Sf[n], Ss[n] = stats_all(pnl(w, rets, gap)), stats_all(pnl(w, rets, gap, fin=True)), stats_all(pnl(w, rets, gap, stress=2))
        if n.startswith("G_"):
            bt.log_attempt(PLAN, f"E128 {n}", "discovery", dict(n=S[n]["discovery"]["days"], mean_bp=S[n]["discovery"]["mean_bp"],
                                                               t_week=S[n]["discovery"]["t_nw"], sharpe=S[n]["discovery"]["sharpe"]))
    a, b = X.DPER["discovery"]
    m = (rets.index >= a) & (rets.index < b)
    idx = rets.index[m]
    rng = np.random.default_rng(4)
    null = []
    for _ in range(200):
        off = int(rng.integers(120, len(idx) - 120))
        best = -9
        for n in grid:
            g, size = gates[n]
            gsh = pd.Series(np.roll(g.reindex(idx).fillna(0).values, off), index=idx)
            w = gsh * (1.0 if size == "FULL" else volsz.reindex(idx))
            s = pnl(pd.DataFrame({"SI": w, "GC": 0.0}), rets[m], gap[m])
            best = max(best, s.mean() / s.std() * np.sqrt(252))
        null.append(best)
    p95 = float(np.percentile(null, 95))
    best = max(grid, key=lambda n: S[n]["discovery"]["sharpe"])
    ctrl = "buy_hold_SI" if best.endswith("FULL") else "vol_only_VOL"
    d = S[best]["discovery"]
    promoted = d["sharpe"] > S["buy_hold_SI"]["discovery"]["sharpe"] and d["sharpe"] > S[ctrl]["discovery"]["sharpe"] and d["sharpe"] >= p95
    checks = {}
    ok = promoted
    for p in ("validation", "final"):
        s, bh, c = S[best][p], S["buy_hold_SI"][p], S[ctrl][p]
        cc = dict(sharpe_gt_bh=s["sharpe"] > bh["sharpe"], sharpe_gt_ctrl=s["sharpe"] > c["sharpe"], dd_le_075bh=s["max_dd"] >= 0.75 * bh["max_dd"],
                  t_ok=s["mean_bp"] > 0 and s["t_nw"] >= (2 if p == "final" else 1.5))
        checks[p] = cc
        ok = ok and all(cc.values())
        if promoted:
            bt.log_attempt(PLAN, f"E128 {best}", p, dict(n=s["days"], mean_bp=s["mean_bp"], t_week=s["t_nw"], sharpe=s["sharpe"]))
    verdict = ("PASS" if ok else ("FAIL (judged)" if promoted else "FAIL before validation (discovery/luck)"))
    res = dict(plan="edges/plans/E128_xag_hold_gates.md", md5=PLAN, stats=S, stats_cfd_financing=Sf, stats_stress=Ss,
               selection=dict(best=best, control=ctrl, discovery_sharpe=d["sharpe"], bh=S["buy_hold_SI"]["discovery"]["sharpe"],
                              ctrl_sharpe=S[ctrl]["discovery"]["sharpe"], shifted_best_sharpe_p95=round(p95, 2), promoted=bool(promoted),
                              checks=checks, verdict=verdict))
    for n in books:
        print(n, {p: (S[n][p]["sharpe"], S[n][p]["cagr"], S[n][p]["max_dd"], S[n][p]["t_nw"]) for p in X.DPER})
    print({k: v for k, v in res["selection"].items()})
    X.save("E128", res)


if __name__ == "__main__":
    main()
