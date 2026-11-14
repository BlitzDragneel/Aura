"""Signal Auditor endpoints. The app keeps the signal log (on the phone, with the time each signal was logged);
this service only reads messages and scores them against real prices. Rules: edges/auditor/RULES.md.

POST /auditor/parse  {text, provider}            -> the signal as read, stamped with the server's time now
POST /auditor/score  {signals:[...], risk_pct}   -> each signal scored + the summary and verdict
POST /auditor/risk   {balance, positions:[...]}  -> how far price can move before the balance is gone
"""
from __future__ import annotations

import statistics
import sys
import time

from fastapi import APIRouter, Body, Depends, HTTPException

from .signals import REPO

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from edges.auditor import core  # noqa: E402
from edges.auditor.data import Prices  # noqa: E402

MAX_SIGNALS = 300


def typical_moves(bars: list[dict]) -> dict:
    """Median high-low range of 15-minute, 1-hour and 1-day windows over the bars given (last 3 days of 1m bars)."""
    out = {}
    for name, ms in (("15-minute", 900_000), ("1-hour", 3_600_000), ("day", 86_400_000)):
        win = {}
        for b in bars:
            k = b["t"] // ms
            lo, hi = win.get(k, (b["l"], b["h"]))
            win[k] = (min(lo, b["l"]), max(hi, b["h"]))
        ranges = [hi - lo for lo, hi in win.values()]
        if len(ranges) >= 3:
            out[name] = round(statistics.median(ranges), 4)
    return out


def router(auth=None, prices: Prices | None = None) -> APIRouter:
    r = APIRouter(prefix="/auditor", dependencies=[Depends(auth)] if auth else [])
    px = prices or Prices()
    cache: dict = {}

    def bars(sym: str, start_ms: int, hours: float):
        key = (core.instrument(sym)[0], start_ms // 60_000, hours)
        hit = cache.get(key)
        if hit and time.time() - hit[0] < 60:
            return hit[1]
        val = px.bars(sym, start_ms, hours)
        cache[key] = (time.time(), val)
        if len(cache) > 500:
            cache.clear()
        return val

    @r.post("/parse")
    def parse(body: dict = Body(...)):
        text = str(body.get("text", ""))[:2000]
        try:
            sig = core.parse(text, int(time.time() * 1000), str(body.get("provider", ""))[:60])
        except ValueError as e:
            raise HTTPException(422, str(e))
        return dict(signal=core.as_dict(sig), problems=core.check(sig))

    @r.post("/score")
    def score(body: dict = Body(...)):
        raw = body.get("signals") or []
        if not isinstance(raw, list) or len(raw) > MAX_SIGNALS:
            raise HTTPException(422, f"signals must be a list of at most {MAX_SIGNALS}")
        fill_h, hold_h = float(body.get("fill_hours", 24)), float(body.get("max_hold_hours", 48))
        risk_pct = min(5.0, max(0.1, float(body.get("risk_pct", 1.0))))
        now = int(time.time() * 1000)
        scored = []
        for d in raw:
            try:
                sig = core.Signal(symbol=str(d["symbol"]), side=str(d["side"]).lower(), logged_ms=int(d["logged_ms"]),
                                  entry=d.get("entry"), entry_hi=d.get("entry_hi"), stop=d.get("stop"),
                                  targets=[float(x) for x in d.get("targets") or []][:6],
                                  provider=str(d.get("provider", ""))[:60], note=str(d.get("note", ""))[:500],
                                  claimed_pips=d.get("claimed_pips"), id=str(d.get("id", ""))[:40])
                if sig.side not in ("buy", "sell") or sig.logged_ms > now + 60_000:
                    raise ValueError("bad side or a logging time in the future")
                b, src = bars(sig.symbol, sig.logged_ms, fill_h + hold_h)
                res = core.score(sig, b, fill_h, hold_h)
                res["source"] = src
            except (KeyError, ValueError, TypeError, RuntimeError) as e:
                res = dict(id=str(d.get("id", "")) if isinstance(d, dict) else "", status="error", error=str(e)[:200])
            scored.append(res)
        groups = {}
        for s in scored:
            if s.get("status") != "error":
                groups.setdefault(s.get("provider") or "unnamed", []).append(s)
        return dict(scored=scored, summary=core.summary([s for s in scored if s.get("status") != "error"], risk_pct),
                    by_provider={k: core.summary(v, risk_pct) for k, v in groups.items()}, rules="edges/auditor/RULES.md")

    @r.post("/risk")
    def risk(body: dict = Body(...)):
        try:
            bal = float(body["balance"])
            pos = [dict(symbol=str(p["symbol"]), side=str(p.get("side", "buy")), lots=float(p["lots"]))
                   for p in (body.get("positions") or [])][:100]
            if bal <= 0 or not pos:
                raise ValueError("balance must be > 0 and at least one position is needed")
            moves = {}
            for name in {core.instrument(p["symbol"])[0] for p in pos}:
                try:
                    b, _ = bars(name, int(time.time() * 1000) - 3 * 86_400_000, 3 * 24)
                    moves[name] = typical_moves(b)
                except RuntimeError:
                    pass
            return core.risk_check(bal, pos, moves)
        except (KeyError, ValueError, TypeError) as e:
            raise HTTPException(422, str(e))

    return r
