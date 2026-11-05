import os
import pytest
from edges.bots import sizing
from edges.bots.state import State

INFO = dict(step=0.001, minQty=0.001, minNotional=5.0, tick=0.01)


def test_quantity_floors_to_step():
    assert sizing.quantity(6, 1, 300.0, INFO) == 0.02             # 6/300 = 0.02
    assert sizing.quantity(10, 1, 3000.0, INFO) == 0.003          # 10/3000 = 0.00333 -> 0.003
    assert sizing.quantity(10, 3, 3000.0, INFO) == 0.01


def test_quantity_refuses_below_min_notional():
    with pytest.raises(sizing.SizingError, match="below the exchange minimum"):
        sizing.quantity(5, 1, 3000.0, dict(INFO, minNotional=20.0))   # ETH min notional 20
    with pytest.raises(sizing.SizingError):
        sizing.quantity(5, 1, 90000.0, dict(INFO, minNotional=100.0))  # BTC min notional 100


def test_quantity_rounds_up_to_minimum_within_10pct():
    assert sizing.quantity(5, 1, 98.5, dict(INFO, step=0.001)) == 0.051           # 0.050 = 4.93 USDT < 5 -> 0.051
    with pytest.raises(sizing.SizingError):
        sizing.quantity(5, 1, 98.5, dict(INFO, step=1.0))                          # 1 contract = 98.5 USDT: refused


def test_price_rounding_is_safe_side():
    assert sizing.round_price(100.019, 0.01, "long", "entry") == 100.01    # never pay more
    assert sizing.round_price(90.011, 0.01, "long", "stop") == 90.02       # stop a hair closer, never toward liquidation
    assert sizing.round_price(100.011, 0.01, "short", "entry") == 100.02
    assert sizing.round_price(110.019, 0.01, "short", "stop") == 110.01
    assert sizing.floor_to(0.123456, 0.0001) == 0.1234


def test_state_persists_and_reloads(bots_home):
    s = State()
    s.orders["a"] = dict(id="a", strategy="panic_h1", sym="ETHUSDT")
    s.positions["b"] = dict(id="b", strategy="climax_a", sym="SOLUSDT")
    s.d["closed"].append(dict(exit_time="2026-11-05T10:00:00+00:00", pnl_usdt=-1.5))
    s.mark_seen("k1")
    s.save()
    assert not os.path.exists(s.file + ".tmp")
    t = State()
    assert t.busy("panic_h1", "ETHUSDT") and not t.busy("panic_h1", "SOLUSDT")
    assert t.open_symbols() == {"ETHUSDT", "SOLUSDT"} and t.open_count() == 2
    assert t.seen("k1") and t.day_pnl("2026-11-05") == -1.5
