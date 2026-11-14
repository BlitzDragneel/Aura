import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from edges.auditor.core import Signal, parse, score, summary, risk_check

M = 60_000


def bars(path, t0=0):
    return [dict(t=t0 + i * M, o=o, h=h, l=l, c=c) for i, (o, h, l, c) in enumerate(path)]


def test_parse_formats():
    s = parse("GOLD SELL @4130-4134 | SL: 4140 | TP: 4125/4120/4110", 5, "T")
    assert (s.symbol, s.side, s.entry, s.entry_hi, s.stop, s.targets) == ("XAUUSD", "sell", 4130, 4134, 4140, [4125, 4120, 4110])
    s = parse("US30 buy limit 46800 sl 46700 tp 47000", 5)
    assert s.targets == [47000] and s.entry == 46800
    s = parse("XAUUSD BUY NOW 4105 SL 4095 TP1 4110 TP2 4120", 5)
    assert s.entry is None and s.stop == 4095


def test_stop_first_and_tp():
    sig = Signal("XAUUSD", "buy", 0, stop=99, targets=[102])
    r = score(sig, bars([(100, 100.5, 99.8, 100), (100, 102.5, 98.5, 101)]))   # both in one bar -> stop
    assert r["tp1"]["outcome"] == "SL" and r["tp1"]["R"] < -1
    r = score(sig, bars([(100, 100.5, 99.8, 100), (100, 102.5, 99.5, 102)]))
    assert r["tp1"]["outcome"] == "TP1" and abs(r["tp1"]["R"] - 1.8) < 1e-9   # 2.0 move - 0.2 spread


def test_ladder_breakeven():
    sig = Signal("XAUUSD", "buy", 0, stop=99, targets=[101, 103])
    r = score(sig, bars([(100, 101.2, 99.9, 101), (101, 101, 99.9, 100)]))
    assert r["ladder"]["outcome"] == "TP1+BE" and r["tp1"]["outcome"] == "TP1"


def test_limit_not_filled_and_logged_time():
    sig = Signal("XAUUSD", "sell", 10 * M, entry=110, stop=112, targets=[105])
    path = [(100, 101, 99, 100)] * 30
    r = score(sig, bars(path), fill_hours=0.25)
    assert r["status"] == "not filled"
    # bars before logging are ignored
    sig2 = Signal("XAUUSD", "buy", 2 * M, stop=95, targets=[105])
    r2 = score(sig2, bars([(50, 200, 1, 50), (50, 200, 1, 50), (100, 101, 99, 100), (100, 106, 99, 105)]))
    assert r2["fill"] == 100


def test_summary_and_risk():
    rs = [dict(status="closed", tp1=dict(R=1.0, pips=10), ladder=dict(R=1.0, pips=10), problems=[])] * 5
    s = summary(rs)
    assert s["tp1"]["n"] == 5 and "Too early" in s["verdict"]
    rc = risk_check(564.58, [dict(symbol="XAUUSDm", side="sell", lots=0.1)] * 9)
    assert rc["by_symbol"][0]["usd_per_1_move"] == 90 and round(rc["by_symbol"][0]["move_to_lose_balance"], 2) == 6.27
