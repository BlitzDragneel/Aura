"""The three asset bots: one class per asset, one shared engine (edges/assetbots/engine.py).

Each bot reads ONE market. It may describe that market (trend, volatility, session, ranges, scout readings) and raise a
WATCH (big-move risk, no direction). A direction - SETUP, TRIGGERED, CONFIRMED, a trade call - only ever comes from a
rule in edges/approved.json for that asset and horizon with status paper, testnet or live (edges/assetbots/rules.py).
"""
from __future__ import annotations

import dataclasses as dc

from edges.assetbots.engine import AssetBot


@dc.dataclass(frozen=True)
class AssetSpec:
    code: str                    # BTC | XAU | XAG (the "asset" field in edges/approved.json)
    name: str                    # plain name for people
    perp: str                    # USDT-M perpetual read every 15 minutes (Live API providers: Binance -> OKX -> Gate)
    spot: str | None             # spot quote symbol (/fx/quote), metals only
    cost_side: float             # cost per side used to score calls (ASSETS_BRIEF.md costs)
    weekend_closed: bool         # spot market shut at weekends (perp still trades, thinly)
    daily_break_utc: tuple | None  # CME daily break (hours UTC), metals
    scout: str                   # where its scouts come from (see scout.py)
    unit: str = "USDT"


BTC_SPEC = AssetSpec("BTC", "Bitcoin", "BTCUSDT", None, 0.0007, False, None, "omega")
XAU_SPEC = AssetSpec("XAU", "Gold", "XAUUSDT", "XAUUSD", 0.0002, True, (21, 22), "asset")
XAG_SPEC = AssetSpec("XAG", "Silver", "XAGUSDT", "XAGUSD", 0.0004, True, (21, 22), "asset")


class BitcoinBot(AssetBot):
    spec = BTC_SPEC


class GoldBot(AssetBot):
    spec = XAU_SPEC


class SilverBot(AssetBot):
    spec = XAG_SPEC


BOTS = {"BTC": BitcoinBot, "XAU": GoldBot, "XAG": SilverBot}
SPECS = {"BTC": BTC_SPEC, "XAU": XAU_SPEC, "XAG": XAG_SPEC}
