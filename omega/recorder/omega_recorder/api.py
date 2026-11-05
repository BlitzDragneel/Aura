import gzip, hmac, json, time
from contextlib import asynccontextmanager
import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Header, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from . import __version__
from .config import Settings
from .db import DB
from .binance import Binance
from .jobs import Recorder
from . import signals, exports

HOUR = 3_600_000
JOBS = {"exchange_info": 6 * 3600, "watchlist": 3600, "klines_1h": 3600, "klines_1m": 300, "premium": 300, "funding": 8 * 3600,
        "oi_ratios": 3600, "depth": 60}

def ms(d):
    try: return int(np.datetime64(d, "ms").astype(np.int64))
    except (ValueError, TypeError, OverflowError): raise HTTPException(400, f"not a date: {str(d)[:40]!r} (use 2026-11-01 or 2026-11-01T13:30)")

MAX_EXPORT_DAYS = 400          # one request cannot ask the server to load years of 1-minute rows into memory

def create_app(settings=None, db=None, start_jobs=None):
    s = settings or Settings(); db = db or DB(s.db_path)
    st = dict(rec=None)

    @asynccontextmanager
    async def life(app):
        if (s.jobs_enabled if start_jobs is None else start_jobs):
            st["rec"] = Recorder(db, Binance(s.rest), s); st["rec"].start()
        yield
        if st["rec"]: await st["rec"].stop()

    def need_read(request: Request):
        """Optional: with OMEGA_READ_TOKEN set, every endpoint except /health needs it (X-Token or ?token=)."""
        rt = getattr(s, "read_token", "") or ""
        if not rt or request.url.path == "/health": return
        got = request.headers.get("x-token") or request.query_params.get("token") or ""
        ok = hmac.compare_digest(got.encode(), rt.encode()) or (s.token and hmac.compare_digest(got.encode(), s.token.encode()))
        if not ok: raise HTTPException(401, "read access needs the X-Token header (OMEGA_READ_TOKEN)")

    app = FastAPI(title="OMEGA Recorder", version=__version__, lifespan=life, dependencies=[Depends(need_read)],
                  description="Records public Binance USDT-M market data for OMEGA research. Paper only: no keys, no orders.")
    app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in s.cors.split(",")], allow_methods=["GET", "POST", "DELETE"],
                       allow_headers=["*"])
    app.state.db = db; app.state.settings = s

    def need_token(tok):
        if not s.token or not hmac.compare_digest((tok or "").encode(), s.token.encode()): raise HTTPException(401, "write access needs the X-Token header (OMEGA_TOKEN)")

    def rng(start, end, default_days):
        e = ms(end) if end else int(time.time() * 1000); b = ms(start) if start else e - default_days * 86400_000
        return b, e

    @app.get("/health")
    def health():
        now = int(time.time() * 1000); out = {}
        for j, period in JOBS.items():
            last = db.one("SELECT * FROM job_runs WHERE job=? ORDER BY started DESC LIMIT 1", (j,))
            ok = db.one("SELECT max(finished) f FROM job_runs WHERE job=? AND ok=1", (j,))["f"]
            late = ok is None or now - ok > 2.5 * period * 1000
            out[j] = dict(last_ok=ok, last_error=(last or {}).get("error") if last and not last["ok"] else None, late=late)
        liq = db.one("SELECT max(t) t FROM liquidations")["t"]
        counts = {t: db.one(f"SELECT count(*) n FROM {t}")["n"] for t in ("symbols", "k1h", "k1m", "funding", "premium", "oi", "ratios", "liquidations", "depth", "events")}
        trading = db.one("SELECT count(*) n FROM symbols WHERE status='TRADING'")["n"]
        gaps = db.q("""SELECT sym, max(t) last FROM k1h WHERE sym IN (SELECT sym FROM symbols WHERE status='TRADING')
                       GROUP BY sym HAVING max(t) < ?""", (now - 3 * HOUR,))
        status = "ok" if not any(v["late"] for v in out.values()) and not gaps else "attention"
        return dict(status=status, version=__version__, paper_only=True, jobs=out, last_liquidation=liq, rows=counts,
                    trading_symbols=trading, hourly_behind=[g["sym"] for g in gaps][:50], hourly_behind_count=len(gaps))

    @app.get("/symbols")
    def symbols(include_delisted: bool = True):
        q = "SELECT * FROM symbols" + ("" if include_delisted else " WHERE status='TRADING'") + " ORDER BY sym"
        return db.q(q)

    @app.get("/listings")
    def listings(): return db.q("SELECT * FROM listing_events ORDER BY ts DESC LIMIT 500")

    @app.get("/candles")
    def candles(sym: str, tf: str = Query("1h", pattern="^(1h|1m)$"), start: str | None = None, end: str | None = None):
        b, e = rng(start, end, 30 if tf == "1h" else 1)
        return db.q(f"SELECT t,o,h,l,c,v,qv,n,tbv FROM k{tf} WHERE sym=? AND t BETWEEN ? AND ? ORDER BY t", (sym.upper(), b, e))

    def simple(table, cols, sym, start, end, days, extra=""):
        b, e = rng(start, end, days)
        return db.q(f"SELECT {cols} FROM {table} WHERE sym=? AND t BETWEEN ? AND ? {extra} ORDER BY t", (sym.upper(), b, e))

    @app.get("/funding")
    def funding(sym: str, start: str | None = None, end: str | None = None): return simple("funding", "t,rate,mark,src", sym, start, end, 90)
    @app.get("/premium")
    def premium(sym: str, start: str | None = None, end: str | None = None): return simple("premium", "t,mark,idx,last_rate,next_t", sym, start, end, 2)
    @app.get("/oi")
    def oi(sym: str, start: str | None = None, end: str | None = None): return simple("oi", "t,oi,oi_value", sym, start, end, 7)
    @app.get("/ratios")
    def ratios(sym: str, kind: str = Query("global", pattern="^(global|top_pos|taker)$"), start: str | None = None, end: str | None = None):
        b, e = rng(start, end, 7)
        return db.q("SELECT t,val,a,b FROM ratios WHERE sym=? AND kind=? AND t BETWEEN ? AND ? ORDER BY t", (sym.upper(), kind, b, e))
    @app.get("/depth")
    def depth(sym: str, start: str | None = None, end: str | None = None): return simple("depth", "t,mid,spread_bps,bid05,ask05,bid2,ask2", sym, start, end, 1)
    @app.get("/liquidations")
    def liquidations(sym: str | None = None, start: str | None = None, end: str | None = None):
        b, e = rng(start, end, 1)
        if sym: return db.q("SELECT * FROM liquidations WHERE sym=? AND t BETWEEN ? AND ? ORDER BY t", (sym.upper(), b, e))
        return db.q("""SELECT (t/3600000)*3600000 hour, side, count(*) n, sum(price*qty) notional FROM liquidations
                       WHERE t BETWEEN ? AND ? GROUP BY hour, side ORDER BY hour""", (b, e))

    def load_series(first_ms, last_ms, syms=None):
        syms = syms or [r["sym"] for r in db.q("SELECT DISTINCT sym FROM k1h")]
        out = {}
        for sy in syms:
            # volume-0 candles are missing: the archive keeps writing flat ones at the last price after a delisting
            rows = db.q("SELECT t,h,l,c FROM k1h WHERE sym=? AND t BETWEEN ? AND ? AND v > 0 ORDER BY t", (sy, first_ms, last_ms))
            if len(rows) >= 24 * 31:
                d = signals.dense(rows, first_ms // HOUR, last_ms // HOUR)
                out[sy] = d
        return out

    @app.get("/panic")
    def panic(hours: int = Query(72, ge=1, le=24 * 30)):
        """Share of coins whose 24h return is in their own bottom 10% (H3's breadth), per hour."""
        last = db.one("SELECT max(t) m FROM k1h")["m"]
        if last is None: return dict(hours=[], note="no hourly data yet")
        first = last - (720 + 48 + hours) * HOUR
        br = signals.breadth_of(signals.prep(*v) for v in load_series(first, last).values())
        keep = sorted(h for h in br if h >= last // HOUR - hours)
        return dict(hours=[dict(t=h * HOUR, share=round(br[h], 4)) for h in keep], h3_bar=0.20)

    @app.get("/signals")
    def forward(days: int = Query(30, ge=1, le=365)):
        """The H1 / H3 forward PAPER record since OMEGA_FORWARD_START (Grade B: passed a fair test, unconfirmed)."""
        last = db.one("SELECT max(t) m FROM k1h")["m"]
        if last is None: return dict(trades=[], summary={})
        fs = ms(s.forward_start) // HOUR
        first = (fs - 720 - 200) * HOUR
        trades, _ = signals.forward_record(load_series(first, last), fs, last // HOUR)
        return dict(forward_start=s.forward_start, paper_only=True, summary=signals.summary(trades),
                    trades=[t for t in trades if t["signal_h"] >= last // HOUR - days * 24])

    class Event(BaseModel):
        kind: str = Field(max_length=40, pattern=r"^[A-Za-z0-9_\-]+$"); t: str = Field(max_length=40)
        note: str = Field("", max_length=2000); source: str = Field("", max_length=200)

    @app.get("/events")
    def events(kind: str | None = None):
        return db.q("SELECT * FROM events" + (" WHERE kind=?" if kind else "") + " ORDER BY t", (kind,) if kind else ())
    @app.post("/events")
    def add_event(ev: Event, x_token: str = Header("")):
        need_token(x_token)
        return dict(id=db.run("INSERT INTO events(kind,t,note,source) VALUES(?,?,?,?)", (ev.kind.upper(), ms(ev.t), ev.note, ev.source)))
    @app.delete("/events/{eid}")
    def del_event(eid: int, x_token: str = Header("")):
        need_token(x_token); db.run("DELETE FROM events WHERE id=?", (eid,)); return dict(deleted=eid)

    @app.get("/export/history")
    def export_history(start: str = "2024-01-01", end: str | None = None, syms: str | None = None, include_delisted: bool = True):
        """Hourly candles in the gzipped format OMEGA's research loader reads (omega_history_*_json.gz)."""
        b, e = rng(start, end, 0)
        if e - b > 3 * 366 * 86400_000: raise HTTPException(400, "ask for at most 3 years per export")
        names = [x.strip().upper() for x in syms.split(",")][:500] if syms else [r["sym"] for r in db.q(
            "SELECT sym FROM symbols" + ("" if include_delisted else " WHERE status='TRADING'") + " ORDER BY sym")]
        markets = []
        for sy in names:
            rows = db.q("SELECT t,o,h,l,c,v FROM k1h WHERE sym=? AND t BETWEEN ? AND ? AND v > 0 ORDER BY t", (sy, b, e))
            if rows: markets.append(exports.encode_market(sy, rows))
        status = {r["sym"]: r["status"] for r in db.q("SELECT sym,status FROM symbols")}
        last_traded = {r["sym"]: r["m"] for r in db.q("SELECT sym, max(t) m FROM k1h WHERE v > 0 GROUP BY sym")}
        blob = exports.history_gz(markets, meta=dict(start=start, end=end, status={m["sym"]: status.get(m["sym"]) for m in markets},
                                                                 last_traded={m["sym"]: last_traded.get(m["sym"]) for m in markets}))
        return Response(blob, media_type="application/gzip",
                        headers={"Content-Disposition": f'attachment; filename="omega_history_recorder_{time.strftime("%Y_%m_%d")}_json.gz"'})

    @app.get("/export/table/{table}")
    def export_table(table: str, start: str | None = None, end: str | None = None):
        if table not in ("funding", "premium", "oi", "ratios", "liquidations", "depth", "k1m", "listing_events", "events"):
            raise HTTPException(404, "unknown table")
        col = "ts" if table == "listing_events" else "t"
        b, e = rng(start, end, 3650 if table in ("listing_events", "events", "funding") else 30)
        if table not in ("listing_events", "events", "funding") and e - b > MAX_EXPORT_DAYS * 86400_000: raise HTTPException(400, f"ask for at most {MAX_EXPORT_DAYS} days of {table} per export")
        rows = db.q(f"SELECT * FROM {table} WHERE {col} BETWEEN ? AND ? ORDER BY {col}", (b, e))
        blob = gzip.compress("\n".join(json.dumps(r) for r in rows).encode())
        return Response(blob, media_type="application/gzip",
                        headers={"Content-Disposition": f'attachment; filename="omega_{table}_{time.strftime("%Y_%m_%d")}.jsonl.gz"'})

    @app.post("/admin/backfill")
    async def admin_backfill(x_token: str = Header(""), syms: str | None = None):
        need_token(x_token)
        if st.get("backfill"): raise HTTPException(409, "a backfill is already running")
        import asyncio, httpx
        from .archive import backfill
        async def job():
            t0 = int(time.time() * 1000)
            try:
                async with httpx.AsyncClient(timeout=60) as c:
                    n, k = await backfill(db, c, s, set(syms.upper().split(",")) if syms else None, log=lambda *_: None)
                db.job("archive_backfill", t0, True, n)
            except Exception as ex:
                db.job("archive_backfill", t0, False, 0, f"{type(ex).__name__}: {ex}"[:500])
            finally:
                st["backfill"] = None
        st["backfill"] = asyncio.create_task(job())
        return dict(started=True, note="watch /health → rows, or GET /jobs?job=archive_backfill")

    @app.get("/jobs")
    def jobs(job: str | None = None, limit: int = Query(50, ge=1, le=1000)):
        if job: return db.q("SELECT * FROM job_runs WHERE job=? ORDER BY started DESC LIMIT ?", (job, limit))
        return db.q("SELECT * FROM job_runs ORDER BY started DESC LIMIT ?", (limit,))

    return app

app = None
def get_app():
    global app
    app = app or create_app(); return app
