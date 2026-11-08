"""WATCH (grade C, paper only): UpScout (E81) as a rule — long when P(up move in 24 h) is in its top 2%, hold 24 h, taker.

Every hour, for the scouts' 30 coins: edges/scouts/model.features(coin, BTC) on hourly bars -> the saved LightGBM model
edges/scouts/models/up_move.txt -> p_up_move; p >= meta.json thresholds.up_move (the 98th percentile of the model's
training-sample predictions) -> buy at market, exit at the close 24 bars after the signal bar.
Research (edges/RESULTS.md, E81, walk-forward models): top-2% longs after costs +121 bp t 2.20 (2024), +118 bp t 1.29
(2025-26) -> not tradable; forward-scored on the watch list. The live model is the one trained on all history to
2026-11-03 (the public scouts' model), so its pre-2026-11 record is in-sample.
"""
import json
import os

import numpy as np

from edges.bots.core import Signal, Strategy, dense, is_current

MODELS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scouts", "models")
HOLD = 24
_META = json.load(open(os.path.join(MODELS, "meta.json")))


class UpScoutWatch(Strategy):
    id = "upscout_watch"
    tf = "1h"
    universe = list(_META["coins"])
    lookback = 900               # features need ~340 bars (r336, 336-bar volume z); RSI's EWM settles within ~200
    needs_all = True             # BTC context features
    threshold = float(_META["thresholds"]["up_move"])
    feature_names = list(_META["features"])

    def __init__(self):
        super().__init__()
        self._booster = None

    def booster(self):
        if self._booster is None:
            import lightgbm as lgb
            self._booster = lgb.Booster(model_file=os.path.join(MODELS, "up_move.txt"))
        return self._booster

    def _probs(self, df, btc, rows=None):
        from edges.scouts.model import features
        F = features(df, btc)
        X = F[self.feature_names] if rows is None else F.iloc[rows][self.feature_names]
        return X.index, self.booster().predict(X)

    def _sig(self, sym, c, p):
        return Signal(sym=sym, side="long", entry="market", valid_for_bars=1, hold_bars=HOLD, strategy=self.id,
                      ref_close=float(c), note=f"p_up_move {p:.3f} >= top-2% threshold {self.threshold:.3f}")

    def signals(self, bars, now):
        btc = bars.get("BTCUSDT")
        if btc is None or not is_current(btc, now, self.tf):
            return []
        btc = dense(btc, self.tf)
        out = []
        for sym in self.universe:
            df = bars.get(sym)
            if df is None or len(df) < 400 or not is_current(df, now, self.tf):
                continue
            df = dense(df, self.tf)
            if not np.isfinite(df.c.values[-1]):
                continue
            _, p = self._probs(df, btc, [len(df) - 1])
            if p[0] >= self.threshold:
                out.append(self._sig(sym, df.c.values[-1], float(p[0])))
        return out

    def scan(self, data, start=None, end=None):
        btc = data.get("BTCUSDT")
        if btc is None:
            return []
        btc = dense(btc, self.tf)
        out = []
        for sym in self.universe:
            df = data.get(sym)
            if df is None or len(df) < 400:
                continue
            df = dense(df, self.tf)
            idx, p = self._probs(df, btc)
            c = df.c.values
            for i in np.where((p >= self.threshold) & np.isfinite(c) & (np.arange(len(c)) >= 399))[0]:
                t = idx[i]
                if (start is None or t >= start) and (end is None or t < end):
                    out.append((t, self._sig(sym, c[i], float(p[i]))))
        return sorted(out, key=lambda x: (x[0], x[1].sym))


STRATEGY = UpScoutWatch()
