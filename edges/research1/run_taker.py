"""E40 (breadth 15m), E41 (climax 15m), E42 (climax 4h), E46 (wick/cascade 5m): taker entry at next open on a per-coin mask.
usage: python run_taker.py E41 [repeats]"""
import sys, time, pickle
import numpy as np, pandas as pd
from numpy.lib.stride_tricks import sliding_window_view as sw
from lib1 import *  # noqa
from searchkit import WeekAgg, random_mask, disc_range


def roll_med_prev(v, n):
    """median of the n values BEFORE each bar (NaN-aware via pandas)."""
    return pd.Series(v).rolling(n, min_periods=n // 2).median().shift(1).values


def sig_prev(c, n=168):
    lr = np.log(pd.Series(c) / pd.Series(c).shift(1))
    return lr.rolling(n, min_periods=120).std(ddof=1).shift(1).values, lr.values


def climax_masks(d, tf, grid):
    c, h, l, v = d.c.values, d.h.values, d.l.values, d.v.values
    sg, lr = sig_prev(c); medv = roll_med_prev(v, 168)
    rng = h - l; cl = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), 0.5)
    age = np.arange(len(c)) >= 30 * 1440 // TFMIN[tf]
    z = lr / sg
    out = {}
    for (Z, V, H) in grid:
        key = (Z, V)
        if key not in out:
            out[key] = np.nan_to_num((z <= -Z) & (v >= V * medv) & (cl >= 0.6), nan=0).astype(bool) & age
    return out, np.isfinite(c) & np.isfinite(sg)


def wick_masks(d, tf, grid):
    o, c, h, l, v = d.o.values, d.c.values, d.h.values, d.l.values, d.v.values
    sg, lr = sig_prev(c); medv = roll_med_prev(v, 288)
    rng = h - l; cl = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), 0.5)
    wick = (np.minimum(o, c) - l) / c
    r3 = np.log(pd.Series(c) / pd.Series(c).shift(3)).values
    v3 = pd.Series(v).rolling(3).sum().values
    age = np.arange(len(c)) >= 30 * 288
    out = {}
    for (kind, K, V, H) in grid:
        key = (kind, K, V)
        if key in out:
            continue
        if kind == "WICK":
            m = (wick >= K * sg) & (v >= V * medv) & (cl >= 0.6)
        else:
            m = (r3 <= -K * sg * np.sqrt(3)) & (v3 >= V * 3 * medv) & (cl >= 0.4)
        out[key] = np.nan_to_num(m, nan=0).astype(bool) & age
    return out, np.isfinite(c) & np.isfinite(sg)


CFG = {
    "E41": dict(tf="15m", coins=coins5, grid=[(Z, V, H) for Z in (3, 4) for V in (3, 5) for H in (12, 48)],
                masks=climax_masks, key=lambda g: g[:2], H=lambda g: g[2], name=lambda g: f"Z{g[0]} V{g[1]} H{g[2]}"),
    "E42": dict(tf="4h", coins=coins4h, grid=[(Z, V, H) for Z in (3, 4) for V in (3, 5) for H in (3, 12)],
                masks=climax_masks, key=lambda g: g[:2], H=lambda g: g[2], name=lambda g: f"Z{g[0]} V{g[1]} H{g[2]}"),
    "E46": dict(tf="5m", coins=coins5, grid=[(k, K, V, H) for k in ("WICK", "CASCADE") for K in (4, 6) for V in (5, 10)
                                             for H in (12, 48)],
                masks=wick_masks, key=lambda g: g[:3], H=lambda g: g[3], name=lambda g: f"{g[0]} K{g[1]} V{g[2]} H{g[3]}"),
}


def main(plan, R):
    cfg = CFG[plan]; tf = cfg["tf"]; G = cfg["grid"]; names = [cfg["name"](g) for g in G]
    syms = cfg["coins"]()
    a, _ = bt.PERIODS["discovery"]
    w0 = int((pd.Timestamp(a).value + 3 * 86400 * 10**9) // (7 * 86400 * 10**9)); w1 = w0 + 215
    agg_luck = WeekAgg((R, len(G)), w0, w1)
    rng = np.random.default_rng(int(plan[1:]))
    real = {i: [] for i in range(len(G))}
    t0 = time.time()
    for si, s in enumerate(syms):
        try:
            d = load_tf(s, tf)
        except Exception as e:
            print("skip", s, e); continue
        if len(d) < 400:
            continue
        o, c, h, l = d.o.values, d.c.values, d.h.values, d.l.values
        q24 = qv24(d, tf)
        masks, valid = cfg["masks"](d, tf, G)
        lo, hi = disc_range(d.index)
        for i, g in enumerate(G):
            rows = sim_taker(o, c, l, h, masks[cfg["key"](g)], cfg["H"](g), 1, 0, len(c))
            tr = to_trades(rows, d, tf, s, q24, "taker")
            if tr is not None:
                real[i].append(tr)
        if hi > lo + 100:
            for rep in range(R):
                rm = {k: random_mask(m, valid, lo, hi, rng) for k, m in masks.items()}
                for i, g in enumerate(G):
                    rows = sim_taker(o, c, l, h, rm[cfg["key"](g)], cfg["H"](g), 1, lo, hi)
                    agg_luck.add((rep, i), to_trades(rows, d, tf, s, q24, "taker"))
        if si % 50 == 0:
            print(f"{si}/{len(syms)} {s} {time.time()-t0:.0f}s", flush=True)
    real = {i: (pd.concat(v, ignore_index=True) if v else pd.DataFrame()) for i, v in real.items()}
    pickle.dump(dict(names=names, V=G, real=real, luck=agg_luck.stats()), open(f"{SCR}/{plan}_stage1.pkl", "wb"))
    print("done", time.time() - t0)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 100)
