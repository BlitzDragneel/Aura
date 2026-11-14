"""E98 dip-in-uptrend swing (plans/E98_btc_dip_in_uptrend.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from libbtc import *  # noqa
from e91_post_shock import daily_trades
MD5 = "cbb9fb9144fceadcd25abd233506f5a9"


def grid(d, rnd=None, rng=None):
    c = d.c
    hi30 = c.rolling(30, min_periods=25).max().shift(1)
    sma = c.rolling(200, min_periods=200).mean()
    up = (c > sma).values
    out = {}
    for X in (0.10, 0.15, 0.20):
        dip = (c <= (1 - X) * hi30)
        first = (dip & ~dip.shift(1, fill_value=False)).values
        for filt in ("NONE", "SMA200"):
            if rnd is None:
                m = first & (up if filt == "SMA200" else True)
                days = np.where(m)[0]
            else:
                cnt = int((first & (up if filt == "SMA200" else True))[rnd].sum())
                pool = rnd[up[rnd]] if filt == "SMA200" else rnd
                days = np.sort(rng.choice(pool, min(cnt, len(pool)), replace=False))
            for H in (5, 10, 20):
                out[f"X{int(X*100)} {filt} H{H}"] = daily_trades(d, days, np.ones(len(days), dtype=int), H)
    return out


def main():
    d = bars("1d")
    real = grid(d)
    rng = np.random.default_rng(98)
    pool = np.where((d.index < "2024-01-01") & (d.index >= "2020-02-01"))[0]
    nulls = []
    for _ in range(200):
        g = grid(d, rnd=pool, rng=rng)
        ts = [fast_t(per(t, P1)["discovery"]) for t in g.values() if len(per(t, P1)["discovery"]) >= 30 and per(t, P1)["discovery"].net.mean() > 0]
        nulls.append(max(ts) if ts else 0.0)
    out = judge(MD5, "E98", real, nulls, P1, nmin=30, years_need=3, final_info=True)
    json.dump(out, open(f"{ROOT}/edges/results/E98_result.json", "w"), indent=1, default=str)
    for k, v in sorted(out["discovery"].items(), key=lambda kv: -(kv[1].get("t_week") or -9))[:8]:
        print(f"{k:18s}", v.get("mean_bp"), v.get("t_week"), v.get("n"), v.get("years"))
    print({k: v for k, v in out.items() if k != "discovery"})


if __name__ == "__main__":
    main()
