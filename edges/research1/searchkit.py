"""Generic per-coin search with luck check (weekly-aggregated so memory stays small)."""
import time
import numpy as np, pandas as pd
from lib1 import bt, to_trades, period_mask

WEEK = 7 * 86400 * 10**9
MON = 3 * 86400 * 10**9  # shift so weeks start Monday (epoch was a Thursday)


def week_id(times):
    return ((pd.DatetimeIndex(times).as_unit("ns").asi8 + MON) // WEEK).astype(np.int64)


class WeekAgg:
    """Accumulates per-variant weekly sums so that the week-clustered t can be computed without storing trades."""

    def __init__(self, shape, w0, w1):
        self.w0 = w0; self.nw = w1 - w0 + 1
        self.S = np.zeros(shape + (self.nw,)); self.N = np.zeros(shape + (self.nw,))

    def add(self, key, tr, period="discovery"):
        if tr is None or len(tr) == 0:
            return
        tr = tr[period_mask(tr.time, period)]
        if len(tr) == 0:
            return
        w = week_id(pd.DatetimeIndex(tr.time)) - self.w0
        ok = (w >= 0) & (w < self.nw)
        np.add.at(self.S[key], w[ok], tr.net.values[ok]); np.add.at(self.N[key], w[ok], 1)

    def stats(self):
        n = self.N.sum(-1); s = self.S.sum(-1)
        with np.errstate(invalid="ignore", divide="ignore"):
            mu = s / n
            var = ((self.S - self.N * mu[..., None]) ** 2).sum(-1) / n ** 2
            t = mu / np.sqrt(var)
        return n, mu, t


def best_t(n, mu, t, nmin=100):
    ok = (n >= nmin) & (mu > 0) & np.isfinite(t)
    return np.where(ok, t, -np.inf).max(axis=-1)


def random_mask(mask, valid, lo, hi, rng):
    """Same number of True (within [lo,hi)) placed at random valid bars in [lo,hi)."""
    k = int(mask[lo:hi].sum())
    cand = np.where(valid[lo:hi])[0] + lo
    out = np.zeros(len(mask), dtype=np.bool_)
    if k and len(cand):
        out[rng.choice(cand, size=min(k, len(cand)), replace=False)] = True
    return out


def disc_range(idx, period="discovery"):
    a, b = bt.PERIODS[period]
    lo = int(np.searchsorted(idx, pd.Timestamp(a, tz="UTC"))); hi = int(np.searchsorted(idx, pd.Timestamp(b, tz="UTC")))
    return lo, hi
