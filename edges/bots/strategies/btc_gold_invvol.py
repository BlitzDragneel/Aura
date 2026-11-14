"""BTC holding rule (E94/E97, grade B, paper): inverse-volatility BTC/gold allocation, set once a month.

Research: edges/research_btc/e94_holding.py (H6) and e97_alloc_2014.py; results edges/results/E94_result.json,
E97_result.json, E97_leverage.json. Rule: at the close of the first UTC day of each month, BTC weight
w = (1/vol60_BTC) / (1/vol60_BTC + 1/vol60_GOLD), gold weight 1 - w (vol60 = std of the last 60 daily log returns of UTC
daily closes; PAXG as the gold leg), held until the close of the first day of the next month. Long only, 1x notional.

Contract note: the Signal has no size field, so each leg's target weight is in `note` ("w=0.1234") and in
`self.last_weights`. The current runner sizes every order the same, so this rule is PAPER ONLY until a weight-aware
sizer exists. It is a drawdown tool: lower return than holding BTC in bull years (see FINDINGS).
"""
import numpy as np
import pandas as pd

from edges.bots.core import Signal, Strategy

GOLD = "PAXGUSDT"


def daily_close(df):
    """UTC daily closes exactly as the research: last close of the day, NaN if fewer than 20 hourly closes."""
    c = df["c"]
    g = c.resample("1D", label="left", closed="left")
    out = g.last()
    return out.where(g.count() >= 20)


def btc_weight(btc_1h, gold_1h):
    """Weight series (index = UTC days) as e94_holding.build H6 before the monthly hold: ffilled, default 0.5."""
    b = daily_close(btc_1h)
    pg = daily_close(gold_1h).reindex(b.index).ffill(limit=3)
    lB = np.log(b).diff(); lG = np.log(pg).diff()
    v60 = lB.rolling(60, min_periods=40).std() * np.sqrt(365)
    vg60 = lG.rolling(60, min_periods=40).std() * np.sqrt(365)
    ib = (1 / v60) / (1 / v60 + 1 / vg60)
    return ib.ffill().fillna(0.5)


class BtcGoldInvVol(Strategy):
    id = "btc_gold_invvol"
    tf = "1h"
    universe = ["BTCUSDT", GOLD]
    lookback = 24 * 120
    needs_all = True

    def __init__(self):
        super().__init__()
        self.last_weights = {}

    def signals(self, bars, now):
        now = pd.Timestamp(now)
        if now.tzinfo is None:
            now = now.tz_localize("UTC")
        bar = now.floor("h")
        # act at the close of the first UTC day of the month: the 23:00 bar of day 1 has just closed
        if not (bar.day == 1 and bar.hour == 23):
            return []
        btc, gold = bars.get("BTCUSDT"), bars.get(GOLD)
        if btc is None or gold is None or len(btc) == 0 or btc.index[-1] != bar:
            return []
        btc = btc[btc.index <= bar]; gold = gold[gold.index <= bar]
        w = float(btc_weight(btc, gold).iloc[-1])
        day1 = bar.normalize()
        nxt = (day1 + pd.offsets.MonthBegin(1)) + pd.Timedelta(hours=23)
        hold = int((nxt - bar) / pd.Timedelta("1h"))
        self.last_weights = {"BTCUSDT": w, GOLD: 1 - w}
        return [Signal(sym="BTCUSDT", side="long", entry="market", hold_bars=hold, note=f"w={w:.10f} BTC leg"),
                Signal(sym=GOLD, side="long", entry="market", hold_bars=hold, note=f"w={1 - w:.10f} gold leg")]


STRATEGY = BtcGoldInvVol()
