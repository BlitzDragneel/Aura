"""Research bot 1 engine (E37-E46). Uses edges/lib/bt.py for data, costs, stats, leverage, bookkeeping."""
import os, sys, json
import numpy as np, pandas as pd
from numba import njit

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from edges.lib import bt  # noqa

DATA = bt.DATA
TFMIN = {"5m": 5, "15m": 15, "1h": 60, "4h": 240}
SCR = "/tmp/claude-0/-home-user-Aura/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/research1"
os.makedirs(SCR, exist_ok=True)


def coins5():
    return sorted(f[:-8] for f in os.listdir(f"{DATA}/5m") if f.endswith(".parquet"))


def coins4h():
    ex = set(json.load(open(os.path.join(ROOT, "edges/research1/tradfi_exclusions.json"))))
    return sorted(f[:-8] for f in os.listdir(f"{DATA}/1h") if f.endswith(".parquet") and f[:-8] not in ex)


def load_tf(sym, tf):
    """Regular grid OHLCV(qv) at tf. 15m from 5m, 4h from 1h; a resampled bar is valid only if all sub-bars exist."""
    src = {"5m": "5m", "15m": "5m", "1h": "1h", "4h": "1h"}[tf]
    d = bt.load(sym, src)[["o", "h", "l", "c", "v", "qv"]]
    d = d[~d.index.duplicated()]
    d.index = d.index.as_unit("ns")
    step = pd.Timedelta(minutes=TFMIN[src])
    full = pd.date_range(d.index[0], d.index[-1], freq=step, tz="UTC")
    d = d.reindex(full)
    if tf != src:
        k = TFMIN[tf] // TFMIN[src]
        g = d.resample(f"{TFMIN[tf]}min", label="left", closed="left", origin="epoch")
        cnt = g.c.count()
        out = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "v": g.v.sum(),
                            "qv": g.qv.sum()})
        bad = cnt < k
        out.loc[bad, ["o", "h", "l", "c"]] = np.nan
        out.loc[bad, ["v", "qv"]] = np.nan
        d = out
    return d


def qv24(d, tf):
    n = 24 * 60 // TFMIN[tf]
    return d.qv.rolling(n, min_periods=n // 2).sum().shift(1).values  # 24h before the signal bar (excl.)


def sigma(c, n=168, minp=120):
    lr = np.log(pd.Series(c) / pd.Series(c).shift(1))
    return lr.rolling(n, min_periods=minp).std().shift(1).values


def day_thresholds(x, lookback, step, q=10):
    n = len(x); lo = np.full(n, np.nan)
    for s in range(lookback, n, step):
        w = x[s - lookback:s]; w = w[np.isfinite(w)]
        if len(w) >= lookback // 2:
            lo[s:s + step] = np.percentile(w, q)
    return lo


# ------------------------------------------------------------------ funding
_FUND = {}


def fund_cum(sym):
    if sym not in _FUND:
        try:
            f = bt.funding(sym)
            ts = pd.DatetimeIndex(f.index).as_unit("ms").asi8
            ts = (np.round(ts / 60000.0) * 60000).astype(np.int64)  # settlement ms, rounded to the minute
            _FUND[sym] = (ts, np.concatenate([[0.0], np.cumsum(f.values)]))
        except FileNotFoundError:
            _FUND[sym] = None
    return _FUND[sym]


def funding_paid(sym, t0_ms, t1_ms):
    """Sum of funding rates with settlement in (t0, t1] (vectorised). Long pays +sum."""
    fc = fund_cum(sym)
    if fc is None:
        return np.zeros(len(t0_ms))
    ts, cs = fc
    a = np.searchsorted(ts, t0_ms, side="right"); b = np.searchsorted(ts, t1_ms, side="right")
    return cs[b] - cs[a]


# ------------------------------------------------------------------ simulators (numba)
@njit(cache=True)
def _next_valid(c, j, lim):
    n = len(c)
    for q in range(j, min(n, j + lim)):
        if c[q] == c[q]:
            return q
    return -1


@njit(cache=True)
def sim_limit(c, l, sig, mask, k, W, H, lo, hi):
    """Limit buy at c[t]*exp(-k*sig[t]) for W bars; fill if l[j] < lim; exit close H bars after fill.
    Returns rows (t, fill, exit, entry_px, exit_px, mae)."""
    n = len(c); out = np.empty((n // 2 + 1, 6)); m = 0; nxt = -1
    for t in range(lo, hi):
        if not mask[t] or t < nxt:
            continue
        if not (sig[t] > 0 and c[t] > 0):
            continue
        lim = c[t] * np.exp(-k * sig[t]); f = -1
        for j in range(t + 1, min(n, t + 1 + W)):
            if l[j] < lim:
                f = j; break
        if f < 0:
            nxt = t + W; continue
        x = _next_valid(c, f + H, 288)
        if x < 0:
            nxt = t + W; continue
        mn = lim
        for j in range(f, x + 1):
            if l[j] == l[j] and l[j] < mn:
                mn = l[j]
        out[m, 0] = t; out[m, 1] = f; out[m, 2] = x; out[m, 3] = lim; out[m, 4] = c[x]; out[m, 5] = mn / lim - 1
        m += 1; nxt = x
    return out[:m]


@njit(cache=True)
def sim_taker(o, c, l, h, mask, H, side, lo, hi):
    """Enter at o[t+1] (side +1 long / -1 short), exit at c[t+H] (next valid). rows (t, fill, exit, entry, exit, mae)."""
    n = len(c); out = np.empty((n // 2 + 1, 6)); m = 0; nxt = -1
    for t in range(lo, hi):
        if not mask[t] or t < nxt or t + 1 >= n:
            continue
        e = o[t + 1]
        if not (e > 0):
            continue
        x = _next_valid(c, t + H, 288)
        if x < 0 or x <= t:
            continue
        mn = 0.0
        for j in range(t + 1, x + 1):
            if side > 0:
                if l[j] == l[j] and l[j] / e - 1 < mn:
                    mn = l[j] / e - 1
            else:
                if h[j] == h[j] and 1 - h[j] / e < mn:
                    mn = 1 - h[j] / e
        out[m, 0] = t; out[m, 1] = t + 1; out[m, 2] = x; out[m, 3] = e; out[m, 4] = c[x]; out[m, 5] = mn
        m += 1; nxt = x
    return out[:m]


def to_trades(rows, d, tf, sym, q24, entry, side=1, hold_h=None):
    """rows from sim -> trade DataFrame with costs and funding."""
    if len(rows) == 0:
        return None
    idx = d.index
    ti, fi, xi = rows[:, 0].astype(int), rows[:, 1].astype(int), rows[:, 2].astype(int)
    bar = pd.Timedelta(minutes=TFMIN[tf])
    time = idx[ti] + bar
    fill_t = idx[fi]
    exit_t = idx[xi] + bar
    gross = side * (rows[:, 4] / rows[:, 3] - 1)
    cost = bt.round_trip_cost(np.nan_to_num(q24[ti], nan=0.0), entry=entry, exit="taker")
    held_h = (exit_t - fill_t).total_seconds().values / 3600
    fund = funding_paid(sym, fill_t.as_unit("ms").asi8, exit_t.as_unit("ms").asi8)
    fund = np.where(held_h > 8, fund, 0.0) * side
    net = gross - cost - fund
    return pd.DataFrame(dict(time=time, sym=sym, exit_time=exit_t, gross=gross, cost=cost, fund=fund, net=net,
                             mae=rows[:, 5]))


# ------------------------------------------------------------------ fast stats for searches
def fast_t(times_ns, net):
    """Week-clustered t (same formula as bt.tstat_weekly) from int64 ns times."""
    if len(net) < 3:
        return np.nan
    wk = (times_ns // (7 * 86400 * 10**9) )  # epoch weeks (Thu-based) — used only for luck repeats
    mu = net.mean(); r = net - mu
    u, inv = np.unique(wk, return_inverse=True)
    g = np.bincount(inv, weights=r)
    var = (g ** 2).sum() / len(net) ** 2
    return mu / np.sqrt(var) if var > 0 else np.nan


def best_of(results, nmin=100):
    """results: list of (name, n, mean, t). Best t among n>=nmin, mean>0."""
    ok = [r for r in results if r[1] >= nmin and r[2] > 0 and r[3] == r[3]]
    return max(ok, key=lambda r: r[3]) if ok else None


def period_mask(times, period):
    a, b = bt.PERIODS[period]
    a, b = pd.Timestamp(a, tz="UTC"), pd.Timestamp(b, tz="UTC")
    return (times >= a) & (times < b)


def stats_periods(tr, name, md5, log=True, disc_start=None):
    out = {}
    for p in ("discovery", "validation", "final"):
        s = tr[period_mask(tr.time, p)] if tr is not None and len(tr) else tr
        st = bt.summarize(s, name) if s is not None and len(s) else dict(label=name, n=0)
        out[p] = st
    return out


def jdump(obj, path):
    json.dump(obj, open(path, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
