import json, os
import pytest
from edges.bots import config as C, guard as G
from edges.bots.core import stop_inside_liquidation, liquidation_distance

RULE = dict(id="panic_h1", status="testnet", max_leverage=3, margin_usdt=5)
OK_ORDER = dict(sym="ETHUSDT", leverage=1, margin_usdt=5, notional=5, stop_pct=0.3)
OK_BOOK = dict(open_count=0, open_symbols=set(), day_pnl_usdt=0.0)


def test_defaults_are_paper_and_safe():
    cfg = C.load()
    assert cfg["mode"] == "paper" and cfg["live"] is False
    assert cfg["binance"]["testnet_url"].startswith("https://demo-fapi.binance.com")
    assert cfg["guard"]["hard_max_leverage"] <= 3


def test_config_refuses_secrets(bots_home):
    json.dump({"binance": {"api_key": "x"}}, open(os.path.join(bots_home, "config.json"), "w"))
    with pytest.raises(ValueError, match="must not contain"):
        C.load()


def test_testnet_needs_keys():
    why = G.mode_refusals(C.load(), "testnet", have_keys=False)
    assert any("no Binance testnet API key" in w for w in why)
    assert G.mode_refusals(C.load(), "testnet", have_keys=True) == []


def test_live_needs_all_three_switches(monkeypatch):
    cfg = C.load()
    why = G.mode_refusals(cfg, "live", have_keys=True, withdrawals_enabled=False)
    assert any("config.json" in w for w in why) and any("OMEGA_LIVE" in w for w in why)
    cfg["live"] = True
    assert any("OMEGA_LIVE" in w for w in G.mode_refusals(cfg, "live", have_keys=True, withdrawals_enabled=False))
    monkeypatch.setenv("OMEGA_LIVE", "yes")                     # wrong phrase
    assert G.mode_refusals(cfg, "live", have_keys=True, withdrawals_enabled=False)
    monkeypatch.setenv("OMEGA_LIVE", G.LIVE_PHRASE)
    assert G.mode_refusals(cfg, "live", have_keys=True, withdrawals_enabled=False) == []
    assert any("WITHDRAW" in w for w in G.mode_refusals(cfg, "live", have_keys=True, withdrawals_enabled=True))
    assert any("could not confirm" in w for w in G.mode_refusals(cfg, "live", have_keys=True, withdrawals_enabled=None))


def test_rule_status_ladder(monkeypatch):
    cfg = C.load()
    assert G.rule_refusals(cfg, "paper", dict(id="x", status="paper")) == []
    assert G.rule_refusals(cfg, "testnet", dict(id="x", status="paper"))
    assert G.rule_refusals(cfg, "testnet", dict(id="x", status="testnet")) == []
    assert G.rule_refusals(cfg, "live", dict(id="x", status="testnet"))
    assert G.rule_refusals(cfg, "live", dict(id="x", status="live"))           # still needs config + env
    cfg["live"] = True
    monkeypatch.setenv("OMEGA_LIVE", G.LIVE_PHRASE)
    assert G.rule_refusals(cfg, "live", dict(id="x", status="live")) == []
    assert G.rule_refusals(cfg, "paper", None) == ["the rule is not in edges/approved.json"]


def test_order_ok_and_each_refusal():
    cfg = C.load()
    assert G.order_refusals(cfg, "testnet", RULE, OK_ORDER, OK_BOOK) == []
    def why(**kw):
        o, b = dict(OK_ORDER), dict(OK_BOOK)
        for k, v in kw.items():
            (b if k in b else o)[k] = v
        return " | ".join(G.order_refusals(cfg, "testnet", RULE, o, b))
    assert "leverage 5x" in why(leverage=5, stop_pct=0.1)                       # above the hard cap 3
    assert "above the allowed 1x" in " ".join(G.order_refusals(cfg, "testnet", dict(RULE, max_leverage=1), dict(OK_ORDER, leverage=2, stop_pct=0.2), OK_BOOK))
    assert "max_margin_usdt" in why(margin_usdt=50)
    assert "needs a stop" in why(stop_pct=None)
    assert "liquidation distance" in why(leverage=3, stop_pct=0.4)
    assert "already open" in why(open_count=3)
    assert "one per coin" in why(open_symbols={"ETHUSDT"})
    assert "daily loss limit" in why(day_pnl_usdt=-5.0)


def test_kill_switch_blocks_entries_not_exits():
    cfg = C.load()
    G.set_kill(True)
    assert G.killed()
    assert any("kill switch" in w for w in G.order_refusals(cfg, "testnet", RULE, OK_ORDER, OK_BOOK))
    assert G.order_refusals(cfg, "testnet", RULE, dict(OK_ORDER, reduce_only=True), OK_BOOK) == []
    G.set_kill(False)
    assert not G.killed()


def test_liquidation_distance_rule():
    assert liquidation_distance(1) == pytest.approx(0.995)
    assert liquidation_distance(20) == pytest.approx(0.045)
    assert stop_inside_liquidation(0.10, 5)          # 10% < 20% - 0.5%
    assert not stop_inside_liquidation(0.195, 5)
    assert not stop_inside_liquidation(0.05, 20)     # 20x liquidates at -4.5%: a 5% stop is outside
    assert stop_inside_liquidation(0.03, 20)
    assert not stop_inside_liquidation(0.03, 40)     # 40x: liquidation at -2.0%
    assert not stop_inside_liquidation(None, 1)


def test_protective_stop_capped_inside_liquidation():
    cfg = C.load()
    assert G.protective_stop(cfg, None, 1) == 0.5
    s3 = G.protective_stop(cfg, None, 3)
    assert stop_inside_liquidation(s3, 3) and s3 < 0.33
    assert G.protective_stop(cfg, 0.1, 1) == 0.1
    for L in (1, 2, 3, 5, 10, 20, 40):
        assert stop_inside_liquidation(G.protective_stop(cfg, None, L), L)


def test_log_redacts_secrets(bots_home):
    C.log("x", note="X-MBX-APIKEY abc")
    C.log("y", ok=1)
    rows = C.tail(5)
    assert rows[-2]["note"].startswith("redacted") and rows[-1]["ok"] == 1


def test_keys_from_env_only_never_files(monkeypatch, bots_home):
    from edges.bots import keys
    monkeypatch.setattr(keys, "_keyring", lambda: None)
    assert keys.binance("testnet") == (None, None)
    monkeypatch.setenv("OMEGA_BINANCE_TESTNET_KEY", "k")
    monkeypatch.setenv("OMEGA_BINANCE_TESTNET_SECRET", "s")
    assert keys.binance("testnet") == ("k", "s")
    assert keys.binance("live") == (None, None)       # a testnet key never serves live
