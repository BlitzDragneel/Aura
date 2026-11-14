"""E89 BTC-only panic bounce 5m/15m with maker TP exit and vol gate (plans/E89_btc_panic_maker.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from numba import njit
from libbtc import *  # noqa
MD5 = "118e78938f74f5b2a4033c0b022f01ed"


@njit(cache=True)
def sim(c, h, l, sig, trig, k, W, H, tp_mode):
    n = len(c); out = np.empty((n // 4 + 1, 7)); m = 0; nxt = -1
    for t in range(n):
        if not trig[t] or t < nxt:
            continue
        if not (sig[t] > 0 and c[t] > 0):
            continue
        lim = c[t] * np.exp(-k * sig[t]); f = -1
        for j in range(t + 1, min(n, t + 1 + W)):
            if l[j] < lim:
                f = j; break
        if f < 0:
            nxt = t + W; continue
        x = f + H
        if x >= n:
            break
        mn = lim; px = c[x]; maker = 0.0; ok = True
        for j in range(f, x + 1):
            if not (l[j] == l[j]):
                ok = False; break
            if l[j] < mn:
                mn = l[j]
            if tp_mode and j > f and h[j] > c[t]:
                px = c[t]; x = j; maker = 1.0; break
        if not ok or not (px > 0):
            nxt = x; continue
        out[m, 0] = t; out[m, 1] = f; out[m, 2] = x; out[m, 3] = lim; out[m, 4] = px; out[m, 5] = mn / lim - 1; out[m, 6] = maker
        m += 1; nxt = x
    return out[:m]


def to_tr(rows, d):
    if len(rows) == 0:
        return pd.DataFrame(columns=["time", "exit_time", "net", "sym", "mae"])
    idx = d.index; bar = idx[1] - idx[0]
    tr = pd.DataFrame({"time": idx[rows[:, 1].astype(int)], "exit_time": idx[rows[:, 2].astype(int)] + bar,
                       "entry": rows[:, 3], "exit": rows[:, 4], "mae": rows[:, 5], "maker_exit": rows[:, 6] > 0})
    tr["sym"] = SYM; tr["side"] = 1
    tr["gross"] = tr.exit / tr.entry - 1
    tr["fund"] = funding_between(tr.time, tr.exit_time, tr.side)
    tr["net"] = tr.gross - MAKER_SIDE - np.where(tr.maker_exit, MAKER_SIDE, TAKER_SIDE) - tr.fund
    return tr


def prep(tf):
    d = bars(tf)
    c = d.c.values
    sg = lib1.sigma(c)
    bph = {"5m": 12, "15m": 4}[tf]
    s1h = pd.Series(sg * np.sqrt(bph), index=d.index)
    nday = 24 * bph
    med = s1h.rolling(365 * nday, min_periods=90 * nday).median()
    hivol = (s1h > med).values
    look, step = (8640, 288) if tf == "5m" else (2880, 96)
    trig = {}
    for L in ((24, 288) if tf == "5m" else (24, 96)):
        r = np.log(d.c / d.c.shift(L)).values
        th = lib1.day_thresholds(r, look, step)
        trig[L] = np.nan_to_num(r <= th, nan=0).astype(np.bool_) & np.isfinite(th)
    H = 288 if tf == "5m" else 96
    return d, sg, hivol, trig, H


def grid(D, rnd=None, rng=None):
    out = {}
    for tf, (d, sg, hivol, trig, H) in D.items():
        c, h, l = d.c.values, d.h.values, d.l.values
        for L, tg in trig.items():
            if rnd is not None:
                pool = rnd[tf]
                tg2 = np.zeros(len(tg), dtype=np.bool_)
                cnt = int(tg[pool].sum())
                tg2[rng.choice(pool, cnt, replace=False)] = True
                tg = tg2
            for gate in ("NONE", "HIVOL"):
                tgg = tg & (hivol if gate == "HIVOL" else True)
                for k in (2, 4):
                    for ex in ("TIME", "TP"):
                        rows = sim(c, h, l, sg, tgg, float(k), 3, H, ex == "TP")
                        out[f"{tf} L{L} k{k} {ex} {gate}"] = to_tr(rows, d)
    return out


def main():
    D = {tf: prep(tf) for tf in ("5m", "15m")}
    real = grid(D)
    rng = np.random.default_rng(89)
    rnd = {}
    for tf, (d, *_r) in D.items():
        rnd[tf] = np.where((d.index < "2024-01-01") & np.isfinite(D[tf][1]))[0]
    nulls = []
    for i in range(200):
        g = grid(D, rnd=rnd, rng=rng)
        ts = []
        for t in g.values():
            dd = per(t, P5)["discovery"]
            if len(dd) >= 100 and dd.net.mean() > 0:
                ts.append(fast_t(dd))
        nulls.append(max(ts) if ts else 0.0)
        if i % 20 == 0:
            print(i, np.percentile(nulls, 95), flush=True)
    out = judge(MD5, "E89", real, nulls, P5, nmin=100, years_need=2, final_info=True)
    json.dump(out, open(f"{ROOT}/edges/results/E89_result.json", "w"), indent=1, default=str)
    for nm, tr in real.items():
        tr.to_parquet(f"{SCR}/E89_{nm.replace(' ', '_')}.parquet")
    for k, v in sorted(out["discovery"].items(), key=lambda kv: -(kv[1].get("t_week") or -9))[:10]:
        print(f"{k:24s}", v.get("mean_bp"), v.get("t_week"), v.get("n"), v.get("years"))
    print({k: v for k, v in out.items() if k != "discovery"})


if __name__ == "__main__":
    main()
