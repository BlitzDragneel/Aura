"""E91 post-shock drift, daily (plans/E91_btc_post_shock.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from libbtc import *  # noqa
MD5 = "59a46b87fccb73d5a0947215e0379045"


def daily_trades(d, sig_days, side, H):
    """entry at open of day i+1, exit close of day i+H; no overlap."""
    o, c = d.o.values, d.c.values
    rows = []; busy = -1
    for i, s in zip(sig_days, side):
        e = i + 1; x = i + H
        if e <= busy or x >= len(d) or not (o[e] > 0 and c[x] > 0):
            continue
        lo = d.l.values[e:x + 1].min(); hi = d.h.values[e:x + 1].max()
        mae = (lo / o[e] - 1) if s > 0 else -(hi / o[e] - 1)
        rows.append((d.index[e], d.index[x] + pd.Timedelta("1D"), s, o[e], c[x], mae))
        busy = x
    tr = pd.DataFrame(rows, columns=["time", "exit_time", "side", "entry", "exit", "mae"])
    if len(tr) == 0:
        return tr.assign(net=[], sym=[])
    tr["sym"] = SYM
    tr["gross"] = tr.side * (tr.exit / tr.entry - 1)
    tr["fund"] = funding_between(tr.time, tr.exit_time, tr.side)
    tr["net"] = tr.gross - 2 * TAKER_SIDE - tr.fund
    return tr


def grid(d, z, rnd=None, rng=None):
    out = {}
    for sgn in (1, -1):
        for k in (2, 3):
            m = (z >= k) if sgn > 0 else (z <= -k)
            days = np.where(m)[0]
            if rnd is not None:
                days = np.sort(rng.choice(rnd, len(days), replace=False))
            for mode in (1, -1):
                for H in (1, 3, 5, 10):
                    side = np.full(len(days), sgn * mode)
                    out[f"{'UP' if sgn>0 else 'DN'} k{k} {'FOLLOW' if mode>0 else 'FADE'} H{H}"] = daily_trades(d, days, side, H)
    return out


def main():
    d = bars("1d")
    lr = np.log(d.c / d.c.shift(1))
    z = (lr / lr.rolling(20, min_periods=15).std().shift(1)).values
    real = grid(d, z)
    rng = np.random.default_rng(91)
    disc_days = np.where((d.index < "2024-01-01") & np.isfinite(z))[0]
    zd = np.where(d.index < "2024-01-01", z, np.nan)
    nulls = []
    for r in range(200):
        g = grid(d, zd, rnd=disc_days, rng=rng)
        ts = [fast_t(per(t, P1)["discovery"]) for t in g.values() if len(per(t, P1)["discovery"]) >= 30]
        nulls.append(max(ts) if ts else np.nan)
    out = judge(MD5, "E91", real, nulls, P1, nmin=30, years_need=3, final_info=True)
    json.dump(out, open(f"{ROOT}/edges/results/E91_result.json", "w"), indent=1, default=str)
    top = sorted(out["discovery"].items(), key=lambda kv: -(kv[1].get("t_week") or -9))[:6]
    for k, v in top: print(k, v["mean_bp"], v["t_week"], v["n"], v["years"])
    print({k: v for k, v in out.items() if k != "discovery"})


if __name__ == "__main__":
    main()
