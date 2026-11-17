"""Candle description shared by the backtest (E162) and the live candle-memory bot. Row t uses bars <= t only."""
import numpy as np
import pandas as pd

FEATS = [f"{k}{i}" for i in range(4) for k in ("body", "uw", "lw", "rng")] + ["r4", "r16", "r96", "pos96", "d20", "d50", "volp", "sess_s", "sess_c", "wkend"]


def describe(f: pd.DataFrame) -> pd.DataFrame:
    o, h, l, c = f.o, f.h, f.l, f.c
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    X = pd.DataFrame(index=f.index)
    for i in range(4):
        oo, hh, ll, cc, a = o.shift(i), h.shift(i), l.shift(i), c.shift(i), atr
        X[f"body{i}"] = (cc - oo) / a
        X[f"uw{i}"] = (hh - np.maximum(oo, cc)) / a
        X[f"lw{i}"] = (np.minimum(oo, cc) - ll) / a
        X[f"rng{i}"] = (hh - ll) / a
    for k in (4, 16, 96):
        X[f"r{k}"] = (c - c.shift(k)) / atr
    hi, lo = h.rolling(96).max(), l.rolling(96).min()
    X["pos96"] = (c - lo) / (hi - lo)
    X["d20"] = (c - c.rolling(20).mean()) / atr
    X["d50"] = (c - c.rolling(50).mean()) / atr
    X["volp"] = (atr / c).rolling(96 * 20, min_periods=96 * 3).rank(pct=True)
    hr = f.index.hour + f.index.minute / 60
    X["sess_s"], X["sess_c"] = np.sin(2 * np.pi * hr / 24), np.cos(2 * np.pi * hr / 24)
    X["wkend"] = (f.index.weekday >= 5).astype(float)
    return X.replace([np.inf, -np.inf], np.nan)


def outcomes(f: pd.DataFrame) -> pd.DataFrame:
    o, c = f.o, f.c
    tr = pd.concat([f.h - f.l, (f.h - c.shift()).abs(), (f.l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    Y = pd.DataFrame(index=f.index)
    nx = o.shift(-1)
    Y["up1"] = (c.shift(-1) > nx).astype(float)                 # next candle closes above its open
    Y["ret1h"] = c.shift(-4) / nx - 1                            # next hour, from the next open
    Y["up1h"] = (Y.ret1h > 0).astype(float)
    Y["up4h"] = (c.shift(-16) > nx).astype(float)
    hi4, lo4 = f.h[::-1].rolling(16).max()[::-1].shift(-1), f.l[::-1].rolling(16).min()[::-1].shift(-1)
    Y["big4h"] = (((hi4 - lo4) / atr) > 4).astype(float)
    Y.loc[Y.ret1h.isna(), ["up1", "up1h", "up4h", "big4h"]] = np.nan
    return Y


RICH = FEATS + [f"{k}_{w}" for w in ("1h", "4h") for k in ("body", "uw", "lw", "rng")] + ["dpdh", "dpdl", "dopen", "streak", "wd_s", "wd_c"]


def describe_rich(f: pd.DataFrame) -> pd.DataFrame:
    """E163: the E162 numbers + the 1h and 4h candle, yesterday's high/low, today's open, colour streak, weekday."""
    X = describe(f)
    o, h, l, c = f.o, f.h, f.l, f.c
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    for w, n in (("1h", 4), ("4h", 16)):
        oo, hh, ll = o.shift(n - 1), h.rolling(n).max(), l.rolling(n).min()
        a = atr * np.sqrt(n)
        X[f"body_{w}"] = (c - oo) / a
        X[f"uw_{w}"] = (hh - np.maximum(oo, c)) / a
        X[f"lw_{w}"] = (np.minimum(oo, c) - ll) / a
        X[f"rng_{w}"] = (hh - ll) / a
    day = f.index.floor("D")
    g = f.groupby(day)
    dh, dl, do = g.h.max(), g.l.min(), g.o.first()
    pdh = pd.Series(dh.shift(1).reindex(day).values, index=f.index)
    pdl = pd.Series(dl.shift(1).reindex(day).values, index=f.index)
    dop = pd.Series(do.reindex(day).values, index=f.index)
    X["dpdh"], X["dpdl"], X["dopen"] = (c - pdh) / atr, (c - pdl) / atr, (c - dop) / atr
    sgn = np.sign(c - o)
    grp = (sgn != sgn.shift()).cumsum()
    X["streak"] = (sgn.groupby(grp).cumcount() + 1) * sgn
    wd = f.index.weekday + (f.index.hour / 24)
    X["wd_s"], X["wd_c"] = np.sin(2 * np.pi * wd / 7), np.cos(2 * np.pi * wd / 7)
    return X.replace([np.inf, -np.inf], np.nan)
