"""E37 / E38 / E39: panic bounce limit entry at 5m / 15m / 4h. Stage 1: all trades saved + discovery luck check.
usage: python run_panic.py E37 [repeats]"""
import sys, time, pickle
import numpy as np, pandas as pd
from lib1 import *  # noqa
from searchkit import WeekAgg, best_t, random_mask, disc_range, week_id

CFG = {
    "E37": dict(tf="5m", coins=coins5, Ls=(24, 288), ks=(1, 2, 4), Ws=(3, 12), Hs=(24, 288), look=8640, step=288),
    "E38": dict(tf="15m", coins=coins5, Ls=(24, 96), ks=(1, 2, 4), Ws=(3, 12), Hs=(24, 96), look=2880, step=96),
    "E39": dict(tf="4h", coins=coins4h, Ls=(6, 24), ks=(1, 2, 3), Ws=(2, 6), Hs=(6, 24), look=180, step=6),
}


def variants(cfg):
    return [(L, k, W, H) for L in cfg["Ls"] for k in cfg["ks"] for W in cfg["Ws"] for H in cfg["Hs"]]


def main(plan, R):
    cfg = CFG[plan]; tf = cfg["tf"]; V = variants(cfg)
    names = [f"L{L} k{k} W{W} H{H}" for (L, k, W, H) in V]
    syms = cfg["coins"]()
    a, b = bt.PERIODS["discovery"]
    w0 = int((pd.Timestamp(a).value + 3 * 86400 * 10**9) // (7 * 86400 * 10**9)); w1 = w0 + 215
    agg_real = WeekAgg((len(V),), w0, w1); agg_luck = WeekAgg((R, len(V)), w0, w1)
    rng = np.random.default_rng(37)
    real = {i: [] for i in range(len(V))}
    t0 = time.time()
    for si, s in enumerate(syms):
        try:
            d = load_tf(s, tf)
        except Exception as e:
            print("skip", s, e); continue
        if len(d) < cfg["look"] + 200:
            continue
        c, l = d.c.values, d.l.values
        sg = sigma(c); q24 = qv24(d, tf)
        valid = np.isfinite(c) & np.isfinite(sg) & (sg > 0)
        masks = {}
        for L in cfg["Ls"]:
            r = np.log(d.c / d.c.shift(L)).values
            th = day_thresholds(r, cfg["look"], cfg["step"])
            masks[L] = np.nan_to_num(r <= th, nan=0).astype(np.bool_) & np.isfinite(th)
        lo, hi = disc_range(d.index)
        for i, (L, k, W, H) in enumerate(V):
            rows = sim_limit(c, l, sg, masks[L], float(k), W, H, 0, len(c))
            tr = to_trades(rows, d, tf, s, q24, "maker")
            if tr is not None:
                real[i].append(tr); agg_real.add((i,), tr)
        if hi > lo + 100:
            for rep in range(R):
                rm = {L: random_mask(masks[L], valid, lo, hi, rng) for L in cfg["Ls"]}
                for i, (L, k, W, H) in enumerate(V):
                    rows = sim_limit(c, l, sg, rm[L], float(k), W, H, lo, hi)
                    tr = to_trades(rows, d, tf, s, q24, "maker")
                    agg_luck.add((rep, i), tr)
        if si % 10 == 0:
            print(f"{si}/{len(syms)} {s} {time.time()-t0:.0f}s", flush=True)
    real = {i: (pd.concat(v, ignore_index=True) if v else pd.DataFrame()) for i, v in real.items()}
    pickle.dump(dict(names=names, V=V, real=real, luck=agg_luck.stats(), realfast=agg_real.stats()),
                open(f"{SCR}/{plan}_stage1.pkl", "wb"))
    print("done", time.time() - t0)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 100)
