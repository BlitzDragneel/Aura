"""Academy paywall: free lessons public, premium only with a token from a verified license (Gumroad mocked)."""
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from omega_live import academy, app as appmod
from omega_live.providers import Http

COURSE = {"title": "T", "version": "1", "disclaimer": "D", "modules": [
    {"id": "m01", "title": "Start", "free": True, "lessons": [{"id": "m01-l01", "title": "a", "minutes": 5, "body_md": "FREE TEXT"}]},
    {"id": "m03", "title": "Charts", "free": False, "lessons": [
        {"id": "m03-l01", "title": "preview", "minutes": 5, "free": True, "body_md": "PREVIEW TEXT"},
        {"id": "m03-l02", "title": "paid", "minutes": 9, "body_md": "SECRET PREMIUM TEXT"}]}]}


@pytest.fixture
def client(tmp_path, monkeypatch):
    (tmp_path / "course.json").write_text(json.dumps(COURSE))
    (tmp_path / "pricing.json").write_text(json.dumps({"launch_price": 49, "regular_price": 97, "checkout_url": ""}))
    monkeypatch.setattr(academy, "ACADEMY", tmp_path)
    monkeypatch.setenv("ACADEMY_SECRET", "s" * 32)
    monkeypatch.setenv("ACADEMY_GUMROAD_PRODUCT_ID", "prod123")
    monkeypatch.delenv("ACADEMY_KEYS", raising=False)

    def gum(req: httpx.Request):
        f = dict(x.split("=") for x in req.content.decode().split("&"))
        if f.get("license_key") == "GOOD-KEY" and f.get("product_id") == "prod123":
            return httpx.Response(200, json={"success": True, "purchase": {"refunded": False}})
        if f.get("license_key") == "REFUNDED":
            return httpx.Response(200, json={"success": True, "purchase": {"refunded": True}})
        return httpx.Response(404, json={"success": False})
    real = academy.router
    monkeypatch.setattr(appmod, "__name__", appmod.__name__)
    gclient = httpx.Client(transport=httpx.MockTransport(gum))
    monkeypatch.setattr(academy, "router", lambda http_client=None: real(gclient))
    http = Http(httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(404))))
    return TestClient(appmod.create_app(http, start_background=False))


def test_catalog_has_free_bodies_only(client):
    c = client.get("/academy/catalog").json()
    text = json.dumps(c)
    assert "FREE TEXT" in text and "PREVIEW TEXT" in text and "SECRET PREMIUM TEXT" not in text
    assert c["pricing"]["launch_price"] == 49 and c["unlock_open"] is True


def test_premium_needs_token(client):
    assert client.get("/academy/lesson/m03-l02").status_code == 402
    assert client.get("/academy/lesson/m03-l01").json()["body_md"] == "PREVIEW TEXT"
    assert client.get("/academy/lesson/m03-l02", headers={"X-Academy-Token": "forged.token"}).status_code == 402


def test_unlock_with_good_key_then_read(client):
    r = client.post("/academy/unlock", json={"license_key": "GOOD-KEY"})
    assert r.status_code == 200
    tok = r.json()["token"]
    les = client.get("/academy/lesson/m03-l02", headers={"X-Academy-Token": tok}).json()
    assert les["body_md"] == "SECRET PREMIUM TEXT"


def test_bad_and_refunded_keys_refused(client):
    assert client.post("/academy/unlock", json={"license_key": "WRONG"}).status_code == 403
    r = client.post("/academy/unlock", json={"license_key": "REFUNDED"})
    assert r.status_code == 403 and "refunded" in r.json()["detail"]


def test_tampered_token_refused(client):
    tok = client.post("/academy/unlock", json={"license_key": "GOOD-KEY"}).json()["token"]
    body, mac = tok.rsplit(".", 1)
    bad = body[:-2] + ("AA" if body[-2:] != "AA" else "BB") + "." + mac
    assert client.get("/academy/lesson/m03-l02", headers={"X-Academy-Token": bad}).status_code == 402


def test_unlock_rate_limited(client):
    for _ in range(10):
        client.post("/academy/unlock", json={"license_key": "WRONG"})
    assert client.post("/academy/unlock", json={"license_key": "GOOD-KEY"}).status_code == 429
