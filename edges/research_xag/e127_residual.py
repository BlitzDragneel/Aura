"""E127 silver vs gold residual reversal (plan E127_xag_residual_reversal.md)."""
import numpy as np
import pandas as pd

from edges.research_xag import xlib as X
from edges.research_xag.dgrid import market, run_grid

PLAN = "cdd9350a1f6a98805d9dfc4bb32ce6bb"


def main():
    df, rets, gap = market()
    ls, lg = np.log(df.SI).diff(), np.log(df.GC).diff()
    beta = (ls.rolling(250).cov(lg) / lg.rolling(250).var())
    e = ls - beta * lg
    sd = e.rolling(60).std()
    V, mins = {}, {}
    for K in (1, 3, 5):
        z = (e.rolling(K).sum() / (sd * np.sqrt(K))).values
        for H in (1, 5):
            pos = np.zeros(len(df))
            i = 0
            while i < len(df):
                if np.isfinite(z[i]) and abs(z[i]) > 1:
                    pos[i:i + H] = -np.sign(z[i])
                    i += H
                else:
                    i += 1
            s = pd.Series(pos, index=df.index)
            for kind in ("PAIR", "SILVER"):
                n = f"RES_K{K}_H{H}_{kind}"
                gcw = -s * beta.fillna(0) if kind == "PAIR" else 0.0 * s
                V[n] = pd.DataFrame({"SI": s, "GC": gcw})
                mins[n] = 30
    out, P, T = run_grid(V, rets, gap, PLAN, "E127", mins)
    out.update(plan="edges/plans/E127_xag_residual_reversal.md", md5=PLAN)
    for k, v in out["variants"].items():
        print(k, {p: (v[p].get("trades"), v[p].get("mean_bp"), v[p].get("t_nw"), v[p].get("stress_mean_bp")) for p in X.DPER})
    print(out["selection"], out["verdict"])
    X.save("E127", out)


if __name__ == "__main__":
    main()
