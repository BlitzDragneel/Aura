"""Bots feed for the OMEGA app: what the paper bot holds and did, and the scouts' latest calls and forward scores.

Source, in order: the local OMEGA Station folder (OMEGA_STATION_HOME, or %APPDATA%/OMEGA-Station, ~/OMEGA-Station) when
this API runs on the laptop next to the Station; otherwise the public bot-state branch on GitHub (the cloud bots).
Read-only and information only.
"""
from __future__ import annotations

import csv
import io
import json
import os
import time
from pathlib import Path

import httpx

RAW = os.environ.get("OMEGA_BOTSTATE_URL", "https://raw.githubusercontent.com/BlitzDragneel/Aura/bot-state")


def station_home() -> Path | None:
    for p in (os.environ.get("OMEGA_STATION_HOME"),
              os.path.join(os.environ.get("APPDATA", ""), "OMEGA-Station") if os.environ.get("APPDATA") else None,
              str(Path.home() / "OMEGA-Station")):
        if p and (Path(p) / "station.json").exists():
            return Path(p)
    return None


class Feed:
    def __init__(self, client: httpx.Client | None = None):
        self.c = client or httpx.Client(timeout=15, headers={"User-Agent": "omega-live/1.0"})
        self._cache: tuple[float, dict] | None = None

    def _read(self, local: Path | None, rel_local: str, rel_remote: str) -> str | None:
        if local is not None:
            f = local / rel_local
            return f.read_text(encoding="utf-8", errors="ignore") if f.exists() else None
        r = self.c.get(f"{RAW}/{rel_remote}", params={"t": int(time.time() // 60)})
        return r.text if r.status_code == 200 else None

    @staticmethod
    def _status(txt: str | None) -> dict | None:
        if not txt:
            return None
        i = txt.find("{")
        try:
            return json.loads(txt[i:]) if i >= 0 else None
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _scouts(txt: str | None, top: int = 12) -> dict | None:
        if not txt:
            return None
        rows = list(csv.DictReader(io.StringIO(txt)))
        if not rows:
            return None
        last = max(r["time"] for r in rows)
        latest = [r for r in rows if r["time"] == last]
        f = lambda r, k: float(r.get(k) or 0)
        latest.sort(key=lambda r: -max(f(r, "p_up_move"), f(r, "p_down_move")))
        scored = [r for r in rows if r.get("fwd") not in (None, "", "nan")]
        def hit(flag, y):
            fl = [r for r in scored if r.get(flag) in ("1", "1.0", "True")]
            return dict(flagged=len(fl), hit_rate=(sum(float(r.get(y) or 0) for r in fl) / len(fl)) if fl else None)
        return dict(latest_time=last, predictions=len(rows), scored=len(scored),
                    base_rate_up=(sum(float(r.get("y_up_move") or 0) for r in scored) / len(scored)) if scored else None,
                    up_flags=hit("flag_up_move", "y_up_move"), down_flags=hit("flag_down_move", "y_down_move"),
                    latest=[{k: r.get(k) for k in ("sym", "close", "p_up_move", "p_down_move", "p_turn_up", "p_turn_down",
                                                     "flag_up_move", "flag_down_move", "flag_turn_up", "flag_turn_down")}
                            for r in latest[:top]])

    def get(self) -> dict:
        if self._cache and time.time() - self._cache[0] < 60:
            return self._cache[1]
        home = station_home()
        out = dict(source="laptop (OMEGA Station)" if home else "cloud bots (GitHub bot-state)", asof=int(time.time() * 1000),
                   note="paper/testnet records and forecasts; information only, never an order")
        try:
            out["paper_bot"] = self._status(self._read(home, "last_status.txt", "STATUS.txt"))
            out["scouts_hourly"] = self._scouts(self._read(home, "scouts/predictions.csv", "scouts/predictions.csv"))
            out["scouts_fast"] = self._scouts(self._read(home, "fast_scouts/predictions.csv", "fast_scouts/predictions.csv"))
        except httpx.HTTPError as e:
            out["error"] = f"could not read the bot records: {type(e).__name__}"
        self._cache = (time.time(), out)
        return out
