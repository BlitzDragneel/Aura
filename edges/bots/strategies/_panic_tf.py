"""Panic-bounce limit entry on short bars (E37 5m / E38 15m): the research's run_panic.py + lib1.sim_limit rule.

At the close of bar t: the coin's L-bar log return is <= its own 10th-percentile block threshold (look bars before the
block, see _intraday) AND sigma > 0 and close > 0 -> resting LIMIT buy at close * exp(-k * sigma); it fills only if one
of the next W bars trades BELOW the limit; exit at the close H bars after the fill bar. One order/position per coin at a
time (the runner and the backtester ignore a signal while the rule is busy in that coin, as sim_limit's `nxt`).
"""
import numpy as np

from edges.bots.core import Signal, Strategy, dense, is_current
from edges.bots.strategies import _intraday as I


class PanicTF(Strategy):
    tf = "5m"
    L = K = W = H = LOOK = STEP = None
    Q = 10
    universe = I.COINS30

    @property
    def lookback(self):
        return self.LOOK + self.STEP + self.L + 32

    def _feats(self, sym, df, rows):
        c = df.c.values.astype(float)
        r = I.log_ret(c, self.L)
        th = I.thresholds(r, df.index, self.tf, I.anchor_of(sym, self.tf), self.LOOK, self.STEP, (self.Q,), rows)[self.Q]
        return c, r, th, I.sigma(c)

    def _mask(self, c, r, th, sg):
        with np.errstate(invalid="ignore"):
            return I.below(r, th) & (sg > 0) & (c > 0)

    def _sig(self, sym, c, r, th, sg, i):
        return Signal(sym=sym, side="long", entry="limit", price=float(c[i] * np.exp(-self.K * sg[i])),
                      valid_for_bars=self.W, hold_bars=self.H, strategy=self.id, ref_close=float(c[i]),
                      note=f"r{self.L} {r[i]*100:.2f}% <= own q{self.Q} {th[i]*100:.2f}%; sigma {sg[i]*100:.3f}%")

    def signals(self, bars, now):
        out = []
        for sym, df in bars.items():
            if df is None or len(df) < self.L + 2 or not is_current(df, now, self.tf):
                continue
            df = dense(df, self.tf)
            i = len(df) - 1
            c, r, th, sg = self._feats(sym, df, [i])
            if self._mask(c, r, th, sg)[i]:
                out.append(self._sig(sym, c, r, th, sg, i))
        return out

    def scan(self, data, start=None, end=None):
        out = []
        for sym, df in data.items():
            if df is None or len(df) < self.L + 2:
                continue
            df = dense(df, self.tf)
            c, r, th, sg = self._feats(sym, df, None)
            for i in np.where(self._mask(c, r, th, sg))[0]:
                t = df.index[i]
                if (start is None or t >= start) and (end is None or t < end):
                    out.append((t, self._sig(sym, c, r, th, sg, i)))
        return sorted(out, key=lambda x: (x[0], x[1].sym))
