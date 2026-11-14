import time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from omega_live.auditor import router


class FakePrices:
    def bars(self, sym, start_ms, hours):
        t0 = start_ms - start_ms % 60_000 + 60_000
        path = [(100, 100.5, 99.8, 100), (100, 102.5, 99.5, 102)] + [(102, 102.2, 101.8, 102)] * 5
        return [dict(t=t0 + i * 60_000, o=o, h=h, l=l, c=c) for i, (o, h, l, c) in enumerate(path)], "fake"


def client():
    app = FastAPI()
    app.include_router(router(None, FakePrices()))
    return TestClient(app)


def test_parse_and_score():
    c = client()
    p = c.post("/auditor/parse", json=dict(text="XAUUSD BUY NOW SL 99 TP 102", provider="Terry")).json()
    sig = p["signal"]
    sig["logged_ms"] = int(time.time() * 1000) - 3_600_000
    r = c.post("/auditor/score", json=dict(signals=[sig])).json()
    assert r["scored"][0]["tp1"]["outcome"] == "TP1" and r["summary"]["closed"] == 1 and "Terry" in r["by_provider"]


def test_bad_input():
    c = client()
    assert c.post("/auditor/parse", json=dict(text="hello")).status_code == 422
    r = c.post("/auditor/score", json=dict(signals=[dict(symbol="XAUUSD", side="up", logged_ms=1)])).json()
    assert r["scored"][0]["status"] == "error"
    assert c.post("/auditor/risk", json=dict(balance=500, positions=[dict(symbol="XAUUSD", lots=0.1)])).json()["by_symbol"][0]["usd_per_1_move"] == 10
