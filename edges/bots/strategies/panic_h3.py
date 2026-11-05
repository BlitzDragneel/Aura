"""Panic bounce H3 (E22, survivorship-checked in E25) — grade B. Market-wide panic, taker.

The coin's 24-hour return is in its own bottom 5% WHILE at least 20% of all measurable coins are in their own bottom 10%
in the same hour -> buy at market at once, exit at the close 24 bars after the signal bar. Coins listed >= 720 hours.
Research: +0.22%/trade (t 3.63, E22), +0.30% (t 4.08, E25). Same tail caveats as H1.
Breadth is cross-sectional: the runner must pass every coin it can (the research used every USDT-M perpetual).
"""
import numpy as np
import pandas as pd
from edges.bots.core import Signal, Strategy, dense
from edges.bots.strategies import _panic as P

Q, B, HOLD = 5, 0.20, 24


class PanicH3(Strategy):
    id = "panic_h3"
    tf = "1h"
    universe = "all"
    lookback = 24 * 34
    needs_all = True

    def _feats(self, data, last_only):
        out = {}
        for sym, df in data.items():
            if df is None or len(df) < 30:
                continue
            df = dense(df, self.tf)
            a, fv = P._anchor(self, sym, df)
            out[sym] = (df.index, P.features(df, a, fv, rows=[len(df) - 1] if last_only else None, qs=(10, Q)))
        return out

    def _mask(self, idx, F, br):
        m = P.base(F, Q)
        b = br.reindex(idx).fillna(0).values >= B
        with np.errstate(invalid="ignore"):
            return m & b & (F["c"] > 0) & (F["age"] >= P.MIN_AGE)

    def _sig(self, sym, F, i, br_v):
        return Signal(sym=sym, side="long", entry="market", price=None, valid_for_bars=1, hold_bars=HOLD,
                      note=f"r24 {F['r24'][i]*100:.1f}% <= own q5; breadth {br_v*100:.0f}% of coins in their bottom 10%",
                      strategy=self.id, ref_close=float(F["c"][i]))

    def signals(self, bars, now):
        live = {s: d for s, d in bars.items() if d is not None and len(d) and d.index[-1] == now}
        FS = self._feats(live, last_only=True)
        br = P.breadth(FS.values())
        out = []
        for sym, (idx, F) in FS.items():
            i = len(idx) - 1
            if self._mask(idx, F, br)[i]:
                out.append(self._sig(sym, F, i, float(br.get(now, 0))))
        return out

    def scan(self, data, start=None, end=None):
        FS = self._feats(data, last_only=False)
        br = P.breadth(FS.values())
        out = []
        for sym, (idx, F) in FS.items():
            for i in np.where(self._mask(idx, F, br))[0]:
                t = idx[i]
                if (start is None or t >= start) and (end is None or t < end):
                    out.append((t, self._sig(sym, F, i, float(br.get(t, 0)))))
        return sorted(out, key=lambda x: (x[0], x[1].sym))


STRATEGY = PanicH3()
