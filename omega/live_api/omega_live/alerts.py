"""Forwards the bots' alert messages to the owner's Telegram / WhatsApp.

The cloud bots (GitHub Actions) write every alert to bot-state/alerts/outbox.md. They then call
GET /alerts/pump?sha=<commit>; this service reads that file at that exact commit and forwards the entries written in
the last 45 minutes that it has not already sent. The channel credentials live only in this service's environment
(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, optional WHATSAPP_PHONE, CALLMEBOT_APIKEY). The endpoint takes no message text,
so calling it can only deliver the bots' own recent messages.
"""
from __future__ import annotations

import datetime as dt
import os
import re

import httpx
from fastapi import APIRouter, HTTPException, Query

RAW = "https://raw.githubusercontent.com/BlitzDragneel/Aura"


def parse(md: str):
    out = []
    for part in md.split("\n## ")[1:]:
        head, _, body = part.partition("\n")
        m = re.match(r"(\d{4}-\d\d-\d\d \d\d:\d\d(?::\d\d)?) UTC", head)
        if m and body.strip():
            ts = m.group(1) + (":00" if len(m.group(1)) == 16 else "")
            out.append((dt.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc), body.strip()))
    return out


def router(client: httpx.Client | None = None) -> APIRouter:
    r = APIRouter(prefix="/alerts")
    c = client or httpx.Client(timeout=20)
    sent: set = set()

    @r.get("/pump")
    def pump(sha: str = Query(..., pattern=r"^[0-9a-f]{40}$")):
        tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
        phone, key = os.environ.get("WHATSAPP_PHONE"), os.environ.get("CALLMEBOT_APIKEY")
        if not ((tok and chat) or (phone and key)):
            raise HTTPException(503, "no channel configured on this service")
        g = c.get(f"{RAW}/{sha}/alerts/outbox.md")
        if g.status_code != 200:
            raise HTTPException(404, "no outbox at that commit")
        now = dt.datetime.now(dt.timezone.utc)
        res = dict(forwarded=0, telegram=None, whatsapp=None)
        for ts, body in parse(g.text):
            k = (ts.isoformat(), hash(body))
            if k in sent or (now - ts).total_seconds() > 45 * 60 or ts > now + dt.timedelta(minutes=5):
                continue
            sent.add(k)
            if tok and chat:
                for i in range(0, len(body), 3900):
                    res["telegram"] = c.post(f"https://api.telegram.org/bot{tok}/sendMessage", json=dict(chat_id=chat, text=body[i:i + 3900])).status_code
            if phone and key:
                res["whatsapp"] = c.get("https://api.callmebot.com/whatsapp.php", params=dict(phone=phone, text=body[:1500], apikey=key)).status_code
            res["forwarded"] += 1
        if len(sent) > 5000:
            sent.clear()
        return res

    return r
