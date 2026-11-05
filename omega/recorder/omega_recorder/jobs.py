"""Recording jobs. Each runs on its own loop and logs every run to job_runs, so /health can show what is working."""
import asyncio, time, traceback, json
from .binance import kline_rows, depth_summary
from .db import kline_sql

def now_ms(): return int(time.time() * 1000)

class Recorder:
    def __init__(self, db, bx, settings):
        self.db, self.bx, self.s = db, bx, settings
        self.watch, self.depth_watch = [], []
        self.tasks = []

    async def _wrap(self, name, fn):
        t0 = now_ms()
        try:
            n = await fn(); self.db.job(name, t0, True, n or 0); return n
        except Exception as e:                       # recorded, never fatal: the next run tries again
            self.db.job(name, t0, False, 0, f"{type(e).__name__}: {e}"[:500]); return None

    def trading(self):
        return [r["sym"] for r in self.db.q("SELECT sym FROM symbols WHERE status='TRADING' AND contract='PERPETUAL' ORDER BY sym")]

    # --- jobs -------------------------------------------------------------------------------------------------------
    async def exchange_info(self):
        info = await self.bx.exchange_info(); t = now_ms(); n = 0
        seen = set()
        for s in info.get("symbols", []):
            if s.get("quoteAsset") != "USDT": continue
            sym = s["symbol"]; seen.add(sym); st = s.get("status"); f = {x["filterType"]: x for x in s.get("filters", [])}
            mn = float(f.get("MIN_NOTIONAL", {}).get("notional", 0) or 0); tick = float(f.get("PRICE_FILTER", {}).get("tickSize", 0) or 0)
            old = self.db.one("SELECT status FROM symbols WHERE sym=?", (sym,))
            if old and old["status"] != st:
                self.db.run("INSERT INTO listing_events VALUES(?,?,?,?)", (t, sym, old["status"], st))
            self.db.run("""INSERT INTO symbols(sym,status,contract,onboard,delivery,min_notional,tick,first_seen,last_seen,delisted_at)
                VALUES(?,?,?,?,?,?,?,?,?,NULL) ON CONFLICT(sym) DO UPDATE SET status=excluded.status, contract=excluded.contract,
                onboard=excluded.onboard, delivery=excluded.delivery, min_notional=excluded.min_notional, tick=excluded.tick,
                last_seen=excluded.last_seen, delisted_at=CASE WHEN excluded.status='TRADING' THEN NULL
                WHEN symbols.status='TRADING' THEN excluded.last_seen ELSE symbols.delisted_at END""",
                (sym, st, s.get("contractType"), s.get("onboardDate"), s.get("deliveryDate"), mn, tick, t, t)); n += 1
        for r in self.db.q("SELECT sym,status FROM symbols WHERE status='TRADING'"):   # gone from exchangeInfo = delisted
            if r["sym"] not in seen:
                self.db.run("UPDATE symbols SET status='GONE', delisted_at=? WHERE sym=?", (t, r["sym"]))
                self.db.run("INSERT INTO listing_events VALUES(?,?,?,?)", (t, r["sym"], "TRADING", "GONE"))
        return n

    async def klines_1h(self):
        n = 0; cutoff = now_ms() - 3_600_000
        for sym in self.trading():
            last = self.db.one("SELECT max(t) m FROM k1h WHERE sym=?", (sym,))["m"]
            start = None if last is None else last - 2 * 3_600_000
            raw = await self.bx.klines(sym, "1h", limit=1500 if last is None or last < now_ms() - 4 * 3_600_000 else 4, start=start)
            rows = [r for r in kline_rows(sym, raw, "rest") if r[1] <= cutoff]   # closed candles only
            n += self.db.many(kline_sql("k1h", True), rows)
        return n

    async def watchlist(self):
        tick = await self.bx.ticker24(); tr = set(self.trading())
        ranked = sorted((x for x in tick if x["symbol"] in tr), key=lambda x: -float(x.get("quoteVolume", 0)))
        self.watch = [x["symbol"] for x in ranked[: self.s.watch_n]]
        self.depth_watch = self.watch[: self.s.depth_n]
        return len(self.watch)

    async def klines_1m(self):
        n = 0; cutoff = now_ms() - 60_000
        for sym in self.watch:
            raw = await self.bx.klines(sym, "1m", limit=15)
            n += self.db.many(kline_sql("k1m", False), [r for r in kline_rows(sym, raw) if r[1] <= cutoff])
        return n

    async def premium(self):
        t = now_ms() // 60_000 * 60_000
        rows = [(x["symbol"], t, float(x["markPrice"]), float(x["indexPrice"]), float(x.get("lastFundingRate") or 0),
                 int(x.get("nextFundingTime") or 0)) for x in await self.bx.premium_all() if x["symbol"].endswith("USDT")]
        return self.db.many("INSERT OR REPLACE INTO premium VALUES(?,?,?,?,?,?)", rows)

    async def funding(self):
        n = 0
        for sym in self.trading():
            last = self.db.one("SELECT max(t) m FROM funding WHERE sym=?", (sym,))["m"]
            raw = await self.bx.funding_hist(sym, start=(last + 1) if last else None)
            await asyncio.sleep(0.7)        # fundingRate has its own limit (500 requests / 5 min / IP)
            n += self.db.many("INSERT OR REPLACE INTO funding(sym,t,rate,mark,src) VALUES(?,?,?,?,?)",
                              [(sym, int(x["fundingTime"]), float(x["fundingRate"]), float(x.get("markPrice") or 0) or None, "rest") for x in raw])
        return n

    async def oi_and_ratios(self):
        n = 0
        for sym in self.watch:
            n += self.db.many("INSERT OR REPLACE INTO oi VALUES(?,?,?,?)",
                [(sym, int(x["timestamp"]), float(x["sumOpenInterest"]), float(x["sumOpenInterestValue"])) for x in await self.bx.oi_hist(sym)])
            for kind in ("global", "top_pos", "taker"):
                raw = await self.bx.ratio(kind, sym); rows = []
                for x in raw:
                    if kind == "taker": rows.append((sym, int(x["timestamp"]), kind, float(x["buySellRatio"]), float(x["buyVol"]), float(x["sellVol"])))
                    else: rows.append((sym, int(x["timestamp"]), kind, float(x["longShortRatio"]), float(x["longAccount"]), float(x["shortAccount"])))
                n += self.db.many("INSERT OR REPLACE INTO ratios VALUES(?,?,?,?,?,?)", rows)
        return n

    async def depth(self):
        n = 0; t = now_ms() // 60_000 * 60_000
        for sym in self.depth_watch:
            d = depth_summary(await self.bx.depth(sym))
            if d: n += self.db.many("INSERT OR REPLACE INTO depth VALUES(?,?,?,?,?,?,?,?)",
                                    [(sym, t, d["mid"], d["spread_bps"], d["bid05"], d["ask05"], d["bid2"], d["ask2"])])
        return n

    def liquidation_rows(self, msg):
        o = msg.get("o") or {}
        if not o: return []
        return [(o["s"], int(o["T"]), o["S"], float(o["p"]), float(o["q"]), float(o.get("ap") or 0), o.get("X"))]

    async def liquidations_stream(self):
        """Binance pushes at most the latest liquidation per symbol per second on this stream: a sample, not every one."""
        import websockets
        while True:
            t0 = now_ms()
            try:
                async with websockets.connect(f"{self.s.ws}/!forceOrder@arr", ping_interval=60) as ws:
                    self.db.job("liquidations", t0, True, 0)
                    async for raw in ws:
                        self.db.many("INSERT INTO liquidations VALUES(?,?,?,?,?,?,?)", self.liquidation_rows(json.loads(raw)))
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self.db.job("liquidations", t0, False, 0, f"{type(e).__name__}: {e}"[:500])
            await asyncio.sleep(10)

    # --- scheduling ---------------------------------------------------------------------------------------------------
    async def _every(self, name, fn, period_s, offset_s=0):
        while True:
            await self._wrap(name, fn)
            wait = period_s - (time.time() - offset_s) % period_s
            await asyncio.sleep(max(1.0, wait))

    def start(self):
        async def boot():
            await self._wrap("exchange_info", self.exchange_info); await self._wrap("watchlist", self.watchlist)
        async def go():
            await boot()
            spec = [("exchange_info", self.exchange_info, 6 * 3600, 0), ("watchlist", self.watchlist, 3600, 300),
                    ("klines_1h", self.klines_1h, 3600, 40), ("klines_1m", self.klines_1m, 300, 20),
                    ("premium", self.premium, 300, 10), ("funding", self.funding, 8 * 3600, 600),
                    ("oi_ratios", self.oi_and_ratios, 3600, 120), ("depth", self.depth, 60, 5)]
            self.tasks += [asyncio.create_task(self._every(*x)) for x in spec]
            self.tasks.append(asyncio.create_task(self.liquidations_stream()))
        self.tasks.append(asyncio.create_task(go()))

    async def stop(self):
        for t in self.tasks: t.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
