"""OMEGA alerts: turns the asset bots' records into short messages for Telegram and WhatsApp.

Usage: python -m edges.alerts.notify <state_dir>      (state_dir holds assets/BTC.json, XAU.json, XAG.json)
Sends only when something changed: a desk enters WATCH (big move likely, direction unknown), a tested rule calls a
trade (SETUP / TRIGGERED / CONFIRMED), a call closes; plus one morning summary a day (first run after 11:00 UTC = 7 am
Trinidad). Nothing is ever sent as a trade call unless it comes from a rule in edges/approved.json.

Channels (all optional; without them the message is only written to <state_dir>/alerts/outbox.md):
  Telegram: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID                (your own bot from @BotFather)
  WhatsApp: WHATSAPP_PHONE, CALLMEBOT_APIKEY                    (CallMeBot's free personal WhatsApp gateway)
"""
from __future__ import annotations

import datetime as dt
import json
import time
import os
import sys
from pathlib import Path

import httpx

ASSETS = ("BTC", "XAU", "XAG")
LOUD = {"WATCH", "SETUP", "TRIGGERED", "CONFIRMED"}


def fmt_price(p):
    return f"{p:,.2f}" if p is not None else "?"


def changes(state: dict, memory: dict) -> list[str]:
    out = []
    a = state["asset"]
    name, price = state.get("name", a), (state.get("read") or {}).get("price")
    for hz, h in (state.get("horizons") or {}).items():
        key, st = f"{a}.{hz}", h.get("state")
        if st != memory.get(key):
            if st in LOUD:
                why = (h.get("reasons") or [""])[0]
                if st == "WATCH":
                    out.append(f"👀 {name} {hz}: WATCH at {fmt_price(price)}. Big move likely, direction unknown. {why}")
                else:
                    out.append(f"📣 {name} {hz}: {st} {h.get('direction') or ''} at {fmt_price(price)}. {why}")
            memory[key] = st
    seen = set(memory.get("calls", []))
    for c in state.get("open_calls") or []:
        cid = str(c.get("id") or c.get("call_id") or json.dumps(c, sort_keys=True, default=str)[:80])
        if cid not in seen:
            out.append(f"✅ {name} CALL ({c.get('rule', 'rule')}, grade {c.get('grade', '?')}, {c.get('status', 'paper')}): "
                       f"{str(c.get('side', '')).upper()} entry {c.get('entry')} stop {c.get('stop')} target {c.get('target')}")
            seen.add(cid)
    memory["calls"] = sorted(seen)[-200:]
    return out


def calendar(state_dir, client=None, max_age_s=3 * 3600):
    """This week's economic calendar (Forex Factory feed), cached in <state>/alerts/calendar.json: the free feed blocks
    callers that ask too often, so it is fetched at most every 3 hours."""
    f = Path(state_dir) / "alerts" / "calendar.json" if state_dir else None
    if f and f.exists() and time.time() - f.stat().st_mtime < max_age_s:
        try:
            return json.loads(f.read_text())
        except ValueError:
            pass
    try:
        c = client or httpx.Client(timeout=15)
        ev = c.get("https://nfs.faireconomy.media/ff_calendar_thisweek.json").json()
        if isinstance(ev, list) and f:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(json.dumps(ev))
        return ev if isinstance(ev, list) else []
    except Exception:
        if f and f.exists():
            try:
                return json.loads(f.read_text())     # stale copy beats nothing
            except ValueError:
                pass
        return []


def news_ahead(memory: dict, now: dt.datetime, client=None) -> list[str]:
    """High-impact USD events starting in the next 15-50 minutes (Forex Factory weekly calendar, faireconomy feed)."""
    ev = calendar(memory.get("_state_dir"), client)
    if not ev:
        return []
    out, seen = [], set(memory.get("news_sent", []))
    for e in ev:
        if e.get("country") != "USD" or e.get("impact") != "High":
            continue
        try:
            t = dt.datetime.fromisoformat(e["date"]).astimezone(dt.timezone.utc)
        except (KeyError, ValueError):
            continue
        mins = (t - now).total_seconds() / 60
        key = f"{e.get('title')}|{t.isoformat()}"
        if 15 <= mins <= 50 and key not in seen:
            seen.add(key)
            local = (t - dt.timedelta(hours=4)).strftime("%I:%M %p")
            fc = f" (forecast {e['forecast']}, previous {e.get('previous')})" if e.get("forecast") else ""
            out.append(f"⏰ US news in {round(mins)} min: {e.get('title')}{fc} at {t:%H:%M} UTC / {local} Trinidad.\n"
                       "Gold usually moves about 45% more in the hour after high-impact US news; the direction could not be "
                       "predicted in testing (E152). Wider stops or stand aside for the release.")
    memory["news_sent"] = sorted(seen)[-300:]
    if len(out) > 1:   # several releases at once: one message
        heads = [o.split("\n")[0] for o in out]
        out = ["\n".join(heads) + "\n" + out[0].split("\n", 1)[1]]
    return out


def summary(states: list[dict]) -> str:
    lines = ["🌅 OMEGA morning read"]
    for s in states:
        r = s.get("read") or {}
        v, sc = r.get("volatility") or {}, (r.get("scouts") or {}).get("day") or {}
        hz = " · ".join(f"{k} {h.get('state')}" for k, h in (s.get("horizons") or {}).items())
        p = sc.get("p_big_move")
        lines.append(f"{s.get('name', s['asset'])} {fmt_price(r.get('price'))} | 1h trend {((r.get('trend') or {}).get('1h') or {}).get('state', '?')}"
                     f" | vol {v.get('regime', '?')} | typical day range {v.get('day_range_pct_median', '?')}%"
                     + (f" | big 4h move chance {p * 100:.0f}%" if isinstance(p, (int, float)) else "") + f" | {hz}")
    lines.append("Calls come only from tested rules. WATCH = move likely, direction unknown.")
    return "\n".join(lines)


def send(text: str, client: httpx.Client | None = None) -> dict:
    c = client or httpx.Client(timeout=20)
    res = {}
    box = os.environ.get("OMEGA_OUTBOX")   # every message is also written here; the Live API forwards it (see /alerts/pump)
    if box:
        os.makedirs(os.path.dirname(box), exist_ok=True)
        with open(box, "a", encoding="utf-8") as f:
            f.write(f"\n## {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M:%S} UTC\n{text}\n")
        res["outbox"] = "written"
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if tok and chat:
        try:
            r = c.post(f"https://api.telegram.org/bot{tok}/sendMessage", json=dict(chat_id=chat, text=text[:4000]))
            res["telegram"] = r.status_code
        except httpx.HTTPError as e:
            res["telegram"] = type(e).__name__
    phone, key = os.environ.get("WHATSAPP_PHONE"), os.environ.get("CALLMEBOT_APIKEY")
    if phone and key:
        try:
            r = c.get("https://api.callmebot.com/whatsapp.php", params=dict(phone=phone, text=text[:1500], apikey=key))
            res["whatsapp"] = r.status_code
        except httpx.HTTPError as e:
            res["whatsapp"] = type(e).__name__
    return res


def main(state_dir: str, now: dt.datetime | None = None, client=None):
    root = Path(state_dir)
    now = now or dt.datetime.now(dt.timezone.utc)
    adir = root / "alerts"
    adir.mkdir(parents=True, exist_ok=True)
    mfile = adir / "memory.json"
    memory = json.loads(mfile.read_text()) if mfile.exists() else {}
    first_run = not memory
    states = [json.loads((root / "assets" / f"{a}.json").read_text()) for a in ASSETS if (root / "assets" / f"{a}.json").exists()]
    msgs = []
    for s in states:
        msgs += changes(s, memory)
    if first_run:
        msgs = []
    memory["_state_dir"] = str(root)
    msgs += news_ahead(memory, now, client)
    memory.pop("_state_dir", None)  # do not flood on the first run; the summary below says where things stand
    today = now.strftime("%Y-%m-%d")
    if states and (first_run or (now.hour >= 11 and memory.get("summary_day") != today)):
        msgs.insert(0, summary(states))
        memory["summary_day"] = today
    sent = {}
    if msgs:
        text = "\n\n".join(msgs)
        sent = send(text, client)
        if not os.environ.get("OMEGA_OUTBOX"):
            with open(adir / "outbox.md", "a", encoding="utf-8") as f:
                f.write(f"\n## {now:%Y-%m-%d %H:%M:%S} UTC\n{text}\n")
    mfile.write_text(json.dumps(memory, indent=1))
    print(f"alerts: {len(msgs)} message(s), channels {sent or 'none configured'}")
    return msgs, sent


if __name__ == "__main__":
    main(sys.argv[1])
