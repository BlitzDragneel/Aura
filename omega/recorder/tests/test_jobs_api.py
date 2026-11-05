"""Recording jobs and the API against a mocked Binance (the build sandbox cannot reach Binance; run selfcheck on the server)."""
import asyncio, gzip, io, json, time, zipfile
import httpx, numpy as np, respx
from fastapi.testclient import TestClient
import reference_load as L
from synth import market
from omega_recorder.config import Settings
from omega_recorder.db import DB
from omega_recorder.binance import Binance
from omega_recorder.jobs import Recorder
from omega_recorder.api import create_app
from omega_recorder import archive
from test_exports_archive import listing, zipped

REST = "https://fapi.test"
H = 3_600_000

def settings(tmp_path, **kw):
    s = Settings(); s.db_path = str(tmp_path / "t.sqlite"); s.rest = REST; s.archive = "https://arch.test"
    s.archive_list = "https://list.test"; s.token = "secret-test"; s.watch_n = 2; s.depth_n = 1
    for k, v in kw.items(): setattr(s, k, v)
    return s

def sym(name, status="TRADING"):
    return dict(symbol=name, quoteAsset="USDT", status=status, contractType="PERPETUAL", onboardDate=1, deliveryDate=4133404800000,
                filters=[dict(filterType="MIN_NOTIONAL", notional="5"), dict(filterType="PRICE_FILTER", tickSize="0.1")])

def kl(t, c): return [t, str(c), str(c * 1.01), str(c * 0.99), str(c), "10", t + H - 1, "1000", 5, "4", "400", "0"]

@respx.mock
def test_jobs_record_symbols_delistings_candles_and_market_data(tmp_path):
    s = settings(tmp_path); db = DB(s.db_path)
    async def go():
        async with httpx.AsyncClient() as c:
            rec = Recorder(db, Binance(REST, c), s)
            respx.get(f"{REST}/fapi/v1/exchangeInfo").mock(return_value=httpx.Response(200, json=dict(symbols=[sym("AAAUSDT"), sym("BBBUSDT"), sym("CCCUSDT")])))
            await rec.exchange_info()
            # BBB moves to SETTLING, CCC disappears: both are delistings, recorded with the time
            respx.get(f"{REST}/fapi/v1/exchangeInfo").mock(return_value=httpx.Response(200, json=dict(symbols=[sym("AAAUSDT"), sym("BBBUSDT", "SETTLING")])))
            await rec.exchange_info()
            now_h = int(time.time() * 1000) // H * H
            respx.get(f"{REST}/fapi/v1/klines").mock(side_effect=lambda req: httpx.Response(200, json=[kl(now_h - 2 * H, 1.0), kl(now_h - H, 1.1), kl(now_h, 1.2)]))
            n = await rec.klines_1h()
            respx.get(f"{REST}/fapi/v1/ticker/24hr").mock(return_value=httpx.Response(200, json=[dict(symbol="AAAUSDT", quoteVolume="9"), dict(symbol="BBBUSDT", quoteVolume="99")]))
            await rec.watchlist()
            respx.get(f"{REST}/fapi/v1/premiumIndex").mock(return_value=httpx.Response(200, json=[dict(symbol="AAAUSDT", markPrice="1.2", indexPrice="1.19", lastFundingRate="0.0001", nextFundingTime=1)]))
            await rec.premium()
            respx.get(f"{REST}/fapi/v1/depth").mock(return_value=httpx.Response(200, json=dict(bids=[["1.19", "100"]], asks=[["1.21", "100"]])))
            await rec.depth()
            respx.get(f"{REST}/futures/data/openInterestHist").mock(return_value=httpx.Response(200, json=[dict(timestamp=now_h, sumOpenInterest="5", sumOpenInterestValue="6")]))
            for p, extra in (("globalLongShortAccountRatio", {}), ("topLongShortPositionRatio", {}), ("takerlongshortRatio", 1)):
                body = [dict(timestamp=now_h, buySellRatio="1.5", buyVol="3", sellVol="2")] if extra == 1 else [dict(timestamp=now_h, longShortRatio="2", longAccount="0.66", shortAccount="0.33")]
                respx.get(f"{REST}/futures/data/{p}").mock(return_value=httpx.Response(200, json=body))
            await rec.oi_and_ratios()
            return n, now_h
    n, now_h = asyncio.run(go())
    st = {r["sym"]: r for r in db.q("SELECT * FROM symbols")}
    assert st["BBBUSDT"]["status"] == "SETTLING" and st["BBBUSDT"]["delisted_at"] and st["CCCUSDT"]["status"] == "GONE" and st["CCCUSDT"]["delisted_at"]
    ev = {(r["sym"], r["new_status"]) for r in db.q("SELECT * FROM listing_events")}
    assert ev == {("BBBUSDT", "SETTLING"), ("CCCUSDT", "GONE")}
    ts = [r["t"] for r in db.q("SELECT t FROM k1h WHERE sym='AAAUSDT' ORDER BY t")]
    assert ts == [now_h - 2 * H, now_h - H]                         # the still-forming candle is not stored
    assert db.one("SELECT count(*) n FROM depth")["n"] == 1 and db.one("SELECT count(*) n FROM ratios")["n"] == 3
    assert db.one("SELECT oi FROM oi")["oi"] == 5.0

def test_liquidation_message_parsing(tmp_path):
    s = settings(tmp_path); rec = Recorder(DB(s.db_path), None, s)
    msg = {"e": "forceOrder", "o": {"s": "BTCUSDT", "S": "SELL", "q": "0.014", "p": "9910", "ap": "9910", "X": "FILLED", "T": 1568014460893}}
    assert rec.liquidation_rows(msg) == [("BTCUSDT", 1568014460893, "SELL", 9910.0, 0.014, 9910.0, "FILLED")]

@respx.mock
def test_rate_limit_backs_off_instead_of_hammering(tmp_path):
    async def go():
        async with httpx.AsyncClient() as c:
            bx = Binance(REST, c)
            respx.get(f"{REST}/fapi/v1/premiumIndex").mock(return_value=httpx.Response(429, headers={"retry-after": "30"}))
            try: await bx.premium_all(); return "no error"
            except RuntimeError as e: first = str(e)
            try: await bx.premium_all(); return "no error"
            except RuntimeError as e: return first, str(e), respx.calls.call_count
    a, b, calls = asyncio.run(go())
    assert "429" in a and "back-off" in b and calls == 1             # second call refused locally, Binance not hit again

@respx.mock
def test_archive_backfill_includes_delisted_symbols(tmp_path):
    s = settings(tmp_path); db = DB(s.db_path)
    root = "data/futures/um/monthly/klines/"
    def lst(req):
        pre = req.url.params["prefix"]
        if pre == root: return httpx.Response(200, text=listing([root + "LIVEUSDT/", root + "DEADUSDT/", root + "BTCBUSD/"]))
        if pre.endswith("/1h/"): sy = pre.split("/")[-3]; return httpx.Response(200, text=listing([], [f"{pre}{sy}-1h-2024-01.zip", f"{pre}{sy}-1h-2019-12.zip"]))
        sy = pre.split("/")[-2]; return httpx.Response(200, text=listing([], [f"{pre}{sy}-fundingRate-2024-01.zip"]))
    respx.get("https://list.test").mock(side_effect=lst)
    respx.get(url__regex=r"https://arch\.test/.*1h-2024-01\.zip").mock(return_value=httpx.Response(200, content=zipped(
        "1704067200000,1,1.1,0.9,1.05,10,1704070799999,10,3,5,5,0\n1704070800000,1.05,1.2,1,1.1,10,1704074399999,10,3,5,5,0\n")))
    respx.get(url__regex=r"https://arch\.test/.*fundingRate.*").mock(return_value=httpx.Response(200, content=zipped(
        "calc_time,funding_interval_hours,last_funding_rate\n1704067200000,8,0.0001\n")))
    async def go():
        async with httpx.AsyncClient() as c:
            r1 = await archive.backfill(db, c, s, log=lambda *_: None)
            r2 = await archive.backfill(db, c, s, log=lambda *_: None)     # second run fetches nothing new
            return r1, r2
    (n1, k1), (n2, _) = asyncio.run(go())
    assert k1 == 2 and n1 == 2 * 2 + 2 and n2 == 0                      # 2 USDT symbols (BUSD skipped), 2019 file skipped
    assert {r["sym"] for r in db.q("SELECT DISTINCT sym FROM k1h")} == {"LIVEUSDT", "DEADUSDT"}
    assert db.one("SELECT status FROM symbols WHERE sym='DEADUSDT'")["status"] == "ARCHIVE_ONLY"

def seed_hourly(db, n_coins=12, n=2400, start_h=473_352):
    from omega_recorder.db import kline_sql
    for i in range(n_coins):
        d = market(i, n, start_h)
        rows = [(f"S{i}USDT", int(h) * H, r.o, r.hi, r.lo, r.c, r.v, r.v, 1, r.v / 2, "test") for h, r in d.dropna().iterrows()]
        db.many(kline_sql("k1h", True), rows)
        db.run("INSERT INTO symbols(sym,status,contract) VALUES(?,?,?)", (f"S{i}USDT", "TRADING" if i else "SETTLING", "PERPETUAL"))
    return start_h

def test_api_endpoints(tmp_path):
    s = settings(tmp_path, forward_start="2024-03-01"); db = DB(s.db_path); start_h = seed_hourly(db)
    with TestClient(create_app(s, db, start_jobs=False)) as c:
        h = c.get("/health").json()
        assert h["paper_only"] is True and h["rows"]["k1h"] > 20000 and h["status"] == "attention"   # no jobs ran: says so
        assert len(c.get("/symbols").json()) == 12 and len(c.get("/symbols?include_delisted=false").json()) == 11
        cd = c.get("/candles", params=dict(sym="s1usdt", start="2024-01-02", end="2024-01-03")).json()
        assert len(cd) >= 20 and all(cd[i]["t"] < cd[i + 1]["t"] for i in range(len(cd) - 1))
        # events need the token; nothing is stored without it
        assert c.post("/events", json=dict(kind="cpi", t="2024-02-13T13:30")).status_code == 401
        e = c.post("/events", json=dict(kind="cpi", t="2024-02-13T13:30", source="bls.gov"), headers={"X-Token": "secret-test"}).json()
        assert c.get("/events?kind=CPI").json()[0]["id"] == e["id"]
        # export reads back through the research decoder, delisted coin included, statuses carried
        blob = c.get("/export/history", params=dict(start="2024-01-01")).content
        doc = json.loads(gzip.decompress(blob)); ms_ = [L.dec_market(m, doc["tf"]) for m in doc["markets"]]
        assert len(ms_) == 12 and doc["status"]["S0USDT"] == "SETTLING"
        got = dict(zip(ms_[0]["t"][:3] * 3_600_000, ms_[0]["c"][:3])); want = {r["t"]: r["c"] for r in db.q("SELECT t,c FROM k1h WHERE sym='S0USDT' ORDER BY t LIMIT 3")}
        assert all(abs(got[k] / want[k] - 1) < 2e-6 for k in want)
        p = c.get("/panic?hours=48").json()
        assert len(p["hours"]) >= 40 and all(0 <= x["share"] <= 1 for x in p["hours"])
        sg = c.get("/signals?days=365").json()
        assert sg["paper_only"] and sg["trades"] and set(sg["summary"]) <= {"H1 limit k2 W3", "H3 q5 breadth>=20%"}
        assert all(t["signal_h"] >= 473_352 + 60 * 24 for t in sg["trades"])                 # nothing before forward start
        assert c.get("/export/table/oi").status_code == 200 and c.get("/export/table/symbols").status_code == 404
        assert c.post("/admin/backfill").status_code == 401

def test_flat_zero_volume_candles_after_delisting_are_missing(tmp_path):
    """The archive's flat volume-0 candles after a delisting must not count as candles (or as panics in H3's breadth)."""
    from omega_recorder.db import kline_sql
    s = settings(tmp_path); db = DB(s.db_path); start_h = seed_hourly(db, n_coins=8, n=1600)
    dead_last = start_h + 1000
    d = market(99, 1001, start_h)
    rows = [("DEADUSDT", int(h) * H, r.o, r.hi, r.lo, r.c, r.v, r.v, 1, r.v / 2, "archive") for h, r in d.dropna().iterrows()]
    last_c = float(d.dropna().c.iloc[-1])
    rows += [("DEADUSDT", (dead_last + k) * H, last_c, last_c, last_c, last_c, 0.0, 0.0, 0, 0.0, "archive") for k in range(1, 600)]
    db.many(kline_sql("k1h", True), rows); db.run("INSERT INTO symbols(sym,status) VALUES('DEADUSDT','ARCHIVE_ONLY')")
    with TestClient(create_app(s, db, start_jobs=False)) as c:
        doc = json.loads(gzip.decompress(c.get("/export/history", params=dict(start="2024-01-01")).content))
        m = [x for x in doc["markets"] if x["sym"] == "DEADUSDT"][0]
        assert sum(m["t"]) * H <= dead_last * H and doc["last_traded"]["DEADUSDT"] // H <= dead_last
        p1 = c.get("/panic?hours=200").json()["hours"]
    with TestClient(create_app(s, db, start_jobs=False)) as c2:
        db.run("DELETE FROM k1h WHERE sym='DEADUSDT' AND v = 0")
        p2 = c2.get("/panic?hours=200").json()["hours"]
    assert p1 == p2                              # the flat candles change nothing
