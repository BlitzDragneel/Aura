"""Hits every Binance endpoint the recorder uses, once, and says plainly what worked. Run this first on a new machine."""
import httpx
from .config import Settings
from .binance import Binance
from .archive import list_all

async def run():
    s = Settings(); bad = 0
    async with httpx.AsyncClient(timeout=20) as c:
        bx = Binance(s.rest, c)
        checks = [("exchangeInfo", bx.exchange_info()), ("klines 1h BTCUSDT", bx.klines("BTCUSDT", "1h", limit=2)),
                  ("premiumIndex", bx.premium_all()), ("fundingRate BTCUSDT", bx.funding_hist("BTCUSDT", limit=2)),
                  ("depth BTCUSDT", bx.depth("BTCUSDT", 5)), ("openInterestHist BTCUSDT", bx.oi_hist("BTCUSDT", limit=2)),
                  ("globalLongShortAccountRatio", bx.ratio("global", "BTCUSDT", limit=2)), ("takerlongshortRatio", bx.ratio("taker", "BTCUSDT", limit=2)),
                  ("archive listing", list_all(c, s.archive_list, "data/futures/um/monthly/klines/BTCUSDT/1h/"))]
        for name, coro in checks:
            try:
                r = await coro; size = len(r[1]) if name == "archive listing" else (len(r) if hasattr(r, "__len__") else 1)
                print(f"ok    {name}: {size} items"); bad += size == 0
            except Exception as e:
                print(f"FAIL  {name}: {type(e).__name__}: {e}"); bad += 1
        try:
            import websockets, asyncio
            async with websockets.connect(f"{s.ws}/!forceOrder@arr", open_timeout=10):
                print("ok    liquidation stream: connected")
        except Exception as e:
            print(f"FAIL  liquidation stream: {type(e).__name__}: {e}"); bad += 1
    print("all good" if not bad else f"{bad} problem(s): the recorder will log these in /health")
    return 1 if bad else 0
