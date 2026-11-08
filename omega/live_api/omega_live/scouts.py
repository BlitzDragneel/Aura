"""On-demand scout readings for the API: the latest CLOSED candle, any time you ask (cached per candle).
Uses the same models and features as the forward-scored scouts in edges/scouts (information only)."""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

from .providers import TF_MS, Crypto, ProviderError
from .signals import REPO

TARGETS = ("up_move", "down_move", "turn_up", "turn_down")
SPEEDS = {"fast": ("15m", "models15", 16), "hourly": ("1h", "models", 24)}


class Scouts:
    def __init__(self, crypto: Crypto):
        self.cx = crypto
        self._m, self._cache = {}, {}

    def _models(self, speed):
        if speed not in self._m:
            import lightgbm as lgb
            if str(REPO) not in sys.path:
                sys.path.insert(0, str(REPO))
            d = REPO / "edges" / "scouts" / SPEEDS[speed][1]
            meta = json.load(open(d / "meta.json"))
            self._m[speed] = (meta, {t: lgb.Booster(model_file=str(d / f"{t}.txt")) for t in TARGETS})
        return self._m[speed]

    def _bars(self, sym, tf):
        k = self.cx.klines(sym, tf, 500)
        df = pd.DataFrame([c for c in k["candles"] if c["closed"]])
        df.index = pd.to_datetime(df.pop("t"), unit="ms", utc=True)
        return df[["o", "h", "l", "c", "v", "qv"]]

    def read(self, speed="fast", symbols=None):
        if speed not in SPEEDS:
            raise ValueError("speed must be fast or hourly")
        tf = SPEEDS[speed][0]
        bar = int(time.time() * 1000) // TF_MS[tf]
        key = (speed, tuple(symbols or ()))
        if key in self._cache and self._cache[key][0] == bar:
            return self._cache[key][1]
        meta, boosters = self._models(speed)   # also puts the repo on sys.path
        from edges.scouts.model import features
        coins = [s.upper() for s in symbols] if symbols else meta["coins"]
        btc = self._bars("BTCUSDT", tf)
        out = []
        for s in coins[:30]:
            try:
                d = btc if s == "BTCUSDT" else self._bars(s, tf)
            except (ProviderError, ValueError, KeyError):
                continue
            if len(d) < 400:
                continue
            x = features(d, btc).iloc[[-1]][meta["features"]]
            r = dict(sym=s, bar=d.index[-1].isoformat(), close=float(d.c.iloc[-1]))
            for t in TARGETS:
                p = float(boosters[t].predict(x)[0])
                r[f"p_{t}"] = round(p, 4)
                r[f"flag_{t}"] = p >= meta["thresholds"][t]
            out.append(r)
        out.sort(key=lambda r: -max(r["p_up_move"], r["p_down_move"]))
        res = dict(speed=speed, candle=tf, horizon=f"{SPEEDS[speed][2]} candles", asof=int(time.time() * 1000),
                   note="information only: predicts big moves better than chance, but trading the calls lost money "
                        "after costs in 2025-26 tests (E81/E82); never an order", readings=out)
        self._cache[key] = (bar, res)
        return res
