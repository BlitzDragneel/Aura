"""WATCH (grade C, paper only): E40 market-wide panic on 15-minute bars, taker — variant judged in FINAL: L96 b20 q5 H96.

Over the research's 30 coins (15m bars built from 5m, core.resample): the coin's 24-hour (96-bar) log return is in its
own bottom 5% WHILE at least 20% of the coins measurable in that bar are in their own bottom 10% (breadth counts coins
with a finite q10 threshold and return; fewer than 10 measurable -> breadth 0) -> buy at market (next open), exit at the
close 96 bars (24 h) after the signal bar. Thresholds: 2880 bars (30 days) before each 96-bar block; blocks anchored at
the research's union index start (2022-01-01 00:00 UTC) = UTC midnight for every coin.
Research (edges/results/E40_result.json): discovery +92.5 bp t 2.63, validation +90.8 t 1.56, FINAL 2025-26 +24.7 bp
t 0.74 (n 3,287), without the best 5% -44.1 -> FAIL. Watch list only. Breadth needs all 30 coins' bars.
"""
import numpy as np
import pandas as pd

from edges.bots.core import Signal, Strategy, dense, is_current
from edges.bots.strategies import _intraday as I

L, B, Q, HOLD, LOOK, STEP, MIN_COINS = 96, 0.20, 5, 96, 2880, 96, 10


class Breadth15mWatch(Strategy):
    id = "breadth15m_watch"
    tf = "15m"
    source_tf = "5m"
    universe = I.COINS30
    lookback = LOOK + STEP + L + 32
    needs_all = True

    def _feats(self, data, last_only):
        out = {}
        for sym, df in data.items():
            if sym not in self.universe or df is None or len(df) < L + 2:
                continue
            df = dense(df, self.tf)
            c = df.c.values.astype(float)
            r = I.log_ret(c, L)
            th = I.thresholds(r, df.index, self.tf, I.anchor_of(sym, self.tf, own=False), LOOK, STEP, (10, Q),
                              [len(df) - 1] if last_only else None)
            out[sym] = (df.index, c, r, th)
        return out

    @staticmethod
    def _breadth(FS):
        cnt = tot = None
        for idx, c, r, th in FS.values():
            ok = np.isfinite(th[10]) & np.isfinite(r)
            t = pd.Series(ok.astype(float), index=idx)
            k = pd.Series((I.below(r, th[10]) & ok).astype(float), index=idx)
            tot = t if tot is None else tot.add(t, fill_value=0)
            cnt = k if cnt is None else cnt.add(k, fill_value=0)
        if tot is None:
            return pd.Series(dtype=float)
        return pd.Series(np.where(tot >= MIN_COINS, cnt / np.maximum(tot, 1), 0.0), index=tot.index)

    def _mask(self, idx, c, r, th, br):
        b = br.reindex(idx).fillna(0).values >= B
        with np.errstate(invalid="ignore"):
            return I.below(r, th[Q]) & b & (c > 0)

    def _sig(self, sym, c, r, i, bv):
        return Signal(sym=sym, side="long", entry="market", valid_for_bars=1, hold_bars=HOLD, strategy=self.id,
                      ref_close=float(c[i]),
                      note=f"r96 {r[i]*100:.2f}% <= own q5; breadth {bv*100:.0f}% of the 30 coins in their bottom 10%")

    def signals(self, bars, now):
        live = {s: d for s, d in bars.items() if d is not None and len(d) and is_current(d, now, self.tf)}
        FS = self._feats(live, last_only=True)
        br = self._breadth(FS)
        out = []
        for sym, (idx, c, r, th) in FS.items():
            i = len(idx) - 1
            if self._mask(idx, c, r, th, br)[i]:
                out.append(self._sig(sym, c, r, i, float(br.get(idx[i], 0))))
        return out

    def scan(self, data, start=None, end=None):
        FS = self._feats(data, last_only=False)
        br = self._breadth(FS)
        out = []
        for sym, (idx, c, r, th) in FS.items():
            for i in np.where(self._mask(idx, c, r, th, br))[0]:
                t = idx[i]
                if (start is None or t >= start) and (end is None or t < end):
                    out.append((t, self._sig(sym, c, r, i, float(br.get(t, 0)))))
        return sorted(out, key=lambda x: (x[0], x[1].sym))


STRATEGY = Breadth15mWatch()
