"""OMEGA Live API - live crypto, forex/metals and options data for the OMEGA apps, one local service.

Run:  python -m omega_live            (binds 127.0.0.1:8787)
Env:  OMEGA_API_HOST / OMEGA_API_PORT
      OMEGA_API_TOKEN      required whenever the host is not 127.0.0.1 (send header  Authorization: Bearer <token>)
      OMEGA_API_ORIGINS    extra allowed browser origins, comma separated (file:// pages send Origin "null"; allowed)
      TWELVEDATA_API_KEY   optional, enables forex candles and a forex fallback
      OMEGA_FX_RECORD      symbols to record from live quotes, default "EURUSD,GBPUSD,USDJPY,XAUUSD"
Read-only: this service never places orders and holds no exchange keys.
"""
from __future__ import annotations

import asyncio
import hmac
import json
import os
import threading
import time
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import StreamingResponse

from . import __version__
from .providers import FX, TF, TF_MS, Crypto, Http, Options, ProviderError
from .signals import LiveSignals, approved_rules

HOST = os.environ.get("OMEGA_API_HOST", "127.0.0.1")
TOKEN = os.environ.get("OMEGA_API_TOKEN", "")
SYM_RE = __import__("re").compile(r"^[A-Za-z0-9/_\-]{2,20}$")


def check_symbol(s: str) -> str:
    if not SYM_RE.match(s or ""):
        raise HTTPException(400, "bad symbol")
    return s


class TTLCache:
    def __init__(self):
        self.d: dict = {}
        self.lock = threading.Lock()

    def get(self, key, ttl, fn):
        now = time.time()
        with self.lock:
            hit = self.d.get(key)
            if hit and now - hit[0] < ttl:
                return hit[1]
        val = fn()
        with self.lock:
            self.d[key] = (now, val)
            if len(self.d) > 2000:
                for k in sorted(self.d, key=lambda k: self.d[k][0])[:500]:
                    del self.d[k]
        return val


class FXRecorder:
    """Builds 1-minute candles from live forex quotes, for when no Twelve Data key is set."""

    def __init__(self, fx: FX, symbols: list[str], every_s: float = 5.0, keep_minutes: int = 6 * 24 * 60):
        self.fx, self.symbols, self.every = fx, symbols, every_s
        self.bars: dict[str, deque] = defaultdict(lambda: deque(maxlen=keep_minutes))
        self.started = int(time.time() * 1000)
        self._stop = threading.Event()

    def tick(self):
        for s in self.symbols:
            try:
                q = self.fx.quote(s)
            except (ProviderError, ValueError):
                continue
            p, m = q["price"], (q["ts"] // 60_000) * 60_000
            dq = self.bars[q["symbol"]]
            if dq and dq[-1]["t"] == m:
                b = dq[-1]
                b["h"], b["l"], b["c"], b["n"] = max(b["h"], p), min(b["l"], p), p, b["n"] + 1
            else:
                if dq:
                    dq[-1]["closed"] = True
                dq.append(dict(t=m, o=p, h=p, l=p, c=p, n=1, closed=False))

    def loop(self):
        while not self._stop.wait(self.every):
            self.tick()

    def start(self):
        threading.Thread(target=self.loop, daemon=True).start()

    def candles(self, sym: str, tf: str):
        step = TF_MS[tf]
        out: dict[int, dict] = {}
        for b in list(self.bars.get(sym.upper(), [])):
            t = (b["t"] // step) * step
            if t not in out:
                out[t] = dict(t=t, o=b["o"], h=b["h"], l=b["l"], c=b["c"], ticks=b["n"])
            else:
                o = out[t]
                o["h"], o["l"], o["c"], o["ticks"] = max(o["h"], b["h"]), min(o["l"], b["l"]), b["c"], o["ticks"] + b["n"]
        rows = [out[k] for k in sorted(out)]
        now = time.time() * 1000
        for r in rows:
            r["closed"] = r["t"] + step <= now
        return rows


def create_app(http: Http | None = None, start_background: bool = True) -> FastAPI:
    if HOST not in ("127.0.0.1", "localhost", "::1") and not TOKEN:
        raise SystemExit("OMEGA_API_TOKEN must be set when OMEGA_API_HOST is not 127.0.0.1")
    http = http or Http()
    crypto, fx, opt = Crypto(http), FX(http), Options(http)
    live = LiveSignals(crypto)
    cache = TTLCache()
    rec = FXRecorder(fx, [s.strip() for s in os.environ.get("OMEGA_FX_RECORD", "EURUSD,GBPUSD,USDJPY,XAUUSD")
                          .split(",") if s.strip()])

    app = FastAPI(title="OMEGA Live API", version=__version__,
                  description="Live crypto, forex/metals and options data for OMEGA. Read-only, places no orders.")
    origins = ["null", "http://localhost", "http://127.0.0.1", "http://localhost:8787", "http://127.0.0.1:8787"]
    origins += [o.strip() for o in os.environ.get("OMEGA_API_ORIGINS", "").split(",") if o.strip()]
    if not TOKEN:
        # No token = loopback only. Refuse any other Host header, so a web page cannot reach this service through
        # DNS rebinding (a hostile name that resolves to 127.0.0.1). OMEGA_API_HOSTS adds names if ever needed.
        hosts = ["127.0.0.1", "localhost", "[::1]", "::1"] + [h.strip() for h in os.environ.get("OMEGA_API_HOSTS", "").split(",") if h.strip()]
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"],
                       allow_headers=["Authorization"], allow_credentials=False)

    def auth(request: Request):
        if not TOKEN:
            return
        got = request.headers.get("authorization", "")
        if not hmac.compare_digest(got, f"Bearer {TOKEN}"):
            raise HTTPException(401, "missing or wrong token")

    def scrub(msg):                       # a provider's message must never carry the Twelve Data key back to a caller
        return msg.replace(fx.key, "***") if fx.key else msg

    def guard(fn):
        try:
            return fn()
        except ValueError as e:
            raise HTTPException(400, scrub(str(e)))
        except ProviderError as e:
            raise HTTPException(502, scrub(f"all providers failed: {e}"))

    def tf_ok(tf):
        if tf not in TF:
            raise HTTPException(400, f"tf must be one of {sorted(TF)}")
        return tf

    if start_background:
        @app.on_event("startup")
        def _start():
            rec.start()

    @app.get("/health")
    def health():
        return dict(ok=True, version=__version__, time=int(time.time() * 1000), providers=http.status(),
                    twelvedata_key=bool(fx.key), fx_recording=rec.symbols, rules=[r.get("id") for r in approved_rules()],
                    auth=bool(TOKEN))

    d = [Depends(auth)]

    @app.get("/crypto/ticker", dependencies=d)
    def crypto_ticker(symbols: str = Query("BTCUSDT,ETHUSDT", max_length=600)):
        syms = [check_symbol(s.strip()) for s in symbols.split(",") if s.strip()][:50]
        return guard(lambda: cache.get(("t", tuple(syms)), 2, lambda: crypto.tickers(syms)))

    @app.get("/crypto/klines", dependencies=d)
    def crypto_klines(symbol: str, tf: str = "1h", limit: int = Query(200, ge=1, le=1000)):
        check_symbol(symbol); tf_ok(tf)
        ttl = min(30, TF_MS[tf] / 1000 / 10)
        return guard(lambda: cache.get(("k", symbol.upper(), tf, limit), ttl, lambda: crypto.klines(symbol, tf, limit)))

    @app.get("/crypto/funding", dependencies=d)
    def crypto_funding(symbol: str = "BTCUSDT"):
        check_symbol(symbol)
        return guard(lambda: cache.get(("f", symbol.upper()), 30, lambda: crypto.funding(symbol)))

    @app.get("/crypto/oi", dependencies=d)
    def crypto_oi(symbol: str = "BTCUSDT"):
        check_symbol(symbol)
        return guard(lambda: cache.get(("oi", symbol.upper()), 30, lambda: crypto.open_interest(symbol)))

    @app.get("/crypto/top", dependencies=d)
    def crypto_top(n: int = Query(30, ge=1, le=200)):
        return guard(lambda: cache.get(("top", n), 300, lambda: crypto.top_by_volume(n)))

    @app.get("/crypto/spot", dependencies=d)
    def crypto_spot(symbol: str = "BTCUSDT"):
        check_symbol(symbol)
        return guard(lambda: cache.get(("s", symbol.upper()), 3, lambda: crypto.spot_price(symbol)))

    @app.get("/crypto/coinbase-premium", dependencies=d)
    def cb_premium(asset: str = "BTC"):
        check_symbol(asset)
        return guard(lambda: cache.get(("cbp", asset.upper()), 10, lambda: crypto.coinbase_premium(asset)))

    @app.get("/fx/quote", dependencies=d)
    def fx_quote(symbol: str = "EURUSD"):
        check_symbol(symbol)
        return guard(lambda: cache.get(("q", symbol.upper()), 2, lambda: fx.quote(symbol)))

    @app.get("/fx/klines", dependencies=d)
    def fx_klines(symbol: str = "EURUSD", tf: str = "1h", limit: int = Query(200, ge=1, le=5000)):
        check_symbol(symbol); tf_ok(tf)
        return guard(lambda: cache.get(("fk", symbol.upper(), tf, limit), 60, lambda: fx.klines(symbol, tf, limit)))

    @app.get("/fx/recorded", dependencies=d)
    def fx_recorded(symbol: str = "EURUSD", tf: str = "1m"):
        check_symbol(symbol); tf_ok(tf)
        return dict(symbol=symbol.upper(), tf=tf, source="swissquote quotes recorded by this service",
                    since=rec.started, candles=rec.candles(symbol.replace("/", ""), tf))

    @app.get("/options/dvol", dependencies=d)
    def options_dvol(currency: str = "BTC", hours: int = Query(48, ge=1, le=24 * 30)):
        check_symbol(currency)
        return guard(lambda: cache.get(("dv", currency.upper(), hours), 60, lambda: opt.dvol(currency, hours)))

    @app.get("/signals", dependencies=d)
    def signals():
        return cache.get(("sig",), 60, live.run)

    @app.get("/stream", dependencies=d)
    async def stream(crypto_symbols: str = "BTCUSDT,ETHUSDT", fx_symbols: str = "EURUSD,XAUUSD",
                     every: float = Query(5, ge=2, le=60)):
        cs = [check_symbol(s.strip()) for s in crypto_symbols.split(",") if s.strip()][:20]
        fs = [check_symbol(s.strip()) for s in fx_symbols.split(",") if s.strip()][:10]

        async def gen():
            for _ in range(int(3600 / every)):  # one hour per connection; EventSource reconnects by itself
                payload = dict(t=int(time.time() * 1000), crypto=[], fx=[], errors=[])
                try:
                    payload["crypto"] = await asyncio.to_thread(
                        lambda: cache.get(("t", tuple(cs)), 2, lambda: crypto.tickers(cs)))
                except ProviderError as e:
                    payload["errors"].append(scrub(str(e)))
                for s in fs:
                    try:
                        payload["fx"].append(await asyncio.to_thread(
                            lambda s=s: cache.get(("q", s.upper()), 2, lambda: fx.quote(s))))
                    except (ProviderError, ValueError) as e:
                        payload["errors"].append(scrub(str(e)))
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(every)
        return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    app.state.recorder, app.state.http = rec, http
    return app
