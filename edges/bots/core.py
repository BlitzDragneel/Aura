"""Strategy contract (see edges/bots/README.md) and the order/position models shared by backtest, paper and live.

One strategy file = one rule. The same `signals()` code runs in the backtest, in paper mode and on the exchange, so a
live signal is trade-for-trade the backtest's. Strategies may also override `scan()` (a vectorised version of calling
`signals()` at every bar) for speed; `edges/tests_bots/test_strategies.py` proves the two agree.
"""
from __future__ import annotations

import dataclasses as dc
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

TF_SECONDS = {"5m": 300, "15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}
STABLES = {"USDCUSDT", "FDUSDUSDT", "TUSDUSDT", "BUSDUSDT", "USDPUSDT", "DAIUSDT", "EURUSDT", "USDEUSDT", "BFUSDUSDT"}


def tf_delta(tf: str) -> pd.Timedelta:
    return pd.Timedelta(seconds=TF_SECONDS[tf])


# ---------------------------------------------------------------- the contract
@dc.dataclass
class Signal:
    """An order to place right now, at the close of the bar that just closed.

    entry: "limit" -> resting buy/sell limit at `price`, filled only if a later bar trades THROUGH it (low < price for a
           long), valid for the next `valid_for_bars` bars; hold_bars counts from the FILL bar (exit at the close of
           fill_bar + hold_bars).
           "market" -> taker order at once (backtest: the next bar's open); hold_bars counts from the SIGNAL bar
           (exit at the close of signal_bar + hold_bars).
    stop_pct / target_pct: fractions of the entry price (0.10 = 10%); None = the rule has none (the live runner still
    places a protective stop, see config guard.protective_stop_pct).
    """
    sym: str
    side: str = "long"                 # long | short
    entry: str = "market"              # market | limit
    price: Optional[float] = None      # limit price (None for market)
    valid_for_bars: int = 1
    hold_bars: int = 24
    stop_pct: Optional[float] = None
    target_pct: Optional[float] = None
    note: str = ""
    # filled in by the runners (not by strategies)
    strategy: str = ""
    ref_close: Optional[float] = None  # close of the signal bar (used to re-base prices on testnet)

    def to_dict(self):
        return dc.asdict(self)


class Strategy:
    id = "base"
    tf = "1h"
    universe = "all"                   # "all" or a list of symbols
    lookback = 24 * 30                 # bars of history signals() needs
    needs_all = False                  # True when the rule is cross-sectional (needs every coin's bars, e.g. breadth)

    def __init__(self):
        # sym -> {"first_ts": pd.Timestamp}: when the coin's history starts (listing). Runners fill this in;
        # rules use it for "listed at least N days" and to anchor daily windows exactly as the research did.
        self.meta: Dict[str, dict] = {}

    def signals(self, bars: Dict[str, pd.DataFrame], now: pd.Timestamp) -> List[Signal]:
        """bars: {sym: DataFrame[o,h,l,c,v,qv] indexed by UTC bar-open time, last row = the bar that just CLOSED}.
        Runners pass dense frames (a row for every bar, missing bars NaN). Return the Signals to place now."""
        raise NotImplementedError

    # -- optional fast path ------------------------------------------------------------
    def scan(self, data: Dict[str, pd.DataFrame], start=None, end=None) -> List[tuple]:
        """[(bar_time, Signal)] for every bar in [start, end) — must equal calling signals() at each bar.
        The default literally does that (slow); strategies override it with a vectorised version."""
        times = sorted(set().union(*[d.index for d in data.values()])) if data else []
        out = []
        for t in times:
            if (start is not None and t < start) or (end is not None and t >= end):
                continue
            win = {s: d.loc[:t].iloc[-self.lookback - 1:] for s, d in data.items() if len(d.loc[:t]) and d.index[-1] >= t}
            win = {s: d for s, d in win.items() if d.index[-1] == t}
            for sg in self.signals(win, t):
                out.append((t, sg))
        return out

    def first_ts(self, sym, df):
        m = self.meta.get(sym)
        if m and m.get("first_ts") is not None:
            return pd.Timestamp(m["first_ts"])
        return None


# ---------------------------------------------------------------- order / position models
@dc.dataclass
class Order:
    id: str
    strategy: str
    sym: str
    side: str                         # long | short (the position side this order opens)
    kind: str                         # limit | market
    qty: float
    price: Optional[float]
    placed_at: str                    # ISO time of the signal bar close
    expires_at: Optional[str]         # ISO time after which an unfilled limit is cancelled
    hold_bars: int
    stop_price: Optional[float] = None
    target_price: Optional[float] = None
    leverage: int = 1
    margin_usdt: float = 0.0
    signal_bar: Optional[str] = None  # ISO bar-open time of the signal bar
    exchange_ids: dict = dc.field(default_factory=dict)
    status: str = "pending"           # pending | filled | expired | cancelled | rejected
    note: str = ""


@dc.dataclass
class Position:
    id: str
    strategy: str
    sym: str
    side: str
    qty: float
    entry: float
    entry_time: str                   # ISO
    exit_due: str                     # ISO time (bar close) at which the rule exits
    stop_price: Optional[float] = None
    target_price: Optional[float] = None
    leverage: int = 1
    margin_usdt: float = 0.0
    entry_kind: str = "market"
    exchange_ids: dict = dc.field(default_factory=dict)
    status: str = "open"              # open | closed
    exit: Optional[float] = None
    exit_time: Optional[str] = None
    exit_reason: str = ""
    pnl_usdt: Optional[float] = None
    note: str = ""


def liquidation_distance(leverage: float, mm: float = 0.005) -> float:
    """Fractional adverse move that liquidates an isolated position (same convention as bt.account)."""
    return 1.0 / float(leverage) - mm


def stop_inside_liquidation(stop_pct: float, leverage: float, buffer: float = 0.005) -> bool:
    """PROTOCOL.md: a stop must sit inside the liquidation distance: stop distance < 1/leverage - 0.5%."""
    return stop_pct is not None and 0 < stop_pct < 1.0 / float(leverage) - buffer


# ---------------------------------------------------------------- data helpers
def dense(df: pd.DataFrame, tf: str = "1h") -> pd.DataFrame:
    """A row for every bar between the first and last bar; missing bars (and volume-0 bars) are NaN."""
    if df is None or len(df) == 0:
        return df
    step = tf_delta(tf)
    full = pd.date_range(df.index[0], df.index[-1], freq=step)
    if len(full) != len(df):
        df = df[~df.index.duplicated(keep="last")].reindex(full)
    if "v" in df:
        bad = ~(df["v"] > 0)
        if bad.any():
            df = df.copy()
            df.loc[bad, [c for c in ("o", "h", "l", "c", "v", "qv") if c in df]] = np.nan
    return df


def bar_time(now, tf="1h") -> pd.Timestamp:
    """The open time of the bar that just closed at `now`. Accepts either a bar-open time (the runners pass the last
    closed bar's open time) or a wall-clock time (e.g. omega/live_api passes Timestamp.now())."""
    now = pd.Timestamp(now)
    if now.tzinfo is None:
        now = now.tz_localize("UTC")
    step = tf_delta(tf)
    fl = now.floor(step)
    return fl if fl == now else fl - step


def is_current(df, now, tf="1h") -> bool:
    """True when df's last row is the bar that closed at `now` (see bar_time)."""
    if df is None or len(df) == 0:
        return False
    last = df.index[-1]
    return last == pd.Timestamp(now) or last == bar_time(now, tf)
