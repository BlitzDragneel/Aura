"""E40: market-wide panic breadth at 15m (30 coins), taker next open."""
import sys, time, pickle
import numpy as np, pandas as pd
from lib1 import *  # noqa
from searchkit import WeekAgg, random_mask, disc_range

LOOK, STEP = 2880, 96
GRID = [(L, b, q, H) for L in (24, 96) for b in (0.2, 0.4) for q in (5, 10) for H in (24, 96)]


def main(R=100):
    syms = coins5(); D = {}
    for s in syms:
        D[s] = load_tf(s, "15m")
    idx = D["BTCUSDT"].index
    for s in syms:
        idx = idx.union(D[s].index)
    for s in syms:
        D[s] = D[s].reindex(idx)
    th = {}  # (s, L, q) -> bool array
    for L in (24, 96):
        below10 = []; okc = []
        for s in syms:
            r = np.log(D[s].c / D[s].c.shift(L)).values
            t10 = day_thresholds(r, LOOK, STEP, 10); t5 = day_thresholds(r, LOOK, STEP, 5)
            th[(s, L, 10)] = np.nan_to_num(r <= t10, nan=0).astype(bool) & np.isfinite(t10)
            th[(s, L, 5)] = np.nan_to_num(r <= t5, nan=0).astype(bool) & np.isfinite(t5)
            below10.append(th[(s, L, 10)]); okc.append(np.isfinite(t10) & np.isfinite(r))
        cnt = np.sum(below10, axis=0); tot = np.sum(okc, axis=0)
        th[("breadth", L)] = np.where(tot >= 10, cnt / np.maximum(tot, 1), 0)
    names = [f"L{L} b{int(b*100)} q{q} H{H}" for (L, b, q, H) in GRID]
    a, _ = bt.PERIODS["discovery"]
    w0 = int((pd.Timestamp(a).value + 3 * 86400 * 10**9) // (7 * 86400 * 10**9)); w1 = w0 + 215
    agg = WeekAgg((R, len(GRID)), w0, w1); rng = np.random.default_rng(40)
    real = {i: [] for i in range(len(GRID))}
    for s in syms:
        d = D[s]; o, c, h, l = d.o.values, d.c.values, d.h.values, d.l.values; q24 = qv24(d, "15m")
        valid = np.isfinite(c); lo, hi = disc_range(d.index)
        masks = [th[(s, L, q)] & (th[("breadth", L)] >= b) for (L, b, q, H) in GRID]
        for i, (L, b, q, H) in enumerate(GRID):
            tr = to_trades(sim_taker(o, c, l, h, masks[i], H, 1, 0, len(c)), d, "15m", s, q24, "taker")
            if tr is not None:
                real[i].append(tr)
        for rep in range(R):
            for i, (L, b, q, H) in enumerate(GRID):
                rm = random_mask(masks[i], valid, lo, hi, rng)
                agg.add((rep, i), to_trades(sim_taker(o, c, l, h, rm, H, 1, lo, hi), d, "15m", s, q24, "taker"))
        print(s, flush=True)
    real = {i: (pd.concat(v, ignore_index=True) if v else pd.DataFrame()) for i, v in real.items()}
    pickle.dump(dict(names=names, V=GRID, real=real, luck=agg.stats()), open(f"{SCR}/E40_stage1.pkl", "wb"))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 100)
