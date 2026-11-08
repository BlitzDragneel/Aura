"""The runner with 5m / 15m rules: bar closes and timing in the rule's own bars (valid_for_bars, hold_bars), 15m bars
built from 5m candles, paper catch-up when it runs every 15 minutes, the watch list's own paper book, the incremental
on-disk candle cache, and MarketData paging / fallback (no real exchange is contacted)."""
import json
import os

import httpx
import pandas as pd
import pytest

from edges.bots import live
from edges.bots.core import Signal
from edges.bots.exchange_binance import MarketData
from edges.tests_bots import fakes as F

M5, M15 = pd.Timedelta(minutes=5), pd.Timedelta(minutes=15)


class Clock:
    def __init__(self, t):
        self.t = pd.Timestamp(t)

    def __call__(self):
        return self.t

    def at_close(self, bar, step):
        self.t = pd.Timestamp(bar) + step + pd.Timedelta(seconds=30)


def config(home, rules, **extra):
    p = os.path.join(home, "approved.json")
    json.dump(rules, open(p, "w"))
    json.dump(dict({"approved_file": p, "universe": ["ETHUSDT"], "fetch_workers": 1}, **extra),
              open(os.path.join(home, "config.json"), "w"))


def rule(**kw):
    return dict(dict(id="fake_rule", status="paper", max_leverage=1, margin_usdt=5, grade="C"), **kw)


def logs(home):
    return [json.loads(x) for x in open(os.path.join(home, "bots_log.jsonl")).read().splitlines()]


def test_5m_limit_window_and_hold_count_5m_bars(monkeypatch, bots_home):
    fr = F.bars("5m")
    at = fr.index[300]
    fr.loc[fr.index[302], "l"] = 98.0                        # trades through 98.5 in the 2nd bar of the window
    fr.loc[fr.index[314], "c"] = 104.0                       # close of fill bar + 12
    sig = Signal(sym="ETHUSDT", entry="limit", price=98.5, valid_for_bars=3, hold_bars=12, ref_close=100.0)
    st = F.EveryBar("5m", [at], sig)
    monkeypatch.setattr(live.S, "load", lambda rid: st)
    config(bots_home, [rule()])
    clock = Clock(at + M5 + pd.Timedelta(seconds=30))
    r = live.Runner(mode="paper", market=F.TFMarket({"5m": {"ETHUSDT": fr}}, clock), now_fn=clock)
    r.cycle()
    (o,) = r.state.orders.values()
    assert pd.Timestamp(o["expires_at"]) == at + 4 * M5 and o["tf"] == "5m"
    clock.at_close(fr.index[302], M5); r.cycle()
    (p,) = r.state.positions.values()
    assert pd.Timestamp(p["entry_bar"]) == fr.index[302] and pd.Timestamp(p["exit_due"]) == fr.index[315]
    clock.at_close(fr.index[313], M5); r.cycle()
    assert r.state.positions
    clock.at_close(fr.index[314], M5); r.cycle()
    c = r.state.d["closed"][-1]
    assert not r.state.positions and c["exit"] == 104.0 and c["exit_reason"] == "time"


def test_5m_limit_expires_after_its_window(monkeypatch, bots_home):
    fr = F.bars("5m")
    at = fr.index[300]
    sig = Signal(sym="ETHUSDT", entry="limit", price=98.5, valid_for_bars=3, hold_bars=12, ref_close=100.0)
    st = F.EveryBar("5m", [at], sig)
    monkeypatch.setattr(live.S, "load", lambda rid: st)
    config(bots_home, [rule()])
    clock = Clock(at + M5 + pd.Timedelta(seconds=30))
    r = live.Runner(mode="paper", market=F.TFMarket({"5m": {"ETHUSDT": fr}}, clock), now_fn=clock)
    r.cycle()
    clock.at_close(fr.index[302], M5); r.cycle()
    assert len(r.state.orders) == 1
    clock.at_close(fr.index[303], M5); r.cycle()
    assert not r.state.orders and not r.state.positions


def test_paper_catches_up_every_5m_bar_when_run_every_15_minutes(monkeypatch, bots_home):
    fr = F.bars("5m")
    st = F.EveryBar("5m", [], Signal(sym="ETHUSDT"))
    monkeypatch.setattr(live.S, "load", lambda rid: st)
    config(bots_home, [rule()])
    clock = Clock(fr.index[300] + M5 + pd.Timedelta(seconds=40))
    mkt = F.TFMarket({"5m": {"ETHUSDT": fr}}, clock)
    r = live.Runner(mode="paper", market=mkt, now_fn=clock)
    r.cycle()
    for k in range(4):
        clock.t += M15
        r.cycle()
    seen = [t for t, _ in st.seen]
    assert seen == list(fr.index[300:313])                   # every bar exactly once, in order
    assert all(b["ETHUSDT"][1] == t for t, b in st.seen)     # the rule saw the frame ending at that bar
    # testnet/live evaluate only the bar that just closed
    r.mode = "testnet"
    clock.t += M15
    assert r._due(clock()) == {"fake_rule": [fr.index[315]]}


def test_15m_rule_from_5m_candles(monkeypatch, bots_home):
    fr = F.bars("5m")
    i0 = 288                                                  # 2026-11-02 00:00, a 15m boundary
    at = fr.index[i0]                                         # 15m bar 00:00-00:15 = 5m bars i0..i0+2
    fr.loc[fr.index[i0 + 4], "l"] = 98.0                      # inside the next 15m bar (00:15) -> its low
    fr.loc[fr.index[i0 + 3 + 3 * 2 + 2], "c"] = 105.0         # last 5m of 15m bar 00:15 + 2 bars = exit close
    sig = Signal(sym="ETHUSDT", entry="limit", price=98.5, valid_for_bars=2, hold_bars=2, ref_close=100.0)
    st = F.EveryBar("15m", [at], sig, source_tf="5m")
    monkeypatch.setattr(live.S, "load", lambda rid: st)
    config(bots_home, [rule()])
    clock = Clock(fr.index[i0 + 3] + M5 + pd.Timedelta(seconds=30))   # 00:20:30: bar 00:15 is still forming
    mkt = F.TFMarket({"5m": {"ETHUSDT": fr}}, clock)
    r = live.Runner(mode="paper", market=mkt, now_fn=clock)
    r.cycle()
    assert {tf for _, tf, _ in mkt.calls} == {"5m"}
    assert st.seen[-1][0] == at and st.seen[-1][1]["ETHUSDT"][1] == at    # the partial 00:15 bin is not a bar
    assert r.frames["15m"]["ETHUSDT"].index[-1] == at
    (o,) = r.state.orders.values()
    assert pd.Timestamp(o["expires_at"]) == at + 3 * M15 and o["tf"] == "15m" and o["src_tf"] == "5m"
    clock.at_close(at + M15, M15); r.cycle()                  # 15m bar 00:15 closed: its low 98 < 98.5
    (p,) = r.state.positions.values()
    assert pd.Timestamp(p["entry_bar"]) == at + M15 and pd.Timestamp(p["exit_due"]) == at + 4 * M15
    clock.at_close(at + 3 * M15, M15); r.cycle()
    c = r.state.d["closed"][-1]
    assert c["exit"] == 105.0 and c["exit_reason"] == "time"
    assert [t for t, _ in st.seen] == [at, at + M15, at + 2 * M15, at + 3 * M15]


def test_watch_rule_keeps_its_own_paper_book(monkeypatch, bots_home):
    fr = F.bars("5m")
    at = fr.index[300]
    sig = Signal(sym="ETHUSDT", entry="market", hold_bars=6, ref_close=100.0)
    st = F.EveryBar("5m", [at], sig)
    monkeypatch.setattr(live.S, "load", lambda rid: st)
    other = dict(id="x", strategy="other_rule", sym="ETHUSDT", side="long", qty=1, entry=100, entry_kind="market",
                 exit_due="2030-01-01T00:00:00+00:00", entry_bar="2026-11-01T00:00:00+00:00", tf="1h")

    def run(book):
        config(bots_home, [rule(**({"book": "own"} if book else {}))], guard={"max_open_positions": 1})
        if os.path.exists(os.path.join(bots_home, "state.json")):
            os.remove(os.path.join(bots_home, "state.json"))
        clock = Clock(at + M5 + pd.Timedelta(seconds=30))
        r = live.Runner(mode="paper", market=F.TFMarket({"5m": {"ETHUSDT": fr}}, clock), now_fn=clock)
        r.state.positions["x"] = dict(other)
        r.cycle()
        return [p for p in r.state.positions.values() if p["strategy"] == "fake_rule"]

    assert run(book=False) == []                             # the shared book is full and ETH is taken
    assert any("already open" in w or "one per coin" in w for x in logs(bots_home) if x["event"] == "refused"
               for w in x["reasons"])
    assert len(run(book=True)) == 1                          # the watch book records it anyway


def test_candle_cache_is_incremental_and_survives_a_restart(monkeypatch, bots_home):
    fr = F.bars("5m", n=2000)
    st = F.EveryBar("5m", [], Signal(sym="ETHUSDT"))
    st.lookback = 900
    monkeypatch.setattr(live.S, "load", lambda rid: st)
    config(bots_home, [rule()])
    clock = Clock(fr.index[1500] + M5 + pd.Timedelta(seconds=30))
    mkt = F.TFMarket({"5m": {"ETHUSDT": fr}}, clock)
    r = live.Runner(mode="paper", market=mkt, now_fn=clock)
    r.cycle()
    assert mkt.calls[-1][2] >= 900
    assert os.path.exists(os.path.join(bots_home, "bars", "5m", "ETHUSDT.parquet"))
    clock.t += M15
    r2 = live.Runner(mode="paper", market=mkt, now_fn=clock)         # a new process (GitHub Actions run)
    r2.cycle()
    assert mkt.calls[-1] == ("ETHUSDT", "5m", 6)                       # 3 new bars + 3 overlap
    d = r2.frames["5m"]["ETHUSDT"]
    assert d.index[-1] == fr.index[1503] and len(d) >= 900 and d.index.is_monotonic_increasing
    n = len(mkt.calls)
    r2.cycle()                                                         # nothing new closed: no request
    assert len(mkt.calls) == n


# ---------------------------------------------------------------- MarketData
def _kl(t0, n, step_ms=300_000):
    return [[t0 + i * step_ms, "1", "2", "0.5", "1.5", "10", t0 + (i + 1) * step_ms - 1, "15", 1, "1", "1", "0"]
            for i in range(n)]


def test_marketdata_pages_binance_history():
    now = 1_800_000_000_000 - 1_800_000_000_000 % 300_000
    seen = []

    def handle(req):
        q = dict(req.url.params)
        seen.append(q)
        end = int(q.get("endTime", now + 300_000 - 1))
        lim = int(q["limit"])
        t1 = end - end % 300_000                               # bar containing endTime (the forming one at first)
        return httpx.Response(200, json=_kl(t1 - (lim - 1) * 300_000, lim))

    md = MarketData(client=httpx.Client(transport=httpx.MockTransport(handle)), spacing=0)
    d = md.history("ETHUSDT", "5m", 3500, now_ms=now + 10_000)
    assert len(d) == 3500 and d.index.is_unique and d.index.is_monotonic_increasing
    assert d.index[-1] == pd.Timestamp(now - 300_000, unit="ms", tz="UTC")   # the forming bar is dropped
    assert (d.index[1:] - d.index[:-1] == M5).all() and len(seen) == 3


def test_marketdata_falls_back_once_and_maps_1000_coins(monkeypatch):
    calls = []

    def handle(req):
        calls.append(req.url.path)
        return httpx.Response(451, json={"msg": "restricted location"})

    class Alt:
        def _k_okx(self, sym, tf, n):
            calls.append(("okx", sym, n))
            t0 = 1_800_000_000_000
            return dict(source="okx-swap", candles=[dict(t=t0 + i * 300_000, o=0.01, h=0.02, l=0.005, c=0.015, v=1000.0,
                                                         qv=15.0, closed=True) for i in range(n)])

    md = MarketData(client=httpx.Client(transport=httpx.MockTransport(handle)), spacing=0)
    monkeypatch.setattr(md, "_alt_crypto", lambda: Alt())
    d = md.history("1000PEPEUSDT", "5m", 50, now_ms=1_900_000_000_000)
    d2 = md.history("1000PEPEUSDT", "5m", 50, now_ms=1_900_000_000_000)
    assert len(d) == 50 and d.c.iloc[0] == pytest.approx(15.0) and d.v.iloc[0] == pytest.approx(1.0)
    assert ("okx", "PEPEUSDT", 51) in calls
    assert sum(1 for c in calls if c == "/fapi/v1/klines") == 1         # Binance is not asked again during the cooldown
    assert md.source == "okx-swap" and len(d2) == 50


def test_watch_rules_are_paper_only(bots_home):
    from edges.bots import guard as G, config as C
    cfg = C.load()
    appr = C.approved(cfg)
    for rid in ("panic5m_watch", "panic15m_watch", "breadth15m_watch", "upscout_watch"):
        r = appr[rid]
        assert r["grade"] == "C" and r["status"] == "paper" and r["max_leverage"] == 1 and r["margin_usdt"] == 5
        assert r["book"] == "own" and "evidence" in r and "note" in r and r["evidence"].startswith("edges/results/E")
        assert G.rule_refusals(cfg, "paper", r) == []
        assert G.rule_refusals(cfg, "testnet", dict(r, status="testnet")) != []      # even if someone edits the status
    assert {"climax_a", "panic_h1", "panic_h3"} <= set(appr)
