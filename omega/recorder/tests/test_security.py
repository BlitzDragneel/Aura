"""Security review (Nov 2026): tokens compared in constant time, optional read token, input limits, bounded exports."""
from fastapi.testclient import TestClient
from omega_recorder.db import DB
from omega_recorder.api import create_app
from test_jobs_api import settings

def app(tmp_path, **kw):
    s = settings(tmp_path, **kw); return TestClient(create_app(s, DB(s.db_path), start_jobs=False))

def test_write_token_and_input_limits(tmp_path):
    with app(tmp_path) as c:
        T = {"X-Token": "secret-test"}
        assert c.post("/events", json=dict(kind="cpi", t="2024-02-13"), headers={"X-Token": "secret-tesX"}).status_code == 401
        assert c.post("/events", json=dict(kind="cpi", t="2024-02-13"), headers={"X-Token": ""}).status_code == 401
        assert c.post("/events", json=dict(kind="cpi", t="2024-02-13", note="x" * 5000), headers=T).status_code == 422
        assert c.post("/events", json=dict(kind="<script>", t="2024-02-13"), headers=T).status_code == 422
        assert c.post("/events", json=dict(kind="cpi", t="not-a-date"), headers=T).status_code == 400
        assert c.delete("/events/1").status_code == 401 and c.post("/admin/backfill").status_code == 401

def test_no_write_token_configured_means_no_writes(tmp_path):
    with app(tmp_path, token="") as c:
        assert c.post("/events", json=dict(kind="cpi", t="2024-02-13"), headers={"X-Token": ""}).status_code == 401

def test_bad_dates_and_huge_ranges_are_400_not_500(tmp_path):
    with app(tmp_path) as c:
        assert c.get("/candles", params=dict(sym="BTCUSDT", start="1'; DROP TABLE k1h;--")).status_code == 400
        assert c.get("/export/table/k1m", params=dict(start="2015-01-01")).status_code == 400
        assert c.get("/export/history", params=dict(start="2015-01-01")).status_code == 400
        assert c.get("/export/table/..%2F..%2Fetc%2Fpasswd").status_code == 404
        assert c.get("/export/table/sqlite_master").status_code == 404
        assert c.get("/jobs", params=dict(limit=10**9)).status_code == 422
        assert c.get("/health").status_code == 200

def test_optional_read_token(tmp_path):
    with app(tmp_path, read_token="read-test") as c:
        assert c.get("/health").status_code == 200                     # health stays open for uptime checks
        assert c.get("/symbols").status_code == 401 and c.get("/export/table/funding").status_code == 401
        assert c.get("/symbols", headers={"X-Token": "read-test"}).status_code == 200
        assert c.get("/symbols", params=dict(token="read-test")).status_code == 200
        assert c.get("/symbols", headers={"X-Token": "secret-test"}).status_code == 200   # the write token reads too
