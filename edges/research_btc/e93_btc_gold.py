"""E93 BTC vs gold relative moves (plans/E93_btc_vs_gold.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from libbtc import *  # noqa
from e91_post_shock import daily_trades
MD5 = "7f41b26fa0cd3e01e44341b31c857ca4"


def paxg_daily():
    x = pd.read_parquet(f"{bt.DATA}/metals/PAXG_1h.parquet")
    g = x.c.resample("1D").last()
    cnt = x.c.resample("1D").count()
    return g.where(cnt >= 20)


def grid(d, z, rnd=None, rng=None):
    out = {}
    for N in (5, 20):
        for k in (1.5, 2):
            zz = z[N]
            lo = np.where(zz <= -k)[0]; hi = np.where(zz >= k)[0]
            idx = np.concatenate([lo, hi]); s0 = np.concatenate([np.ones(len(lo)), -np.ones(len(hi))])
            o = np.argsort(idx); idx, s0 = idx[o], s0[o]
            if rnd is not None:
                idx = np.sort(rng.choice(rnd, len(idx), replace=False)); s0 = rng.permutation(s0)
            for mode in (1, -1):
                for H in (5, 10):
                    out[f"N{N} k{k} {'CATCHUP' if mode>0 else 'MOM'} H{H}"] = daily_trades(d, idx, (mode * s0).astype(int), H)
    return out


def main():
    d = bars("1d")
    pg = paxg_daily().reindex(d.index)
    z = {}
    for N in (5, 20):
        rel = np.log(d.c / d.c.shift(N)) - np.log(pg / pg.shift(N))
        sd = rel.rolling(365, min_periods=180).std().shift(1)
        z[N] = (rel / sd).values
    real = grid(d, z)
    rng = np.random.default_rng(93)
    mask_d = (d.index < "2024-01-01")
    disc_days = np.where(mask_d & np.isfinite(z[20]))[0]
    zd = {N: np.where(mask_d, v, np.nan) for N, v in z.items()}
    nulls = []
    for _ in range(200):
        g = grid(d, zd, rnd=disc_days, rng=rng)
        ts = [fast_t(per(t, P1)["discovery"]) for t in g.values() if len(per(t, P1)["discovery"]) >= 30]
        nulls.append(max(ts) if ts else np.nan)
    out = judge(MD5, "E93", real, nulls, P1, nmin=30, years_need=3, final_info=True)
    out["note"] = "z needs 180 days of history: first usable signal ~2021-03; discovery years 2021-2023 (3) -> years_need 3 means all three"
    json.dump(out, open(f"{ROOT}/edges/results/E93_result.json", "w"), indent=1, default=str)
    for k, v in sorted(out["discovery"].items(), key=lambda kv: -(kv[1].get("t_week") or -9))[:6]:
        print(k, v.get("mean_bp"), v.get("t_week"), v.get("n"), v.get("years"))
    print({k: v for k, v in out.items() if k != "discovery"})


if __name__ == "__main__":
    main()
