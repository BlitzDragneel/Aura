"""Shared helpers for the gold (XAU) research bot, plans E100-E112 (edges/plans/E100_common_xau.md)."""
import json, os
import numpy as np
import pandas as pd
from edges.lib import bt

D = "/home/user/data/metals"
HERE = os.path.dirname(os.path.abspath(__file__))
MD5 = json.load(open(os.path.join(HERE, "plan_md5.json")))
SPREAD, FIN = 0.0002, 0.065 / 360          # CFD per side, financing per night (E100)
NY, LDN, TK, CT = "America/New_York", "Europe/London", "Asia/Tokyo", "America/Chicago"

PER_PAXG = {"discovery": ("2020-08-01", "2024-01-01"), "validation": ("2024-01-01", "2025-01-01"),
            "final": ("2025-01-01", "2026-11-01")}
PER_GC1H = {"discovery": ("2024-06-01", "2025-07-01"), "validation": ("2025-07-01", "2026-01-01"),
            "final": ("2026-01-01", "2026-12-01")}
PER_D = {"discovery": ("2000-08-01", "2016-01-01"), "validation": ("2016-01-01", "2021-01-01"),
         "final": ("2021-01-01", "2026-12-01")}


def bars(name):
    df = pd.read_parquet(f"{D}/{name}.parquet").sort_index()
    df.index = pd.DatetimeIndex(df.index).tz_convert("UTC") if df.index.tz else pd.DatetimeIndex(df.index).tz_localize("UTC")
    df = df[~df.index.duplicated()]
    if name.startswith("GC_1h"):
        df = df[df.index.minute == 0]
    return df


def daily_close(name="GC_1d"):
    d = pd.read_parquet(f"{D}/{name}.parquet").c.dropna()
    d.index = d.index.tz_convert(NY).normalize().tz_localize(None) if d.index.tz else d.index.normalize()
    return d[~d.index.duplicated(keep="last")]


def cut(x, per, col=None):
    a, b = per
    if len(x) == 0:
        return x
    idx = x[col] if col else x.index
    m = (idx >= pd.Timestamp(a, tz="UTC")) & (idx < pd.Timestamp(b, tz="UTC")) if getattr(idx, "tz", None) is not None or (col and x[col].dt.tz is not None) else (idx >= pd.Timestamp(a)) & (idx < pd.Timestamp(b))
    return x[m]


def nights(t0, t1):
    """Number of 17:00 New York rollovers strictly inside (t0, t1]."""
    a, b = t0.tz_convert(NY), t1.tz_convert(NY)
    n = (b.normalize() - a.normalize()).days
    n += (b.hour >= 17) - (a.hour >= 17)
    return max(0, int(n))


def net_of(gross, nts, mult=1.0, spread=SPREAD):
    return gross - mult * (2 * spread + nts * FIN)


def summ(tr, label=""):
    s = bt.summarize(tr, label) if len(tr) else dict(label=label, n=0)
    return s


def halves_pos(tr):
    if len(tr) < 4:
        return None
    t = tr.sort_values("time"); h = len(t) // 2
    return [round(t.net.iloc[:h].mean() * 1e4, 1), round(t.net.iloc[h:].mean() * 1e4, 1)]


def nw_t(x, lags=10):
    x = pd.Series(x).dropna().values
    n = len(x)
    if n < 20:
        return np.nan
    e = x - x.mean()
    v = e @ e / n
    for L in range(1, lags + 1):
        v += 2 * (1 - L / (lags + 1)) * (e[L:] @ e[:-L]) / n
    return float(x.mean() / np.sqrt(v / n)) if v > 0 else np.nan


def log(plan, name, period, stats):
    if os.environ.get("XAU_NOLOG"):          # re-runs of an identical, already-logged computation
        return
    st = {k: v for k, v in stats.items() if k not in ("years",)}
    bt.log_attempt(MD5[plan], name, period, st)


# ------------------------------------------------------------- hourly cell engine (24/7 PAXG)
class Cells:
    """Hourly log returns of a 24/7 series laid out as cells (UTC day, hour). A window trade = a set of consecutive cells.
    Window return = exp(sum of log returns of its bars) - 1 (open of first bar ~ close of the previous bar for PAXG)."""

    def __init__(self, df, freq="1h"):
        self.freq = pd.Timedelta(freq); self.k = int(pd.Timedelta("1D") / self.freq)
        c = df.c.resample(freq).last()
        self.idx = pd.date_range(c.index[0].normalize(), c.index[-1].normalize() + pd.Timedelta("1D") - self.freq, freq=freq, tz="UTC")
        c = c.reindex(self.idx).ffill(limit=2)       # CME break / short outages: flat cell, gap lands in the next bar
        r = np.log(c).diff()
        self.valid = r.notna().values
        self.r = r.fillna(0.0).values
        self.lo = np.log(df.l.reindex(self.idx) / c.shift(1)).values      # low vs previous close
        self.hi = np.log(df.h.reindex(self.idx) / c.shift(1)).values
        self.t0 = self.idx[0]
        self.ndays = len(self.idx) // self.k

    def pos(self, ts):
        return int((ts - self.t0) / self.freq)

    def windows(self, tz, start, end, weekdays=(0, 1, 2, 3, 4), next_day=False, dates=None):
        """start/end 'HH:MM' local; returns (entry_ts list, matrix of cell positions padded with -1)."""
        if dates is None:
            dates = pd.date_range(self.idx[0].tz_convert(tz).date(), self.idx[-1].tz_convert(tz).date(), freq="D")
        ents, rows = [], []
        for d in dates:
            if d.weekday() not in weekdays:
                continue
            a = pd.Timestamp(f"{d.date()} {start}", tz=tz)
            b = pd.Timestamp(f"{(d + pd.Timedelta(days=1 if next_day else 0)).date()} {end}", tz=tz)
            a, b = a.tz_convert("UTC"), b.tz_convert("UTC")
            pa, pb = self.pos(a), self.pos(b)
            if pa < 1 or pb > len(self.r) or pb <= pa:
                continue
            ents.append(a); rows.append(list(range(pa, pb)))
        m = max(len(x) for x in rows)
        M = np.full((len(rows), m), -1, dtype=np.int64)
        for i, x in enumerate(rows):
            M[i, :len(x)] = x
        return pd.DatetimeIndex(ents), M

    def wret(self, M, rot=None):
        """Log return of each window; rot = per-day offsets (null) mapping cell (d,h) -> (d,(h+off)%24)."""
        P = M.copy()
        if rot is not None:
            ok = P >= 0
            d, h = P // self.k, P % self.k
            P = np.where(ok, d * self.k + (h + rot[np.clip(d, 0, len(rot) - 1)]) % self.k, -1)
        v = np.where(P >= 0, self.r[np.clip(P, 0, None)], 0.0)
        good = np.where(P >= 0, self.valid[np.clip(P, 0, None)], True).all(1)
        return v.sum(1), good

    def wmae(self, M, side):
        """Worst adverse excursion (fraction) during the window for side +1/-1."""
        cum = np.cumsum(np.where(M >= 0, self.r[np.clip(M, 0, None)], 0.0), axis=1)
        prev = np.concatenate([np.zeros((len(M), 1)), cum[:, :-1]], axis=1)
        lo = np.where(M >= 0, prev + np.nan_to_num(self.lo[np.clip(M, 0, None)]), 0.0)
        hi = np.where(M >= 0, prev + np.nan_to_num(self.hi[np.clip(M, 0, None)]), 0.0)
        return np.where(side > 0, np.exp(lo.min(1)) - 1, np.exp(-hi.max(1)) - 1)


def trades_from(ents, lr, side, good, nts, mae=None, mult=1.0, spread=SPREAD, hours=None):
    side = np.broadcast_to(np.asarray(side, dtype=float), lr.shape)
    gross = np.where(side > 0, np.exp(lr) - 1, np.where(side < 0, np.exp(-lr) - 1, np.nan))
    df = pd.DataFrame(dict(time=ents, gross=gross, side=side, nts=nts))
    df["net"] = net_of(df.gross, df.nts, mult, spread)
    if mae is not None:
        df["mae"] = mae
    if hours is not None:
        df["exit_time"] = df.time + pd.to_timedelta(hours, unit="h")
    df = df[good & (side != 0) & np.isfinite(df.gross.values)]
    df["sym"] = "XAU"
    return df.reset_index(drop=True)


def eligible(s, min_years_frac=0.6):
    return s.get("n", 0) >= 20 and (s.get("t_week") or -9) >= 2 and s["mean_bp"] > 0 and \
        s["years_pos"] >= np.ceil(min_years_frac * s["years_total"])


def dump(plan, res):
    os.makedirs("/home/user/Aura/edges/results", exist_ok=True)
    json.dump(res, open(f"/home/user/Aura/edges/results/{plan}_result.json", "w"), indent=1, default=str)
