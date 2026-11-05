"""Shared features of the panic-bounce rules (E22 H1/H3), computed EXACTLY as the research engine
omega/research/e25kit/reference_e22.py (verbatim e22_lib) does, on a dense hourly grid:

  r24  = log(c / c 24 bars earlier)
  th_q = the q-th percentile (numpy 'linear') of r24 over the 720 bars before the block start; blocks are 24 bars long and
         start 720, 744, 768 ... bars after the coin's first bar (the research anchors them to the first bar of the
         coin's history, not to UTC midnight); needs >= 360 finite values
  sig  = std (ddof 1) of the 168 hourly log returns before the bar (>= 120 valid)
  age  = bars since the coin's first valid close; the research (E25 run) required >= 720
"""
import numpy as np
import pandas as pd

LOOKBACK, STEP, MIN_AGE = 720, 24, 720
H = pd.Timedelta(hours=1)


def _anchor(strategy, sym, df):
    m = strategy.meta.get(sym) or {}
    a = m.get("first_ts")
    a = pd.Timestamp(a) if a is not None else df.index[0].floor("D")      # fallback: UTC-midnight blocks (as Prime)
    fv = m.get("first_valid_ts", m.get("first_ts"))
    if fv is None:
        ok = np.isfinite(df.c.values) & (df.c.values > 0)
        fv = df.index[int(np.argmax(ok))] if ok.any() else df.index[-1]
    return a, pd.Timestamp(fv)


def features(df, anchor, first_valid, rows=None, qs=(10, 5)):
    """df: dense 1h frame. rows: positions (ints) where thresholds are needed (None = all)."""
    c = df.c.values.astype(float)
    n = len(c)
    with np.errstate(divide="ignore", invalid="ignore"):
        r24 = np.log(c / np.r_[np.full(24, np.nan), c[:-24]]) if n > 24 else np.full(n, np.nan)
    pos = np.asarray((df.index - anchor) // H, dtype=np.int64)            # bars since the anchor
    th = {q: np.full(n, np.nan) for q in qs}
    idx = np.arange(n) if rows is None else np.asarray(rows, dtype=np.int64)
    p = pos[idx]
    ok = p >= LOOKBACK
    blocks = {}
    for i, pi in zip(idx[ok], p[ok]):
        s = LOOKBACK + STEP * ((pi - LOOKBACK) // STEP)
        blocks.setdefault(int(s), []).append(i)
    pos0 = int(pos[0]) if n else 0
    for s, members in blocks.items():
        i0, i1 = s - LOOKBACK - pos0, s - pos0
        if i0 < 0:                                     # the window does not reach back far enough
            continue
        w = r24[i0:i1]
        w = w[np.isfinite(w)]
        if len(w) >= LOOKBACK // 2:
            vals = np.percentile(w, list(qs))
            for q, v in zip(qs, vals):
                th[q][members] = v
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = pd.Series(np.log(c / np.r_[np.nan, c[:-1]]))
    sig = lr.rolling(168, min_periods=120).std().shift(1).values
    age = np.asarray((df.index - first_valid) // H, dtype=np.int64)
    return dict(c=c, l=df.l.values.astype(float), r24=r24, th=th, sig=sig, age=age)


def base(F, q):
    t = F["th"][q]
    with np.errstate(invalid="ignore"):
        return np.nan_to_num(F["r24"] <= t, nan=0).astype(bool) & np.isfinite(t)


def breadth(feats):
    """{time: share of coins in their own bottom-10% 24h move} over hours with >= 5 coins measurable (reference breadth_of)."""
    cnt = tot = None
    for idx, F in feats:
        ok = np.isfinite(F["th"][10]) & np.isfinite(F["r24"])
        if not ok.any():
            continue
        t = pd.Series(1.0, index=idx[ok])
        c = pd.Series(base(F, 10)[ok].astype(float), index=idx[ok])
        tot = t if tot is None else tot.add(t, fill_value=0)
        cnt = c if cnt is None else cnt.add(c, fill_value=0)
    if tot is None:
        return pd.Series(dtype=float)
    keep = tot >= 5
    return (cnt[keep] / tot[keep])
