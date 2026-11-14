"""E125 silver multi-day momentum/reversal with vol targeting, post-shock drift (plan E125_xag_momentum_shock_swing.md)."""
import numpy as np
import pandas as pd

from edges.research_xag import xlib as X
from edges.research_xag.dgrid import market, run_grid

PLAN = "997a208b90c5a13a7bbe5ee99c420d24"


def main():
    df, rets, gap = market()
    c = df.SI
    lr = np.log(c).diff()
    vol20 = lr.rolling(20).std() * np.sqrt(252)
    notional = (0.20 / vol20).clip(upper=2.0)
    V, mins = {}, {}
    for L in (5, 10, 20, 60):
        s = np.sign(np.log(c) - np.log(c.shift(L)))
        for mode in ("MOM", "REV"):
            ss = s if mode == "MOM" else -s
            for side in ("LS", "LONG"):
                w = ss if side == "LS" else ss.clip(lower=0)
                V[f"{mode}_L{L}_{side}"] = pd.DataFrame({"SI": (w * notional).fillna(0.0), "GC": 0.0}, index=c.index)
    sig60 = lr.rolling(60).std().shift(1)
    z = (lr / sig60).values
    for k in (2, 3):
        for mode in ("FOLLOW", "FADE"):
            for H in (1, 5, 10):
                pos = np.zeros(len(c))
                i = 0
                while i < len(c):
                    if np.isfinite(z[i]) and abs(z[i]) > k:
                        sd = np.sign(z[i]) * (1 if mode == "FOLLOW" else -1)
                        pos[i:i + H] = sd   # enter at close i, hold H days
                        i += H
                    else:
                        i += 1
                n = f"SHOCK_k{k}_{mode}_H{H}"
                V[n] = pd.DataFrame({"SI": pos, "GC": 0.0}, index=c.index)
                mins[n] = 30
    out, P, T = run_grid(V, rets, gap, PLAN, "E125", mins)
    out.update(plan="edges/plans/E125_xag_momentum_shock_swing.md", md5=PLAN)
    for k, v in out["variants"].items():
        print(k, {p: (v[p].get("trades"), v[p].get("mean_bp"), v[p].get("t_nw"), v[p].get("sharpe")) for p in X.DPER})
    print(out["selection"], out["verdict"])
    X.save("E125", out)


if __name__ == "__main__":
    main()
