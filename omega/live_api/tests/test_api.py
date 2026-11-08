"""Offline tests: every provider is mocked with httpx.MockTransport (no network needed)."""
import json
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from omega_live import app as appmod
from omega_live.providers import Http, fx_pair, okx_swap

NOW = int(time.time() * 1000)


def handler(blocked=("fapi.binance.com",)):
    def h(req: httpx.Request):
        host, path = req.url.host, req.url.path
        if host in blocked:
            return httpx.Response(451, json={"msg": "restricted location"})
        if host == "fapi.binance.com" and path == "/fapi/v1/klines":
            k = [[NOW - 7200000, "1", "2", "0.5", "1.5", "10", NOW - 3600001, "15", 5, "1", "1", "0"],
                 [NOW - 3600000, "1.5", "2", "1", "1.8", "10", NOW + 1000, "18", 5, "1", "1", "0"]]
            return httpx.Response(200, json=k)
        if host == "www.okx.com" and path == "/api/v5/market/candles":
            return httpx.Response(200, json={"code": "0", "data": [
                [str(NOW - 3600000), "1.5", "2", "1", "1.8", "100", "10", "18", "0"],
                [str(NOW - 7200000), "1", "2", "0.5", "1.5", "100", "10", "15", "1"]]})
        if host == "www.okx.com" and path == "/api/v5/market/tickers":
            return httpx.Response(200, json={"code": "0", "data": [
                {"instId": "BTC-USDT-SWAP", "last": "100", "bidPx": "99.9", "askPx": "100.1", "ts": str(NOW),
                 "volCcy24h": "1000"},
                {"instId": "SNDK-USDT-SWAP", "last": "100", "bidPx": "1", "askPx": "1", "ts": str(NOW),
                 "volCcy24h": "99999"}]})
        if host == "www.okx.com" and path == "/api/v5/public/instruments":
            return httpx.Response(200, json={"code": "0", "data": [
                {"instId": "BTC-USDT-SWAP", "instCategory": "1"}, {"instId": "SNDK-USDT-SWAP", "instCategory": "3"}]})
        if host == "forex-data-feed.swissquote.com":
            return httpx.Response(200, json=[{"ts": NOW, "spreadProfilePrices": [
                {"spreadProfile": "prime", "bid": 1.1, "ask": 1.1002}]}])
        if host == "www.deribit.com":
            return httpx.Response(200, json={"result": {"data": [[NOW, 40, 41, 39, 40.5]]}})
        return httpx.Response(404)
    return h


@pytest.fixture
def client(monkeypatch):
    http = Http(httpx.Client(transport=httpx.MockTransport(handler())), cooldown=60)
    monkeypatch.delenv("TWELVEDATA_API_KEY", raising=False)
    return TestClient(appmod.create_app(http, start_background=False)), http


def test_health(client):
    c, _ = client
    r = c.get("/health").json()
    assert r["ok"] and r["twelvedata_key"] is False


def test_klines_fall_back_to_okx_when_binance_blocked(client):
    c, http = client
    r = c.get("/crypto/klines?symbol=BTCUSDT&tf=1h&limit=2").json()
    assert r["source"] == "okx-swap"
    assert [x["closed"] for x in r["candles"]] == [True, False]  # sorted oldest first, live bar flagged
    assert http.status()["binance"]["last_error"] == "HTTP 451"


def test_binance_used_when_reachable():
    http = Http(httpx.Client(transport=httpx.MockTransport(handler(blocked=()))))
    c = TestClient(appmod.create_app(http, start_background=False))
    r = c.get("/crypto/klines?symbol=BTCUSDT&tf=1h&limit=2").json()
    assert r["source"] == "binance-futures" and r["candles"][-1]["closed"] is False


def test_top_excludes_stock_perps(client):
    c, _ = client
    assert c.get("/crypto/top?n=5").json() == ["BTCUSDT"]


def test_fx_quote_and_exness_suffix(client):
    c, _ = client
    r = c.get("/fx/quote?symbol=XAUUSDm").json()
    assert r["symbol"] == "XAUUSD" and r["source"] == "swissquote" and r["bid"] == 1.1
    assert fx_pair("EUR/USD") == ("EUR", "USD") and okx_swap("ETHUSDT") == "ETH-USDT-SWAP"


def test_fx_klines_fall_back_to_yahoo_without_key(monkeypatch):
    monkeypatch.delenv("TWELVEDATA_API_KEY", raising=False)
    def h(req):
        if req.url.host == "query2.finance.yahoo.com":
            assert req.url.path.endswith("/EURUSD=X")
            return httpx.Response(200, json={"chart": {"result": [{"timestamp": [NOW // 1000 - 7200, NOW // 1000 - 3600],
                "indicators": {"quote": [{"open": [1.1, 1.2], "high": [1.2, 1.3], "low": [1.0, 1.1], "close": [1.15, 1.25], "volume": [0, 0]}]}}]}})
        return httpx.Response(404)
    c = TestClient(appmod.create_app(Http(httpx.Client(transport=httpx.MockTransport(h))), start_background=False))
    r = c.get("/fx/klines?symbol=EURUSD&tf=1h&limit=5").json()
    assert r["source"] == "yahoo" and [x["c"] for x in r["candles"]] == [1.15, 1.25]
    assert c.get("/fx/list").json()["majors"][0] == "EURUSD"


def test_fx_klines_502_when_every_source_fails(client):
    c, _ = client
    assert c.get("/fx/klines?symbol=EURUSD").status_code == 502


def test_fx_recorder_builds_candles(client):
    c, _ = client
    rec = c.app.state.recorder
    rec.tick(); rec.tick()
    r = c.get("/fx/recorded?symbol=EURUSD&tf=1m").json()
    assert len(r["candles"]) == 1 and r["candles"][0]["ticks"] == 2


def test_bad_input_rejected(client):
    c, _ = client
    assert c.get("/crypto/klines?symbol=BTC;rm&tf=1h").status_code == 400
    assert c.get("/crypto/klines?symbol=BTCUSDT&tf=7m").status_code == 400
    assert c.get("/crypto/klines?symbol=BTCUSDT&limit=5000").status_code == 422


def test_dvol(client):
    c, _ = client
    assert c.get("/options/dvol?currency=BTC&hours=2").json()["last"] == 40.5


def test_token_required_when_set(monkeypatch):
    monkeypatch.setattr(appmod, "TOKEN", "s3cret")
    http = Http(httpx.Client(transport=httpx.MockTransport(handler())))
    c = TestClient(appmod.create_app(http, start_background=False))
    assert c.get("/crypto/top").status_code == 401
    assert c.get("/crypto/top", headers={"Authorization": "Bearer s3cret"}).status_code == 200
    assert c.get("/health").status_code == 200


def test_public_bind_without_token_refused(monkeypatch):
    monkeypatch.setattr(appmod, "HOST", "0.0.0.0")
    monkeypatch.setattr(appmod, "TOKEN", "")
    with pytest.raises(SystemExit):
        appmod.create_app(Http(httpx.Client(transport=httpx.MockTransport(handler()))), start_background=False)


def test_signals_without_rules(client, monkeypatch, tmp_path):
    from omega_live import signals
    monkeypatch.setattr(signals, "APPROVED", tmp_path / "none.json")
    c, _ = client
    assert c.get("/signals").json()["rules"] == []


def test_dns_rebinding_host_refused_without_token(client):
    c, _ = client
    assert c.get("/health", headers={"Host": "evil.example"}).status_code == 400
    assert c.get("/health").status_code == 200


def test_provider_errors_never_echo_the_twelvedata_key(monkeypatch):
    monkeypatch.setenv("TWELVEDATA_API_KEY", "TDKEY1234567890")
    def h(req):
        if req.url.host == "api.twelvedata.com":
            return httpx.Response(200, json={"status": "error", "message": "bad key TDKEY1234567890"})
        return httpx.Response(503)
    c = TestClient(appmod.create_app(Http(httpx.Client(transport=httpx.MockTransport(h))), start_background=False))
    r = c.get("/fx/klines?symbol=EURUSD&tf=1h")
    assert r.status_code == 502 and "TDKEY1234567890" not in r.text
