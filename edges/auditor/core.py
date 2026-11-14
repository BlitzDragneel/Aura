"""Signal Auditor: scores trade signals from any provider (a Telegram group, a friend, OMEGA itself) against real prices.

Honesty rules, fixed before any signal is scored (edges/auditor/RULES.md explains them in plain words):
  1. A signal counts from the moment it was LOGGED (the time OMEGA received it), never from a time someone claims later.
  2. Every logged signal is scored: losses, breakevens and never-filled orders included. Nothing can be deleted from
     the score once its outcome is known (the app only allows deleting before the signal is filled).
  3. Entry: "now"/market signals fill at the open of the first 1-minute bar after logging; a price away from the market
     fills only when price trades to it (a zone fills at its nearer edge); unfilled after `fill_hours` = NOT FILLED.
  4. After the fill each 1-minute bar is checked stop-first: if the stop and a target are both inside one bar, it is a
     stop (we cannot see the order inside the bar, so we assume the worse case).
  5. Two management styles are scored for every signal: "TP1" (everything closed at the first target) and
     "ladder" (equal parts closed at each target, stop moved to entry once TP1 is hit). Max hold `max_hold_h`, then
     closed at market.
  6. Costs: a typical retail spread (SPREAD table) is charged once per trade.
  7. A signal with no stop cannot be measured in R (risk units); it is still scored in pips and flagged NO STOP.
"""
from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field

# ---------------------------------------------------------------- instruments
# pip = the unit signal groups count in; usd_per_unit_per_lot = dollars per 1.0 price move for 1 lot (Exness-typical
# contract sizes: check your own broker's specification).
INSTR = {
    "XAUUSD": dict(pip=0.10, usd_per_unit_per_lot=100.0, spread=0.20, data="XAUUSDT", kind="perp"),
    "XAGUSD": dict(pip=0.01, usd_per_unit_per_lot=5000.0, spread=0.03, data="XAGUSDT", kind="perp"),
    "BTCUSD": dict(pip=1.0, usd_per_unit_per_lot=1.0, spread=10.0, data="BTCUSDT", kind="perp"),
    "ETHUSD": dict(pip=0.1, usd_per_unit_per_lot=1.0, spread=1.0, data="ETHUSDT", kind="perp"),
    "US30": dict(pip=1.0, usd_per_unit_per_lot=1.0, spread=2.0, data="YM=F", kind="yahoo"),
    "NAS100": dict(pip=1.0, usd_per_unit_per_lot=1.0, spread=1.5, data="NQ=F", kind="yahoo"),
    "US500": dict(pip=0.1, usd_per_unit_per_lot=1.0, spread=0.5, data="ES=F", kind="yahoo"),
    "GER40": dict(pip=1.0, usd_per_unit_per_lot=1.0, spread=1.5, data="^GDAXI", kind="yahoo"),
}
ALIASES = {"GOLD": "XAUUSD", "XAU": "XAUUSD", "XAUUSDM": "XAUUSD", "SILVER": "XAGUSD", "XAG": "XAGUSD",
           "XAGUSDM": "XAGUSD", "BTC": "BTCUSD", "BITCOIN": "BTCUSD", "BTCUSDT": "BTCUSD", "ETH": "ETHUSD",
           "DJ30": "US30", "DOW": "US30", "US30M": "US30", "USTEC": "NAS100", "NAS": "NAS100", "US100": "NAS100",
           "NAS100M": "NAS100", "NASDAQ": "NAS100", "SPX": "US500", "SP500": "US500", "DAX": "GER40", "DE40": "GER40"}
FX_CCY = {"EUR", "USD", "GBP", "JPY", "AUD", "NZD", "CAD", "CHF"}


def instrument(sym: str) -> tuple[str, dict]:
    s = re.sub(r"[^A-Z0-9]", "", sym.upper())
    s = ALIASES.get(s, s)
    if s.endswith("M") and s[:-1] in INSTR:
        s = s[:-1]
    if s in INSTR:
        return s, INSTR[s]
    if len(s) in (6, 7) and s[:3] in FX_CCY and s[3:6] in FX_CCY:
        s = s[:6]
        jpy = s.endswith("JPY")
        return s, dict(pip=0.01 if jpy else 0.0001, usd_per_unit_per_lot=100_000.0, spread=0.015 if jpy else 0.00015,
                       data=f"{s}=X", kind="yahoo", quote=s[3:])
    raise ValueError(f"unknown instrument {sym!r}")


# ---------------------------------------------------------------- signals
@dataclass
class Signal:
    symbol: str
    side: str                      # "buy" | "sell"
    logged_ms: int                 # when OMEGA received it (the only time that counts)
    entry: float | None = None     # None = market / now
    entry_hi: float | None = None  # zone upper bound (entry = lower bound) when a zone was given
    stop: float | None = None
    targets: list[float] = field(default_factory=list)
    provider: str = ""
    note: str = ""
    claimed_pips: float | None = None   # what the provider later claimed for it (optional, to compare)
    id: str = ""


NUM = r"(\d{1,6}(?:[.,]\d{1,6})?)"


def _f(x: str) -> float:
    return float(x.replace(",", "."))


def parse(text: str, logged_ms: int, provider: str = "") -> Signal:
    """Reads the usual signal formats, e.g. 'XAUUSD BUY NOW 4105 SL 4095 TP1 4110 TP2 4120',
    'GOLD SELL @4130-4134 | SL: 4140 | TP: 4125/4120/4110', 'US30 buy limit 46800 sl 46700 tp 47000'."""
    t = text.upper().replace("—", "-").replace("–", "-")
    sym = None
    for tok in re.findall(r"[A-Z][A-Z0-9/]{1,9}", t):
        try:
            sym = instrument(tok.replace("/", ""))[0]
            break
        except ValueError:
            continue
    if sym is None:
        raise ValueError("no instrument found (e.g. XAUUSD, GOLD, US30, NAS100, GBPJPY)")
    m = re.search(r"\b(BUY|SELL|LONG|SHORT)\b", t)
    if not m:
        raise ValueError("no direction found (BUY or SELL)")
    side = "buy" if m.group(1) in ("BUY", "LONG") else "sell"
    rest = t[m.end():]
    stop = None
    ms = re.search(r"\b(?:SL|S/L|STOP\s*LOSS|STOP)\b\s*[:=@]?\s*" + NUM, rest)
    if ms:
        stop = _f(ms.group(1))
    targets = []
    for mt in re.finditer(r"\b(?:TP|T/P|TAKE\s*PROFIT|TARGET)\s*(?:\d\b)?\s*[:=@]?\s*((?:" + NUM[1:-1] + r")(?:\s*[/|,&]\s*" + NUM[1:-1] + r")*)", rest):
        targets += [_f(x) for x in re.findall(NUM, mt.group(1))]
    # entry: the numbers before the first SL/TP keyword
    head = re.split(r"\b(?:SL|S/L|STOP|TP\s*\d?|T/P|TAKE|TARGET)\b", rest)[0]
    nums = [_f(x) for x in re.findall(NUM, head)]
    entry = entry_hi = None
    if nums:
        raw = re.findall(NUM, head)
        if len(nums) >= 2 and nums[1] < nums[0] and len(raw[1]) < len(raw[0].split(".")[0]):
            # shorthand zone '4118-14' = 4118 to 4114
            k = len(raw[1].split(".")[0])
            nums[1] = float(raw[0].split(".")[0][:-k] + raw[1])
        if len(nums) >= 2 and abs(nums[1] - nums[0]) < 0.02 * nums[0]:
            entry, entry_hi = min(nums[:2]), max(nums[:2])
        else:
            entry = nums[0]
    if re.search(r"\b(NOW|MARKET|CMP|INSTANT)\b", head) and entry_hi is None:
        entry = None  # market order; a quoted price is only the reference
    return Signal(symbol=sym, side=side, logged_ms=int(logged_ms), entry=entry, entry_hi=entry_hi, stop=stop,
                  targets=sorted(targets, reverse=(side == "sell")), provider=provider, note=text.strip()[:500])


def check(sig: Signal) -> list[str]:
    """Plain-language problems with a signal (they are scored anyway)."""
    p = []
    if sig.stop is None:
        p.append("NO STOP: risk is unlimited and cannot be measured")
    if not sig.targets:
        p.append("no target: closed at the time limit")
    ref = sig.entry
    if ref is not None and sig.stop is not None:
        if (sig.side == "buy" and sig.stop >= ref) or (sig.side == "sell" and sig.stop <= ref):
            p.append("stop is on the wrong side of the entry")
        risk = abs(ref - sig.stop)
        if sig.targets and risk > 0:
            rr = abs(sig.targets[0] - ref) / risk
            if rr < 0.5:
                p.append(f"first target pays only {rr:.2f}x the risk")
    return p


# ---------------------------------------------------------------- scoring
def _fill(sig: Signal, bars: list[dict], fill_hours: float):
    """Returns (index, price) of the fill or (None, None)."""
    if not bars:
        return None, None
    if sig.entry is None:
        return 0, bars[0]["o"]
    lo, hi = sig.entry, sig.entry_hi if sig.entry_hi is not None else sig.entry
    first = bars[0]["o"]
    # already inside the zone at logging time = market fill
    if lo <= first <= hi:
        return 0, first
    limit_ms = bars[0]["t"] + fill_hours * 3_600_000
    for i, b in enumerate(bars):
        if b["t"] > limit_ms:
            break
        if first > hi and b["l"] <= hi:      # price comes down to the zone: nearer edge is the top
            return i, min(hi, b["o"])
        if first < lo and b["h"] >= lo:      # price comes up to the zone: nearer edge is the bottom
            return i, max(lo, b["o"])
    return None, None


def _walk(sig, bars, i0, px, targets, ladder, max_hold_h):
    """Walks bars from the fill; returns (exit_avg_price_move_in_favour, outcome, exit_ms, mfe, mae)."""
    d = 1 if sig.side == "buy" else -1
    stop = sig.stop
    parts = len(targets) if (ladder and targets) else 1
    tg = targets if ladder else targets[:1]
    open_parts, realised, hit = parts, 0.0, 0
    end_ms = bars[i0]["t"] + max_hold_h * 3_600_000
    mfe = mae = 0.0
    for j in range(i0, len(bars)):
        b = bars[j]
        fav, adv = ((b["h"] - px), (px - b["l"])) if d == 1 else ((px - b["l"]), (b["h"] - px))
        mfe, mae = max(mfe, fav), max(mae, adv)
        if b["t"] >= end_ms:
            realised += open_parts * d * (b["o"] - px)
            return realised / parts, ("timeout" if hit == 0 else f"TP{hit}+timeout"), b["t"], mfe, mae
        # stop first (worse case inside one bar); on the fill bar only the part after the fill is known, so use it too
        if stop is not None and ((d == 1 and b["l"] <= stop) or (d == -1 and b["h"] >= stop)):
            realised += open_parts * d * (stop - px)
            out = "SL" if hit == 0 else (f"TP{hit}+BE" if stop == px else f"TP{hit}+SL")
            return realised / parts, out, b["t"], mfe, mae
        while hit < len(tg) and ((d == 1 and b["h"] >= tg[hit]) or (d == -1 and b["l"] <= tg[hit])):
            realised += d * (tg[hit] - px)
            open_parts -= 1
            hit += 1
            if ladder and hit == 1:
                stop = px  # breakeven after TP1
            if open_parts == 0:
                return realised / parts, f"TP{hit}", b["t"], mfe, mae
    last = bars[-1]
    realised += open_parts * d * (last["c"] - px)
    return realised / parts, "open", last["t"], mfe, mae


def score(sig: Signal, bars: list[dict], fill_hours: float = 24.0, max_hold_h: float = 48.0) -> dict:
    """bars: 1-minute candles (dict t,o,h,l,c) starting at or after sig.logged_ms, oldest first."""
    name, spec = instrument(sig.symbol)
    bars = [b for b in bars if b["t"] >= sig.logged_ms]  # first bar that OPENS after logging
    out = dict(symbol=name, side=sig.side, provider=sig.provider, logged_ms=sig.logged_ms, problems=check(sig),
               id=sig.id, claimed_pips=sig.claimed_pips)
    if not bars:
        return {**out, "status": "no data yet"}
    i, px = _fill(sig, bars, fill_hours)
    if i is None:
        waited = (bars[-1]["t"] - bars[0]["t"]) / 3_600_000
        return {**out, "status": "not filled" if waited >= fill_hours else "waiting for entry"}
    cost = spec["spread"]
    risk = abs(px - sig.stop) if sig.stop is not None else None
    if risk is not None and risk == 0:
        risk = None
    res = {}
    for style, ladder in (("tp1", False), ("ladder", True)):
        move, outcome, t_exit, mfe, mae = _walk(sig, bars, i, px, sig.targets, ladder, max_hold_h)
        net = move - cost
        res[style] = dict(outcome=outcome, pips=round(net / spec["pip"], 1), R=round(net / risk, 3) if risk else None,
                          exit_ms=t_exit, usd_per_lot=round(net * spec["usd_per_unit_per_lot"], 2))
    closed = res["tp1"]["outcome"] != "open" and res["ladder"]["outcome"] != "open"
    return {**out, "status": "closed" if closed else "running", "fill_ms": bars[i]["t"], "fill": px,
            "risk_pips": round(risk / spec["pip"], 1) if risk else None, "mfe_pips": round(mfe / spec["pip"], 1),
            "mae_pips": round(mae / spec["pip"], 1), **res}


# ---------------------------------------------------------------- summary
def _stats(rs: list[float], risk_pct: float = 1.0) -> dict:
    n = len(rs)
    if n == 0:
        return dict(n=0)
    mean = sum(rs) / n
    sd = math.sqrt(sum((r - mean) ** 2 for r in rs) / (n - 1)) if n > 1 else 0.0
    eq, peak, dd, streak, worst = 1.0, 1.0, 0.0, 0, 0
    for r in rs:
        eq *= max(0.0, 1 + r * risk_pct / 100)
        peak = max(peak, eq)
        dd = min(dd, eq / peak - 1)
        streak = streak + 1 if r < 0 else 0
        worst = max(worst, streak)
    return dict(n=n, win_rate=round(sum(r > 0 for r in rs) / n, 3), avg_R=round(mean, 3), total_R=round(sum(rs), 2),
                t=round(mean / sd * math.sqrt(n), 2) if sd > 0 else None, max_losing_streak=worst,
                account_change_pct=round((eq - 1) * 100, 1), max_drawdown_pct=round(dd * 100, 1), risk_pct=risk_pct)


def summary(scored: list[dict], risk_pct: float = 1.0) -> dict:
    closed = [s for s in scored if s.get("status") == "closed"]
    out = dict(logged=len(scored), closed=len(closed),
               not_filled=sum(s.get("status") == "not filled" for s in scored),
               running=sum(s.get("status") in ("running", "waiting for entry", "no data yet") for s in scored),
               no_stop=sum(any(p.startswith("NO STOP") for p in s.get("problems", [])) for s in scored))
    for style in ("tp1", "ladder"):
        rs = [s[style]["R"] for s in closed if s[style]["R"] is not None]
        out[style] = _stats(rs, risk_pct)
        out[style]["pips_scored"] = round(sum(s[style]["pips"] for s in closed), 1)
    claimed = [s for s in closed if s.get("claimed_pips") is not None]
    if claimed:
        out["claimed_vs_scored"] = dict(n=len(claimed), claimed_pips=round(sum(s["claimed_pips"] for s in claimed), 1),
                                        scored_pips_tp1=round(sum(s["tp1"]["pips"] for s in claimed), 1))
    out["verdict"] = verdict(out)
    return out


def verdict(s: dict) -> str:
    st = s["tp1"] if s["tp1"].get("n", 0) >= s["ladder"].get("n", 0) else s["ladder"]
    n = st.get("n", 0)
    if n < 30:
        return (f"Too early: {n} closed signals with a stop. About 30 are needed before the numbers mean anything, "
                f"50+ to trust them.")
    if (st.get("avg_R") or 0) > 0 and (st.get("t") or 0) >= 2:
        return (f"Evidence of an edge: {n} signals, average {st['avg_R']:+.2f}R after spread, t={st['t']}. "
                "Keep auditing; size small (1% risk or less).")
    if (st.get("avg_R") or 0) > 0:
        return f"Positive but not proven: average {st['avg_R']:+.2f}R over {n} signals (t={st['t']}); could be luck."
    return f"No edge in the record: average {st['avg_R']:+.2f}R over {n} signals after spread."


# ---------------------------------------------------------------- risk check (lots vs balance)
def risk_check(balance: float, positions: list[dict], typical_moves: dict | None = None) -> dict:
    """positions: [{symbol, side, lots}] -> how far price can move against the book before the equity is gone."""
    per_unit, notional_note = {}, []
    for p in positions:
        name, spec = instrument(p["symbol"])
        d = 1 if str(p.get("side", "buy")).lower().startswith("b") else -1
        per_unit[name] = per_unit.get(name, 0.0) + d * float(p["lots"]) * spec["usd_per_unit_per_lot"]
    out = []
    for name, usd in per_unit.items():
        spec = instrument(name)[1]
        wipe = balance / abs(usd) if usd else None
        row = dict(symbol=name, net_direction="buy" if usd > 0 else "sell", usd_per_1_move=round(abs(usd), 2),
                   usd_per_pip=round(abs(usd) * spec["pip"], 2),
                   move_to_lose_balance=round(wipe, 3) if wipe else None,
                   pips_to_lose_balance=round(wipe / spec["pip"], 1) if wipe else None)
        tm = (typical_moves or {}).get(name)
        if tm and wipe:
            row["typical_moves"] = tm
            row["plain"] = "; ".join(f"a typical {k} move is {v:g} ({v / wipe * 100:.0f}% of the balance)" for k, v in tm.items())
        out.append(row)
    return dict(balance=balance, by_symbol=out)


def as_dict(sig: Signal) -> dict:
    return asdict(sig)
