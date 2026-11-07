"""Fixes for audits/security/BOTS_FINDINGS.md: naked positions, one kill switch with the Bridge, limits from the
exchange, per-trade risk cap, MT5 through the Bridge guard, IP-restricted live key, clock drift, kill confirmation."""
import json, os
import pandas as pd
import pytest
from edges.bots import live, guard as G, config as C
from edges.bots.exchange_binance import BinanceFutures
from edges.bots.exchange_mt5 import MT5Broker
from edges.tests_bots import fakes as F
from edges.tests_bots.test_runner import MARKET, LIMIT, _testnet, logs, setup


def test_stop_fails_and_undo_fails_kill_and_keep_unprotected(monkeypatch, bots_home):
    fb = F.FakeBinance()
    fb.algo_fail, fb.close_fail = True, True
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET, fb=fb)
    r.cycle()
    assert G.killed()
    (p,) = r.state.positions.values()                   # NOT forgotten
    assert p["status"] == "UNPROTECTED" and p["sym"] == "ETHUSDT"
    assert any(x["event"] == "UNPROTECTED" for x in logs(bots_home))
    fb.close_fail = False                                # next cycle: the kill switch closes it
    clock.t += pd.Timedelta(minutes=1)
    r.cycle(full=False)
    assert fb.pos["ETHUSDT"] == 0 and not r.state.positions
    G.set_kill(False)


def test_stop_fails_undo_works_nothing_left(monkeypatch, bots_home):
    fb = F.FakeBinance()
    fb.algo_fail = True
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET, fb=fb)
    r.cycle()
    assert fb.pos.get("ETHUSDT", 0) == 0 and not r.state.positions and not G.killed()


def test_legacy_stop_path_falls_back_to_algo_on_4120(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET)
    r.broker.api.cfg["stop_via_algo"] = False
    r.cycle()
    assert [q for q in fb.sent("/fapi/v1/order") if q["type"] == "STOP_MARKET"]      # tried the old path: -4120
    (stop,) = fb.sent("/fapi/v1/algoOrder")                                          # then the Algo Order API
    assert stop["closePosition"] == "true" and len(r.state.positions) == 1


def test_entry_timeout_is_checked_on_the_exchange(monkeypatch, bots_home):
    fb = F.FakeBinance()
    fb.timeout_once = True
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET, fb=fb)
    r.cycle()
    assert fb.pos["ETHUSDT"] == 0.05
    (p,) = r.state.positions.values()                    # recorded although the reply never came
    assert p["exchange_ids"].get("stop")
    assert [q for (m, path, q) in fb.calls if path == "/fapi/v1/order" and m == "GET" and "origClientOrderId" in q]


def test_bridge_kill_file_stops_the_bots(monkeypatch, bots_home):
    os.makedirs(bots_home / "bridge", exist_ok=True)
    open(bots_home / "bridge" / "KILL", "w").write("Bridge kill\n")
    assert G.killed()
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET)
    assert r.cycle() == dict(killed=True) and not fb.sent("/fapi/v1/order")
    G.set_kill(False)
    assert not G.killed() and not os.path.exists(bots_home / "bridge" / "KILL")


def test_bot_kill_writes_the_bridge_kill_file(bots_home):
    G.set_kill(True)
    assert os.path.exists(bots_home / "KILL") and os.path.exists(bots_home / "bridge" / "KILL")
    G.set_kill(False)


def test_limits_counted_from_the_exchange(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET)
    fb.pos["ETHUSDT"] = 0.3                              # a manual / Bridge position in the same coin
    r.cycle()
    assert not [q for q in fb.sent("/fapi/v1/order") if q["type"] == "MARKET"]
    (ref,) = [x for x in logs(bots_home) if x["event"] == "refused"]
    assert any("one per coin" in w for w in ref["reasons"])


def test_open_count_includes_exchange_positions_and_resting_entries(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET)
    fb.pos.update(BTCUSDT=0.002, SOLUSDT=1.0)
    fb.orders[1] = dict(orderId=1, symbol="XRPUSDT", side="BUY", type="LIMIT", status="NEW", reduceOnly="false")
    r.cycle()
    (ref,) = [x for x in logs(bots_home) if x["event"] == "refused"]
    assert any("3 positions/orders already open" in w for w in ref["reasons"])


def test_per_trade_risk_cap():
    cfg = C.load()
    rule = dict(id="x", status="testnet", max_leverage=3)
    book = dict(open_count=0, open_symbols=set(), day_pnl_usdt=0)
    ok = dict(sym="A", leverage=1, margin_usdt=5, notional=5.0, stop_pct=0.5)
    assert G.order_refusals(cfg, "testnet", rule, ok, book) == []                     # 2.50 USDT at risk
    big = dict(ok, leverage=3, margin_usdt=10, notional=30.0, stop_pct=0.3)
    assert any("max_risk_usdt" in w for w in G.order_refusals(cfg, "testnet", rule, big, book))   # 9 USDT


def test_live_uses_wider_liquidation_buffer(monkeypatch):
    cfg = C.load()
    assert G.protective_stop(cfg, None, 3, "live") < G.protective_stop(cfg, None, 3, "testnet")
    rule = dict(id="x", status="live", max_leverage=3)
    cfg["live"] = True
    monkeypatch.setenv("OMEGA_LIVE", G.LIVE_PHRASE)
    o = dict(sym="A", leverage=3, margin_usdt=1, notional=3, stop_pct=0.32)
    book = dict(open_count=0, open_symbols=set(), day_pnl_usdt=0)
    assert G.order_refusals(cfg, "testnet", dict(rule, status="testnet"), o, book) == []
    assert any("liquidation" in w for w in G.order_refusals(cfg, "live", rule, o, book))


def test_live_refuses_key_without_ip_restriction(monkeypatch, bots_home):
    monkeypatch.setenv("OMEGA_BINANCE_LIVE_KEY", F.KEY); monkeypatch.setenv("OMEGA_BINANCE_LIVE_SECRET", F.SECRET)
    monkeypatch.setenv("OMEGA_LIVE", G.LIVE_PHRASE)
    fb = F.FakeBinance()
    fb.ip = False
    monkeypatch.setattr(live, "BinanceFutures", lambda url, k, s, cfg=None: BinanceFutures(url, k, s, cfg, client=fb.client()))
    fr, at, st, clock, mkt = setup(monkeypatch, bots_home, MARKET, status="live")
    cfg = C.load(); cfg["live"] = True
    with pytest.raises(SystemExit, match="not restricted to your IP"):
        live.Runner(cfg=cfg, mode="live", market=mkt, now_fn=clock)


def test_clock_drift_resyncs_once(monkeypatch, bots_home):
    fb = F.FakeBinance()
    api = BinanceFutures("https://demo-fapi.binance.com", F.KEY, F.SECRET, client=fb.client())
    fb.drift_once = True
    assert api.balance() == 100.0
    assert fb.sent("/fapi/v1/time", "GET")


def test_kill_keeps_positions_the_exchange_did_not_close(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET)
    r.cycle()
    fb.close_fail = True
    fb.pos["BTCUSDT"] = 0.002
    out = r.kill()
    assert out["still_open"] == ["ETHUSDT"] and len(r.state.positions) == 1
    assert next(iter(r.state.positions.values()))["status"] == "KILL_PENDING"
    assert {x["sym"] for x in out["exchange"] if "sym" in x} >= {"ETHUSDT", "BTCUSDT"}   # loop did not stop
    fb.close_fail = False
    clock.t += pd.Timedelta(minutes=1)
    r.cycle(full=False)                                   # KILL file still there: retried
    assert not r.state.positions and fb.pos["ETHUSDT"] == 0
    G.set_kill(False)


class FakeBridge:
    def __init__(self, allowed):
        self.allowed, self.placed = allowed, []

    def preview(self, venue, sym, side, **kw):
        return dict(allowed=self.allowed, preview_id="p1" if self.allowed else None,
                    blocked_because=[] if self.allowed else ["risk above max_risk_usd"])

    def place(self, venue, sym, side, confirm=False, preview_id=None, **kw):
        self.placed.append((venue, sym, side, confirm, preview_id, kw))
        return dict(sent=True)


def test_mt5_goes_through_the_bridge_guard():
    b = FakeBridge(allowed=False)
    m = MT5Broker({"enabled": True}, bridge=b)
    r = m.entry("XAUUSD", "long", risk_usd=1.0, stop_price=1990.0)
    assert r["sent"] is False and not b.placed and "risk above" in r["blocked_because"][0]
    b.allowed = True
    m.entry("XAUUSD", "long", risk_usd=1.0, stop_price=1990.0)
    (call,) = b.placed
    assert call[0] == "mt5" and call[3] is True and call[4] == "p1" and call[5]["stop"] == 1990.0
    G.set_kill(True)
    assert m.entry("XAUUSD", "long", risk_usd=1.0, stop_price=1990.0)["sent"] is False and len(b.placed) == 1
    G.set_kill(False)


def test_mt5_disabled_by_default():
    from edges.bots.exchange_mt5 import MT5Unavailable
    with pytest.raises(MT5Unavailable):
        MT5Broker(C.load()["mt5"])
