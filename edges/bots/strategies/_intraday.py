"""Shared features of the 5m / 15m panic-bounce watch rules (E37, E38, E40), computed EXACTLY as the research engine
edges/research1/lib1.py + run_panic.py / run_breadth.py does, on a dense grid of `tf` bars:

  r_L  = log(c / c L bars earlier)                                    (L bars, e.g. 288 x 5m = 24 h)
  th_q = numpy percentile q ('linear') of r_L over the `look` bars before the block start; blocks are `step` bars long
         and start look, look+step, ... bars after the research frame's first bar (lib1.day_thresholds); >= look//2 finite
  sig  = std (ddof 1) of the 168 log returns (of `tf` bars) before the bar, >= 120 valid (lib1.sigma)

Block anchors. The research anchors blocks at the first bar of its data frame:
  E37 / E38: each coin's own frame, i.e. the first row of the coin's 5m parquet file (floored to 15m for E38);
  E40: all 30 coins reindexed to one union index starting 2022-01-01 00:00 -> UTC-midnight blocks for every coin.
Blocks are one day long (288 x 5m, 96 x 15m), so only the anchor's time of day matters. ANCHOR5M holds the research
files' first rows (/home/user/data/5m, Nov 2026) so a live frame of any length reproduces the research's blocks.
"""
import numpy as np
import pandas as pd

from edges.bots.core import tf_delta

# the 30 coins with 5m files (lib1.coins5()) and each file's first bar (UTC)
ANCHOR5M = {
    "1000PEPEUSDT": "2023-05-05 16:30", "AAVEUSDT": "2022-01-01 00:00", "ADAUSDT": "2022-01-01 00:00",
    "APTUSDT": "2022-10-19 02:00", "ARBUSDT": "2023-03-23 15:00", "ATOMUSDT": "2022-01-01 00:00",
    "AVAXUSDT": "2022-01-01 00:00", "BCHUSDT": "2022-01-01 00:00", "BNBUSDT": "2022-01-01 00:00",
    "BTCUSDT": "2022-01-01 00:00", "DOGEUSDT": "2022-01-01 00:00", "DOTUSDT": "2022-01-01 00:00",
    "ETCUSDT": "2022-01-01 00:00", "ETHUSDT": "2022-01-01 00:00", "FILUSDT": "2022-01-01 00:00",
    "HBARUSDT": "2022-01-01 00:00", "INJUSDT": "2022-08-17 02:45", "LINKUSDT": "2022-01-01 00:00",
    "LTCUSDT": "2022-01-01 00:00", "NEARUSDT": "2022-01-01 00:00", "OPUSDT": "2022-06-01 14:00",
    "SEIUSDT": "2023-08-17 02:30", "SOLUSDT": "2022-01-01 00:00", "SUIUSDT": "2023-05-03 16:00",
    "TIAUSDT": "2023-10-31 18:00", "TRXUSDT": "2022-01-01 00:00", "UNIUSDT": "2022-01-01 00:00",
    "WIFUSDT": "2024-01-18 14:15", "XLMUSDT": "2022-01-01 00:00", "XRPUSDT": "2022-01-01 00:00",
}
COINS30 = sorted(ANCHOR5M)
E40_ANCHOR = pd.Timestamp("2022-01-01 00:00", tz="UTC")


def anchor_of(sym, tf, own=True):
    """Block anchor for `sym` at `tf`. own=False -> the E40 union-index anchor (UTC midnight)."""
    if not own or sym not in ANCHOR5M:
        return E40_ANCHOR
    return pd.Timestamp(ANCHOR5M[sym], tz="UTC").floor(tf_delta(tf))


def log_ret(c, L):
    n = len(c)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log(c / np.r_[np.full(L, np.nan), c[:-L]]) if n > L else np.full(n, np.nan)


def thresholds(r, idx, tf, anchor, look, step, qs, rows=None):
    """{q: array} of block thresholds (NaN where the research had none). rows: positions needed (None = all)."""
    n = len(r)
    bar = tf_delta(tf)
    pos = np.asarray((idx - anchor) // bar, dtype=np.int64)
    th = {q: np.full(n, np.nan) for q in qs}
    rr = np.arange(n) if rows is None else np.asarray(rows, dtype=np.int64)
    p = pos[rr]
    ok = p >= look
    blocks = {}
    for i, pi in zip(rr[ok], p[ok]):
        blocks.setdefault(int(look + step * ((pi - look) // step)), []).append(i)
    pos0 = int(pos[0]) if n else 0
    for s, members in blocks.items():
        i0, i1 = s - look - pos0, s - pos0
        if i0 < 0:                       # the frame does not reach back to the window start (live: fetch more history)
            continue
        w = r[i0:i1]
        w = w[np.isfinite(w)]
        if len(w) >= look // 2:
            vals = np.percentile(w, list(qs))
            for q, v in zip(qs, vals):
                th[q][members] = v
    return th


def sigma(c, n=168, minp=120):
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = pd.Series(np.log(c / np.r_[np.nan, c[:-1]]))
    return lr.rolling(n, min_periods=minp).std().shift(1).values


def below(r, t):
    with np.errstate(invalid="ignore"):
        return np.nan_to_num(r <= t, nan=0).astype(bool) & np.isfinite(t)
