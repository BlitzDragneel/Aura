"""The execution model on synthetic candles: through-fills, expiry, market next-open, exits, stops with gaps,
liquidation in the account, costs."""
import numpy as np
import pandas as pd
import pytest
from edges.bots import backtest as B
from edges.bots.core import Signal
from edges.lib import bt


def frame(n=80, p=100.0):
    idx = pd.date_range("2024-03-01", periods=n, freq="h", tz="UTC")
    c = np.full(n, p)
    return pd.DataFrame(dict(o=c, h=c * 1.01, l=c * 0.99, c=c, v=1.0, qv=1e9 / 24), index=idx)


def run(df, sig, at=10, **kw):
    return B.simulate("X", df, [(df.index[at], sig)], funding=False, **kw)


def test_limit_needs_trade_through():
    df = frame()
    df.loc[df.index[12], "l"] = 98.0
    s = Signal(sym="X", entry="limit", price=98.0, valid_for_bars=3, hold_bars=24)
    (r,) = run(df, s)
    assert r["status"] == "missed"                   # touching 98.0 is not a fill
    df.loc[df.index[12], "l"] = 97.9
    df.loc[df.index[12 + 24], "c"] = 101.0
    (r,) = run(df, s)
    assert r["status"] == "filled" and r["entry"] == 98.0 and r["entry_time"] == df.index[12]
    assert r["exit_bar"] == df.index[36] and r["exit"] == 101.0
    assert r["cost"] == pytest.approx(bt.round_trip_cost(1e9, entry="maker", exit="taker"))
    assert r["mae"] == pytest.approx(97.9 / 98 - 1)


def test_limit_window_is_exactly_valid_bars():
    df = frame()
    df.loc[df.index[14], "l"] = 90.0                  # bar t+4: outside a 3-bar window
    (r,) = run(df, Signal(sym="X", entry="limit", price=95.0, valid_for_bars=3, hold_bars=5))
    assert r["status"] == "missed"


def test_market_enters_next_open_exits_signal_plus_hold():
    df = frame()
    df.loc[df.index[11], "o"] = 100.5
    df.loc[df.index[22], "c"] = 103.0
    (r,) = run(df, Signal(sym="X", entry="market", hold_bars=12))
    assert r["entry"] == 100.5 and r["exit_bar"] == df.index[22] and r["gross"] == pytest.approx(103 / 100.5 - 1)


def test_busy_coin_ignores_new_signals():
    df = frame()
    s = Signal(sym="X", entry="market", hold_bars=12)
    out = B.simulate("X", df, [(df.index[10], s), (df.index[15], s), (df.index[22], s)], funding=False)
    assert [r["signal_time"] for r in out] == [df.index[10], df.index[22]]   # 15 ignored; 22 allowed (exit bar)


def test_stop_and_gap_through():
    df = frame()
    df.loc[df.index[13], "l"] = 85.0
    (r,) = run(df, Signal(sym="X", entry="market", hold_bars=12), stop_pct=0.10)
    assert r["reason"] == "stop" and r["exit"] == pytest.approx(90.0)
    df.loc[df.index[13], "o"] = 80.0
    (r,) = run(df, Signal(sym="X", entry="market", hold_bars=12), stop_pct=0.10)
    assert r["exit"] == 80.0                          # gapped through: filled at the open, worse than the stop


def test_gap_policy_and_delisting():
    df = frame()
    df.loc[df.index[22], "c"] = np.nan
    df.loc[df.index[23], "c"] = 104.0
    (r,) = run(df, Signal(sym="X", entry="market", hold_bars=12))
    assert r["reason"] == "after_gap" and r["exit"] == 104.0
    assert run(df, Signal(sym="X", entry="market", hold_bars=12), gap_policy="skip") == []
    d2 = frame(30)
    out = run(d2, Signal(sym="X", entry="market", hold_bars=40), data_end=d2.index[-1] + pd.Timedelta(days=10),
              last_valid=d2.index[-1])
    assert out[0]["reason"] == "delisted" and out[0]["exit"] == pytest.approx(95.0)


def test_seat_account_liquidates_from_mae():
    t = pd.date_range("2024-01-01", periods=4, freq="D", tz="UTC")
    tr = pd.DataFrame(dict(signal_time=t, time=t, exit_time=t + pd.Timedelta(hours=12), status="filled",
                           net=[0.01, 0.01, 0.01, 0.01], mae=[-0.01, -0.06, -0.01, -0.30]))
    a1 = B.seat_account(tr, leverage=1)
    a20 = B.seat_account(tr, leverage=20)
    a3 = B.seat_account(tr, leverage=3)
    assert a1["liquidations"] == 0 and a3["liquidations"] == 0
    assert a20["liquidations"] == 2 and a20["final"] < 100
    table = [dict(leverage=L, liquidations=B.seat_account(tr, leverage=L)["liquidations"],
                  max_dd=B.seat_account(tr, leverage=L)["max_dd"]) for L in (1, 2, 3, 5, 10, 20)]
    assert B.max_safe_leverage(table) == 3            # 5x: -30% mae passes the -19.5% line
