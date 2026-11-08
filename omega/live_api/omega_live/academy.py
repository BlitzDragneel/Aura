"""OMEGA Academy endpoints (contract: omega/academy/CONTRACT.md).

Public:   GET  /academy/catalog            course outline + FREE lesson bodies + pricing
Buyers:   POST /academy/unlock             {"license_key"} -> verified with Gumroad (or ACADEMY_KEYS) -> signed token
          GET  /academy/lesson/{id}        free lessons for anyone; premium lessons need header X-Academy-Token
Env:      ACADEMY_SECRET               HMAC key for tokens (required to unlock; without it unlocking is off)
          ACADEMY_GUMROAD_PRODUCT_ID   Gumroad product id (license keys enabled on the product)
          ACADEMY_KEYS                 optional comma list of extra keys (gifts, testers)
Premium text is only ever sent by /academy/lesson to a valid token; it is never inside the app.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from collections import defaultdict, deque
from pathlib import Path

import httpx
from fastapi import APIRouter, Body, Header, HTTPException, Request

from .signals import REPO

ACADEMY = Path(os.environ.get("ACADEMY_DIR", REPO / "omega" / "academy"))
TOKEN_DAYS = 365


def _secret() -> bytes:
    return os.environ.get("ACADEMY_SECRET", "").encode()


def sign(payload: dict) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    mac = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{body}.{mac}"


def check(token: str | None) -> dict | None:
    if not token or "." not in token or not _secret():
        return None
    body, mac = token.rsplit(".", 1)
    good = hmac.new(_secret(), body.encode(), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(mac, good):
        return None
    try:
        p = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
    except (ValueError, json.JSONDecodeError):
        return None
    return p if p.get("exp", 0) > time.time() else None


class Course:
    def __init__(self):
        self._mtime, self._data = None, None

    def data(self) -> dict:
        f = ACADEMY / "course.json"
        if not f.exists():
            return {"title": "OMEGA Academy", "modules": [], "disclaimer": "", "status": "being written"}
        m = f.stat().st_mtime
        if m != self._mtime:
            self._data, self._mtime = json.loads(f.read_text(encoding="utf-8")), m
        return self._data

    @staticmethod
    def is_free(module: dict, lesson: dict) -> bool:
        return bool(lesson.get("free", module.get("free", False)))

    def find(self, lid: str):
        for mo in self.data().get("modules", []):
            for le in mo.get("lessons", []):
                if le.get("id") == lid:
                    return mo, le
        return None, None


def pricing() -> dict:
    f = ACADEMY / "pricing.json"
    return json.loads(f.read_text()) if f.exists() else {}


def verify_license(key: str, client: httpx.Client | None = None) -> tuple[bool, str]:
    key = key.strip()
    extra = {k.strip() for k in os.environ.get("ACADEMY_KEYS", "").split(",") if k.strip()}
    if key and key in extra:
        return True, "key list"
    pid = os.environ.get("ACADEMY_GUMROAD_PRODUCT_ID", "").strip()
    if not pid:
        return False, "sales are not open yet (no product configured)"
    c = client or httpx.Client(timeout=10)
    try:
        r = c.post("https://api.gumroad.com/v2/licenses/verify",
                   data={"product_id": pid, "license_key": key, "increment_uses_count": "false"})
        d = r.json()
    except (httpx.HTTPError, ValueError):
        return False, "could not reach the checkout to verify; try again in a minute"
    if not d.get("success"):
        return False, "this license key was not found"
    p = d.get("purchase", {})
    if p.get("refunded") or p.get("chargebacked") or p.get("disputed"):
        return False, "this purchase was refunded or disputed"
    return True, "gumroad"


def router(http_client: httpx.Client | None = None) -> APIRouter:
    r = APIRouter(prefix="/academy", tags=["academy"])
    course = Course()
    attempts: dict[str, deque] = defaultdict(lambda: deque(maxlen=20))

    @r.get("/catalog")
    def catalog():
        d = course.data()
        mods = []
        for mo in d.get("modules", []):
            les = []
            for le in mo.get("lessons", []):
                free = course.is_free(mo, le)
                item = {k: le.get(k) for k in ("id", "title", "minutes")}
                item["free"] = free
                if free:
                    item.update({k: le.get(k) for k in ("body_md", "key_points", "quiz")})
                les.append(item)
            mods.append(dict(id=mo.get("id"), title=mo.get("title"), summary=mo.get("summary"), free=bool(mo.get("free")),
                             lessons=les))
        return dict(title=d.get("title"), version=d.get("version"), updated=d.get("updated"),
                    disclaimer=d.get("disclaimer"), pricing=pricing(), modules=mods,
                    unlock_open=bool(_secret()) and bool(os.environ.get("ACADEMY_GUMROAD_PRODUCT_ID") or os.environ.get("ACADEMY_KEYS")))

    @r.post("/unlock")
    def unlock(request: Request, payload: dict = Body(...)):
        ip = request.client.host if request.client else "?"
        q = attempts[ip]
        now = time.time()
        while q and now - q[0] > 600:
            q.popleft()
        if len(q) >= 10:
            raise HTTPException(429, "too many attempts; wait 10 minutes")
        q.append(now)
        key = str(payload.get("license_key", ""))[:200]
        if not key.strip():
            raise HTTPException(400, "enter your license key")
        if not _secret():
            raise HTTPException(503, "unlocking is not switched on yet")
        ok, why = verify_license(key, http_client)
        if not ok:
            raise HTTPException(403, why)
        kh = hashlib.sha256(key.strip().encode()).hexdigest()[:16]
        return dict(ok=True, token=sign(dict(k=kh, exp=int(now + TOKEN_DAYS * 86400))), via=why)

    @r.get("/lesson/{lid}")
    def lesson(lid: str, x_academy_token: str | None = Header(default=None)):
        if len(lid) > 40:
            raise HTTPException(400, "bad lesson id")
        mo, le = course.find(lid)
        if le is None:
            raise HTTPException(404, "no such lesson")
        if not course.is_free(mo, le) and not check(x_academy_token):
            raise HTTPException(402, "this lesson is part of the full course")
        return dict(module=mo.get("id"), **le)

    return r
