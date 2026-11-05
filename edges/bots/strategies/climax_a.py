"""Climax reversal (round 16) — grade A, the only direction rule that passed a final test on 324 untouched coins.

At a bar's close the coin fell >= 3 of its own hourly standard deviations (sigma of the 168 hourly log returns before,
>= 120 valid, ddof 1), on >= 3x the median volume of those 168 bars (>= 120 valid), and closed in the top 40% of the
bar's range (close - low >= 0.6 * (high - low)); listed >= 720 hours -> buy the next open, exit at the close 12 bars
after the signal bar (held 12 hours). Same definitions as OMEGA Prime's climax watch (prime_post.js) and the research
script omega/research/archive-2026-10-20/climax.py. Stablecoins excluded. About +1.6%/trade before costs; rare.
"""
import numpy as np
import pandas as pd
from edges.bots.core import STABLES, Signal, Strategy, dense

ZK, VK, LK, HOLD, N, NMIN, AGE = 3.0, 3.0, 0.6, 12, 168, 120, 720
H = pd.Timedelta(hours=1)


def features(df, first_valid):
    c, h, l = df.c.values.astype(float), df.h.values.astype(float), df.l.values.astype(float)
    v = df.v.where(np.isfinite(df.c)).astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        lr = np.log(c / np.r_[np.nan, c[:-1]])
    sig = pd.Series(lr).rolling(N, min_periods=NMIN).std().shift(1).values
    med = v.rolling(N, min_periods=NMIN).median().shift(1).values
    rng = h - l
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(sig > 0, lr / sig, 0.0)
        vr = np.where(med > 0, v.values / med, 0.0)
        loc = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), 0.0)
    age = np.asarray((df.index - first_valid) // H, dtype=np.int64)
    with np.errstate(invalid="ignore"):
        fire = (z <= -ZK) & (vr >= VK) & (loc >= LK) & (age >= AGE) & np.isfinite(lr)
    return dict(z=z, vr=vr, loc=loc, fire=fire, c=c)


class ClimaxA(Strategy):
    id = "climax_a"
    tf = "1h"
    universe = "all"
    lookback = 24 * 8

    def _fv(self, sym, df):
        m = self.meta.get(sym) or {}
        fv = m.get("first_valid_ts", m.get("first_ts"))
        if fv is None:
            ok = np.isfinite(df.c.values)
            fv = df.index[int(np.argmax(ok))] if ok.any() else df.index[-1]
        return pd.Timestamp(fv)

    def _sig(self, sym, F, i):
        return Signal(sym=sym, side="long", entry="market", valid_for_bars=1, hold_bars=HOLD,
                      note=f"fell {abs(F['z'][i]):.1f} sigma on {F['vr'][i]:.1f}x volume, closed at {F['loc'][i]*100:.0f}% of range",
                      strategy=self.id, ref_close=float(F["c"][i]))

    def signals(self, bars, now):
        out = []
        for sym, df in bars.items():
            if sym in STABLES or df is None or len(df) < NMIN + 2 or df.index[-1] != now:
                continue
            df = dense(df, self.tf)
            fv = self._fv(sym, df)
            df = df.iloc[-(N + 2):]
            F = features(df, fv)
            if F["fire"][-1]:
                out.append(self._sig(sym, F, len(df) - 1))
        return out

    def scan(self, data, start=None, end=None):
        out = []
        for sym, df in data.items():
            if sym in STABLES:
                continue
            df = dense(df, self.tf)
            F = features(df, self._fv(sym, df))
            for i in np.where(F["fire"])[0]:
                t = df.index[i]
                if (start is None or t >= start) and (end is None or t < end):
                    out.append((t, self._sig(sym, F, i)))
        return sorted(out, key=lambda x: (x[0], x[1].sym))


STRATEGY = ClimaxA()
