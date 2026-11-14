"""Which rules may give an asset bot a direction: edges/approved.json entries with this "asset" and "horizon" and a
status of paper, testnet or live, whose strategy file edges/bots/strategies/<id>.py exists. Nothing else can.

Flags per rule (shown with every call):
  execution_allowed  True only when the rule's status is testnet or live (orders are the trading bot's job, not ours)
  research_only      True while the status is paper: the call is a paper record to build the forward record
"""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
APPROVED = Path(os.environ.get("OMEGA_APPROVED") or REPO / "edges" / "approved.json")
HORIZONS = ("day", "swing", "hold")
PASS_STATUS = ("paper", "testnet", "live")


def load_approved(path: Path | None = None) -> list[dict]:
    p = Path(path or APPROVED)
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return []


def rules_for(asset: str, horizon: str, approved: list[dict] | None = None) -> list[dict]:
    rows = load_approved() if approved is None else approved
    out = []
    for r in rows:
        if r.get("asset") != asset or r.get("horizon") != horizon:
            continue
        if r.get("status") not in PASS_STATUS:
            continue
        rr = dict(r)
        rr["execution_allowed"] = r.get("status") in ("testnet", "live")
        rr["research_only"] = not rr["execution_allowed"]
        out.append(rr)
    return out


def load_strategy(rule_id: str):
    """The Strategy object for a rule, or None if its file is missing/broken (then the rule cannot give a direction)."""
    try:
        mod = importlib.import_module(f"edges.bots.strategies.{rule_id}")
        return getattr(mod, "STRATEGY", None)
    except Exception:          # a broken strategy file must not take the bot down; it simply gives no direction
        return None
