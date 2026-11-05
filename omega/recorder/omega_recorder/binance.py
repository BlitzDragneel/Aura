"""Public Binance USDT-M futures endpoints only. No keys, no orders."""
import asyncio, time
import httpx

class Binance:
    def __init__(self, base, client=None, max_weight=1800):
        self.base = base.rstrip("/")
        self.c = client or httpx.AsyncClient(timeout=20)
        self.max_weight = max_weight
        self.used = 0
        self.banned_until = 0.0

    async def get(self, path, **params):
        if time.time() < self.banned_until:
            raise RuntimeError(f"Binance back-off until {time.strftime('%H:%M:%S', time.gmtime(self.banned_until))} UTC")
        if self.used >= self.max_weight:               # close to the 2400/min limit: wait for the next minute
            await asyncio.sleep(61 - time.time() % 60); self.used = 0
        for attempt in range(4):
            try:
                r = await self.c.get(self.base + path, params=params)
            except httpx.TransportError:
                await asyncio.sleep(2 ** attempt); continue
            w = r.headers.get("x-mbx-used-weight-1m")
            if w and w.isdigit():
                self.used = int(w)
            if r.status_code in (429, 418):
                wait = int(r.headers.get("retry-after", "60"))
                self.banned_until = time.time() + wait
                raise RuntimeError(f"Binance rate limit {r.status_code}; backing off {wait}s")
            if r.status_code >= 500:
                await asyncio.sleep(2 ** attempt); continue
            r.raise_for_status()
            return r.json()
        raise RuntimeError(f"{path}: no answer after 4 attempts")

    async def exchange_info(self):            return await self.get("/fapi/v1/exchangeInfo")
    async def klines(self, sym, interval, limit=500, start=None):
        p = dict(symbol=sym, interval=interval, limit=limit)
        if start is not None: p["startTime"] = start
        return await self.get("/fapi/v1/klines", **p)
    async def premium_all(self):              return await self.get("/fapi/v1/premiumIndex")
    async def funding_hist(self, sym, start=None, limit=1000):
        p = dict(symbol=sym, limit=limit)
        if start is not None: p["startTime"] = start
        return await self.get("/fapi/v1/fundingRate", **p)
    async def ticker24(self):                 return await self.get("/fapi/v1/ticker/24hr")
    async def depth(self, sym, limit=100):    return await self.get("/fapi/v1/depth", symbol=sym, limit=limit)
    async def oi_hist(self, sym, period="5m", limit=30):
        return await self.get("/futures/data/openInterestHist", symbol=sym, period=period, limit=limit)
    async def ratio(self, kind, sym, period="5m", limit=30):
        path = {"global": "/futures/data/globalLongShortAccountRatio", "top_pos": "/futures/data/topLongShortPositionRatio",
                "taker": "/futures/data/takerlongshortRatio"}[kind]
        return await self.get(path, symbol=sym, period=period, limit=limit)

def kline_rows(sym, raw, src=None):
    """Binance kline arrays -> table rows. Times are ms (archive files after 2025 may use µs: normalised)."""
    out = []
    for k in raw:
        t = int(k[0]); t = t // 1000 if t > 10**14 else t
        row = (sym, t, float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5]), float(k[7]), int(k[8]), float(k[9]))
        out.append(row + ((src,) if src is not None else ()))
    return out

def depth_summary(book):
    bids = [(float(p), float(q)) for p, q in book.get("bids", [])]
    asks = [(float(p), float(q)) for p, q in book.get("asks", [])]
    if not bids or not asks:
        return None
    bb, ba = bids[0][0], asks[0][0]; mid = (bb + ba) / 2
    def side(levels, lo, hi): return sum(p * q for p, q in levels if lo <= p <= hi)
    return dict(mid=mid, spread_bps=(ba - bb) / mid * 1e4,
                bid05=side(bids, mid * 0.995, mid), ask05=side(asks, mid, mid * 1.005),
                bid2=side(bids, mid * 0.98, mid), ask2=side(asks, mid, mid * 1.02))
