"""Panic bounce H1 (E22, survivorship-checked in E25) — grade B.

A coin's 24-hour return falls into its own bottom 10% (thresholds from the 720 bars before, refreshed every 24 bars) ->
buy LIMIT at close * exp(-2 sigma) (sigma = std of the 168 hourly returns before, >= 120); it fills only if one of the next
3 candles trades BELOW the limit; exit at the close 24 bars after the fill bar. Coins listed >= 720 hours.
Research: +0.36%/trade (t 4.34, E22), +0.32% (t 4.54, E25 incl. 143 delisted coins). Single trades lost 77-93%;
as a 100 USDT account drawdowns were 56-59% (E26). Paper/testnet first.
"""
import numpy as np
from edges.bots.core import Signal, Strategy, dense
from edges.bots.strategies import _panic as P

K, W, Q, HOLD = 2.0, 3, 10, 24


class PanicH1(Strategy):
    id = "panic_h1"
    tf = "1h"
    universe = "all"
    lookback = 24 * 34          # 720-bar threshold window + its 24-bar block + r24's 24 bars + slack

    def _mask(self, F):
        m = P.base(F, Q)
        with np.errstate(invalid="ignore"):
            m &= (F["sig"] > 0) & (F["c"] > 0) & (F["age"] >= P.MIN_AGE)
        return m

    def _sig(self, sym, F, i, t):
        c, s = F["c"][i], F["sig"][i]
        return Signal(sym=sym, side="long", entry="limit", price=float(c * np.exp(-K * s)), valid_for_bars=W,
                      hold_bars=HOLD, note=f"r24 {F['r24'][i]*100:.1f}% <= own q10 {F['th'][Q][i]*100:.1f}%; sigma {s*100:.2f}%",
                      strategy=self.id, ref_close=float(c))

    def signals(self, bars, now):
        out = []
        for sym, df in bars.items():
            if df is None or len(df) < 30 or df.index[-1] != now:
                continue
            df = dense(df, self.tf)
            a, fv = P._anchor(self, sym, df)
            F = P.features(df, a, fv, rows=[len(df) - 1], qs=(Q,))
            i = len(df) - 1
            if self._mask(F)[i]:
                out.append(self._sig(sym, F, i, now))
        return out

    def scan(self, data, start=None, end=None):
        out = []
        for sym, df in data.items():
            df = dense(df, self.tf)
            a, fv = P._anchor(self, sym, df)
            F = P.features(df, a, fv, qs=(Q,))
            for i in np.where(self._mask(F))[0]:
                t = df.index[i]
                if (start is None or t >= start) and (end is None or t < end):
                    out.append((t, self._sig(sym, F, i, t)))
        return sorted(out, key=lambda x: (x[0], x[1].sym))


STRATEGY = PanicH1()
