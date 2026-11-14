"""E123 silver hourly shocks with vol gates + maker-only panic-bounce limits (plan E123_xag_day_shock_maker.md)."""
import numpy as np
import pandas as pd

from edges.lib import bt
from edges.research_xag import xlib as X
from edges.research_xag.e122_sessions import grid_eval

PLAN = "ead0af26e384fc7ea6f750b785e21084"


def sigma(A):
    r = pd.Series(np.log(A.c)).diff()
    return r.rolling(168, min_periods=100).std().shift(1).values, r.values


def volgate(A):
    c = X.daily("SI")
    v20 = np.log(c).diff().rolling(20).std()
    hi = (v20 > v20.rolling(250, min_periods=120).median()).astype(float).where(v20.notna())
    # known for bars on the NEXT calendar day after the daily close
    hi.index = hi.index + pd.Timedelta(days=1)
    return hi.reindex(A.t.normalize(), method="ffill").values


def limits(A, k, H, side, sg):
    out, i = [], 200
    while i < A.n - 2:
        if not np.isfinite(sg[i]):
            i += 1
            continue
        lim = A.c[i] * np.exp(-side * k * sg[i])
        fill = None
        for j in range(i + 1, min(i + 4, A.n)):
            if (side > 0 and A.l[j] < lim) or (side < 0 and A.h[j] > lim):
                fill = j
                break
        if fill is None:
            i += 1
            continue
        r = X.sim(A, fill, side, None, None, H + 1, venue="perp", entry_px=lim, entry_maker=True)
        if r is None:
            break
        out.append(r)
        i = r["x"] + 1
    return pd.DataFrame(out)


def main():
    A = X.H(X.hourly("SI"))
    sg, r = sigma(A)
    hv = volgate(A)
    V = {}
    for z in (2, 3):
        for mode in ("FOLLOW", "FADE"):
            for g in ("all", "high", "low"):
                sigs = []
                for i in range(200, A.n - 1):
                    if not (np.isfinite(sg[i]) and np.isfinite(r[i])) or abs(r[i]) <= z * sg[i]:
                        continue
                    if g == "high" and hv[i] != 1:
                        continue
                    if g == "low" and hv[i] != 0:
                        continue
                    sigs.append((i, int(np.sign(r[i])) * (1 if mode == "FOLLOW" else -1)))
                for h in (1, 4):
                    V[f"shock_z{z}_{mode}_{g}_h{h}"] = dict(sigs=sigs, lag=1, stop_atr=2.0, tgt_atr=None, hold=h)
    outA, _ = grid_eval(A, V, PLAN, "E123A")
    # B: maker-only limit bounce
    resB, trB = {}, {}
    for k in (2, 3):
        for H in (4, 12):
            for side, nm in ((1, "BUY"), (-1, "SELLmirror_info")):
                tr = limits(A, k, H, side, sg)
                row = {p: X.hsum(s, nm) for p, s in X.hsplit(tr).items()}
                name = f"limit_{nm}_k{k}_H{H}"
                bt.log_attempt(PLAN, f"E123B {name}", "discovery", row["discovery"])
                resB[name] = row
                trB[name] = tr
    cand = {k: v["discovery"] for k, v in resB.items() if "BUY" in k and v["discovery"].get("n", 0) >= 30}
    selB = {}
    if cand:
        best = max(cand, key=lambda k: cand[k]["t_week"] if cand[k]["t_week"] == cand[k]["t_week"] else -9)
        d = cand[best]
        H = int(best.split("_H")[1])
        disc = X.hsplit(trB[best])["discovery"]
        rc = X.random_control(A, disc, None, None, H + 1, n=200, venue="perp", maker=True)
        p95 = float(np.nanpercentile(rc, 95)) * 1e4
        promoted = d["t_week"] >= 2 and d["mean_bp"] > p95
        v, f = resB[best]["validation"], resB[best]["final"]
        selB = dict(best=best, discovery=d, random_entry_p95_bp=round(p95, 2), promoted=bool(promoted),
                    validation=v, final_info=f)
        if promoted:
            bt.log_attempt(PLAN, f"E123B {best}", "validation", v)
        vpass = promoted and v.get("n", 0) and v["mean_bp"] > 0 and v["t_week"] >= 1.5
        selB["verdict"] = ("FINAL to judge" if vpass else "FAIL before FINAL")
    out = dict(plan="edges/plans/E123_xag_day_shock_maker.md", md5=PLAN, A=outA, B=dict(variants=resB, selection=selB))
    for k, v in outA["variants"].items():
        print(k, [(p, v[p].get("n"), v[p].get("mean_bp"), v[p].get("t_week")) for p in ("discovery",)])
    print("A:", outA.get("selection"), outA["verdict"])
    for k, v in resB.items():
        print(k, [(p, v[p].get("n"), v[p].get("mean_bp"), v[p].get("t_week")) for p in X.HPER])
    print("B:", selB)
    X.save("E123", out)


if __name__ == "__main__":
    main()
