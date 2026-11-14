"""Asset desks for the OMEGA app: what the Bitcoin, Gold and Silver bots read, their per-horizon states (WAIT / WATCH /
SETUP / TRIGGERED / CONFIRMED / INVALIDATED / EXPIRED), any call (only from tested rules), their forward record and
notebook. Written every 15 minutes by edges/assetbots.

Source, like feed.py: the local OMEGA Station folder (<home>/assets/) when this API runs next to the Station, otherwise
the bot-state branch on GitHub (bot-state/assets/). Read-only and information only.
"""
from __future__ import annotations

import json
import time

import httpx

from .feed import RAW, station_home

ASSETS = {"BTC": "Bitcoin", "XAU": "Gold", "XAG": "Silver"}
ALIASES = {"BTCUSDT": "BTC", "BITCOIN": "BTC", "XAUUSDT": "XAU", "XAUUSD": "XAU", "GOLD": "XAU",
           "XAGUSDT": "XAG", "XAGUSD": "XAG", "SILVER": "XAG"}


def norm(asset: str) -> str:
    a = (asset or "").strip().upper()
    a = ALIASES.get(a, a)
    if a not in ASSETS:
        raise ValueError(f"asset must be one of {sorted(ASSETS)} (or gold/silver/bitcoin)")
    return a


class AssetDesks:
    def __init__(self, client: httpx.Client | None = None, ttl: float = 60):
        self.c = client or httpx.Client(timeout=15, headers={"User-Agent": "omega-live/1.0"})
        self.ttl = ttl
        self._cache: dict[str, tuple[float, dict]] = {}

    def _read(self, rel: str) -> tuple[dict | None, str]:
        home = station_home()
        if home is not None:
            f = home / "assets" / rel
            src = "laptop (OMEGA Station)"
            if not f.exists():
                return None, src
            try:
                return json.loads(f.read_text(encoding="utf-8")), src
            except json.JSONDecodeError:
                return None, src
        src = "cloud bots (GitHub bot-state)"
        r = self.c.get(f"{RAW}/assets/{rel}", params={"t": int(time.time() // 60)})
        if r.status_code != 200:
            return None, src
        try:
            return r.json(), src
        except ValueError:
            return None, src

    def _cached(self, key: str, rel: str) -> dict:
        hit = self._cache.get(key)
        if hit and time.time() - hit[0] < self.ttl:
            return hit[1]
        try:
            data, src = self._read(rel)
            out = dict(source=src, available=data is not None)
            if data is None:
                out["note"] = "this desk has not written a record yet (the asset bots run every 15 minutes)"
            else:
                out.update(data)
                try:
                    age = time.time() - __import__("pandas").Timestamp(data.get("asof")).timestamp()
                    out["age_minutes"] = round(age / 60, 1)
                    out["stale"] = age > 3600
                except Exception:
                    pass
        except httpx.HTTPError as e:
            out = dict(source="unreachable", available=False, error=f"could not read the desk: {type(e).__name__}")
        out["disclaimer"] = ("information only: calls come only from rules that passed a pre-registered test; "
                             "WAIT when nothing qualifies; never an order")
        self._cache[key] = (time.time(), out)
        return out

    def get(self, asset: str) -> dict:
        a = norm(asset)
        return self._cached(a, f"{a}.json")

    def index(self) -> dict:
        out = self._cached("INDEX", "INDEX.json")
        out["assets"] = ASSETS
        return out
