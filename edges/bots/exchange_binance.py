"""Binance USDT-M futures: public market data (with OKX/Gate fallback through omega/live_api) and a signed trading
adapter (HMAC-SHA256). Testnet base URL by default (https://demo-fapi.binance.com, configurable).

Order flow for one rule signal (one-way mode, isolated margin):
  1. marginType ISOLATED, leverage L for the symbol.
  2. entry: LIMIT BUY (GTD = the rule's window, so it dies on the exchange even if the bot is off) or MARKET BUY.
  3. protective stop placed at once: STOP_MARKET SELL closePosition=true workingType=MARK_PRICE through the Algo Service
     (POST /fapi/v1/algoOrder, algoType=CONDITIONAL — Binance moved conditional orders there on 2025-12-09; the old
     /fapi/v1/order path answers -4120). A closePosition stop does nothing while there is no position, so it can rest
     beside a resting limit (price must cross the limit before it reaches the stop).
  4. exit at the rule's time: MARKET SELL reduceOnly, then cancel the symbol's open orders and algo orders.
Nothing here can withdraw: the adapter has no transfer/withdraw call, and live mode refuses a key that can withdraw.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import sys
import time
import urllib.parse

import httpx
import pandas as pd

from edges.bots.sizing import round_price

UA = {"User-Agent": "omega-bots/1.0"}


class BinanceError(Exception):
    def __init__(self, msg, status=None, code=None):
        super().__init__(msg)
        self.status, self.code = status, code


class TransportError(BinanceError):
    """Network failure / timeout: the request MAY have reached the exchange (an order may exist)."""


# ---------------------------------------------------------------- public market data
class MarketData:
    """Closed candles for the signal side. Binance futures first; if unreachable, omega/live_api's providers
    (OKX, Gate) when that package is importable. Every frame is indexed by UTC bar-open time; the bar still forming is
    dropped. A Binance failure is remembered for `cooldown_s` so a blocked fapi (HTTP 451) costs one request per
    cooldown, not one per coin. `history()` pages past the per-request limits (Binance 1500, OKX 300 per call)."""

    TF_MS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}

    def __init__(self, base="https://fapi.binance.com", client=None, spacing=0.12, fallback=True, cooldown_s=900,
                 alt_gap_s=None):
        self.base = base.rstrip("/")
        self.c = client or httpx.Client(timeout=15, headers=UA)
        self.spacing = spacing
        self.fallback = fallback
        self.cooldown_s = cooldown_s
        self.alt_gap_s = alt_gap_s
        self._alt = None
        self._down_until = 0.0
        self.source = "binance"

    def _get(self, path, **params):
        if self.fallback and time.time() < self._down_until:
            raise BinanceError(f"Binance skipped for {self._down_until - time.time():.0f}s after an error", status=0)
        try:
            r = self.c.get(self.base + path, params=params)
        except httpx.HTTPError:
            self._down_until = time.time() + self.cooldown_s
            raise
        if r.status_code != 200:
            if r.status_code not in (400, 404):
                self._down_until = time.time() + self.cooldown_s
            raise BinanceError(f"Binance {r.status_code} on {path}", status=r.status_code)
        return r.json()

    def exchange_info(self):
        return self._get("/fapi/v1/exchangeInfo")

    def universe(self, info=None, top=None):
        try:
            return self._universe(info, top)
        except (BinanceError, httpx.HTTPError):
            if not self.fallback:
                raise
            syms = self._alt_crypto().top_by_volume(min(int(top or 200), 200))   # OKX/Gate via omega/live_api
            self.source = "fallback"
            return {s: {} for s in syms}

    def _universe(self, info=None, top=None):
        info = info or self.exchange_info()
        syms = {s["symbol"]: dict(onboard=s.get("onboardDate")) for s in info["symbols"]
                if s.get("quoteAsset") == "USDT" and s.get("contractType") == "PERPETUAL" and s.get("status") == "TRADING"}
        if top:
            t = self._get("/fapi/v1/ticker/24hr")
            vol = {x["symbol"]: float(x.get("quoteVolume", 0)) for x in t}
            keep = sorted(syms, key=lambda s: -vol.get(s, 0))[:top]
            syms = {s: syms[s] for s in keep}
        return syms

    def _alt_crypto(self):
        if self._alt is None:
            root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "omega", "live_api")
            if root not in sys.path:
                sys.path.insert(0, root)
            from omega_live.providers import Crypto, Http   # noqa: import-optional
            h = Http()
            if self.alt_gap_s is not None:
                h.min_gap["okx"] = float(self.alt_gap_s)
            self._alt = Crypto(h)
        return self._alt

    @staticmethod
    def _alt_symbol(sym):
        """Binance '1000PEPEUSDT' is OKX/Gate 'PEPE' (price per coin): returns (provider symbol, price multiplier)."""
        if sym.startswith("1000") and len(sym) > 8:
            return sym[4:], 1000.0
        return sym, 1.0

    @staticmethod
    def _frame(rows):
        df = pd.DataFrame(rows, columns=["ts", "o", "h", "l", "c", "v", "qv"])
        df = df.drop_duplicates("ts", keep="last").sort_values("ts")
        df.index = pd.to_datetime(df.pop("ts"), unit="ms", utc=True)
        return df.astype(float)

    def _binance_rows(self, sym, tf, n, now_ms):
        rows, end = [], None
        while len(rows) < n:
            p = dict(symbol=sym, interval=tf, limit=min(1500, n - len(rows) + 1))
            if end is not None:
                p["endTime"] = end
            d = self._get("/fapi/v1/klines", **p)
            chunk = [(int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5]), float(k[7]))
                     for k in d if int(k[6]) < now_ms]
            if not d:
                break
            rows = chunk + rows
            end = int(d[0][0]) - 1
            if len(d) < p["limit"]:
                break
            if self.spacing:
                time.sleep(self.spacing)
        return rows

    def _alt_rows(self, sym, tf, n):
        alt = self._alt_crypto()
        asym, mult = self._alt_symbol(sym)
        errors = []
        for name, fn in (("okx", lambda: alt._k_okx(asym, tf, n)), ("gate", lambda: alt._k_gate(asym, tf, min(n, 1999)))):
            try:
                k = fn()
                break
            except Exception as e:          # ProviderError, bad payloads: try the next provider
                errors.append(f"{name}: {type(e).__name__}: {e}")
        else:
            raise BinanceError("no candle provider answered: " + "; ".join(errors))
        self.source = k.get("source", "fallback")
        return [(c["t"], c["o"] * mult, c["h"] * mult, c["l"] * mult, c["c"] * mult, c["v"] / mult, c["qv"])
                for c in k["candles"] if c.get("closed")]

    def history(self, sym, tf="1h", n=1000, now_ms=None):
        """The last `n` CLOSED bars (fewer if the coin is younger), paging as needed."""
        now_ms = now_ms or int(time.time() * 1000)
        n = max(1, int(n))
        try:
            rows = self._binance_rows(sym, tf, n, now_ms)
            self.source = "binance"
        except (BinanceError, httpx.HTTPError):
            if not self.fallback:
                raise
            rows = [r for r in self._alt_rows(sym, tf, n + 1) if r[0] + self.TF_MS[tf] <= now_ms]
        return self._frame(rows).iloc[-n:]

    def klines(self, sym, tf="1h", limit=1000, now_ms=None):
        df = self.history(sym, tf, limit, now_ms)
        if self.spacing and self.source == "binance":
            time.sleep(self.spacing)
        return df


# ---------------------------------------------------------------- signed trading
class BinanceFutures:
    def __init__(self, base, key, secret, cfg=None, client=None):
        if not (key and secret):
            raise BinanceError("no API key/secret (keys come from the OS vault or environment variables only)")
        self.base = base.rstrip("/")
        self._k, self._s = key, secret
        self.cfg = cfg or {}
        self.c = client or httpx.Client(timeout=15, headers=UA)
        self._info = None
        self._prepared = set()

    def __repr__(self):            # never print the key
        return f"BinanceFutures({self.base})"

    def _req(self, method, path, params=None, signed=True, base=None, _retry=True):
        p = {k: v for k, v in (params or {}).items() if v is not None}
        headers = {}
        if signed:
            p["timestamp"] = int(time.time() * 1000 + self._offset_ms)
            p["recvWindow"] = int(self.cfg.get("recv_window", 5000))
            q = urllib.parse.urlencode(p)
            p["signature"] = hmac.new(self._s.encode(), q.encode(), hashlib.sha256).hexdigest()
            headers["X-MBX-APIKEY"] = self._k
        try:
            r = self.c.request(method, (base or self.base) + path, params=p, headers=headers)
        except httpx.HTTPError as e:
            raise TransportError(f"network error on {path}: {type(e).__name__}") from None
        if r.status_code >= 400:
            try:
                j = r.json()
                code, msg = j.get("code"), j.get("msg")
            except Exception:
                code, msg = None, r.text[:200]
            if code == -1021 and signed and _retry:          # PC clock drifted: resync once with the server and retry
                self.resync()
                p = {k: v for k, v in p.items() if k not in ("timestamp", "signature", "recvWindow")}
                return self._req(method, path, p, signed, base, _retry=False)
            raise BinanceError(f"Binance {r.status_code} on {path}: {code}: {msg}", status=r.status_code, code=code)
        return r.json()

    _offset_ms = 0

    def resync(self):
        try:
            st = self._req("GET", "/fapi/v1/time", signed=False)["serverTime"]
            self._offset_ms = int(st) - int(time.time() * 1000)
        except (BinanceError, KeyError, TypeError):
            pass

    # -- public
    def info(self, sym):
        if self._info is None:
            self._info = {s["symbol"]: s for s in self._req("GET", "/fapi/v1/exchangeInfo", signed=False)["symbols"]}
        s = self._info.get(sym)
        if not s:
            raise BinanceError(f"{sym} is not listed on this venue ({self.base})")
        f = {x["filterType"]: x for x in s["filters"]}
        return dict(step=float(f["LOT_SIZE"]["stepSize"]), minQty=float(f["LOT_SIZE"]["minQty"]),
                    mstep=float(f.get("MARKET_LOT_SIZE", f["LOT_SIZE"])["stepSize"]),
                    tick=float(f["PRICE_FILTER"]["tickSize"]),
                    minNotional=float(f.get("MIN_NOTIONAL", {}).get("notional", 5)), status=s.get("status"))

    def price(self, sym):
        return float(self._req("GET", "/fapi/v1/ticker/price", {"symbol": sym}, signed=False)["price"])

    # -- account
    def dual_side(self):
        return bool(self._req("GET", "/fapi/v1/positionSide/dual").get("dualSidePosition"))

    def key_restrictions(self, spot_url="https://api.binance.com"):
        """The key's own permissions (Binance spot API), or None if they cannot be read (live is then refused)."""
        try:
            return self._req("GET", "/sapi/v1/account/apiRestrictions", base=spot_url.rstrip("/"))
        except BinanceError:
            return None

    def withdrawals_enabled(self, spot_url="https://api.binance.com"):
        r = self.key_restrictions(spot_url)
        return None if r is None else bool(r.get("enableWithdrawals")) or bool(r.get("enableInternalTransfer"))

    def open_orders(self, sym=None):
        return self._req("GET", "/fapi/v1/openOrders", {"symbol": sym} if sym else {})

    def open_algo_orders(self):
        try:
            r = self._req("GET", "/fapi/v1/openAlgoOrders")
            return r.get("orders", r) if isinstance(r, dict) else r
        except BinanceError as e:
            if e.status in (404, 405):
                return []
            raise

    def pending_entries(self):
        """Symbols with a resting ENTRY order (not reduce-only, not close-position): it can fill later, so it counts."""
        return sorted({x["symbol"] for x in self.open_orders() if str(x.get("reduceOnly")).lower() != "true"
                       and str(x.get("closePosition")).lower() != "true"})

    def find_order(self, sym, client_id):
        """After a network error: did the order reach the exchange? Returns the order or None (never placed)."""
        try:
            return self._req("GET", "/fapi/v1/order", {"symbol": sym, "origClientOrderId": client_id})
        except TransportError:
            raise
        except BinanceError:
            return None

    def positions(self):
        try:
            rows = self._req("GET", "/fapi/v3/positionRisk")
        except BinanceError as e:
            if e.status != 404:
                raise
            rows = self._req("GET", "/fapi/v2/positionRisk")
        return {p["symbol"]: dict(qty=float(p["positionAmt"]), entry=float(p["entryPrice"]),
                                  pnl=float(p.get("unRealizedProfit", 0))) for p in rows if float(p["positionAmt"]) != 0}

    def balance(self):
        b = [x for x in self._req("GET", "/fapi/v2/balance") if x["asset"] == "USDT"]
        return float(b[0]["balance"]) if b else 0.0

    def day_pnl(self):
        t0 = int(pd.Timestamp.now(tz="UTC").floor("D").timestamp() * 1000)
        inc = self._req("GET", "/fapi/v1/income", {"startTime": t0, "limit": 1000})
        realized = sum(float(x["income"]) for x in inc if x["incomeType"] in ("REALIZED_PNL", "COMMISSION", "FUNDING_FEE"))
        return realized + sum(p["pnl"] for p in self.positions().values())

    # -- orders
    def prepare(self, sym, leverage):
        if (sym, leverage) in self._prepared:
            return
        try:
            self._req("POST", "/fapi/v1/marginType", {"symbol": sym, "marginType": self.cfg.get("margin_type", "ISOLATED")})
        except BinanceError as e:
            if e.code != -4046:                       # -4046: no need to change margin type
                raise
        self._req("POST", "/fapi/v1/leverage", {"symbol": sym, "leverage": int(leverage)})
        self._prepared.add((sym, leverage))

    def place_limit(self, sym, side, qty, price, expires_ms=None, client_id=None, now_ms=None):
        p = dict(symbol=sym, side="BUY" if side == "long" else "SELL", type="LIMIT", quantity=qty, price=price,
                 timeInForce="GTC", newClientOrderId=client_id, newOrderRespType="RESULT")
        now_ms = now_ms or time.time() * 1000
        if expires_ms and self.cfg.get("use_gtd", True):     # Binance: GTD must be > 600 s ahead; never a forgotten GTC
            p.update(timeInForce="GTD", goodTillDate=int(max(expires_ms, now_ms + 660_000)))
        return self._req("POST", "/fapi/v1/order", p)

    def place_market(self, sym, side, qty, client_id=None, reduce_only=False):
        p = dict(symbol=sym, side="BUY" if side == "long" else "SELL", type="MARKET", quantity=qty,
                 newClientOrderId=client_id, newOrderRespType="RESULT", reduceOnly="true" if reduce_only else None)
        return self._req("POST", "/fapi/v1/order", p)

    def place_stop(self, sym, side, stop_price, client_id=None):
        """Close-position protective stop for a `side` position (a SELL stop for a long)."""
        xs = "SELL" if side == "long" else "BUY"
        algo = lambda: dict(algo=True, **self._req("POST", "/fapi/v1/algoOrder", dict(
            algoType="CONDITIONAL", symbol=sym, side=xs, type="STOP_MARKET", triggerPrice=stop_price,
            closePosition="true", workingType="MARK_PRICE", priceProtect="true", clientAlgoId=client_id)))
        legacy = lambda: dict(algo=False, **self._req("POST", "/fapi/v1/order", dict(
            symbol=sym, side=xs, type="STOP_MARKET", stopPrice=stop_price, closePosition="true",
            workingType="MARK_PRICE", priceProtect="true", newClientOrderId=client_id)))
        if self.cfg.get("stop_via_algo", True):
            try:
                return algo()
            except BinanceError as e:
                if e.status not in (404, 405) or isinstance(e, TransportError):   # venue without the Algo Service
                    raise
            return legacy()
        try:
            return legacy()
        except BinanceError as e:
            if e.code != -4120:                       # -4120: conditional orders moved to the Algo Order API
                raise
            return algo()

    def order(self, sym, order_id):
        return self._req("GET", "/fapi/v1/order", {"symbol": sym, "orderId": order_id})

    def cancel(self, sym, order_id):
        try:
            return self._req("DELETE", "/fapi/v1/order", {"symbol": sym, "orderId": order_id})
        except BinanceError as e:
            if e.code in (-2011, -2013):              # unknown order / already gone
                return dict(note=str(e))
            raise

    def cancel_all(self, sym):
        out = {}
        for path in ("/fapi/v1/allOpenOrders", "/fapi/v1/algoOpenOrders"):
            try:
                out[path] = self._req("DELETE", path, {"symbol": sym})
            except BinanceError as e:
                out[path] = str(e)
        return out

    def close(self, sym):
        """Market-close the whole position in sym (reduce-only), then cancel its orders. Returns (qty, avg price)."""
        pos = self.positions().get(sym)
        res = None
        if pos:
            side = "long" if pos["qty"] > 0 else "short"
            res = self.place_market(sym, "short" if side == "long" else "long", abs(pos["qty"]), reduce_only=True)
        self.cancel_all(sym)
        if not res:
            return 0.0, None
        return float(res.get("executedQty", 0) or 0), float(res.get("avgPrice", 0) or 0) or None

    def last_fill_price(self, sym):
        try:
            t = self._req("GET", "/fapi/v1/userTrades", {"symbol": sym, "limit": 5})
            return float(t[-1]["price"]) if t else None
        except BinanceError:
            return None


def round_for(info, side, entry=None, stop=None):
    return (None if entry is None else round_price(entry, info["tick"], side, "entry"),
            None if stop is None else round_price(stop, info["tick"], side, "stop"))
