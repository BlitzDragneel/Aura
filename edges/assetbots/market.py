"""The market read: a compact, descriptive picture of one market on CLOSED bars. Never a direction call.

trend per timeframe  - where the close sits against its 20/50-bar averages and which way the 20-bar average slopes
volatility regime    - 1h ATR14 as % of price and its percentile over the last ~500 hours; daily 20-day realised vol
                       and its percentile over the daily history fetched
session              - Asia / London / New York / late US, CME daily break and weekend (metals: spot closed)
range extremes       - distance to the 24 h / 7 d / 30 d high and low, in % and in 1h ATRs
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TREND_TFS = ("15m", "1h", "4h", "1d")


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    tr = pd.concat([df.h - df.l, (df.h - df.c.shift()).abs(), (df.l - df.c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n, min_periods=n).mean()


def trend(df: pd.DataFrame | None) -> dict | None:
    if df is None or len(df) < 60:
        return None
    c = df.c.astype(float)
    m20, m50 = c.rolling(20).mean(), c.rolling(50).mean()
    a = atr(df).iloc[-1]
    slope = (m20.iloc[-1] - m20.iloc[-6]) / a if a and a == a else 0.0
    last = c.iloc[-1]
    if last > m20.iloc[-1] > m50.iloc[-1] and slope > 0.25:
        st = "up"
    elif last < m20.iloc[-1] < m50.iloc[-1] and slope < -0.25:
        st = "down"
    else:
        st = "flat"
    return dict(state=st, close=float(last), ma20=float(m20.iloc[-1]), ma50=float(m50.iloc[-1]),
                slope_atr=round(float(slope), 2), bar=df.index[-1].isoformat())


def pct_rank(s: pd.Series, x: float) -> float | None:
    s = s.dropna()
    if len(s) < 30 or x != x:
        return None
    return round(float((s < x).mean() * 100), 1)


def regime_name(p: float | None) -> str:
    if p is None:
        return "unknown"
    return "extreme" if p >= 95 else "active" if p >= 75 else "quiet" if p <= 25 else "normal"


def volatility(h1: pd.DataFrame | None, d1: pd.DataFrame | None) -> dict:
    out = {}
    if h1 is not None and len(h1) > 60:
        ap = atr(h1) / h1.c
        out["atr1h_pct"] = round(float(ap.iloc[-1] * 100), 3)
        out["atr1h_pctile"] = pct_rank(ap.iloc[-500:], ap.iloc[-1])
        out["atr1h"] = float(atr(h1).iloc[-1])
    if d1 is not None and len(d1) > 40:
        rv = np.log(d1.c).diff().rolling(20).std() * np.sqrt(365)
        out["rv20d_ann_pct"] = round(float(rv.iloc[-1] * 100), 1)
        out["rv20d_pctile"] = pct_rank(rv, rv.iloc[-1])
        out["day_range_pct_median"] = round(float(((d1.h - d1.l) / d1.c).iloc[-60:].median() * 100), 2)
    p = out.get("atr1h_pctile")
    out["regime"] = regime_name(p)
    out["regime_daily"] = regime_name(out.get("rv20d_pctile"))
    return out


def session(now: pd.Timestamp, spec) -> dict:
    now = pd.Timestamp(now).tz_convert("UTC") if pd.Timestamp(now).tzinfo else pd.Timestamp(now, tz="UTC")
    h, dow = now.hour, now.dayofweek
    name = "Asia" if h < 7 else "London" if h < 13 else "New York" if h < 21 else "late US"
    weekend = (dow == 5) or (dow == 6 and h < 22) or (dow == 4 and h >= 21)
    out = dict(name=name, utc_hour=h, weekday=now.day_name(), weekend=bool(weekend))
    if spec.daily_break_utc:
        a, b = spec.daily_break_utc
        out["cme_break"] = a <= h < b and not weekend
        out["spot_open"] = not weekend and not out["cme_break"]
        if weekend:
            out["note"] = "spot gold/silver closed for the weekend; the perpetual still trades but thinly - moves are less reliable"
        elif out["cme_break"]:
            out["note"] = "CME daily break (21-22 UTC): spot quotes pause"
    else:
        out["note"] = "Bitcoin trades 24/7" + ("; weekend liquidity is thinner" if dow >= 5 else "")
    return out


def ranges(h1: pd.DataFrame | None, d1: pd.DataFrame | None) -> dict:
    out = {}
    if h1 is None or len(h1) < 30:
        return out
    c = float(h1.c.iloc[-1])
    a = float(atr(h1).iloc[-1]) if len(h1) > 15 else float("nan")
    windows = (("24h", h1.iloc[-24:]), ("7d", h1.iloc[-168:]))
    if d1 is not None and len(d1) >= 30:
        windows += (("30d", d1.iloc[-30:]),)
    for name, w in windows:
        hi, lo = float(w.h.max()), float(w.l.min())
        out[name] = dict(high=hi, low=lo, to_high_pct=round((hi / c - 1) * 100, 2), to_low_pct=round((c / lo - 1) * 100, 2),
                         to_high_atr=round((hi - c) / a, 1) if a == a and a > 0 else None,
                         to_low_atr=round((c - lo) / a, 1) if a == a and a > 0 else None,
                         position=round((c - lo) / (hi - lo), 2) if hi > lo else None)
    return out


def read(bars: dict, now, spec, quote: dict | None = None, funding: dict | None = None, scouts: dict | None = None) -> dict:
    """bars: {tf: DataFrame[o,h,l,c,v,qv]} of CLOSED bars. Returns the descriptive market read (JSON-able)."""
    h1, d1 = bars.get("1h"), bars.get("1d")
    last = next((bars[t] for t in ("15m", "1h") if bars.get(t) is not None and len(bars[t])), None)
    out = dict(price=float(last.c.iloc[-1]) if last is not None else None,
               bar=last.index[-1].isoformat() if last is not None else None,
               trend={tf: trend(bars.get(tf)) for tf in TREND_TFS},
               volatility=volatility(h1, d1), session=session(now, spec), ranges=ranges(h1, d1),
               note="descriptive only: trend words say where price sits against its averages, they are not a call")
    if d1 is not None and len(d1) > 1:
        out["change_24h_pct"] = round(float((d1.c.iloc[-1] / d1.c.iloc[-2] - 1) * 100), 2)
    if quote:
        q = {k: quote.get(k) for k in ("price", "bid", "ask", "spread", "age_s", "stale", "note", "source")}
        if out["price"] and q.get("price") and not q.get("stale"):
            q["perp_premium_pct"] = round((out["price"] / q["price"] - 1) * 100, 3)
        out["spot"] = q
    if funding:
        out["funding"] = {k: funding.get(k) for k in ("rate", "next_time", "source")}
    if scouts:
        out["scouts"] = scouts
    return out


def big_move_threshold(h1: pd.DataFrame, hours: int = 4) -> float:
    """What counts as a big move over `hours` (log return): the handoff's max(40 bp, 2 x ATR14) on 1h bars."""
    a = float((atr(h1) / h1.c).iloc[-1])
    return max(0.004, 2 * a)
