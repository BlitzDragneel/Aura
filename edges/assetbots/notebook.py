"""'What I know about <asset>': a plain-language notebook built without any language model from
  1. the research findings (edges/assets/<asset>/FINDINGS.md, written by the research bots),
  2. the rules approved for this asset (edges/approved.json),
  3. what the bot measures itself on recent candles (habits of the market), and
  4. its own forward record (readings and calls scored after the fact).
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SESS = (("Asia", 0, 7), ("London", 7, 13), ("New York", 13, 21), ("late US", 21, 24))


def findings(asset: str, path: Path | None = None) -> dict:
    """{'general': [...], 'day': [...], 'swing': [...], 'hold': [...]} - short lines from FINDINGS.md."""
    f = Path(path or REPO / "edges" / "assets" / asset / "FINDINGS.md")
    out = {"general": [], "day": [], "swing": [], "hold": []}
    if not f.exists():
        return out
    cur = "general"
    for raw in f.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("|---") or line.startswith("```"):
            continue
        if line.startswith("#"):
            h = line.lower()
            cur = ("day" if re.search(r"\bday\b|intraday", h) else "swing" if "swing" in h
                   else "hold" if re.search(r"\bhold", h) else "general")
            continue
        text = re.sub(r"^[-*+]\s+|^\d+\.\s+", "", line)
        text = re.sub(r"\*\*|__|`", "", text).strip()
        if text and len(out[cur]) < 8:
            out[cur].append(text if len(text) <= 300 else text[:297] + "...")
    return out


def habits(spec, bars: dict) -> list[str]:
    out = []
    h1, d1 = bars.get("1h"), bars.get("1d")
    if h1 is not None and len(h1) > 100:
        r = np.log(h1.c).diff().abs()
        hrs = h1.index.hour
        act = {n: float(r[(hrs >= a) & (hrs < b)].mean()) for n, a, b in SESS}
        best = max(act, key=act.get)
        quiet = min(act, key=act.get)
        out.append(f"Over the last {len(h1) // 24} days the busiest session was {best} (average hourly move "
                   f"{act[best] * 100:.2f}%) and the quietest {quiet} ({act[quiet] * 100:.2f}%).")
        if spec.weekend_closed:
            wk = r[h1.index.dayofweek >= 5].mean()
            wd = r[h1.index.dayofweek < 5].mean()
            if wk == wk and wd == wd and wd > 0:
                out.append(f"At weekends, while spot is closed, the perpetual moves {wk / wd:.0%} as much per hour as on "
                           "weekdays: weekend prices are thin and less reliable.")
    if d1 is not None and len(d1) > 30:
        rng = ((d1.h - d1.l) / d1.c).iloc[-60:]
        up = (d1.c.diff() > 0).iloc[-60:].mean()
        out.append(f"A typical day ranges {rng.median() * 100:.1f}% from low to high (last 60 days); "
                   f"{up:.0%} of those days closed higher.")
        ch = d1.c.iloc[-1] / d1.c.iloc[max(0, len(d1) - 31)] - 1
        out.append(f"Over the last 30 days the price moved {ch * 100:+.1f}% (a fact, not a forecast).")
    return out


def build(spec, read: dict, fwd: dict, bars: dict, approved: list, findings_path: Path | None = None) -> dict:
    fd = findings(spec.code, findings_path)
    rules = [r for r in approved if r.get("asset") == spec.code]
    passed = [r for r in rules if r.get("status") in ("paper", "testnet", "live")]
    sections = []
    s1 = []
    if any(fd.values()):
        s1 += fd["general"][:6]
    else:
        s1.append(f"The research on {spec.name} is still running: edges/assets/{spec.code}/FINDINGS.md is not written yet.")
    sections.append(dict(title="What the research found", lines=s1))
    for hz, title in (("day", "Day trades"), ("swing", "Swing trades (1-20 days)"), ("hold", "Holding (weeks-months)")):
        ln = list(fd[hz][:6])
        mine = [r for r in passed if r.get("horizon") == hz]
        if mine:
            ln += [f"Tested rule I can call: {r['id']} (grade {r.get('grade')}, status {r.get('status')}). "
                   f"Evidence: {r.get('evidence')}" for r in mine]
        else:
            ln.append("No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.")
        f = fwd.get(hz) or {}
        if f.get("text"):
            ln.append("My own record: " + f["text"] + ".")
        sections.append(dict(title=title, lines=ln))
    sections.append(dict(title="Habits I measure myself", lines=habits(spec, bars) or ["Not enough candles yet."]))
    v = read.get("volatility", {})
    now = [f"Price {read.get('price')}; volatility regime {v.get('regime', 'unknown')}"
           + (f" (hourly ATR {v.get('atr1h_pct')}% of price, {v.get('atr1h_pctile')}th percentile)" if v.get("atr1h_pct") else "")
           + "."]
    if read.get("session", {}).get("note"):
        now.append(read["session"]["note"] + ".")
    sp = read.get("spot")
    if sp and sp.get("price"):
        now.append(f"Spot {spec.spot} {sp['price']:.2f}" + (" (stale: market closed)" if sp.get("stale") else "")
                   + (f"; the perpetual trades {sp['perp_premium_pct']:+.2f}% from spot" if sp.get("perp_premium_pct") is not None else "")
                   + ".")
    sections.append(dict(title="Right now", lines=now))
    c = fwd.get("calls") or {}
    sections.append(dict(title="My calls so far", lines=[c.get("text", "none")]))
    md = [f"# What I know about {spec.name} ({spec.code})", "",
          "Built automatically from the research findings, the approved rules and my own forward record. "
          "No language model; no invented directions.", ""]
    for s in sections:
        md += [f"## {s['title']}", ""] + [f"- {x}" for x in s["lines"]] + [""]
    return dict(sections=sections, markdown="\n".join(md))
