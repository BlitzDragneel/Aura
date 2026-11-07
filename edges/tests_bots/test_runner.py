"""The runner end to end with simulated market data: paper fills/exits/stops, persistence across a restart, the
mocked Binance order flow (testnet), the kill switch, and the start-up refusals. No real exchange is contacted
(fapi.binance.com answers 451 from Claude's sandbox; the testnet is not reachable either)."""
import json, os
import pandas as pd
import pytest
from edges.bots import live, guard as G, config as C
from edges.bots.core import Signal
from edges.bots.exchange_binance import BinanceFutures
from edges.tests_bots import fakes as F

H = pd.Timedelta(hours=1)


class Clock:
    def __init__(self, t):
        self.t = pd.Timestamp(t)

    def __call__(self):
        return self.t

    def at_close(self, bar):                      # 30 s after bar `bar` closed
        self.t = bar + H + pd.Timedelta(seconds=30)


def setup(monkeypatch, home, sig, status="paper", frame=None, max_lev=1):
    frame = frame if frame is not None else F.hourly()
    F.approve(home, [dict(id="fake_rule", status=status, max_leverage=max_lev, margin_usdt=5, grade="B")])
    at = frame.index[20]
    strat = F.OneShot(at, sig)
    monkeypatch.setattr(live.S, "load", lambda rid: strat)
    clock = Clock(at)
    clock.at_close(at)
    mkt = F.FrameMarket({"ETHUSDT": frame}, clock)
    return frame, at, strat, clock, mkt


def logs(home):
    return [json.loads(x) for x in open(os.path.join(home, "bots_log.jsonl")).read().splitlines()]


LIMIT = Signal(sym="ETHUSDT", entry="limit", price=98.5, valid_for_bars=3, hold_bars=5, ref_close=100.0, note="t")
MARKET = Signal(sym="ETHUSDT", entry="market", hold_bars=4, ref_close=100.0, note="t")


def test_paper_limit_fill_exit_and_restart(monkeypatch, bots_home):
    fr = F.hourly()
    fr.loc[fr.index[22], "l"] = 98.0          # trades THROUGH the 98.5 limit in the 2nd bar of the window
    fr.loc[fr.index[27], "c"] = 103.0         # the exit bar: close of fill bar + 5
    fr, at, st, clock, mkt = setup(monkeypatch, bots_home, LIMIT, frame=fr)
    r = live.Runner(mode="paper", market=mkt, now_fn=clock)
    r.cycle()
    (o,) = r.state.orders.values()
    assert o["price"] == 98.5 and o["stop_price"] == pytest.approx(49.25) and o["qty"] == 0.051
    clock.at_close(fr.index[21]); r.cycle()
    assert len(r.state.orders) == 1 and not r.state.positions             # 99 low: no fill
    clock.at_close(fr.index[22]); r.cycle()
    (p,) = r.state.positions.values()
    assert p["entry"] == 98.5 and pd.Timestamp(p["exit_due"]) == fr.index[28]
    # restart from disk
    r2 = live.Runner(mode="paper", market=mkt, now_fn=clock)
    assert len(r2.state.positions) == 1
    clock.at_close(fr.index[26]); r2.cycle()
    assert len(r2.state.positions) == 1                                     # not due yet
    clock.at_close(fr.index[27]); r2.cycle()
    assert not r2.state.positions
    c = r2.state.d["closed"][-1]
    assert c["exit"] == 103.0 and c["exit_reason"] == "time" and c["pnl_usdt"] > 0
    ev = [x["event"] for x in logs(bots_home)]
    assert ev.count("order") == 1 and "filled" in ev and "closed" in ev
    assert st.calls >= 3


def test_paper_limit_touch_is_not_a_fill(monkeypatch, bots_home):
    fr = F.hourly()
    fr.loc[fr.index[21:24], "l"] = 98.5        # touches, never trades through
    fr, at, st, clock, mkt = setup(monkeypatch, bots_home, LIMIT, frame=fr)
    r = live.Runner(mode="paper", market=mkt, now_fn=clock)
    r.cycle()
    for k in (21, 22):
        clock.at_close(fr.index[k]); r.cycle()
        assert len(r.state.orders) == 1
    clock.at_close(fr.index[23]); r.cycle()                                 # window over at the close of bar t+3
    assert not r.state.orders and not r.state.positions
    assert "expired" in [x["event"] for x in logs(bots_home)]


def test_paper_stop_from_intrabar_low(monkeypatch, bots_home):
    fr = F.hourly()
    fr.loc[fr.index[23], "l"] = 40.0
    fr, at, st, clock, mkt = setup(monkeypatch, bots_home, MARKET, frame=fr)
    r = live.Runner(mode="paper", market=mkt, now_fn=clock)
    r.cycle()
    assert len(r.state.positions) == 1
    clock.at_close(fr.index[23]); r.cycle()
    c = r.state.d["closed"][-1]
    assert c["exit_reason"] == "stop" and c["exit"] == pytest.approx(50.0)


def test_testnet_refuses_paper_status_rule(monkeypatch, bots_home):
    monkeypatch.setenv("OMEGA_BINANCE_TESTNET_KEY", F.KEY); monkeypatch.setenv("OMEGA_BINANCE_TESTNET_SECRET", F.SECRET)
    fb = F.FakeBinance()
    monkeypatch.setattr(live, "BinanceFutures", lambda url, k, s, cfg=None: BinanceFutures(url, k, s, cfg, client=fb.client()))
    fr, at, st, clock, mkt = setup(monkeypatch, bots_home, LIMIT, status="paper")
    r = live.Runner(mode="testnet", market=mkt, now_fn=clock)
    assert r.rules == {}
    r.cycle()
    assert not fb.sent("/fapi/v1/order")
    assert any(x["event"] == "rule_skipped" for x in logs(bots_home))


def test_testnet_needs_keys(monkeypatch, bots_home):
    fr, at, st, clock, mkt = setup(monkeypatch, bots_home, LIMIT, status="testnet")
    with pytest.raises(SystemExit, match="no Binance testnet API key"):
        live.Runner(mode="testnet", market=mkt, now_fn=clock)


def _testnet(monkeypatch, home, sig, fb=None, **kw):
    monkeypatch.setenv("OMEGA_BINANCE_TESTNET_KEY", F.KEY); monkeypatch.setenv("OMEGA_BINANCE_TESTNET_SECRET", F.SECRET)
    fb = fb or F.FakeBinance()
    monkeypatch.setattr(live, "BinanceFutures", lambda url, k, s, cfg=None: BinanceFutures(url, k, s, cfg, client=fb.client()))
    fr, at, st, clock, mkt = setup(monkeypatch, home, sig, status="testnet", **kw)
    return fb, fr, at, clock, live.Runner(mode="testnet", market=mkt, now_fn=clock)


def test_testnet_limit_order_flow(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, LIMIT)
    assert r.broker.api.base == "https://demo-fapi.binance.com"
    r.cycle()
    (lim,) = [q for q in fb.sent("/fapi/v1/order") if q["type"] == "LIMIT"]
    assert lim["side"] == "BUY" and lim["price"] == "98.5" and lim["quantity"] == "0.051" and lim["timeInForce"] == "GTD"
    assert int(lim["goodTillDate"]) == int((at + 4 * H).timestamp() * 1000)
    assert fb.sent("/fapi/v1/marginType")[0]["marginType"] == "ISOLATED" and fb.sent("/fapi/v1/leverage")[0]["leverage"] == "1"
    (stop,) = fb.sent("/fapi/v1/algoOrder")
    assert stop["algoType"] == "CONDITIONAL" and stop["type"] == "STOP_MARKET" and stop["closePosition"] == "true"
    assert stop["side"] == "SELL" and float(stop["triggerPrice"]) == pytest.approx(49.25)
    # the exchange fills it during bar 22
    (oid,) = [o["orderId"] for o in fb.orders.values() if o["type"] == "LIMIT"]
    fb.fill(oid, int((fr.index[22] + pd.Timedelta(minutes=20)).timestamp() * 1000))
    clock.at_close(fr.index[22]); r.cycle()
    (p,) = r.state.positions.values()
    assert pd.Timestamp(p["exit_due"]) == fr.index[28] and fb.pos["ETHUSDT"] == 0.051
    clock.at_close(fr.index[27]); r.cycle()
    (sell,) = [q for q in fb.sent("/fapi/v1/order") if q["type"] == "MARKET"]
    assert sell["side"] == "SELL" and sell["reduceOnly"] == "true" and sell["quantity"] == "0.051"
    assert fb.sent("/fapi/v1/allOpenOrders", "DELETE") and fb.sent("/fapi/v1/algoOpenOrders", "DELETE")
    assert fb.pos["ETHUSDT"] == 0 and not r.state.positions
    assert fb.bad_sig == 0
    raw = open(os.path.join(bots_home, "bots_log.jsonl")).read() + open(os.path.join(bots_home, "state.json")).read()
    assert F.SECRET not in raw and F.KEY not in raw
    assert all(F.SECRET not in json.dumps(q) for (_, _, q) in fb.calls)


def test_testnet_unfilled_limit_is_cancelled_with_its_stop(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, LIMIT)
    r.cycle()
    clock.at_close(fr.index[23]); r.cycle()
    assert not r.state.orders
    assert all(o["status"] == "CANCELED" for o in fb.orders.values() if o["type"] == "LIMIT")
    assert all(a["algoStatus"] == "CANCELED" for a in fb.algos.values())


def test_market_entry_without_stop_is_closed_at_once(monkeypatch, bots_home):
    fb = F.FakeBinance()
    fb.algo_fail = True
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET, fb=fb)
    r.cycle()
    assert fb.pos.get("ETHUSDT", 0) == 0 and not r.state.positions
    assert any(x["event"] == "order_error" for x in logs(bots_home))


def test_legacy_stop_path_when_no_algo_service(monkeypatch, bots_home):
    fb = F.FakeBinance(algo=False)
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET, fb=fb)
    r.cycle()   # the fake also answers -4120 on the old path, so the order is refused and closed: never unprotected
    assert fb.pos.get("ETHUSDT", 0) == 0


def test_guard_refusal_is_logged_not_sent(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET)
    r.rules["fake_rule"]["margin_usdt"] = 50                     # above guard.max_margin_usdt (10)
    r.cycle()
    assert not fb.sent("/fapi/v1/order")
    (ref,) = [x for x in logs(bots_home) if x["event"] == "refused"]
    assert any("max_margin_usdt" in w for w in ref["reasons"])


def test_daily_loss_limit_blocks_new_orders(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET)
    monkeypatch.setattr(r.broker, "day_pnl", lambda st: -6.0)
    r.cycle()
    assert not fb.sent("/fapi/v1/order")
    (ref,) = [x for x in logs(bots_home) if x["event"] == "refused"]
    assert any("daily loss limit" in w for w in ref["reasons"])


def test_kill_switch_cancels_and_closes_everything(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET)
    fb.pos["BTCUSDT"] = 0.002                                    # a position the bot did not open: closed too
    r.cycle()
    assert fb.pos["ETHUSDT"] == 0.05
    out = r.kill()
    assert G.killed() and fb.pos["ETHUSDT"] == 0 and fb.pos["BTCUSDT"] == 0
    assert not r.state.positions and r.state.d["closed"][-1]["exit_reason"] == "kill"
    assert set(x["sym"] for x in out["exchange"] if "sym" in x) >= {"ETHUSDT", "BTCUSDT"}
    n = len(fb.sent("/fapi/v1/order"))
    clock.at_close(fr.index[21])
    assert r.cycle() == dict(killed=True) and len(fb.sent("/fapi/v1/order")) == n
    G.set_kill(False)


def test_kill_file_triggers_flatten_on_next_cycle(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET)
    r.cycle()
    open(os.path.join(bots_home, "KILL"), "w").write("stop\n")
    clock.at_close(fr.index[21]); r.cycle(full=False)
    assert fb.pos["ETHUSDT"] == 0 and not r.state.positions


def test_live_start_refusals(monkeypatch, bots_home):
    monkeypatch.setenv("OMEGA_BINANCE_LIVE_KEY", F.KEY); monkeypatch.setenv("OMEGA_BINANCE_LIVE_SECRET", F.SECRET)
    fb = F.FakeBinance(withdrawals=True)
    monkeypatch.setattr(live, "BinanceFutures", lambda url, k, s, cfg=None: BinanceFutures(url, k, s, cfg, client=fb.client()))
    fr, at, st, clock, mkt = setup(monkeypatch, bots_home, MARKET, status="live")
    with pytest.raises(SystemExit, match="config.json"):
        live.Runner(mode="live", market=mkt, now_fn=clock)
    cfg = C.load(); cfg["live"] = True
    with pytest.raises(SystemExit, match="OMEGA_LIVE"):
        live.Runner(cfg=cfg, mode="live", market=mkt, now_fn=clock)
    monkeypatch.setenv("OMEGA_LIVE", G.LIVE_PHRASE)
    with pytest.raises(SystemExit, match="WITHDRAW"):
        live.Runner(cfg=cfg, mode="live", market=mkt, now_fn=clock)
    fb.withdrawals = False
    r = live.Runner(cfg=cfg, mode="live", market=mkt, now_fn=clock)
    assert r.broker.api.base == "https://fapi.binance.com" and list(r.rules) == ["fake_rule"]


def test_hedge_mode_refused(monkeypatch, bots_home):
    with pytest.raises(SystemExit, match="Hedge Mode"):
        _testnet(monkeypatch, bots_home, MARKET, fb=F.FakeBinance(dual=True))


def test_leverage_never_above_rule_or_cap(monkeypatch, bots_home):
    fb, fr, at, clock, r = _testnet(monkeypatch, bots_home, MARKET, max_lev=20)
    r.cfg["guard"]["max_risk_usdt"] = 10.0                       # (the default 3 USDT risk cap refuses 15 USDT x 32%)
    r.cycle()
    assert fb.sent("/fapi/v1/leverage")[0]["leverage"] == "3"          # rule says 20, hard cap 3
    (stop,) = fb.sent("/fapi/v1/algoOrder")
    assert 1 - float(stop["triggerPrice"]) / 100 < 1 / 3 - 0.005       # stop inside the 3x liquidation distance
