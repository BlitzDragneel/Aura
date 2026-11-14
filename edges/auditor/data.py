"""Price history after a signal was logged: 1-minute bars where possible.

Gold/silver/BTC/ETH: Binance USDT-M perpetual (XAUUSDT, XAGUSDT ... 24/7) -> OKX swap 1m.
  A perpetual tracks spot gold closely but not exactly (a few cents to ~$1 apart); scores say which source was used.
Indices / forex: Yahoo Finance futures and FX (YM=F, NQ=F, ES=F, GBPJPY=X), 1m for the last 7 days, else 5m.
"""
from __future__ import annotations

import time

import httpx

from .core import instrument

H = 3_600_000


class Prices:
    def __init__(self, client: httpx.Client | None = None):
        self.c = client or httpx.Client(timeout=12, headers={"User-Agent": "omega-auditor/1.0"})

    def bars(self, symbol: str, start_ms: int, hours: float = 72.0) -> tuple[list[dict], str]:
        name, spec = instrument(symbol)
        end_ms = min(int(time.time() * 1000), start_ms + int(hours * H))
        errors = []
        fns = [self._binance, self._okx] if spec["kind"] == "perp" else [self._yahoo]
        for fn in fns:
            try:
                rows, src = fn(spec["data"], start_ms, end_ms)
                if rows and spec.get("cash"):
                    rows, src = self._to_cash(rows, src, spec["cash"], start_ms)
                if rows:
                    return rows, src
                errors.append(f"{fn.__name__}: empty")
            except (httpx.HTTPError, KeyError, ValueError, TypeError, IndexError) as e:
                errors.append(f"{fn.__name__}: {type(e).__name__} {e}"[:160])
        raise RuntimeError("; ".join(errors))

    def _binance(self, sym, a, b):
        out, t = [], a - a % 60_000
        while t < b and len(out) < 20_000:
            r = self.c.get("https://fapi.binance.com/fapi/v1/klines",
                           params=dict(symbol=sym, interval="1m", startTime=t, endTime=b, limit=1500))
            r.raise_for_status()
            d = r.json()
            if not d:
                break
            out += [dict(t=int(k[0]), o=float(k[1]), h=float(k[2]), l=float(k[3]), c=float(k[4])) for k in d]
            t = int(d[-1][0]) + 60_000
        now = time.time() * 1000
        return [x for x in out if x["t"] + 60_000 <= now], "binance-perp-1m"

    def _okx(self, sym, a, b):
        inst = sym.replace("USDT", "") + "-USDT-SWAP"
        out, after = [], b + 60_000
        for _ in range(80):
            r = self.c.get("https://www.okx.com/api/v5/market/history-candles",
                           params=dict(instId=inst, bar="1m", after=str(after), limit="100"))
            r.raise_for_status()
            d = r.json().get("data") or []
            if not d:
                break
            out += [dict(t=int(k[0]), o=float(k[1]), h=float(k[2]), l=float(k[3]), c=float(k[4])) for k in d if k[8] == "1"]
            after = int(d[-1][0])
            if after <= a:
                break
            time.sleep(0.12)
        out = sorted({x["t"]: x for x in out if x["t"] >= a - 60_000}.values(), key=lambda x: x["t"])
        return out, "okx-perp-1m"

    def _to_cash(self, rows, src, cash, start_ms):
        """Index CFDs trade nearly 24 h at the cash index level; futures sit a carry gap (basis) above it. Shift the
        futures bars by the median futures-minus-cash gap over the overlapping minutes of the last few sessions."""
        a = start_ms - 3 * 86_400_000
        fut, _ = self._yahoo(src.split("-")[1], a, rows[-1]["t"])
        idx, _ = self._yahoo(cash, a, rows[-1]["t"])
        fc = {r["t"]: r["c"] for r in fut}
        gaps = sorted(fc[r["t"]] - r["c"] for r in idx if r["t"] in fc)
        if len(gaps) < 20:
            return rows, src + " (futures level: no cash overlap to correct)"
        g = gaps[len(gaps) // 2]
        return [dict(t=r["t"], o=r["o"] - g, h=r["h"] - g, l=r["l"] - g, c=r["c"] - g) for r in rows], f"{src} minus basis {g:.1f}"

    def _yahoo(self, sym, a, b):
        recent = (time.time() * 1000 - a) < 6.5 * 24 * H
        iv = "1m" if recent else "5m"
        r = self.c.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",
                       params=dict(period1=a // 1000 - 60, period2=b // 1000 + 60, interval=iv))
        r.raise_for_status()
        res = r.json()["chart"]["result"][0]
        q = res["indicators"]["quote"][0]
        out = []
        for i, ts in enumerate(res.get("timestamp") or []):
            o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
            if None in (o, h, l, c):
                continue
            out.append(dict(t=ts * 1000, o=o, h=h, l=l, c=c))
        return out, f"yahoo-{sym}-{iv}"
