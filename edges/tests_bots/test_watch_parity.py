"""PARITY of the watch-list rules with the research code that judged them.

  panic5m_watch    vs edges/research1/run_panic.py E37 (lib1.load_tf / sigma / day_thresholds / sim_limit), L288 k4 W3 H288
  panic15m_watch   vs run_panic.py E38, L96 k2 W12 H96 (15m bars from 5m: lib1.load_tf vs core.resample)
  breadth15m_watch vs edges/research1/run_breadth.py E40, L96 b20 q5 H96 (30 coins, union index)
  upscout_watch    vs edges/scouts: model.features on the research loader's hourly frame + the saved LightGBM model,
                   flag = p_up_move >= meta.json thresholds.up_move

The bots' side runs the way the backtester/runner do: the bot's own dense frames (core.dense, core.resample) cut to a
window of a few months plus the rule's lookback, strategy.scan() (proven equal to signals() bar by bar below), and
edges/bots/backtest.simulate() for fills/exits. Trades are compared one by one: signal bar, fill bar, exit bar, entry
price, gross return."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

from edges.lib import bt
from edges.bots import backtest as B, strategies as S
from edges.bots.core import dense, resample, tf_delta

R1 = os.path.join(os.path.dirname(__file__), "..", "research1")
if R1 not in sys.path:
    sys.path.insert(0, os.path.abspath(R1))

HAVE5 = os.path.isdir(f"{bt.DATA}/5m") and len([f for f in os.listdir(f"{bt.DATA}/5m") if f.endswith(".parquet")]) >= 30
need5 = pytest.mark.skipif(not HAVE5, reason="the 30 research 5m files are not in $OMEGA_DATA/5m")
COINS = ["BTCUSDT", "SOLUSDT", "1000PEPEUSDT", "WIFUSDT", "INJUSDT"]     # incl. coins whose blocks are not at midnight
W0, W1 = pd.Timestamp("2025-03-01", tz="UTC"), pd.Timestamp("2025-07-01", tz="UTC")


def L1():
    import lib1
    return lib1


def bot_frame(sym, tf, lookback):
    """The bot's frame: parquet -> dense 5m (core.dense) -> core.resample for 15m, cut to [W0 - lookback, W1 + 3 days]."""
    d = bt.load(sym, "5m")
    d = d[~d.index.duplicated(keep="last")].sort_index()
    d = dense(d[["o", "h", "l", "c", "v", "qv"]].astype(float), "5m")
    a = (W0 - (lookback + 10) * tf_delta(tf)).floor("D")
    d = d[(d.index >= a) & (d.index < W1 + pd.Timedelta(days=3))]
    return resample(d, tf, "5m") if tf != "5m" else d


def bot_trades(sid, syms, frames):
    st = S.load(sid)
    sigs = st.scan(frames, W0, W1)
    out = []
    for s in syms:
        lst = [(t, g) for t, g in sigs if g.sym == s]
        for r in B.simulate(s, frames[s], lst, st.tf, gap_policy="next", funding=False):
            if r["status"] == "filled":
                out.append((s, r["signal_time"], r["entry_time"], r["exit_bar"], round(r["entry"], 10), round(r["gross"], 10)))
    return sorted(out), sigs


def same(got, want, rtol=1e-9):
    """Identical trades: same coin and bars; entry price and gross equal up to float noise (rolling std summed over a
    shorter frame differs in the last digits)."""
    assert [g[:4] for g in got] == [w[:4] for w in want]
    for g, w in zip(got, want):
        assert np.isclose(g[4], w[4], rtol=rtol, atol=0) and np.isclose(g[5], w[5], rtol=1e-7, atol=1e-12), (g, w)
    return True


def ref_rows(sym, d, rows):
    return [(sym, d.index[int(t)], d.index[int(f)], d.index[int(x)], round(float(e), 10), round(float(xp / e - 1), 10))
            for t, f, x, e, xp, _ in rows]


def research_panic(tf, L, k, W, H, look, step, syms):
    lib = L1()
    want = []
    for s in syms:
        d = lib.load_tf(s, tf)
        c, l = d.c.values, d.l.values
        sg = lib.sigma(c)
        r = np.log(d.c / d.c.shift(L)).values
        th = lib.day_thresholds(r, look, step)
        mask = np.nan_to_num(r <= th, nan=0).astype(np.bool_) & np.isfinite(th)
        lo, hi = int(np.searchsorted(d.index, W0)), int(np.searchsorted(d.index, W1))
        want += ref_rows(s, d, lib.sim_limit(c, l, sg, mask, float(k), W, H, lo, hi))
    return sorted(want)


@need5
def test_panic5m_parity():
    st = S.load("panic5m_watch")
    assert (st.L, st.K, st.W, st.H, st.LOOK, st.STEP, st.tf) == (288, 4.0, 3, 288, 8640, 288, "5m")
    frames = {s: bot_frame(s, "5m", st.lookback) for s in COINS}
    got, _ = bot_trades("panic5m_watch", COINS, frames)
    want = research_panic("5m", 288, 4, 3, 288, 8640, 288, COINS)
    assert len(want) >= 30, len(want)
    assert same(got, want)


@need5
def test_panic15m_parity():
    st = S.load("panic15m_watch")
    assert (st.L, st.K, st.W, st.H, st.LOOK, st.STEP, st.tf, st.source_tf) == (96, 2.0, 12, 96, 2880, 96, "15m", "5m")
    frames = {s: bot_frame(s, "15m", st.lookback) for s in COINS}
    got, _ = bot_trades("panic15m_watch", COINS, frames)
    want = research_panic("15m", 96, 2, 12, 96, 2880, 96, COINS)
    assert len(want) >= 30, len(want)
    assert same(got, want)


@need5
def test_resample_matches_research_loader():
    lib = L1()
    for s in ("SOLUSDT", "WIFUSDT"):
        ref = lib.load_tf(s, "15m")
        mine = bot_frame(s, "15m", 4000)
        ref = ref.loc[mine.index[0]:mine.index[-1]]
        assert (mine.index == ref.index).all() and len(mine) == len(ref)
        assert np.allclose(mine[["o", "h", "l", "c"]].values, ref[["o", "h", "l", "c"]].values, equal_nan=True, rtol=0, atol=0)
        assert np.allclose(mine.qv.values, ref.qv.values, equal_nan=True)


@need5
def test_breadth15m_parity():
    """E40 research code (run_breadth.main's mask construction) on all 30 coins, then lib1.sim_taker per coin."""
    lib = L1()
    st = S.load("breadth15m_watch")
    syms = lib.coins5()
    assert sorted(st.universe) == syms
    D = {s: lib.load_tf(s, "15m") for s in syms}
    idx = D["BTCUSDT"].index
    for s in syms:
        idx = idx.union(D[s].index)
    for s in syms:
        D[s] = D[s].reindex(idx)
    L, b, q, H, LOOK, STEP = 96, 0.2, 5, 96, 2880, 96
    below10, okc, m5 = [], [], {}
    for s in syms:
        r = np.log(D[s].c / D[s].c.shift(L)).values
        t10 = lib.day_thresholds(r, LOOK, STEP, 10)
        t5 = lib.day_thresholds(r, LOOK, STEP, 5)
        below10.append(np.nan_to_num(r <= t10, nan=0).astype(bool) & np.isfinite(t10))
        okc.append(np.isfinite(t10) & np.isfinite(r))
        m5[s] = np.nan_to_num(r <= t5, nan=0).astype(bool) & np.isfinite(t5)
    cnt, tot = np.sum(below10, axis=0), np.sum(okc, axis=0)
    breadth = np.where(tot >= 10, cnt / np.maximum(tot, 1), 0)
    lo, hi = int(np.searchsorted(idx, W0)), int(np.searchsorted(idx, W1))
    want = []
    for s in syms:
        d = D[s]
        rows = lib.sim_taker(d.o.values, d.c.values, d.l.values, d.h.values, m5[s] & (breadth >= b), H, 1, lo, hi)
        want += ref_rows(s, d, rows)
    frames = {s: bot_frame(s, "15m", st.lookback) for s in syms}
    got, _ = bot_trades("breadth15m_watch", syms, frames)
    assert len(want) >= 20, len(want)
    assert same(got, sorted(want))


# ---------------------------------------------------------------- UpScout
UP_COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "1000PEPEUSDT", "LINKUSDT"]
U0, U1 = pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2025-07-01", tz="UTC")


def test_upscout_parity():
    pytest.importorskip("lightgbm")
    from edges.scouts.model import features
    st = S.load("upscout_watch")
    syms = [s for s in UP_COINS if os.path.exists(f"{bt.DATA}/1h/{s}.parquet")]
    if len(syms) < 4:
        pytest.skip("hourly data missing")
    btc = bt.load("BTCUSDT")
    want = set()
    for s in syms:                                    # research: features on bt.load's frame (as backtest_scouts.py)
        d = bt.load(s)
        F = features(d, btc)
        p = st.booster().predict(F[st.feature_names])
        t = F.index[(p >= st.threshold) & (F.index >= U0) & (F.index < U1)]
        want |= {(s, x) for x in t}
    data = {}
    for s in syms:                                    # bots: dense frames cut to the window + lookback
        d, _ = B.load_coin(s)
        data[s] = d[(d.index >= U0 - pd.Timedelta(hours=st.lookback)) & (d.index < U1)]
    sigs = st.scan(data, U0, U1)
    got = {(g.sym, t) for t, g in sigs}
    assert len(want) >= 20, len(want)
    assert got == want
    assert all(g.entry == "market" and g.hold_bars == 24 for _, g in sigs)


# ---------------------------------------------------------------- scan() == signals() bar by bar (the live path)
@need5
@pytest.mark.parametrize("sid,tf,span", [("panic5m_watch", "5m", 600), ("panic15m_watch", "15m", 400),
                                         ("breadth15m_watch", "15m", 300)])
def test_watch_scan_equals_bar_by_bar(sid, tf, span):
    st = S.load(sid)
    syms = S.load("breadth15m_watch").universe if st.needs_all else COINS[:3]
    frames = {s: bot_frame(s, tf, st.lookback) for s in syms}
    full = st.scan(frames, W0, W1)
    assert full
    t0 = full[len(full) // 2][0] - span // 2 * tf_delta(tf)
    t1 = t0 + span * tf_delta(tf)
    a = [(t, g.sym, g.entry, g.price and round(g.price, 6), g.hold_bars, g.valid_for_bars) for t, g in full if t0 <= t < t1]
    b = sorted(B.bar_by_bar(st, frames, t0, t1), key=lambda x: (x[0], x[1].sym))
    assert a and a == [(t, g.sym, g.entry, g.price and round(g.price, 6), g.hold_bars, g.valid_for_bars) for t, g in b]


def test_upscout_scan_equals_bar_by_bar():
    pytest.importorskip("lightgbm")
    st = S.load("upscout_watch")
    syms = [s for s in UP_COINS if os.path.exists(f"{bt.DATA}/1h/{s}.parquet")]
    data = {s: B.load_coin(s)[0] for s in syms}
    data = {s: d[(d.index >= U0 - pd.Timedelta(hours=st.lookback)) & (d.index < U1)] for s, d in data.items()}
    full = st.scan(data, U0, U1)
    assert full
    t0 = full[len(full) // 2][0] - pd.Timedelta(hours=60)
    t1 = t0 + pd.Timedelta(hours=120)
    a = [(t, g.sym) for t, g in full if t0 <= t < t1]
    b = [(t, g.sym) for t, g in sorted(B.bar_by_bar(st, data, t0, t1), key=lambda x: (x[0], x[1].sym))]
    assert a and a == b
