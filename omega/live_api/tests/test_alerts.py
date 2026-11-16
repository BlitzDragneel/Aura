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


def test_kind():
    from omega_live.alerts import kind
    assert kind("⚡ Gold: BREAKOUT\n🧪 PAPER\nGold SELL now ~1\nSL 2\nTP1 0") == "signal"
    assert kind("❌ Silver SELL (fib pullback) closed: SL, -1.11R") == "signal"
    assert kind("🔁 Learning: breakout with the trend is now MUTED") == "signal"
    assert kind("⏰ US news in 30 min: CPI") == "info"
    assert kind("🌅 OMEGA morning read") == "info"
    assert kind("⚡ Silver: PULLBACK\nℹ️ No trade plan: on past data ...") == "info"


def test_info_off(monkeypatch):
    import datetime as dt
    now = dt.datetime.now(dt.timezone.utc)
    md = f"\n## {now:%Y-%m-%d %H:%M:%S} UTC\n⏰ US news in 30 min: CPI\n\n## {now:%Y-%m-%d %H:%M:%S} UTC\nGold SELL now ~1\nSL 2\n"
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "x"); monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100"); monkeypatch.setenv("TELEGRAM_INFO_CHAT_ID", "off")
    f = Fake(md); app = FastAPI(); app.include_router(router(f)); c = TestClient(app)
    c.get("/alerts/pump", params=dict(sha="b" * 40))
    assert f.posts == ["Gold SELL now ~1\nSL 2"]
