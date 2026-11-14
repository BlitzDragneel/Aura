"""Asset bots: state transitions, no direction without an approved rule, calls only from approved rules, scoring.
All data is synthetic (no network). Run: python -m pytest edges/assetbots/tests -q"""
import json

import numpy as np
import pandas as pd
import pytest

from edges.assetbots import machine, notebook, rules
from edges.assetbots.assets import BOTS, XAU_SPEC
from edges.bots.core import Signal, Strategy

T0 = pd.Timestamp("2026-11-10 12:00", tz="UTC")       # a Tuesday
STEP = {"15m": pd.Timedelta(minutes=15), "1h": pd.Timedelta(hours=1), "4h": pd.Timedelta(hours=4), "1d": pd.Timedelta(days=1)}
N = {"15m": 500, "1h": 500, "4h": 300, "1d": 400}


def frame(tf, end, n=None, price=4000.0, vol=0.002, seed=1, ramp=None):
    n = n or N[tf]
    idx = pd.date_range(end=end, periods=n, freq=STEP[tf])
    r = np.random.default_rng(seed).normal(0, vol, n)
    if ramp is not None:
        r[-ramp[0]:] = ramp[1]
    c = price * np.exp(np.cumsum(r) - np.cumsum(r)[-1])
    o = np.r_[c[0], c[:-1]]
    return pd.DataFrame(dict(o=o, h=np.maximum(o, c) * 1.001, l=np.minimum(o, c) * 0.999, c=c, v=1.0, qv=c), index=idx)


def bars_at(end_1h, **kw):
    """Closed bars ending at the 1h bar `end_1h` (its open time)."""
    return {"15m": frame("15m", end_1h + pd.Timedelta(minutes=45), **kw), "1h": frame("1h", end_1h, **kw),
            "4h": frame("4h", end_1h.floor("4h"), **kw), "1d": frame("1d", end_1h.floor("1D") - pd.Timedelta(days=1), **kw)}


class NoScouts:
    def __init__(self, flag=False):
        self.flag = flag

    def read(self, bars, spec):
        s = dict(horizon="4 h", p_big_move=0.6 if self.flag else 0.1, flag=self.flag, skill_ok=True,
                 direction="none: big-move risk only")
        return {"day": s, "swing": dict(s, horizon="24 h")}


class FireOnce(Strategy):
    """Fires a long market call on the bar at `when` (1h)."""
    id, tf, universe, lookback = "xau_test_rule", "1h", ["XAUUSDT"], 50

    def __init__(self, when, entry="market", price=None, stop=0.01, target=0.02, hold=6, valid=2):
        super().__init__()
        self.when, self.kw = when, dict(entry=entry, price=price, stop_pct=stop, target_pct=target, hold_bars=hold,
                                        valid_for_bars=valid)

    def signals(self, bars, now):
        if pd.Timestamp(now) != self.when:
            return []
        return [Signal(sym="XAUUSDT", side="long", note="test", **self.kw)]


def rule(status="paper", asset="XAU", horizon="day", rid="xau_test_rule"):
    return dict(id=rid, asset=asset, horizon=horizon, grade="B", status=status, max_leverage=1, margin_usdt=5,
                evidence="edges/results/TEST.json", tf="1h")


@pytest.fixture
def home(tmp_path):
    return tmp_path


def bot(home, approved, strat=None, monkeypatch=None, flag=False):
    if monkeypatch is not None:
        monkeypatch.setattr(rules, "load_strategy", lambda rid: strat if strat and rid == strat.id else None)
    return BOTS["XAU"](home, approved=approved, scouts=NoScouts(flag))


# ---------------------------------------------------------------- no direction without an approved rule
def test_no_rules_means_wait_and_no_direction(home):
    d = bot(home, []).run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    for hz in ("day", "swing", "hold"):
        h = d["horizons"][hz]
        assert h["state"] in ("WAIT", "WATCH")
        assert h["direction"] is None and "call" not in h
        assert any("no rule" in r for r in h["reasons"])
    assert d["open_calls"] == [] and d["recent_calls"] == []
    assert (home / "assets" / "XAU.json").exists() and (home / "assets" / "XAU" / "NOTEBOOK.md").exists()


def test_watch_has_no_direction(home):
    d = bot(home, [], flag=True).run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    h = d["horizons"]["day"]
    assert h["state"] == "WATCH" and h["direction"] is None
    assert any("direction unknown" in r for r in h["reasons"])


def test_high_volatility_raises_watch(home):
    b = bars_at(T0)
    b["1h"] = frame("1h", T0, ramp=(3, 0.03))          # three huge hourly bars at the end
    d = bot(home, []).run_once(bars=b, now=T0 + pd.Timedelta(hours=1, minutes=2))
    assert d["horizons"]["day"]["state"] == "WATCH"
    assert any("volatility is high" in r for r in d["horizons"]["day"]["reasons"])


@pytest.mark.parametrize("bad", [rule(asset="XAG"), rule(horizon="swing"), rule(status="retired"),
                                 rule(status="research"), {k: v for k, v in rule().items() if k != "asset"}])
def test_rules_for_other_asset_horizon_or_unpassed_status_are_ignored(home, monkeypatch, bad):
    strat = FireOnce(T0)
    d = bot(home, [bad], strat, monkeypatch).run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    assert d["horizons"]["day"]["state"] in ("WAIT", "WATCH")
    assert not [c for c in d["open_calls"] if c["horizon"] == "day"]
    if bad.get("horizon") != "swing":
        assert d["open_calls"] == []


def test_missing_strategy_file_gives_no_direction(home, monkeypatch):
    d = bot(home, [rule()], None, monkeypatch).run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    assert d["horizons"]["day"]["state"] in ("WAIT", "WATCH") and d["open_calls"] == []
    assert any("strategy file missing" in r for r in d["horizons"]["day"]["reasons"])


# ---------------------------------------------------------------- calls only from approved rules + transitions
def test_call_lifecycle_triggered_confirmed_invalidated(home, monkeypatch):
    strat = FireOnce(T0)
    b = bot(home, [rule()], strat, monkeypatch)
    d = b.run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    h = d["horizons"]["day"]
    assert h["state"] == "TRIGGERED" and h["direction"] == "long"
    c = h["call"]
    assert c["rule"] == "xau_test_rule" and c["grade"] == "B" and c["evidence"] == "edges/results/TEST.json"
    assert c["size"] == dict(margin_usdt=5.0, leverage=1.0, notional_usdt=5.0)
    assert c["research_only"] is True and c["execution_allowed"] is False
    assert c["stop"] < c["entry"] < c["target"]
    calls_log = (home / "assets" / "XAU" / "calls-2026-11.jsonl").read_text()
    assert '"event":"called"' in calls_log                     # logged before any outcome
    # next hour: filled at the open, no stop
    t1 = T0 + pd.Timedelta(hours=1)
    bb = bars_at(t1)
    entry = c["entry"]
    bb["1h"].loc[t1, ["o", "h", "l", "c"]] = [entry, entry * 1.002, entry * 0.998, entry]
    d = b.run_once(bars=bb, now=t1 + pd.Timedelta(hours=1, minutes=2))
    assert d["horizons"]["day"]["state"] == "CONFIRMED"
    # next hour: the low pierces the stop
    t2 = t1 + pd.Timedelta(hours=1)
    bb = bars_at(t2)
    bb["1h"].loc[t1, ["o", "h", "l", "c"]] = [entry, entry * 1.002, entry * 0.998, entry]
    bb["1h"].loc[t2, ["o", "h", "l", "c"]] = [entry, entry * 1.001, entry * 0.95, entry * 0.97]
    d = b.run_once(bars=bb, now=t2 + pd.Timedelta(hours=1, minutes=2))
    h = d["horizons"]["day"]
    assert h["state"] == "INVALIDATED" and h["call"]["outcome"] == "stop hit"
    assert h["call"]["net_pct"] < -1.0
    assert d["forward"]["calls"]["closed"] == 1 and d["forward"]["calls"]["wins"] == 0
    # one cycle later it falls back
    d = b.run_once(bars=bars_at(t2 + pd.Timedelta(hours=1)), now=t2 + pd.Timedelta(hours=2, minutes=2))
    assert d["horizons"]["day"]["state"] in ("WAIT", "WATCH")


def test_target_hit_expires_with_profit(home, monkeypatch):
    b = bot(home, [rule()], FireOnce(T0), monkeypatch)
    d = b.run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    e = d["horizons"]["day"]["call"]["entry"]
    t1 = T0 + pd.Timedelta(hours=1)
    bb = bars_at(t1)
    bb["1h"].loc[t1, ["o", "h", "l", "c"]] = [e, e * 1.05, e * 0.999, e * 1.03]
    d = b.run_once(bars=bb, now=t1 + pd.Timedelta(hours=1, minutes=2))
    c = d["horizons"]["day"]["call"]
    assert d["horizons"]["day"]["state"] == "EXPIRED" and c["outcome"] == "target hit"
    assert c["net_pct"] == pytest.approx((0.02 - 2 * XAU_SPEC.cost_side) * 100, abs=1e-6)


def test_limit_never_filled_expires(home, monkeypatch):
    b = bot(home, [rule()], FireOnce(T0, entry="limit", price=1.0, valid=2), monkeypatch)
    b.run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    t2 = T0 + pd.Timedelta(hours=2)
    d = b.run_once(bars=bars_at(t2), now=t2 + pd.Timedelta(hours=1, minutes=2))
    assert d["horizons"]["day"]["state"] == "EXPIRED"
    assert d["horizons"]["day"]["call"]["outcome"] == "not filled in time"


def test_testnet_rule_allows_execution_flag(home, monkeypatch):
    d = bot(home, [rule(status="testnet")], FireOnce(T0), monkeypatch).run_once(
        bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    c = d["horizons"]["day"]["call"]
    assert c["execution_allowed"] is True and c["research_only"] is False


def test_same_signal_is_not_called_twice(home, monkeypatch):
    b = bot(home, [rule()], FireOnce(T0), monkeypatch)
    b.run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    d = b.run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=17))
    assert len(d["open_calls"]) == 1


# ---------------------------------------------------------------- machine
def test_machine_setup_then_fade_expires():
    ctx = dict(now="t1", watch=[], setups=[dict(rule="r", grade="A", detail={})], open_calls=[], closed_now=[], n_rules=1)
    h = machine.step(None, ctx)
    assert h["state"] == "SETUP" and h["direction"] is None
    h2 = machine.step(h, dict(ctx, now="t2", setups=[]))
    assert h2["state"] == "EXPIRED"
    h3 = machine.step(h2, dict(ctx, now="t3", setups=[]))
    assert h3["state"] == "WAIT"


def test_machine_since_kept_while_state_unchanged():
    ctx = dict(now="t1", watch=["x"], setups=[], open_calls=[], closed_now=[], n_rules=0)
    a = machine.step(None, ctx)
    b = machine.step(a, dict(ctx, now="t2"))
    assert a["state"] == b["state"] == "WATCH" and b["since"] == "t1"


def test_rules_flags():
    rs = rules.rules_for("XAU", "day", [rule(), rule(status="live", rid="x2"), rule(status="watch", rid="x3")])
    assert [r["id"] for r in rs] == ["xau_test_rule", "x2"]
    assert rs[0]["execution_allowed"] is False and rs[1]["execution_allowed"] is True


# ---------------------------------------------------------------- scoring (forward record)
def test_readings_are_scored_after_their_horizon(home):
    b = bot(home, [], flag=True)
    b.run_once(bars=bars_at(T0), now=T0 + pd.Timedelta(hours=1, minutes=2))
    st = json.loads((home / "assets" / "XAU" / "state.json").read_text())
    assert {p["horizon"] for p in st["pending"]} >= {"day", "swing"}
    t5 = T0 + pd.Timedelta(hours=5)
    bb = bars_at(t5)
    bb["1h"].loc[T0 + pd.Timedelta(hours=4), "c"] = bb["1h"].loc[T0, "c"] * 1.05     # a big move 4 h later
    d = b.run_once(bars=bb, now=t5 + pd.Timedelta(hours=1, minutes=2))
    f = d["forward"]["day"]
    assert f["scored"] >= 1 and f["watch_readings"] >= 1 and f["big_move_rate_when_watch"] == 1.0
    scores = (home / "assets" / "XAU" / "scores-2026-11.jsonl").read_text().splitlines()
    assert json.loads(scores[0])["big"] is True
    assert (home / "assets" / "XAU" / "readings-2026-11.jsonl").read_text().count("\n") == 2


def test_notebook_reads_findings(tmp_path):
    f = tmp_path / "F.md"
    f.write_text("# Gold\nOverall: nothing passed.\n## Day trades\n- breakout failed (t -1.2)\n## Swing\n- ratio C grade\n"
                 "## Holding\n- trend controller: smaller drawdowns, no edge\n")
    fd = notebook.findings("XAU", f)
    assert fd["general"] == ["Overall: nothing passed."] and fd["day"] == ["breakout failed (t -1.2)"]
    assert fd["swing"] == ["ratio C grade"] and fd["hold"][0].startswith("trend controller")
    nb = notebook.build(XAU_SPEC, dict(price=1, volatility={}, session={}), {}, {}, [], f)
    assert "No rule has passed for this horizon" in nb["markdown"]


def test_metal_scouts_load_and_carry_skill_labels(home):
    from edges.assetbots.scout import ScoutReader
    out = ScoutReader("XAG").read({"1h": frame("1h", T0, price=48, vol=0.004)}, BOTS["XAG"].spec)
    assert "missing" not in out
    assert out["swing"]["skill_ok"] is False and out["swing"]["flag"] is False      # no validated skill -> never WATCH
    assert out["day"]["direction"].startswith("none")


# ---------------------------------------------------------------- multi-symbol rules (e.g. BTC/gold allocation)
class TwoLegs(Strategy):
    id, tf, universe, lookback = "btc_two_legs", "1h", ["BTCUSDT", "PAXGUSDT"], 700

    def __init__(self, when):
        super().__init__()
        self.when, self.seen = when, {}

    def signals(self, bars, now):
        self.seen = {k: (len(v), float(v.c.iloc[-1])) for k, v in bars.items()}
        if pd.Timestamp(now) != self.when:
            return []
        return [Signal(sym="BTCUSDT", side="long", hold_bars=24, note="w=0.3 BTC leg"),
                Signal(sym="PAXGUSDT", side="long", hold_bars=24, note="w=0.7 gold leg")]


class FakeProvider:
    def __init__(self):
        self.asked = []

    def klines(self, sym, tf, limit):
        self.asked.append((sym, tf, limit))
        return frame(tf, T0, n=limit, price=4000.0 if sym == "PAXGUSDT" else 75000.0, seed=3)


def test_other_legs_use_their_own_candles_with_the_rule_lookback(home, monkeypatch):
    strat, prov = TwoLegs(T0), FakeProvider()
    monkeypatch.setattr(rules, "load_strategy", lambda rid: strat if rid == strat.id else None)
    b = BOTS["BTC"](home, provider=prov, approved=[rule(asset="BTC", horizon="hold", rid="btc_two_legs")], scouts=NoScouts())
    d = b.run_once(bars=bars_at(T0, price=75000.0), now=T0 + pd.Timedelta(hours=1, minutes=4))
    assert strat.seen["PAXGUSDT"][1] == pytest.approx(4000.0) and strat.seen["BTCUSDT"][1] == pytest.approx(75000.0)
    assert strat.seen["PAXGUSDT"][0] >= 700 and strat.seen["BTCUSDT"][0] >= 700        # the rule's lookback, not 500
    assert ("PAXGUSDT", "1h", 705) in prov.asked
    legs = {c["symbol"]: c for c in d["open_calls"]}
    assert set(legs) == {"BTCUSDT", "PAXGUSDT"} and legs["PAXGUSDT"]["entry"] == pytest.approx(4000.0)
    assert legs["PAXGUSDT"]["note"] == "w=0.7 gold leg" and legs["BTCUSDT"]["id"] != legs["PAXGUSDT"]["id"]
    assert d["horizons"]["hold"]["state"] == "TRIGGERED"
