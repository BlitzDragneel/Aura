"""Market-data providers with automatic fallback.

Crypto perpetuals: Binance USDT-M futures (works from Tobago; blocked from US/cloud hosts with HTTP 451)
                   -> OKX swaps -> Gate.io futures.
Crypto spot:       Binance public mirror (data-api.binance.vision) -> Coinbase -> Kraken.
Forex / metals:    Swissquote public quotes (keyless, live bid/ask) -> Twelve Data (needs TWELVEDATA_API_KEY).
Options:           Deribit public API (DVOL implied-volatility index, BTC/ETH).

Every provider returns the same normalised shapes:
  candle = {"t": open_ms, "o", "h", "l", "c", "v", "qv", "closed": bool}
  ticker = {"symbol", "price", "bid", "ask", "ts", "source"}
"""
from __future__ import annotations

import os
import time
from typing import Callable

import httpx

TF = {"1m", "5m", "15m", "1h", "4h", "1d"}
TF_MS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}


class ProviderError(Exception):
    pass


class Http:
    """One shared client; a provider that fails is skipped for `cooldown` seconds (circuit breaker)."""

    def __init__(self, client: httpx.Client | None = None, cooldown: float = 60.0):
        self.c = client or httpx.Client(timeout=8.0, headers={"User-Agent": "omega-live/1.0"})
        self.cooldown = cooldown
        self.down: dict[str, float] = {}
        self.last_error: dict[str, str] = {}

    def get(self, name: str, url: str, **params):
        if self.down.get(name, 0) > time.time():
            raise ProviderError(f"{name} cooling down after error: {self.last_error.get(name, '')}")
        try:
            r = self.c.get(url, params=params or None)
        except httpx.HTTPError as e:
            self._fail(name, f"network: {type(e).__name__}")
            raise ProviderError(f"{name}: {type(e).__name__}") from None
        if r.status_code != 200:
            self._fail(name, f"HTTP {r.status_code}")
            raise ProviderError(f"{name}: HTTP {r.status_code}")
        self.down.pop(name, None)
        return r.json()

    def _fail(self, name, msg):
        self.down[name] = time.time() + self.cooldown
        self.last_error[name] = msg

    def status(self):
        now = time.time()
        return {n: {"ok": until <= now, "retry_in_s": max(0, round(until - now)), "last_error": self.last_error.get(n)}
                for n, until in self.down.items()}


def first_ok(attempts: list[tuple[str, Callable]]):
    errors = []
    for name, fn in attempts:
        try:
            return fn()
        except (ProviderError, KeyError, ValueError, IndexError, TypeError) as e:
            errors.append(f"{name}: {e}")
    raise ProviderError("; ".join(errors) or "no provider")


# ------------------------------------------------------------------ symbol mapping
def base_of(sym: str) -> str:
    s = sym.upper().replace("-", "").replace("_", "").replace("/", "")
    if s.endswith("USDT"):
        return s[:-4]
    if s.endswith("USD"):
        return s[:-3]
    return s


def okx_swap(sym):
    return f"{base_of(sym)}-USDT-SWAP"


def gate_contract(sym):
    return f"{base_of(sym)}_USDT"


def fx_pair(sym: str) -> tuple[str, str]:
    s = sym.upper().replace("/", "").replace("_", "").replace("-", "")
    s = s[:-1] if s.endswith("M") and len(s) == 7 else s  # Exness 'XAUUSDm' style suffix
    if len(s) != 6:
        raise ValueError(f"forex symbol must look like EURUSD or XAU/USD, got {sym}")
    return s[:3], s[3:]


# ------------------------------------------------------------------ crypto perpetuals
class Crypto:
    BINANCE_F = os.environ.get("OMEGA_BINANCE_FAPI", "https://fapi.binance.com")
    OKX = "https://www.okx.com"
    GATE = "https://api.gateio.ws/api/v4"
    BSPOT = "https://data-api.binance.vision"

    def __init__(self, http: Http):
        self.h = http

    # klines --------------------------------------------------------
    def klines(self, sym: str, tf: str = "1h", limit: int = 200) -> dict:
        if tf not in TF:
            raise ValueError(f"tf must be one of {sorted(TF)}")
        limit = max(1, min(int(limit), 1000))
        return first_ok([("binance", lambda: self._k_binance(sym, tf, limit)),
                         ("okx", lambda: self._k_okx(sym, tf, limit)),
                         ("gate", lambda: self._k_gate(sym, tf, limit))])

    def _k_binance(self, sym, tf, limit):
        d = self.h.get("binance", f"{self.BINANCE_F}/fapi/v1/klines", symbol=sym.upper(), interval=tf, limit=limit)
        now = time.time() * 1000
        rows = [dict(t=int(k[0]), o=float(k[1]), h=float(k[2]), l=float(k[3]), c=float(k[4]), v=float(k[5]),
                     qv=float(k[7]), closed=int(k[6]) < now) for k in d]
        return dict(symbol=sym.upper(), tf=tf, source="binance-futures", candles=rows)

    def _k_okx(self, sym, tf, limit):
        bar = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1H", "4h": "4H", "1d": "1Dutc"}[tf]
        rows, after = [], None
        while len(rows) < limit:
            p = dict(instId=okx_swap(sym), bar=bar, limit=min(300, limit - len(rows)))
            if after:
                p["after"] = after
            d = self.h.get("okx", f"{self.OKX}/api/v5/market/{'history-candles' if after else 'candles'}", **p)
            if d.get("code") != "0":
                raise ProviderError(f"okx: {d.get('msg')}")
            chunk = d["data"]
            if not chunk:
                break
            # k: ts,o,h,l,c,vol(contracts),volCcy(base),volCcyQuote(USDT),confirm
            rows += [dict(t=int(k[0]), o=float(k[1]), h=float(k[2]), l=float(k[3]), c=float(k[4]), v=float(k[6]),
                          qv=float(k[7]), closed=k[8] == "1") for k in chunk]
            after = chunk[-1][0]
        rows.sort(key=lambda r: r["t"])
        return dict(symbol=sym.upper(), tf=tf, source="okx-swap", candles=rows[-limit:])

    def _k_gate(self, sym, tf, limit):
        d = self.h.get("gate", f"{self.GATE}/futures/usdt/candlesticks", contract=gate_contract(sym), interval=tf,
                       limit=limit)
        step = TF_MS[tf]
        now = time.time() * 1000
        rows = [dict(t=int(k["t"]) * 1000, o=float(k["o"]), h=float(k["h"]), l=float(k["l"]), c=float(k["c"]),
                     v=float(k.get("v", 0)), qv=float(k.get("sum", 0)), closed=int(k["t"]) * 1000 + step <= now)
                for k in d]
        return dict(symbol=sym.upper(), tf=tf, source="gate-futures", candles=rows)

    # tickers -------------------------------------------------------
    def tickers(self, syms: list[str]) -> list[dict]:
        return first_ok([("binance", lambda: self._t_binance(syms)), ("okx", lambda: self._t_okx(syms))])

    def _t_binance(self, syms):
        d = self.h.get("binance", f"{self.BINANCE_F}/fapi/v1/ticker/bookTicker")
        want = {s.upper() for s in syms}
        ts = int(time.time() * 1000)
        out = [dict(symbol=x["symbol"], bid=float(x["bidPrice"]), ask=float(x["askPrice"]),
                    price=(float(x["bidPrice"]) + float(x["askPrice"])) / 2, ts=int(x.get("time") or ts),
                    source="binance-futures") for x in d if x["symbol"] in want]
        if not out:
            raise ProviderError("binance: none of the symbols found")
        return out

    def _t_okx(self, syms):
        d = self.h.get("okx", f"{self.OKX}/api/v5/market/tickers", instType="SWAP")
        idx = {x["instId"]: x for x in d["data"]}
        out = []
        for s in syms:
            x = idx.get(okx_swap(s))
            if x:
                out.append(dict(symbol=s.upper(), price=float(x["last"]), bid=float(x["bidPx"] or 0),
                                ask=float(x["askPx"] or 0), ts=int(x["ts"]), source="okx-swap"))
        if not out:
            raise ProviderError("okx: none of the symbols found")
        return out

    def top_by_volume(self, n: int = 60) -> list[str]:
        """Most liquid USDT perpetuals right now (24h quote volume)."""
        def binance():
            d = self.h.get("binance", f"{self.BINANCE_F}/fapi/v1/ticker/24hr")
            d = [x for x in d if x["symbol"].endswith("USDT")]
            d.sort(key=lambda x: -float(x["quoteVolume"]))
            return [x["symbol"] for x in d[:n]]

        def okx():
            if not getattr(self, "_okx_crypto", None):  # instCategory 1 = crypto (3/4 = stock/commodity perps)
                ins = self.h.get("okx", f"{self.OKX}/api/v5/public/instruments", instType="SWAP")["data"]
                self._okx_crypto = {x["instId"] for x in ins if x.get("instCategory", "1") == "1"}
            d = self.h.get("okx", f"{self.OKX}/api/v5/market/tickers", instType="SWAP")["data"]
            d = [x for x in d if x["instId"].endswith("-USDT-SWAP") and x["instId"] in self._okx_crypto]
            d.sort(key=lambda x: -float(x["volCcy24h"]) * float(x["last"] or 0))
            return [x["instId"].replace("-USDT-SWAP", "USDT") for x in d[:n]]
        return first_ok([("binance", binance), ("okx", okx)])

    # funding / open interest -------------------------------------
    def funding(self, sym: str) -> dict:
        def binance():
            d = self.h.get("binance", f"{self.BINANCE_F}/fapi/v1/premiumIndex", symbol=sym.upper())
            return dict(symbol=sym.upper(), rate=float(d["lastFundingRate"]), next_time=int(d["nextFundingTime"]),
                        mark=float(d["markPrice"]), index=float(d["indexPrice"]), source="binance-futures")

        def okx():
            d = self.h.get("okx", f"{self.OKX}/api/v5/public/funding-rate", instId=okx_swap(sym))["data"][0]
            return dict(symbol=sym.upper(), rate=float(d["fundingRate"]), next_time=int(d["fundingTime"]),
                        premium=float(d.get("premium") or 0), source="okx-swap")
        return first_ok([("binance", binance), ("okx", okx)])

    def open_interest(self, sym: str) -> dict:
        def binance():
            d = self.h.get("binance", f"{self.BINANCE_F}/fapi/v1/openInterest", symbol=sym.upper())
            return dict(symbol=sym.upper(), oi_contracts=float(d["openInterest"]), ts=int(d["time"]),
                        source="binance-futures")

        def okx():
            d = self.h.get("okx", f"{self.OKX}/api/v5/public/open-interest", instType="SWAP",
                           instId=okx_swap(sym))["data"][0]
            return dict(symbol=sym.upper(), oi_base=float(d["oiCcy"]), oi_usd=float(d["oiUsd"]), ts=int(d["ts"]),
                        source="okx-swap")
        return first_ok([("binance", binance), ("okx", okx)])

    def spot_price(self, sym: str) -> dict:
        b = base_of(sym)

        def bspot():
            d = self.h.get("binance-spot", f"{self.BSPOT}/api/v3/ticker/bookTicker", symbol=f"{b}USDT")
            bid, ask = float(d["bidPrice"]), float(d["askPrice"])
            return dict(symbol=f"{b}USDT", bid=bid, ask=ask, price=(bid + ask) / 2, ts=int(time.time() * 1000),
                        source="binance-spot")

        def coinbase():
            d = self.h.get("coinbase", f"https://api.exchange.coinbase.com/products/{b}-USD/ticker")
            return dict(symbol=f"{b}USD", bid=float(d["bid"]), ask=float(d["ask"]), price=float(d["price"]),
                        ts=int(time.time() * 1000), source="coinbase")
        return first_ok([("binance-spot", bspot), ("coinbase", coinbase)])

    def coinbase_premium(self, sym: str = "BTC") -> dict:
        """Coinbase (US spot, USD) vs Binance spot (USDT). Information only - not a tested signal."""
        b = base_of(sym)
        cb = self.h.get("coinbase", f"https://api.exchange.coinbase.com/products/{b}-USD/ticker")
        bn = self.h.get("binance-spot", f"{self.BSPOT}/api/v3/ticker/price", symbol=f"{b}USDT")
        p_cb, p_bn = float(cb["price"]), float(bn["price"])
        return dict(asset=b, coinbase_usd=p_cb, binance_usdt=p_bn, premium_pct=round((p_cb / p_bn - 1) * 100, 4),
                    note="information only; USDT/USD drift is included", ts=int(time.time() * 1000))


# ------------------------------------------------------------------ forex / metals
class FX:
    SQ = "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument"
    TD = "https://api.twelvedata.com"

    def __init__(self, http: Http):
        self.h = http
        self.key = os.environ.get("TWELVEDATA_API_KEY", "").strip()

    def quote(self, sym: str) -> dict:
        a, b = fx_pair(sym)

        def swissquote():
            d = self.h.get("swissquote", f"{self.SQ}/{a}/{b}")
            best = None
            for plat in d:
                for p in plat.get("spreadProfilePrices", []):
                    if p.get("spreadProfile") in ("prime", "standard", "premium", "elite"):
                        cand = dict(bid=float(p["bid"]), ask=float(p["ask"]), ts=int(plat["ts"]),
                                    profile=p["spreadProfile"])
                        if best is None or cand["ts"] > best["ts"] or (cand["profile"] == "prime"
                                                                        and cand["ts"] == best["ts"]):
                            best = cand
            if not best:
                raise ProviderError("swissquote: no prices")
            return dict(symbol=a + b, bid=best["bid"], ask=best["ask"], price=(best["bid"] + best["ask"]) / 2,
                        spread=round(best["ask"] - best["bid"], 6), ts=best["ts"], source="swissquote")

        def twelve():
            if not self.key:
                raise ProviderError("twelvedata: no TWELVEDATA_API_KEY set")
            d = self.h.get("twelvedata", f"{self.TD}/price", symbol=f"{a}/{b}", apikey=self.key)
            if "price" not in d:
                raise ProviderError(f"twelvedata: {d.get('message', 'no price')}")
            p = float(d["price"])
            return dict(symbol=a + b, price=p, bid=None, ask=None, ts=int(time.time() * 1000), source="twelvedata")
        return first_ok([("swissquote", swissquote), ("twelvedata", twelve)])

    def klines(self, sym: str, tf: str = "1h", limit: int = 200) -> dict:
        a, b = fx_pair(sym)
        if not self.key:
            raise ProviderError("forex candles need a Twelve Data key: set TWELVEDATA_API_KEY "
                                "(or use /fx/recorded for candles built from live quotes since the service started)")
        iv = {"1m": "1min", "5m": "5min", "15m": "15min", "1h": "1h", "4h": "4h", "1d": "1day"}[tf]
        d = self.h.get("twelvedata", f"{self.TD}/time_series", symbol=f"{a}/{b}", interval=iv,
                       outputsize=min(int(limit), 5000), timezone="UTC", apikey=self.key)
        if d.get("status") != "ok":
            raise ProviderError(f"twelvedata: {d.get('message', 'error')}")
        import datetime as dt
        rows = []
        for v in reversed(d["values"]):
            t = dt.datetime.fromisoformat(v["datetime"]).replace(tzinfo=dt.timezone.utc)
            rows.append(dict(t=int(t.timestamp() * 1000), o=float(v["open"]), h=float(v["high"]), l=float(v["low"]),
                             c=float(v["close"]), v=float(v.get("volume") or 0), qv=0.0, closed=True))
        if rows:
            rows[-1]["closed"] = rows[-1]["t"] + TF_MS[tf] <= time.time() * 1000
        return dict(symbol=a + b, tf=tf, source="twelvedata", candles=rows)


# ------------------------------------------------------------------ options
class Options:
    D = "https://www.deribit.com/api/v2/public"

    def __init__(self, http: Http):
        self.h = http

    def dvol(self, currency: str = "BTC", hours: int = 48) -> dict:
        cur = currency.upper()
        if cur not in ("BTC", "ETH"):
            raise ValueError("DVOL exists for BTC and ETH")
        end = int(time.time() * 1000)
        d = self.h.get("deribit", f"{self.D}/get_volatility_index_data", currency=cur, resolution=3600,
                       start_timestamp=end - int(hours) * 3_600_000, end_timestamp=end)
        rows = [dict(t=int(r[0]), o=r[1], h=r[2], l=r[3], c=r[4]) for r in d["result"]["data"]]
        return dict(currency=cur, source="deribit", note="30-day implied volatility index; information only",
                    candles=rows, last=rows[-1]["c"] if rows else None)
