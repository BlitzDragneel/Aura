"""Run the TESTED rules (edges/approved.json) on live, closed candles.

Uses the same strategy files the backtester and trading bot use (edges/bots/strategies/<id>.py, each exposing
STRATEGY with .id .tf .universe .lookback and .signals(bars, now)), so a live signal here is the backtest's signal.
Only rules listed in approved.json are run; nothing here places orders.
"""
from __future__ import annotations

import concurrent.futures as cf
import importlib.util
import json
import os
import time
from pathlib import Path

import pandas as pd

from .providers import TF_MS, Crypto, ProviderError

REPO = Path(os.environ.get("OMEGA_REPO", Path(__file__).resolve().parents[3]))
APPROVED = REPO / "edges" / "approved.json"
STRAT_DIR = REPO / "edges" / "bots" / "strategies"


def approved_rules() -> list[dict]:
    if not APPROVED.exists():
        return []
    try:
        return json.loads(APPROVED.read_text())
    except json.JSONDecodeError:
        return []


def load_strategy(rule_id: str):
    if not rule_id.replace("_", "").isalnum():
        raise ValueError("bad rule id")
    f = STRAT_DIR / f"{rule_id}.py"
    if not f.exists():
        raise FileNotFoundError(f"no strategy file for {rule_id}")
    import sys
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(f"omega_strategy_{rule_id}", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.STRATEGY


def to_frame(candles: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame([c for c in candles if c.get("closed")])
    if df.empty:
        return df
    df.index = pd.to_datetime(df.pop("t"), unit="ms", utc=True)
    return df[["o", "h", "l", "c", "v", "qv"]]


class LiveSignals:
    def __init__(self, crypto: Crypto, universe_size: int = 60, workers: int = 3):
        self.crypto = crypto
        self.n = universe_size
        self.workers = workers
        self._bars_cache: dict[tuple, tuple[int, dict]] = {}

    def bars(self, syms: list[str], tf: str, lookback: int) -> dict[str, pd.DataFrame]:
        """Closed candles per symbol. One fetch per symbol per bar is shared by every rule on that timeframe."""
        bar_id = int(time.time() * 1000) // TF_MS[tf]
        store = self._bars_cache.setdefault(tf, (bar_id, {}))
        if store[0] != bar_id:
            store = self._bars_cache[tf] = (bar_id, {})
        have = store[1]
        need = [s for s in syms if s not in have or len(have[s]) < min(lookback, 999)]

        def one(s):
            try:
                return s, to_frame(self.crypto.klines(s, tf, min(max(lookback, 720) + 1, 1000))["candles"])
            except (ProviderError, ValueError):
                return s, None
        with cf.ThreadPoolExecutor(self.workers) as ex:
            for s, df in ex.map(one, need):
                if df is not None and len(df):
                    have[s] = df
        return {s: have[s].iloc[-lookback:] for s in syms if s in have}

    def run(self) -> dict:
        rules = approved_rules()
        res = dict(asof=int(time.time() * 1000), rules=[], note="signals from tested rules only; nothing is ordered")
        for r in rules:
            entry = dict(id=r.get("id"), grade=r.get("grade"), status=r.get("status"), signals=[], error=None)
            try:
                st = load_strategy(r["id"])
                syms = st.universe if isinstance(st.universe, list) else self.crypto.top_by_volume(self.n)
                bars = self.bars(syms, st.tf, int(getattr(st, "lookback", 200)))
                now = pd.Timestamp.now(tz="UTC")
                for sg in st.signals(bars, now) or []:
                    entry["signals"].append({k: (v if isinstance(v, (int, float, str, bool, type(None))) else str(v))
                                             for k, v in getattr(sg, "__dict__", dict(sg)).items()})
                entry["coins_seen"] = len(bars)
                entry["tf"] = st.tf
            except Exception as e:  # one broken rule must not hide the others
                entry["error"] = f"{type(e).__name__}: {e}"
            res["rules"].append(entry)
        return res
