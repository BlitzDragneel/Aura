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
  S7 big move         price moved at least twice its normal hourly range within the last hour: follow it
Alerts go out the moment an event setup fires on a closed 15-minute bar (S1, S2, S4, S5, S7); S3 and S6 are opinions
about what might happen, so they are only logged until their record earns a grade.
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

MARKETS = {"XAUUSD": "Gold", "XAGUSD": "Silver", "BTCUSD": "Bitcoin", "NAS100": "Nasdaq 100", "US30": "Dow 30",
           "ETHUSD": "Ethereum", "SOLUSD": "Solana", "BNBUSD": "BNB", "XRPUSD": "XRP", "DOGEUSD": "Dogecoin", "ADAUSD": "Cardano",
           "AVAXUSD": "Avalanche", "LINKUSD": "Chainlink", "LTCUSD": "Litecoin", "SUIUSD": "Sui"}
CORE = {"XAUUSD", "XAGUSD", "BTCUSD", "NAS100", "US30"}     # every event alert is sent for these
COIN_LIVE = {"S2", "S7"}                                    # other coins: only breakouts and big moves are sent (plus anything graded)
SETUPS = {"S1": "trend pullback", "S2": "breakout", "S3": "stretch fade", "S4": "fib pullback", "S5": "session drive", "S6": "daily bias",
          "S7": "big move"}
LIVE = {"S1": "TREND resuming", "S2": "BREAKOUT", "S4": "PULLBACK in a strong move", "S5": "SESSION DRIVE", "S7": "BIG MOVE under way"}  # alerted as they happen
H = 3_600_000


def frames15(rows):
    f = pd.DataFrame(rows).set_index(pd.to_datetime([b["t"] for b in rows], unit="ms", utc=True))[["o", "h", "l", "c"]]
    h1 = f.resample("1h").agg(dict(o="first", h="max", l="min", c="last")).dropna()
    now = pd.Timestamp.now(tz="UTC")
    return f, h1[h1.index + pd.Timedelta("1h") <= now]


def digits(px):
    return max(0, 5 - len(str(int(px)))) if px >= 1 else 6


def review(s, r, ctx_stats):
    """Plain-language reason for a closed signal: what price did, and how this kind of signal has done in this state."""
    R = s["R"]
    spec = core.instrument(s["symbol"])[1]
    pip = spec["pip"] or s["ref_price"] * 1e-4
    mfe, mae = r["mfe_pips"] * pip / R, r["mae_pips"] * pip / R
    mins = round((r["ladder"]["exit_ms"] - r["fill_ms"]) / 60000)
    o = r["ladder"]["outcome"]
    st_ = s.get("state") or {}
    if o == "SL":
        why = (f"Stopped out after {mins} min. Price never reached TP1 (best was {mfe:.1f}R in favour, TP1 needs 0.5R)." if mfe < 0.5
               else f"Stopped out after {mins} min.")
        if st_ and not st_.get("with_trend"):
            why += " The signal was against the 15-minute trend."
        if st_.get("vol") == "high":
            why += " Volatility was high, so a 1R stop was easy to hit."
        if st_.get("shape") == "compressed":
            why += " The range was compressed: breaks from tight ranges often fail first."
    elif o.endswith("+BE"):
        why = f"Reached {o.split('+')[0]} then came back to the entry (best {mfe:.1f}R). Partial profit kept by moving the stop to entry."
    elif o.startswith("TP5"):
        why = f"All five targets hit in {mins} min: the move kept going ({mfe:.1f}R)."
    elif "timeout" in o:
        why = f"Closed at the 24-hour limit ({o}); the move stalled (best {mfe:.1f}R, worst -{mae:.1f}R)."
    else:
        why = f"{o} after {mins} min (best {mfe:.1f}R, worst -{mae:.1f}R)."
    if st_:
        k = f"{s['setup']} | {'with' if st_.get('with_trend') else 'against'} trend"
        c = ctx_stats.get(k)
        if c and c["n"] >= 3:
            why += f" Lesson so far: {SETUPS[s['setup']]} {'with' if st_.get('with_trend') else 'against'} the trend: {c['n']} closed, avg {c['avg_R']:+.2f}R, {round(c['win'] * 100)}% won."
    return why


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
    r4h, r24 = f.h.iloc[-16:].max() - f.l.iloc[-16:].min(), f.h.iloc[-96:].max() - f.l.iloc[-96:].min()
    am = a.iloc[-288:].median()
    state = dict(trend="up" if up else ("down" if dn else "flat"),
                 vol="high" if A > 1.3 * am else ("low" if A < 0.7 * am else "normal"),
                 shape="compressed" if r4h < 0.35 * r24 else ("expanding" if r4h > 0.7 * r24 else "normal"),
                 session="Asia" if t.hour < 7 else ("London" if t.hour < 13 else ("New York" if t.hour < 21 else "late")))
    mv1 = c.iloc[i] - c.iloc[i - 4]
    if abs(mv1) >= 2 * R:
        out.append(("S7", int(np.sign(mv1)), f"moved {mv1:+.2f} in the last hour, twice its normal hourly range"))
    R_eff = max(R, 0.002 * float(c.iloc[i]))
    return out, dict(state=state, price=float(c.iloc[i]), R=R, bar_close_ms=int((t + pd.Timedelta("15min")).timestamp() * 1000),
                     exc=excursions(f, R_eff) if out else {})


def excursions(f, R, horizon=16):
    """What this market has actually been doing: for every 15m bar of the last ~3 days, how far price went in favour of a
    long (and of a short) within the next 4 hours BEFORE going 1R against. Returns for each side the levels reached in
    60%, 40% and 20% of those windows (as multiples of R). This is the bot's "what I believe will happen" for targets."""
    H, L, C = f.h.values[-300:], f.l.values[-300:], f.c.values[-300:]
    n = len(C) - horizon - 1
    if n < 50:
        return {}
    idx = np.arange(n)[:, None] + np.arange(1, horizon + 1)[None, :]
    Hm, Lm, C0 = H[idx], L[idx], C[:n, None]
    res = {}
    for d in (1, -1):
        fav = (Hm - C0) if d == 1 else (C0 - Lm)
        adv = (C0 - Lm) if d == 1 else (Hm - C0)
        hit = adv >= R
        first = np.where(hit.any(axis=1), hit.argmax(axis=1), horizon)          # stop bar (stop first inside it)
        mask = np.arange(horizon)[None, :] < first[:, None]
        best = np.where(mask, fav, 0).max(axis=1) / R
        q = np.quantile(best, [0.4, 0.6, 0.8])
        res[d] = [round(float(x), 3) for x in q]
    return res


ADAPTIVE_TP = True


def make(sym, setup, d, why, ctx):
    name, spec = core.instrument(sym)
    px = ctx["price"]
    dec = (2 if spec["pip"] >= 0.1 else 3) if spec.get("pip") else digits(px)
    R = max(ctx["R"], 6 * (spec["spread"] if spec.get("spread") is not None else px * spec["spread_frac"]), 0.002 * px)   # stop never tighter than 6 spreads or 0.2% of price (about 8 USD on gold)
    return dict(id=f"{name}-{setup}-{ctx['bar_close_ms']}", symbol=name, setup=setup, side="buy" if d == 1 else "sell", why=why,
state=dict(ctx.get("state") or {}, with_trend=(ctx.get("state") or {}).get("trend") == ("up" if d == 1 else "down")),
                logged_ms=ctx["bar_close_ms"], ref_price=round(px, dec), stop=round(px - d * R, dec),
                targets=targets_for(px, d, R, ctx, spec, dec), R=round(R, dec + 1), status="open",
                target_odds=[60, 40, 20] if (ADAPTIVE_TP and (ctx.get("exc") or {}).get(d)) else None)


def targets_for(px, d, R, ctx, spec, dec):
    q = (ctx.get("exc") or {}).get(d) if ADAPTIVE_TP else None
    if not q:
        return [round(px + d * R * 0.5 * k, dec) for k in range(1, 6)]
    cost = spec["spread"] if spec.get("spread") is not None else px * spec["spread_frac"]
    lv, last = [], 0.0
    for m in q:
        m = max(m, last + 0.15, 0.25, 3 * cost / R)       # at least 0.25R, 3 spreads, and spaced 0.15R apart
        lv.append(m); last = m
    return [round(px + d * R * m, dec) for m in lv]


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


try:
    _P = json.loads((Path(__file__).parent / "priors.json").read_text())
    PRIORS, EVERYWHERE, HISTORY = _P["priors"], _P.get("everywhere") or {}, _P.get("history") or {}
except (OSError, ValueError, KeyError):
    PRIORS, EVERYWHERE, HISTORY = {}, {}, {}


def history_line(sig):
    """'Time machine' line: how this exact setup did on this market's own recent history (E148/E149 replay, final period)."""
    k = f"{sig['setup']} {'with' if (sig.get('state') or {}).get('with_trend') else 'against'}"
    h = (HISTORY.get(sig["symbol"]) or {}).get(k)
    if not h or not h.get("n"):
        return ""
    return f"\n⏪ On this market's recent history: {h['n']} of these, {round((h['win'] or 0) * 100)}% ended positive, average {h['avg_R']:+.2f}R"


MUTED_OLD = {"XAGUSD-S4-1794757500000"}   # 15 Nov silver alert sent without a plan before plan_sent existed
ADAPT: dict = {}   # filled by adapt() from the FORWARD record each run; it overrides the backtest priors


def side_key(sig):
    return f"{sig['setup']} {'with' if (sig.get('state') or {}).get('with_trend') else 'against'}"


def adapt(S: dict) -> list[str]:
    """Self-learning without anyone present: every setup x trend-side cell (pooled over all markets) is judged on its own
    forward record. 30+ closed with average < 0 and t <= -1.5 -> muted; a cell muted by the backtest that earns 30+ closed
    with average > 0 and t >= 1.5 -> unmuted. Changes are logged in S["adapt_log"] and announced."""
    cells = {}
    for x in S["signals"]:
        if x["status"] == "closed" and x.get("R_ladder") is not None and x.get("state"):
            cells.setdefault(side_key(x), []).append(x["R_ladder"])
    new = {}
    for k, v in cells.items():
        st = stats(v)
        if st["n"] >= 30 and (st["avg_R"] or 0) < 0 and (st["t"] or 0) <= -1.5:
            new[k] = dict(state="muted", **st)
        elif st["n"] >= 30 and (st["avg_R"] or 0) > 0 and (st["t"] or 0) >= 1.5:
            new[k] = dict(state="earned", **st)
    old = S.get("adapt") or {}
    msgs = []
    for k in sorted(set(new) | set(old)):
        a, b = (old.get(k) or {}).get("state"), (new.get(k) or {}).get("state")
        if a != b:
            setup, side = k.split()
            v = new.get(k) or {}
            line = (f"🔁 Learning: {SETUPS[setup]} {side} the trend is now {'MUTED (no trade plans)' if b == 'muted' else ('EARNED (trade plans sent again, tagged)' if b == 'earned' else 'back to normal')}"
                    + (f" after {v['n']} live signals averaging {v['avg_R']:+.2f}R." if v else "."))
            msgs.append(line)
            S.setdefault("adapt_log", []).append(dict(ms=int(time.time() * 1000), cell=k, frm=a, to=b, **({k2: v[k2] for k2 in ('n', 'avg_R', 't')} if v else {})))
    S["adapt"] = new
    ADAPT.clear(); ADAPT.update(new)
    return msgs


def prior(sig):
    """('muted'|'plus'|None, avg R) for this setup and trend side: the forward record first, then the backtests (E148/E149)."""
    k = side_key(sig)
    if k in ADAPT:
        a = ADAPT[k]
        return ("muted" if a["state"] == "muted" else "earned"), a["avg_R"]
    p = PRIORS.get(sig["symbol"]) or {}
    if k in (p.get("muted") or {}):
        return "muted", p["muted"][k]
    if k in (p.get("plus") or {}):
        return "plus", p["plus"][k]
    if k in (EVERYWHERE.get("muted") or {}):     # lost on at least 4 of the 5 replayed markets (E149)
        return "muted", EVERYWHERE["muted"][k]
    return None, None


def text(sig, g, rec):
    pk, pv = prior(sig)
    if pk == "muted" and g == "PAPER":
        st0 = sig.get("state") or {}
        src = "its live record" if ADAPT.get(side_key(sig)) else "past data"
        return (f"⚡ {MARKETS[sig['symbol']]}: {LIVE.get(sig['setup'], SETUPS[sig['setup']])} right now ({sig['why']}), price ~{sig['ref_price']}\n"
                f"Market now: trend {st0.get('trend')}, volatility {st0.get('vol')}, {st0.get('session')} session\n"
                f"ℹ️ No trade plan: on {src}, trading this kind of move {'with' if st0.get('with_trend') else 'against'} the trend lost money (avg {pv:+.2f}R). Logged and scored anyway.")
    name = MARKETS[sig["symbol"]]
    tag = {"CONFIDENT": "🟢 CONFIDENT", "PROMISING": "🟡 PROMISING", "PAPER": "🧪 PAPER (untested, do not trade)"}[g]
    if pk == "earned":
        tag += f"\n✅ EARNED LIVE (this setup averaged {pv:+.2f}R over its live signals)"
    if pk == "plus":
        tag += f"\n📈 BACKTEST+ (made {pv:+.2f}R per signal on past data; live record still needed)"
    tag += history_line(sig)
    r = f"record of this setup here: {rec['n']} closed, avg {rec['avg_R']:+.2f}R, {round(rec['win'] * 100)}% won" if rec["n"] else "no record yet"
    head = f"⚡ {name}: {LIVE[sig['setup']]} right now\n" if sig["setup"] in LIVE else ""
    st_ = sig.get("state") or {}
    head += (f"Market now: trend {st_.get('trend')}, volatility {st_.get('vol')}, {st_.get('shape')} range, {st_.get('session')} session\n" if st_ else "")
    return (f"{head}{tag}\n{name} {sig['side'].upper()} now ~{sig['ref_price']}\nSL {sig['stop']}\n" + "\n".join(f"TP{k + 1} {t}" + (f" (reached in {sig['target_odds'][k]}% of similar moments in the last 3 days)" if sig.get("target_odds") else "") for k, t in enumerate(sig["targets"]))
            + f"\nSetup: {SETUPS[sig['setup']]} ({sig['why']})\n{r}")


def scout_flags(state_root: Path, S: dict) -> list[str]:
    """UpScout / DownScout: send each NEW top-2% call (hourly scouts, 24h horizon) once, with the scouts' forward record."""
    f = state_root / "scouts" / "predictions.csv"
    if not f.exists():
        return []
    try:
        d = pd.read_csv(f)
    except Exception:
        return []
    d["t"] = pd.to_datetime(d.time, utc=True)
    rec = {}
    for k, lab_ in (("up_move", "y_up_move"), ("down_move", "y_down_move")):
        sc = d[(d[f"flag_{k}"] == 1) & d[lab_].notna()]
        rec[k] = (len(sc), float(sc[lab_].mean()) if len(sc) else None, float(d[lab_].dropna().mean()) if d[lab_].notna().any() else None)
    last = pd.Timestamp(S.get("scout_last") or "2000-01-01", tz="UTC") if not str(S.get("scout_last", "")).endswith("+00:00") else pd.Timestamp(S["scout_last"])
    new = d[(d.t > last) & ((d.flag_up_move == 1) | (d.flag_down_move == 1) | (d.flag_turn_up == 1) | (d.flag_turn_down == 1))]
    if len(d):
        S["scout_last"] = d.t.max().isoformat()
    if not len(new) or last.year == 2000:          # first run: remember the point, do not flood
        return []
    lines = []
    for _, r in new.sort_values("t").tail(8).iterrows():
        kinds = [n for n, c in (("big UP move likely", "flag_up_move"), ("big DOWN move likely", "flag_down_move"),
                                ("trend turning UP", "flag_turn_up"), ("trend turning DOWN", "flag_turn_down")) if r[c] == 1]
        lines.append(f"{r.sym.replace('USDT', '')} {r.close:g}: " + ", ".join(kinds) + f" (up {r.p_up_move:.0%} / down {r.p_down_move:.0%} in 24h)")
    def fr(k):
        n, h, b = rec[k]
        return f"{n} scored, {h:.0%} came true vs {b:.0%} normally" if n and h is not None and b is not None else "no scored calls yet"
    return ["🔭 Scouts (24-hour forecasts, information only, not trade signals):\n" + "\n".join(lines)
            + f"\nUpScout record: {fr('up_move')}. DownScout record: {fr('down_move')}."]


def main(state_dir, prices=None, now_ms=None, client=None):
    root = Path(state_dir) / "siglab"
    root.mkdir(parents=True, exist_ok=True)
    sf = root / "signals.json"
    S = json.loads(sf.read_text()) if sf.exists() else dict(signals=[], sent_day={}, digest_day="")
    px = prices or Prices()
    now_ms = now_ms or int(time.time() * 1000)
    msgs, new = adapt(S), []
    by = {}
    for s in S["signals"]:
        if s["status"] == "closed" and s.get("R_ladder") is not None:
            by.setdefault((s["symbol"], s["setup"]), []).append(s["R_ladder"])
    for sym in MARKETS:
        try:
            rows15 = px.candles15(sym) if hasattr(px, "candles15") else None
            opens = [s for s in S["signals"] if s["symbol"] == sym and s["status"] == "open"]
            if rows15 is None:
                bars, src = px.bars(sym, now_ms - 72 * H, 72)
            elif opens:
                t0 = min(s["logged_ms"] for s in opens)
                bars, src = px.bars(sym, t0, min(30, (now_ms - t0) / H + 0.1))
            else:
                bars, src = [], "okx-15m"
        except Exception as e:
            print(sym, "data error", str(e)[:120])
            continue
        # score open signals of this market
        for s in S["signals"]:
            if s["symbol"] != sym or s["status"] != "open" or not bars:
                continue
            sg = core.Signal(symbol=sym, side=s["side"], logged_ms=s["logged_ms"], stop=s["stop"], targets=s["targets"], id=s["id"])
            r = core.score(sg, bars, fill_hours=1, max_hold_h=24)
            if r.get("status") == "closed":
                s.update(status="closed", fill=r["fill"], outcome=r["ladder"]["outcome"], R_ladder=r["ladder"]["R"], R_tp1=r["tp1"]["R"],
                         pips=r["ladder"]["pips"], closed_ms=r["ladder"]["exit_ms"], source=src)
                by.setdefault((sym, s["setup"]), []).append(s["R_ladder"])
                s["review"] = review(s, r, S.get("record_by_context") or {})
                if s.get("sent") and s.get("plan_sent", s["id"] not in MUTED_OLD):
                    msgs.append(f"{'✅' if s['R_ladder'] > 0 else ('➖' if s['R_ladder'] == 0 else '❌')} {MARKETS[sym]} {s['side'].upper()} ({SETUPS[s['setup']]}) closed: {s['outcome']}, {s['R_ladder']:+.2f}R ({s['pips']:+.0f} pips)\nWhy: {s['review']}")
            elif now_ms - s["logged_ms"] > 80 * H:
                s.update(status="expired")
        f, h1 = frames15(rows15) if rows15 else frames(bars)
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
            if g != "PAPER" or (setup in LIVE and (sym in CORE or setup in COIN_LIVE)):        # alert when the move/breakout/trend happens; forecasts (S3, S6) only once they earn trust
                sig["sent"] = True
                sig["plan_sent"] = not (prior(sig)[0] == "muted" and g == "PAPER")   # muted: event alert only, no trade plan
                msgs.append(text(sig, g, rec))
            new.append(sig)
    msgs += adapt(S)
    msgs += scout_flags(Path(state_dir), S)
    S["signals"] += new
    S["signals"] = S["signals"][-5000:]
    table = {f"{k[0]} {k[1]}": dict(stats(v), grade=grade(stats(v))) for k, v in sorted(by.items())}
    per_setup = {}
    for (sym, st), v in by.items():
        per_setup.setdefault(st, []).extend(v)
    ctxs = {}
    for x in S["signals"]:
        if x["status"] == "closed" and x.get("R_ladder") is not None and x.get("state"):
            st_ = x["state"]
            for key in (f"{x['setup']} | {'with' if st_.get('with_trend') else 'against'} trend", f"{x['setup']} | vol {st_.get('vol')}",
                        f"{x['setup']} | {st_.get('shape')}", f"{x['setup']} | {st_.get('session')}"):
                ctxs.setdefault(key, []).append(x["R_ladder"])
    S["record_by_context"] = {k: stats(v) for k, v in sorted(ctxs.items())}   # which response fits which market state
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
                                           + (f" {s.get('outcome')} {s.get('R_ladder'):+.2f}R. {s.get('review', '')}" if s["status"] == "closed" else "") for s in S["signals"][-60:][::-1]]
    (root / "SIGNALS.md").write_text("\n".join(md))
    res = send("\n\n".join(msgs), client) if msgs else {}
    print(f"siglab: {len(new)} new, {len(msgs)} messages, channels {res or 'none'}; record {S['record']['all']}")
    return new, msgs


if __name__ == "__main__":
    main(sys.argv[1])
