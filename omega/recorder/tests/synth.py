import numpy as np, pandas as pd

def market(seed, n=2400, start_h=None, gaps=True, crash_every=97):
    """Synthetic hourly coin starting at 00:00 UTC, with fat-tailed moves, injected panics and optional missing candles."""
    rng = np.random.default_rng(seed)
    start_h = start_h if start_h is not None else 473_352 + 0  # 2024-01-01 00:00 UTC in epoch hours
    r = rng.standard_t(3, n) * 0.008
    for k in range(200, n, crash_every + seed % 13): r[k:k + 6] -= rng.uniform(0.01, 0.03)   # panics
    c = 10 * (1 + seed) * np.exp(np.cumsum(r)); o = np.r_[c[0], c[:-1]]
    hi = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.006, n))); lo = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.012, n)))
    v = rng.lognormal(10, 1, n); idx = np.arange(start_h, start_h + n)
    df = pd.DataFrame(dict(o=o, hi=hi, lo=lo, c=c, v=v), index=idx)
    if gaps:
        for g in rng.choice(np.arange(800, n - 50), 3, replace=False): df.loc[idx[g]:idx[g] + rng.integers(1, 4)] = np.nan
    return df
