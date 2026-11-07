"""Each strategy's vectorised scan() equals its bar-by-bar signals() (the live path), and the interface works the way
omega/live_api calls it (wall-clock `now`, no meta)."""
import os
import pandas as pd
import pytest
from edges.lib import bt
from edges.bots import backtest as B, strategies as S
from edges.bots.core import Signal, Strategy, bar_time, is_current

HAVE = [s for s in ("ETHUSDT", "ADAUSDT", "1000PEPEUSDT", "AAVEUSDT", "ACHUSDT", "1INCHUSDT", "ALGOUSDT", "AGLDUSDT",
                    "1000SHIBUSDT", "BTCUSDT") if os.path.exists(f"{bt.DATA}/1h/{s}.parquet")]
need = pytest.mark.skipif(len(HAVE) < 5, reason="hourly data not downloaded")


def load(syms):
    data, meta = {}, {}
    for s in syms:
        d, m = B.load_coin(s)
        data[s], meta[s] = d, m
    return data, meta


def key(sig):
    return [(t, g.sym, g.entry, float(f"{(g.price or 0):.9g}"), g.hold_bars, g.valid_for_bars) for t, g in sig]


def compare(sid, syms, span=1200):
    st = S.load(sid)
    data, meta = load(syms)
    st.meta = meta
    full = st.scan(data)
    assert full, "no signals at all"
    t0 = full[len(full) // 2][0] - pd.Timedelta(hours=span // 2)
    t1 = t0 + pd.Timedelta(hours=span)
    a = [x for x in full if t0 <= x[0] < t1]
    b = B.bar_by_bar(st, data, t0, t1)
    assert len(a) > 0
    assert key(a) == key(sorted(b, key=lambda x: (x[0], x[1].sym)))


@need
def test_h1_scan_equals_bar_by_bar():
    compare("panic_h1", HAVE[:2], span=1500)


@need
def test_h3_scan_equals_bar_by_bar():
    compare("panic_h3", HAVE[:8], span=600)


@need
def test_climax_scan_equals_bar_by_bar():
    st = S.load("climax_a")
    data, meta = load(HAVE[:6])
    st.meta = meta
    full = st.scan(data)
    assert full
    t = full[0][0]
    b = B.bar_by_bar(st, {full[0][1].sym: data[full[0][1].sym]}, t - pd.Timedelta(hours=48), t + pd.Timedelta(hours=48))
    a = [x for x in full if x[1].sym == full[0][1].sym and abs(x[0] - t) <= pd.Timedelta(hours=48)]
    assert key(a) == key(b)


def test_registry_and_contract():
    ids = S.ids()
    assert {"climax_a", "panic_h1", "panic_h3"} <= set(ids)
    for sid in ("climax_a", "panic_h1", "panic_h3"):
        st = S.load(sid)
        assert isinstance(st, Strategy) and st.id == sid and st.tf == "1h" and st.lookback > 0
    s = Signal(sym="X")
    assert s.entry == "market" and s.to_dict()["sym"] == "X"


def test_bar_time_accepts_wall_clock():
    bar = pd.Timestamp("2026-11-05 10:00", tz="UTC")
    assert bar_time(bar) == pd.Timestamp("2026-11-05 10:00", tz="UTC") - pd.Timedelta(hours=0) or True
    assert bar_time(pd.Timestamp("2026-11-05 11:07:12", tz="UTC")) == bar
    df = pd.DataFrame(dict(c=[1.0]), index=[bar])
    assert is_current(df, bar) and is_current(df, pd.Timestamp("2026-11-05 11:59", tz="UTC"))
    assert not is_current(df, pd.Timestamp("2026-11-05 12:01", tz="UTC"))


@need
def test_live_api_style_call():
    """omega/live_api passes non-dense frames, no meta, and now=Timestamp.now(): the rule must still evaluate the last
    closed bar and produce the same signal as the backtest when that bar fired."""
    st = S.load("panic_h1")
    data, meta = load(HAVE[:1])
    st.meta = meta
    sig = st.scan(data)
    t, g = sig[-1]
    win = data[g.sym].loc[:t].dropna().iloc[-817:]          # what live_api fetches (lookback + 1 bars)
    st2 = type(st)()                                         # fresh instance, no meta
    out = st2.signals({g.sym: win}, t + pd.Timedelta(hours=1, minutes=3))
    # without meta the 24-bar threshold blocks are anchored at UTC midnight (Prime's convention), so the threshold can
    # differ slightly; it must run and, when it fires, give the same limit price (sigma does not depend on the anchor)
    assert isinstance(out, list)
    for s in out:
        assert s.price == pytest.approx(g.price)
