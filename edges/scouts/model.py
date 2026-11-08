"""UpScout and DownScout — trend-change predictors that are scored in public.

Each scout answers one question per market every hour, using only closed candles:
  UpScout:   "will this market make a real UP move in the next 24 hours?"
             label = the 24 h forward return is >= +1 x sigma24 (sigma24 = recent 24-hour volatility) AND the
             12-bar moving average is rising 24 h from now while it is falling or flat now  -> a trend turning up
             (first label 'up_move' is used for scoring; 'turn_up' is reported alongside)
  DownScout: the mirror image (<= -1 x sigma24; MA falling later while rising/flat now).
Model: LightGBM on ~30 technical features (returns over many lookbacks, moving-average slopes and distances, RSI,
ATR, Bollinger position, volume z-scores, range position, candle shape, BTC context, hour/weekday).
Honesty rules: trained only on the past (walk-forward), scored on data it never saw; skill is reported against
the base rate (AUC, Brier skill score) and as a tradeable test after costs. A scout's signal feeds no bot until its
FORWARD record shows skill.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

H = 24  # prediction horizon, hours

FEATURES = None  # filled by features()


def rsi(c, n=14):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def features(df: pd.DataFrame, btc: pd.DataFrame | None = None) -> pd.DataFrame:
    """df: hourly o,h,l,c,v indexed by UTC time. Returns a feature frame on the same index (row t uses data <= t)."""
    c, h, l, o, v = df.c, df.h, df.l, df.o, df.v
    lr = np.log(c).diff()
    f = pd.DataFrame(index=df.index)
    for k in (1, 3, 6, 12, 24, 72, 168, 336):
        f[f"r{k}"] = np.log(c / c.shift(k))
    sig = lr.rolling(168, min_periods=100).std()
    f["sig168"] = sig
    for k in (6, 24, 72, 168):
        f[f"rz{k}"] = f[f"r{k}"] / (sig * np.sqrt(k))
    for n in (12, 24, 72, 200):
        ma = c.rolling(n, min_periods=n // 2).mean()
        f[f"dist_ma{n}"] = np.log(c / ma) / sig
        f[f"slope_ma{n}"] = np.log(ma / ma.shift(6)) / sig
    f["ma_cross_12_72"] = np.sign(c.rolling(12).mean() - c.rolling(72).mean())
    f["rsi14"] = rsi(c, 14)
    f["rsi14_chg"] = f.rsi14.diff(6)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    f["atr_ratio"] = tr.rolling(14).mean() / tr.rolling(168, min_periods=100).mean()
    mid, sd = c.rolling(20).mean(), c.rolling(20).std()
    f["bb_pos"] = (c - mid) / (2 * sd)
    f["bb_width"] = (4 * sd / mid) / (4 * sd / mid).rolling(168, min_periods=100).mean()
    hi, lo = h.rolling(72).max(), l.rolling(72).min()
    f["range_pos72"] = (c - lo) / (hi - lo)
    lv = np.log1p(v)
    f["vol_z24"] = (lv.rolling(24).mean() - lv.rolling(336, min_periods=168).mean()) / lv.rolling(336, min_periods=168).std()
    f["vol_z1"] = (lv - lv.rolling(168, min_periods=100).mean()) / lv.rolling(168, min_periods=100).std()
    rng = (h - l).replace(0, np.nan)
    f["close_pos"] = (c - l) / rng
    f["body"] = (c - o) / rng
    if btc is not None:
        bc = btc.c.reindex(df.index)
        f["btc_r24"] = np.log(bc / bc.shift(24))
        f["btc_r168"] = np.log(bc / bc.shift(168))
        f["btc_dist_ma200"] = np.log(bc / bc.rolling(200, min_periods=100).mean())
    f["hour"] = df.index.hour
    f["dow"] = df.index.dayofweek
    return f.replace([np.inf, -np.inf], np.nan)


def labels(df: pd.DataFrame) -> pd.DataFrame:
    c = df.c
    lr = np.log(c).diff()
    sig24 = lr.rolling(168, min_periods=100).std() * np.sqrt(H)
    fwd = np.log(c.shift(-H) / c)
    ma = c.rolling(12).mean()
    slope_now = np.log(ma / ma.shift(6))
    slope_fut = slope_now.shift(-H)
    out = pd.DataFrame(index=df.index)
    out["fwd"] = fwd
    out["sig24"] = sig24
    out["up_move"] = (fwd >= sig24).astype(float)
    out["down_move"] = (fwd <= -sig24).astype(float)
    out["turn_up"] = ((slope_now <= 0) & (slope_fut > 0) & (fwd >= 0.5 * sig24)).astype(float)
    out["turn_down"] = ((slope_now >= 0) & (slope_fut < 0) & (fwd <= -0.5 * sig24)).astype(float)
    out.loc[fwd.isna() | sig24.isna(), ["up_move", "down_move", "turn_up", "turn_down"]] = np.nan
    return out


def fit(X, y, seed=0):
    import lightgbm as lgb
    m = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=31, min_child_samples=400,
                           subsample=0.7, subsample_freq=1, colsample_bytree=0.7, reg_lambda=5.0,
                           random_state=seed, verbose=-1)
    m.fit(X, y)
    return m
