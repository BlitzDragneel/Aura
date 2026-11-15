import datetime as dt
from fastapi import FastAPI
from fastapi.testclient import TestClient
from omega_live.alerts import router, parse


class Fake:
    def __init__(self, md): self.md, self.posts = md, []
    def get(self, url, **k):
        class R: status_code = 200
        R.text = self.md; return R
    def post(self, url, json=None, **k):
        self.posts.append(json["text"])
        class R: status_code = 200
        return R


def test_pump(monkeypatch):
    now = dt.datetime.now(dt.timezone.utc)
    md = f"\n## {now - dt.timedelta(hours=3):%Y-%m-%d %H:%M:%S} UTC\nold\n\n## {now - dt.timedelta(minutes=2):%Y-%m-%d %H:%M:%S} UTC\nfresh one\nline2\n"
    assert len(parse(md)) == 2
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x"); monkeypatch.setenv("TELEGRAM_CHAT_ID", "1")
    f = Fake(md); app = FastAPI(); app.include_router(router(f)); c = TestClient(app)
    assert c.get("/alerts/pump", params=dict(sha="a" * 40)).json()["forwarded"] == 1 and f.posts == ["fresh one\nline2"]
    assert c.get("/alerts/pump", params=dict(sha="a" * 40)).json()["forwarded"] == 0      # not sent twice
    assert c.get("/alerts/pump", params=dict(sha="zz")).status_code == 422
