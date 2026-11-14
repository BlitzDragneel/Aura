"""GET /assets and /assets/{asset}: the BTC / gold / silver desks, from the Station folder or the bot-state branch."""
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from omega_live import app as appmod
from omega_live import assets as assetsmod
from omega_live.providers import Http

DESK = {"asset": "XAU", "name": "Gold", "asof": "2026-11-14T15:49:00+00:00", "read": {"price": 3842.7},
        "horizons": {"day": {"state": "WAIT", "direction": None}, "swing": {"state": "WATCH", "direction": None},
                     "hold": {"state": "WAIT", "direction": None}},
        "open_calls": [], "recent_calls": [], "forward": {}, "notebook": [{"title": "Right now", "lines": ["x"]}]}


def make_client(monkeypatch, remote=None):
    calls = []

    def h(req: httpx.Request):
        calls.append(str(req.url))
        if req.url.host == "raw.githubusercontent.com" and remote is not None:
            name = req.url.path.rsplit("/", 1)[-1]
            if name in remote:
                return httpx.Response(200, json=remote[name])
        return httpx.Response(404)
    real = assetsmod.AssetDesks
    monkeypatch.setattr(appmod, "AssetDesks", lambda: real(httpx.Client(transport=httpx.MockTransport(h))))
    http = Http(httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(404))), cooldown=60)
    return TestClient(appmod.create_app(http, start_background=False)), calls


@pytest.fixture
def no_station(monkeypatch, tmp_path):
    monkeypatch.setenv("OMEGA_STATION_HOME", str(tmp_path / "none"))
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr(assetsmod, "station_home", lambda: None)


def test_desk_from_bot_state_branch(monkeypatch, no_station):
    c, calls = make_client(monkeypatch, {"XAU.json": DESK})
    r = c.get("/assets/XAU")
    assert r.status_code == 200
    d = r.json()
    assert d["available"] and d["source"].startswith("cloud") and d["horizons"]["swing"]["state"] == "WATCH"
    assert "never an order" in d["disclaimer"]
    assert any("/bot-state/assets/XAU.json" in u for u in calls)
    assert c.get("/assets/gold").json()["asset"] == "XAU"          # aliases


def test_desk_from_station_folder(monkeypatch, tmp_path):
    home = tmp_path / "OMEGA-Station"
    (home / "assets").mkdir(parents=True)
    (home / "station.json").write_text("{}")
    (home / "assets" / "XAG.json").write_text(json.dumps(dict(DESK, asset="XAG", name="Silver")))
    monkeypatch.setattr(assetsmod, "station_home", lambda: home)
    c, calls = make_client(monkeypatch)
    d = c.get("/assets/XAG").json()
    assert d["available"] and d["source"].startswith("laptop") and d["name"] == "Silver"
    assert calls == []                                              # nothing fetched from GitHub
    assert c.get("/assets/BTC").json()["available"] is False       # not written yet -> honest note


def test_missing_desk_and_bad_asset(monkeypatch, no_station):
    c, _ = make_client(monkeypatch, {})
    d = c.get("/assets/BTC").json()
    assert d["available"] is False and "not written" in d["note"]
    assert c.get("/assets/DOGE").status_code == 400


def test_index(monkeypatch, no_station):
    c, _ = make_client(monkeypatch, {"INDEX.json": {"XAU": {"price": 1, "states": {"day": "WAIT"}}}})
    d = c.get("/assets").json()
    assert d["available"] and d["XAU"]["states"]["day"] == "WAIT" and set(d["assets"]) == {"BTC", "XAU", "XAG"}


def test_assets_need_token_when_set(monkeypatch, no_station):
    monkeypatch.setattr(appmod, "TOKEN", "s3cret")
    c, _ = make_client(monkeypatch, {"XAU.json": DESK})
    assert c.get("/assets/XAU").status_code == 401
    assert c.get("/assets/XAU", headers={"Authorization": "Bearer s3cret"}).status_code == 200
