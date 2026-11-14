"""Silver (XAG) research toolkit for E120-E139 (plan edges/plans/E120_common_xag.md)."""
import json
import os

import numpy as np
import pandas as pd

from edges.lib import bt

MET = "/home/user/data/metals"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DPER = {"discovery": ("2000-01-01", "2016-01-01"), "validation": ("2016-01-01", "2021-01-01"),
        "final": ("2021-01-01", "2100-01-01")}
HPER = {"discovery": ("2024-06-01", "2025-07-01"), "validation": ("2025-07-01", "2026-01-01"),
        "final": ("2026-01-01", "2100-01-01")}
SPREAD = {"SI": 0.0004, "GC": 0.0002}
FIN_NIGHT = 0.065 / 360
PERP_MAKER, PERP_TAKER = 0.0002, 0.0005 + 0.0002


# ------------------------------------------------------------------ data
def hourly(sym="SI"):
    d = pd.read_parquet(f"{MET}/{sym}_1h.parquet").sort_index()
    d = d[~d.index.duplicated(keep="last")]
    tr = pd.concat([d.h - d.l, (d.h - d.c.shift()).abs(), (d.l - d.c.shift()).abs()], axis=1).max(axis=1)
    d["atr"] = tr.rolling(14).mean()
    d["flat"] = (d.o == d.h) & (d.h == d.l) & (d.l == d.c)
    return d


def daily(sym="SI"):
    d = pd.read_parquet(f"{MET}/{sym}_1d.parquet").sort_index()
    c = d.c.copy()
    c.index = c.index.normalize()
    return c[~c.index.duplicated(keep="last")]


# ------------------------------------------------------------------ hourly trade engine
def nights(t0, t1):
    """Financing nights: crossings of 21:00 UTC in (t0, t1]; a Friday crossing counts 3."""
    n = 0
    d = t0.normalize()
    while d <= t1:
        x = d + pd.Timedelta(hours=21)
        if t0 < x <= t1:
            n += 3 if x.weekday() == 4 else 1
        d += pd.Timedelta(days=1)
    return n


class H:
    """Arrays of an hourly frame for fast simulation."""

    def __init__(self, d):
        self.d = d
        self.o, self.h, self.l, self.c = (d[k].values.astype(float) for k in "ohlc")
        self.atr = d.atr.values
        self.t = d.index
        self.n = len(d)


def sim(A, e, side, stop_d, tgt_d, hold, venue="cfd", entry_px=None, entry_maker=False, stress=1.0):
    """One trade. e = entry bar index (fills at its open unless entry_px given = limit fill inside bar e).
    stop_d/tgt_d: absolute price distances (None = none). hold: bars incl. the entry bar; exit at close of e+hold-1.
    Returns dict or None."""
    if e >= A.n:
        return None
    px = A.o[e] if entry_px is None else entry_px
    if not np.isfinite(px):
        return None
    stop = None if stop_d is None else px - side * stop_d
    tgt = None if tgt_d is None else px + side * tgt_d
    last = min(e + hold - 1, A.n - 1)
    exit_px, xi, why = None, last, "time"
    mae = 0.0
    for j in range(e, last + 1):
        o, h, l = A.o[j], A.h[j], A.l[j]
        adverse = (l / px - 1) if side > 0 else (1 - h / px)
        if j > e or entry_px is None:
            if stop is not None and j > e and ((side > 0 and o <= stop) or (side < 0 and o >= stop)):
                exit_px, xi, why = o, j, "stop_gap"
                mae = min(mae, (o / px - 1) * side)
                break
            if tgt is not None and j > e and ((side > 0 and o >= tgt) or (side < 0 and o <= tgt)):
                exit_px, xi, why = o, j, "tgt_gap"
                break
        mae = min(mae, adverse)
        if stop is not None and ((side > 0 and l <= stop) or (side < 0 and h >= stop)):
            exit_px, xi, why = stop, j, "stop"
            break
        if tgt is not None and ((side > 0 and h >= tgt) or (side < 0 and l <= tgt)):
            exit_px, xi, why = tgt, j, "tgt"
            break
    if exit_px is None:
        exit_px = A.c[last]
    gross = side * (exit_px / px - 1)
    t0, t1 = A.t[e], A.t[xi] + pd.Timedelta(hours=1)
    if venue == "cfd":
        cost = 2 * SPREAD["SI"] * stress + nights(t0, t1) * FIN_NIGHT * stress
    else:  # perp
        cost = ((PERP_MAKER if entry_maker else PERP_TAKER) + PERP_TAKER) * stress
    return dict(time=t0, exit_time=t1, side=side, gross=gross, net=gross - cost, mae=mae, why=why, e=e, x=xi,
                sym="XAG", stop_frac=(stop_d / px) if stop_d else np.nan)


def run_signals(A, sigs, entry_lag, stop_atr=2.0, tgt_atr=6.0, hold=4, venue="cfd", stress=1.0, stop_abs=None):
    """sigs: list of (signal_idx, side[, stop_dist]); no overlap. Returns DataFrame of trades."""
    out, busy = [], -1
    for s in sigs:
        i, side = s[0], s[1]
        e = i + entry_lag
        if e <= busy or e >= A.n:
            continue
        a = A.atr[i]
        if not np.isfinite(a) or a <= 0:
            continue
        sd = s[2] if len(s) > 2 and s[2] is not None else (stop_atr * a if stop_atr else None)
        td = tgt_atr * a if tgt_atr else None
        r = sim(A, e, side, sd, td, hold, venue=venue, stress=stress)
        if r is None:
            continue
        out.append(r)
        busy = r["x"]
    return pd.DataFrame(out)


def hsplit(tr):
    if len(tr) == 0:
        return {p: tr for p in HPER}
    return {p: tr[(tr.time >= a) & (tr.time < b)] for p, (a, b) in HPER.items()}


def halfyears_pos(tr):
    if len(tr) == 0:
        return 0, 0
    g = tr.groupby([tr.time.dt.year, (tr.time.dt.month > 6)]).net.mean()
    return int((g > 0).sum()), int(len(g))


def hsum(tr, label=""):
    s = bt.summarize(tr, label) if len(tr) else dict(label=label, n=0)
    if len(tr):
        s["halves_pos"], s["halves"] = halfyears_pos(tr)
        # handoff-style account: 10,000, risk 25 per trade at the stop, notional <= 1x
        notional = np.minimum(1.0, 0.0025 / tr.stop_frac.fillna(0.01))
        s["handoff_account_pct"] = round(float((tr.net * notional).sum() * 100), 3)
    return s


def random_control(A, tr, stop_atr, tgt_atr, hold, n=200, seed=1, venue="cfd", by_hour=True, maker=False):
    """Same count, same entry hour-of-day, same sides, same exits; random entry bars in the same period."""
    if len(tr) == 0:
        return np.array([])
    rng = np.random.default_rng(seed)
    hrs = A.t.hour.values
    lo, hi = tr.e.min(), tr.e.max()
    pool = {}
    for hh in range(24):
        idx = np.where((hrs == hh) & (np.arange(A.n) >= lo) & (np.arange(A.n) <= hi) & np.isfinite(A.atr))[0]
        pool[hh] = idx
    means = []
    ent_h = A.t[tr.e.values].hour.values
    sides = tr.side.values
    for _ in range(n):
        rs = []
        for hh, sd in zip(ent_h, sides):
            p = pool[hh] if by_hour and len(pool[hh]) else np.arange(lo, hi + 1)
            e = int(rng.choice(p))
            a = A.atr[e - 1] if e > 0 else np.nan
            if not np.isfinite(a):
                continue
            r = sim(A, e, sd, stop_atr * a if stop_atr else None, tgt_atr * a if tgt_atr else None, hold, venue=venue,
                    entry_maker=maker)
            if r:
                rs.append(r["net"])
        means.append(np.mean(rs) if rs else np.nan)
    return np.array(means)


# ------------------------------------------------------------------ daily books
def nw_t(x, lag=10):
    x = np.asarray(pd.Series(x).dropna(), float)
    n = len(x)
    if n < 20:
        return np.nan
    u = x - x.mean()
    v = u @ u / n
    for k in range(1, lag + 1):
        w = 1 - k / (lag + 1)
        v += 2 * w * (u[k:] @ u[:-k]) / n
    return float(x.mean() / np.sqrt(v / n)) if v > 0 else np.nan


def book(weights, rets, days_gap, spread, fin=True, stress=1.0):
    """weights: DataFrame/Series of positions decided at close t (per leg); rets: next-day simple returns per leg
    (aligned at t); days_gap: calendar days to the next close. Returns daily net P&L Series (at t)."""
    W = weights if isinstance(weights, pd.DataFrame) else weights.to_frame("x")
    R = rets if isinstance(rets, pd.DataFrame) else rets.to_frame("x")
    sp = spread if isinstance(spread, dict) else {k: spread for k in W.columns}
    pnl = pd.Series(0.0, index=W.index)
    for k in W.columns:
        w = W[k].fillna(0.0)
        turn = w.diff().abs().fillna(w.abs())
        pnl += w * R[k] - stress * sp[k] * turn
        if fin:
            pnl -= stress * FIN_NIGHT * days_gap * w.abs()
    return pnl.dropna()


def dsplit(x):
    return {p: x[(x.index >= a) & (x.index < b)] for p, (a, b) in DPER.items()}


def runs(pos):
    """Trades = runs of constant nonzero sign. Returns list of (start_idx, end_idx_inclusive, sign)."""
    s = np.sign(pos.fillna(0).values)
    out, i = [], 0
    while i < len(s):
        if s[i] != 0:
            j = i
            while j + 1 < len(s) and s[j + 1] == s[i]:
                j += 1
            out.append((i, j, int(s[i])))
            i = j + 1
        else:
            i += 1
    return out


def dstats(p, ann=252, trades=None):
    p = p.dropna()
    if len(p) < 5:
        return dict(days=len(p))
    eq = (1 + p).cumprod()
    yr = p.groupby(p.index.year).sum()
    out = dict(days=int(len(p)), mean_bp=round(p.mean() * 1e4, 3), t_nw=round(nw_t(p), 2),
               sharpe=round(float(p.mean() / p.std() * np.sqrt(ann)), 2) if p.std() > 0 else None,
               cagr=round(float(eq.iloc[-1] ** (ann / len(p)) - 1), 4), max_dd=round(float((eq / eq.cummax() - 1).min()), 3),
               years_pos=int((yr > 0).sum()), years=int(len(yr)))
    if trades is not None:
        out["trades"] = int(trades)
    return out


def save(name, obj):
    json.dump(obj, open(os.path.join(ROOT, "results", f"{name}_result.json"), "w"), indent=1, default=str)
