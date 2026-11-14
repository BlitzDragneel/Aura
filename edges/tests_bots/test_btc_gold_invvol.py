"""PARITY of btc_gold_invvol (E94 H6 / E97, grade B, paper) with the research code.

Research weights: edges/research_btc/e94_holding.py -> monthly(inverse-vol weight) on the research's daily frames
(BTC: lib1.load_tf 1h -> UTC days; gold: PAXG 1h from /home/user/data/metals). The bot is fed the same hourly data, cut
to its lookback window at every month's signal bar (the 23:00 UTC bar of day 1), and must give the same weight, and a
hold that ends at the next month's signal bar (research: weight applied from day 2 through day 1 of the next month)."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

from edges.lib import bt
from edges.bots import strategies as S

RB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "research_btc"))
HAVE = os.path.exists(f"{bt.DATA}/1h/BTCUSDT.parquet") and os.path.exists(f"{bt.DATA}/metals/PAXG_1h.parquet")
need = pytest.mark.skipif(not HAVE, reason="BTC 1h / PAXG 1h data not downloaded")


def research_weights():
    if RB not in sys.path:
        sys.path.insert(0, RB)
    import libbtc
    from e93_btc_gold import paxg_daily
    from e94_holding import monthly
    d = libbtc.bars("1d")
    pg = paxg_daily().reindex(d.index).ffill(limit=3)
    lB = np.log(d.c).diff(); lG = np.log(pg).diff()
    v60 = lB.rolling(60, min_periods=40).std() * np.sqrt(365)
    vg60 = lG.rolling(60, min_periods=40).std() * np.sqrt(365)
    ib = ((1 / v60) / (1 / v60 + 1 / vg60)).ffill().fillna(0.5)
    return monthly(ib)


def frames():
    if RB not in sys.path:
        sys.path.insert(0, RB)
    import libbtc
    btc = libbtc.lib1.load_tf("BTCUSDT", "1h")[["o", "h", "l", "c", "v", "qv"]]
    g = pd.read_parquet(f"{bt.DATA}/metals/PAXG_1h.parquet")
    g.index = pd.DatetimeIndex(g.index).tz_convert("UTC") if g.index.tz is not None else pd.DatetimeIndex(g.index).tz_localize("UTC")
    return btc, g


@need
def test_weights_and_timing_match_research():
    st = S.load("btc_gold_invvol")
    rw = research_weights()
    btc, gold = frames()
    months = pd.date_range("2021-01-01", "2026-10-01", freq="MS", tz="UTC")
    checked = 0
    for m in months:
        bar = m + pd.Timedelta(hours=23)
        if bar not in btc.index or pd.isna(btc.c.get(bar)):
            continue
        win = {"BTCUSDT": btc[btc.index <= bar].iloc[-st.lookback - 1:],
               "PAXGUSDT": gold[gold.index <= bar].iloc[-st.lookback - 1:]}
        sigs = st.signals(win, bar)
        assert [s.sym for s in sigs] == ["BTCUSDT", "PAXGUSDT"]
        w = float(sigs[0].note.split("w=")[1].split()[0])
        assert abs(w - rw.loc[m]) < 1e-8, (m, w, rw.loc[m])
        assert abs(float(sigs[1].note.split("w=")[1].split()[0]) - (1 - rw.loc[m])) < 1e-8
        nxt = m + pd.offsets.MonthBegin(1) + pd.Timedelta(hours=23)
        assert bar + pd.Timedelta(hours=sigs[0].hold_bars) == nxt
        assert all(s.entry == "market" and s.side == "long" for s in sigs)
        checked += 1
    assert checked >= 60


def test_no_signal_off_schedule():
    st = S.load("btc_gold_invvol")
    idx = pd.date_range("2025-03-01", "2025-03-02 22:00", freq="h", tz="UTC")
    df = pd.DataFrame({"o": 1.0, "h": 1.0, "l": 1.0, "c": 1.0, "v": 1.0, "qv": 1.0}, index=idx)
    assert st.signals({"BTCUSDT": df, "PAXGUSDT": df}, idx[-1]) == []
    assert st.signals({"BTCUSDT": df.iloc[:12], "PAXGUSDT": df.iloc[:12]}, idx[11]) == []
