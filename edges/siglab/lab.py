"""OMEGA Signal Lab: produces paper signals every day on five markets, scores every one in real money, and learns
which setups deserve to be sent as real signals.

Markets: gold, silver, Bitcoin (24/7 perps) + NAS100 and US30 (futures shifted to the cash level).
Six setups, each can fire at most once per market per UTC day (so several paper signals a day per market):
  S1 trend pullback   15m close back above/below EMA20 while EMA50 is above/below EMA200 (with the trend)
  S2 breakout         15m close beyond the prior 4-hour range by 0.1 ATR, range expanding
  S3 stretch fade     price more than 2.5 ATR(15m) from its 4-hour mean: fade back toward it
  S4 fib pullback     50% retracement of a >= 3 ATR impulse leg (the Profit4Life chart method), with the leg
  S5 session drive    first 30 minutes after the London (07:00 UTC) or New York (13:30 UTC) open: follow it
  S6 daily bias       once a day at 07:00 UTC: with the 3-day drift
Template (Profit4Life geometry): entry at market, stop = 1 ATR of 1-hour bars (R), targets every 0.5 R up to 2.5 R.
Scoring: edges/auditor/core.py rules (1-minute bars, stop first, spread charged, max 24 h): "ladder" = fifths at each
target with the stop moved to entry after TP1.
Grades per setup+market from the FORWARD record only: CONFIDENT = at least 30 closed, average > 0 R with t >= 2;
PROMISING = at least 15 closed and average > 0; otherwise PAPER. Thirty setup-markets are being watched at once, so
one or two will look good by luck: CONFIDENT signals are still to be traded small.

Usage: python -m edges.siglab.lab <state_dir>
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from edges.alerts.notify import send
from edges.auditor import core
from edges.auditor.data import Prices

MARKETS = {"XAUUSD": "Gold", "XAGUSD": "Silver", "BTCUSD": "Bitcoin", "NAS100": "Nasdaq 100", "US30": "Dow 30"}
SETUPS = {"S1": "trend pullback", "S2": "breakout", "S3": "stretch fade", "S4": "fib pullback", "S5": "session drive", "S6": "daily bias"}
H = 3_600_000


def frames(bars):
    m = pd.DataFrame(bars).set_index(pd.to_datetime([b["t"] for b in bars], unit="ms", utc=True))[["o", "h", "l", "c"]]
    agg = dict(o="first", h="max", l="min", c="last")
    f = m.resample("15min").agg(agg).dropna()
    h1 = m.resample("1h").agg(agg).dropna()
    now = pd.Timestamp.now(tz="UTC")
    return f[f.index + pd.Timedelta("15min") <= now], h1[h1.index + pd.Timedelta("1h") <= now]


def atr(d, n=14):
    tr = pd.concat([d.h - d.l, (d.h - d.c.shift()).abs(), (d.l - d.c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def detect(f, h1):
    """Setups firing on the LAST closed 15m bar -> list of (setup, direction, why)."""
    out = []
    if len(f) < 210 or len(h1) < 20:
        return out, None
    c, a = f.c, atr(f)
    e20, e50, e200 = c.ewm(span=20).mean(), c.ewm(span=50).mean(), c.ewm(span=200).mean()
    i, t = -1, f.index[-1]
    A = a.iloc[i]
    R = float(atr(h1).iloc[-1])
    if not (A > 0 and R > 0):
        return out, None
    up, dn = e50.iloc[i] > e200.iloc[i], e50.iloc[i] < e200.iloc[i]
    if up and c.iloc[i - 1] < e20.iloc[i - 1] and c.iloc[i] > e20.iloc[i]:
        out.append(("S1", 1, "uptrend, price closed back above its short average after a dip"))
    if dn and c.iloc[i - 1] > e20.iloc[i - 1] and c.iloc[i] < e20.iloc[i]:
        out.append(("S1", -1, "downtrend, price closed back below its short average after a bounce"))
    hh, ll = f.h.iloc[-17:-1].max(), f.l.iloc[-17:-1].min()
    wide = (f.h.iloc[i] - f.l.iloc[i]) > 1.2 * A
    if c.iloc[i] > hh + 0.1 * A and wide:
        out.append(("S2", 1, "closed above the last 4 hours' high on a wide bar"))
    if c.iloc[i] < ll - 0.1 * A and wide:
        out.append(("S2", -1, "closed below the last 4 hours' low on a wide bar"))
    mean4 = c.iloc[-16:].mean()
    if c.iloc[i] > mean4 + 2.5 * A:
        out.append(("S3", -1, "stretched far above its 4-hour average"))
    if c.iloc[i] < mean4 - 2.5 * A:
        out.append(("S3", 1, "stretched far below its 4-hour average"))
    seg = f.iloc[-12:-1]
    hi, lo = seg.h.max(), seg.l.min()
    if hi - lo >= 3 * A:
        if seg.h.idxmax() > seg.l.idxmin() and f.l.iloc[i] <= hi - 0.5 * (hi - lo) <= f.h.iloc[i] and c.iloc[i] > lo:
            out.append(("S4", 1, "pulled back half of a strong up-leg"))
        if seg.l.idxmin() > seg.h.idxmax() and f.l.iloc[i] <= lo + 0.5 * (hi - lo) <= f.h.iloc[i] and c.iloc[i] < hi:
            out.append(("S4", -1, "bounced back half of a strong down-leg"))
    hm = (t.hour, t.minute)
    if hm in ((7, 15), (13, 45)) and t.weekday() < 5:      # bar closing 07:30 / 14:00 UTC
        mv = c.iloc[i] - f.o.iloc[i - 1]
        if abs(mv) > 0.5 * A:
            out.append(("S5", int(np.sign(mv)), ("London" if hm[0] == 7 else "New York") + " open drive"))
    if hm == (6, 45) and t.weekday() < 5:                  # bar closing 07:00 UTC
        mv = c.iloc[i] - c.iloc[0]
        out.append(("S6", int(np.sign(mv)) or 1, "with the 3-day drift"))
    return out, dict(price=float(c.iloc[i]), R=R, bar_close_ms=int((t + pd.Timedelta("15min")).timestamp() * 1000))


def make(sym, setup, d, why, ctx):
    name, spec = core.instrument(sym)
    dec = 2 if spec["pip"] >= 0.1 else 3
    px, R = ctx["price"], max(ctx["R"], 6 * spec["spread"])       # the stop is never tighter than 6 spreads
    return dict(id=f"{name}-{setup}-{ctx['bar_close_ms']}", symbol=name, setup=setup, side="buy" if d == 1 else "sell", why=why,
                logged_ms=ctx["bar_close_ms"], ref_price=round(px, dec), stop=round(px - d * R, dec),
                targets=[round(px + d * R * 0.5 * k, dec) for k in range(1, 6)], R=round(R, dec + 1), status="open")


def stats(rs):
    n = len(rs)
    if n == 0:
        return dict(n=0, avg_R=None, t=None, win=None, total_R=0.0)
    mu = sum(rs) / n
    sd = math.sqrt(sum((r - mu) ** 2 for r in rs) / (n - 1)) if n > 1 else 0.0
    return dict(n=n, avg_R=round(mu, 3), t=round(mu / sd * math.sqrt(n), 2) if sd > 0 else None, win=round(sum(r > 0 for r in rs) / n, 3), total_R=round(sum(rs), 2))


def grade(s):
    if s["n"] >= 30 and (s["avg_R"] or 0) > 0 and (s["t"] or 0) >= 2:
        return "CONFIDENT"
    if s["n"] >= 15 and (s["avg_R"] or 0) > 0:
        return "PROMISING"
    return "PAPER"


def text(sig, g, rec):
    name = MARKETS[sig["symbol"]]
    tag = {"CONFIDENT": "🟢 CONFIDENT", "PROMISING": "🟡 PROMISING", "PAPER": "🧪 PAPER (untested, do not trade)"}[g]
    r = f"record of this setup here: {rec['n']} closed, avg {rec['avg_R']:+.2f}R, {round(rec['win'] * 100)}% won" if rec["n"] else "no record yet"
    return (f"{tag}\n{name} {sig['side'].upper()} now ~{sig['ref_price']}\nSL {sig['stop']}\n" + "\n".join(f"TP{k + 1} {t}" for k, t in enumerate(sig["targets"]))
            + f"\nSetup: {SETUPS[sig['setup']]} ({sig['why']})\n{r}")


def main(state_dir, prices=None, now_ms=None, client=None):
    root = Path(state_dir) / "siglab"
    root.mkdir(parents=True, exist_ok=True)
    sf = root / "signals.json"
    S = json.loads(sf.read_text()) if sf.exists() else dict(signals=[], sent_day={}, digest_day="")
    px = prices or Prices()
    now_ms = now_ms or int(time.time() * 1000)
    msgs, new = [], []
    by = {}
    for s in S["signals"]:
        if s["status"] == "closed" and s.get("R_ladder") is not None:
            by.setdefault((s["symbol"], s["setup"]), []).append(s["R_ladder"])
    for sym in MARKETS:
        try:
            bars, src = px.bars(sym, now_ms - 72 * H, 72)
        except Exception as e:
            print(sym, "data error", str(e)[:120])
            continue
        # score open signals of this market on the same bars
        for s in S["signals"]:
            if s["symbol"] != sym or s["status"] != "open":
                continue
            sg = core.Signal(symbol=sym, side=s["side"], logged_ms=s["logged_ms"], stop=s["stop"], targets=s["targets"], id=s["id"])
            r = core.score(sg, bars, fill_hours=1, max_hold_h=24)
            if r.get("status") == "closed":
                s.update(status="closed", fill=r["fill"], outcome=r["ladder"]["outcome"], R_ladder=r["ladder"]["R"], R_tp1=r["tp1"]["R"],
                         pips=r["ladder"]["pips"], closed_ms=r["ladder"]["exit_ms"], source=src)
                by.setdefault((sym, s["setup"]), []).append(s["R_ladder"])
                if s.get("sent"):
                    msgs.append(f"{'✅' if s['R_ladder'] > 0 else ('➖' if s['R_ladder'] == 0 else '❌')} {MARKETS[sym]} {s['side'].upper()} ({SETUPS[s['setup']]}) closed: {s['outcome']}, {s['R_ladder']:+.2f}R ({s['pips']:+.0f} pips)")
            elif now_ms - s["logged_ms"] > 80 * H:
                s.update(status="expired")
        f, h1 = frames(bars)
        found, ctx = detect(f, h1)
        if not ctx or now_ms - ctx["bar_close_ms"] > 20 * 60_000:      # stale data (market closed): no new signals
            continue
        day = time.strftime("%Y-%m-%d", time.gmtime(ctx["bar_close_ms"] / 1000))
        for setup, d, why in found:
            if any(s["symbol"] == sym and s["setup"] == setup and s["day"] == day for s in S["signals"]):
                continue
            sig = make(sym, setup, d, why, ctx)
            sig["day"] = day
            rec = stats(by.get((sym, setup), []))
            g = grade(rec)
            sig["grade_at_issue"] = g
            first_today = S["sent_day"].get(sym) != day
            if g != "PAPER" or first_today:                              # every confident/promising one + one paper per market per day
                sig["sent"] = True
                S["sent_day"][sym] = day
                msgs.append(text(sig, g, rec))
            new.append(sig)
    S["signals"] += new
    S["signals"] = S["signals"][-5000:]
    table = {f"{k[0]} {k[1]}": dict(stats(v), grade=grade(stats(v))) for k, v in sorted(by.items())}
    per_setup = {}
    for (sym, st), v in by.items():
        per_setup.setdefault(st, []).extend(v)
    S["record"] = dict(by_setup_market=table, by_setup={k: stats(v) for k, v in sorted(per_setup.items())},
                       all=stats([r for v in by.values() for r in v]), open=sum(s["status"] == "open" for s in S["signals"]))
    today = time.strftime("%Y-%m-%d", time.gmtime(now_ms / 1000))
    if time.gmtime(now_ms / 1000).tm_hour >= 21 and S.get("digest_day") != today:
        S["digest_day"] = today
        a = S["record"]["all"]
        lines = [f"📊 Signal Lab, end of day: {a['n']} paper signals closed so far, avg {a['avg_R'] if a['avg_R'] is not None else 0:+.2f}R, {S['record']['open']} open."]
        for k, v in S["record"]["by_setup"].items():
            lines.append(f"{SETUPS[k]}: {v['n']} closed, avg {v['avg_R']:+.2f}R, {round(v['win'] * 100)}% won")
        good = [f"{k} ({v['grade']}, {v['n']} closed, {v['avg_R']:+.2f}R)" for k, v in table.items() if v["grade"] != "PAPER"]
        lines.append("Earning trust: " + (", ".join(good) if good else "none yet (needs 15+ closed and a positive average)"))
        msgs.append("\n".join(lines))
    sf.write_text(json.dumps(S, indent=1))
    md = ["# OMEGA Signal Lab (paper signals, every one scored)", "", f"Updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now_ms / 1000))}", "",
          "| setup · market | closed | avg R | t | won | grade |", "|---|---|---|---|---|---|"]
    md += [f"| {k} | {v['n']} | {v['avg_R']} | {v['t']} | {v['win']} | {v['grade']} |" for k, v in table.items()]
    md += ["", "## Latest signals", ""] + [f"- {time.strftime('%d %b %H:%M', time.gmtime(s['logged_ms'] / 1000))} {s['symbol']} {s['side']} {s['setup']} @ {s['ref_price']} SL {s['stop']} → {s['status']}"
                                           + (f" {s.get('outcome')} {s.get('R_ladder'):+.2f}R" if s["status"] == "closed" else "") for s in S["signals"][-40:][::-1]]
    (root / "SIGNALS.md").write_text("\n".join(md))
    res = send("\n\n".join(msgs), client) if msgs else {}
    print(f"siglab: {len(new)} new, {len(msgs)} messages, channels {res or 'none'}; record {S['record']['all']}")
    return new, msgs


if __name__ == "__main__":
    main(sys.argv[1])
