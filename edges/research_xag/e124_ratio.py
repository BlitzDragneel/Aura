"""E124 gold/silver ratio swing (plan E124_xag_ratio_swing.md)."""
import numpy as np
import pandas as pd

from edges.research_xag import xlib as X
from edges.research_xag.dgrid import market, run_grid

PLAN = "99ad36a48e53a275a526c1cb1d7d0f25"


def mr_pos(R, L, e, maxhold=20):
    mu, sd = R.rolling(L).mean(), R.rolling(L).std()
    z = ((R - mu) / sd).values
    pos = np.zeros(len(R))
    cur, held = 0, 0
    for i in range(len(R)):
        if not np.isfinite(z[i]):
            continue
        if cur != 0:
            held += 1
            if np.sign(z[i]) != cur or held >= maxhold:  # cur=+1 entered at z>e (long silver): exit when z<=0
                cur, held = 0, 0
        if cur == 0:
            if z[i] > e:
                cur, held = 1, 0
            elif z[i] < -e:
                cur, held = -1, 0
        pos[i] = cur
    return pd.Series(pos, index=R.index)


def legs(s, kind):
    return pd.DataFrame({"SI": s, "GC": -s if kind == "PAIR" else 0.0 * s})


def main():
    df, rets, gap = market()
    R = np.log(df.GC / df.SI)
    V, mins = {}, {}
    for L in (60, 120, 250):
        for e in (1.5, 2.0):
            s = mr_pos(R, L, e)
            for kind in ("PAIR", "SILVER"):
                n = f"MR_L{L}_e{e}_{kind}"
                V[n], mins[n] = legs(s, kind), 30
    for L in (20, 60, 120):
        m = R - R.shift(L)
        s = pd.Series(np.where(m < 0, 1.0, np.where(m > 0, -1.0, 0.0)), index=R.index).where(m.notna(), 0.0)
        for kind in ("PAIR", "SILVER"):
            V[f"TREND_L{L}_{kind}"] = legs(s, kind)
    out, P, T = run_grid(V, rets, gap, PLAN, "E124", mins)
    out.update(plan="edges/plans/E124_xag_ratio_swing.md", md5=PLAN)
    for k, v in out["variants"].items():
        print(k, {p: (v[p].get("trades"), v[p].get("mean_bp"), v[p].get("t_nw"), v[p].get("sharpe")) for p in X.DPER})
    print(out["selection"], out["verdict"])
    X.save("E124", out)


if __name__ == "__main__":
    main()
