"""The Observer: once a day it writes what happened in the markets and what the bots did and learned, so the daily
research session (and the owner) start from facts. Output: <state>/journal/YYYY-MM-DD.md and journal.jsonl (one JSON
line per day), plus an "issues" list for the researcher to fix (data errors, stale feeds, losing streaks, muted cells).
Runs inside the 15-minute workflow; writes once per UTC day for the previous day.
Usage: python -m edges.observer.journal <state_dir> [YYYY-MM-DD]"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

MARKETS = {"XAUUSD": "Gold", "XAGUSD": "Silver", "BTCUSD": "Bitcoin", "NAS100": "Nasdaq 100", "US30": "Dow 30"}   # the owner's five
OKX = {"XAUUSD": "XAU-USDT-SWAP", "XAGUSD": "XAG-USDT-SWAP", "BTCUSD": "BTC-USDT-SWAP"}
YAHOO = {"NAS100": "NQ=F", "US30": "YM=F"}


def hourly(c, inst, day):
    end = int((pd.Timestamp(day, tz="UTC") + pd.Timedelta("1D")).timestamp() * 1000)
    rows, after = [], end
    for _ in range(6):
        d = c.get("https://www.okx.com/api/v5/market/history-candles", params=dict(instId=inst, bar="1H", after=str(after), limit="100")).json().get("data") or []
        if not d:
            break
        rows += [(int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4])) for k in d]
        after = int(d[-1][0])
        if len(rows) >= 520:
            break
    h = pd.DataFrame(rows, columns=["t", "o", "h", "l", "c"]).drop_duplicates("t").sort_values("t")
    h.index = pd.to_datetime(h.t, unit="ms", utc=True)
    return h


def yahoo_hourly(c, ticker):
    r = c.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}", params=dict(range="60d", interval="1h"), headers={"User-Agent": "Mozilla/5.0"})
    j = r.json()["chart"]["result"][0]; q = j["indicators"]["quote"][0]
    h = pd.DataFrame(dict(o=q["open"], h=q["high"], l=q["low"], c=q["close"]), index=pd.to_datetime(j["timestamp"], unit="s", utc=True)).dropna()
    return h


def market_day(h, day):
    d0 = pd.Timestamp(day, tz="UTC")
    x = h[(h.index >= d0) & (h.index < d0 + pd.Timedelta("1D"))]
    if len(x) < 12:
        return None
    dd = h.resample("1D").agg(dict(o="first", h="max", l="min", c="last")).dropna()
    rng = (dd.h - dd.l) / dd.o
    past = rng[rng.index < d0].tail(20)
    mv = (x.c - x.o).abs() / x.o
    big = mv.idxmax()
    sess = lambda t: "Asia" if t.hour < 7 else ("London" if t.hour < 13 else ("New York" if t.hour < 21 else "late"))
    by_sess = (x.h - x.l).groupby([sess(t) for t in x.index]).sum() / x.o.iloc[0] * 100
    return dict(open=round(float(x.o.iloc[0]), 4), close=round(float(x.c.iloc[-1]), 4), change_pct=round(float((x.c.iloc[-1] / x.o.iloc[0] - 1) * 100), 2),
                range_pct=round(float((x.h.max() - x.l.min()) / x.o.iloc[0] * 100), 2),
                range_vs_20d=round(float(((x.h.max() - x.l.min()) / x.o.iloc[0]) / past.median()), 2) if len(past) >= 10 else None,
                biggest_hour=dict(utc=big.strftime("%H:%M"), session=sess(big), move_pct=round(float((x.c[big] - x.o[big]) / x.o[big] * 100), 2)),
                active_session=str(by_sess.idxmax()))


def main(state_dir, day=None):
    root = Path(state_dir)
    jd = root / "journal"; jd.mkdir(parents=True, exist_ok=True)
    day = day or (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).strftime("%Y-%m-%d")
    if (jd / f"{day}.md").exists() and len(sys.argv) < 3:
        print("journal exists for", day); return
    c = httpx.Client(timeout=20)
    J = dict(day=day, markets={}, issues=[])
    for sym in MARKETS:
        try:
            h = hourly(c, OKX[sym], day) if sym in OKX else yahoo_hourly(c, YAHOO[sym])
            J["markets"][sym] = market_day(h, day)
        except Exception as e:
            J["issues"].append(f"data: {sym} hourly candles failed ({type(e).__name__})")
    try:
        from edges.alerts.notify import calendar
        ev = calendar(root, c)
        J["news"] = [f"{e['date'][11:16]} ET {e['title']} (forecast {e.get('forecast') or '-'})"
                     for e in ev if e.get("impact") == "High" and e.get("country") == "USD" and e.get("date", "")[:10] == day]
    except Exception:
        J["news"] = []; J["issues"].append("data: news calendar unreachable")
    lab = root / "siglab" / "signals.json"
    if lab.exists():
        S = json.loads(lab.read_text())
        d0 = int(pd.Timestamp(day, tz="UTC").timestamp() * 1000); d1 = d0 + 86_400_000
        issued = [s for s in S["signals"] if d0 <= s["logged_ms"] < d1]
        closed = [s for s in S["signals"] if s.get("closed_ms") and d0 <= s["closed_ms"] < d1]
        core_ = [s for s in closed if s["symbol"] in MARKETS]
        other = [s for s in closed if s["symbol"] not in MARKETS and s.get("R_ladder") is not None]
        J["signals"] = dict(issued=len(issued), with_plan=sum(bool(s.get("plan_sent")) for s in issued),
                            closed=[dict(m=s["symbol"], setup=s["setup"], side=s["side"], outcome=s.get("outcome"), R=s.get("R_ladder"), why=s.get("review")) for s in core_],
                            others=dict(n=len(other), avg_R=round(float(np.mean([s["R_ladder"] for s in other])), 3) if other else None))
        board = {}
        for s in S["signals"]:
            if s.get("status") == "closed" and s.get("R_ladder") is not None and s.get("state"):
                k = f"{s['setup']} {'with' if s['state'].get('with_trend') else 'against'}"
                board.setdefault(k, {}).setdefault(s["logged_ms"] // 3_600_000, []).append(s["R_ladder"])
        J["scoreboard"] = {k: dict(signals=sum(len(v) for v in h.values()), moments=len(h),
                                   avg_R=round(float(np.mean([np.mean(v) for v in h.values()])), 3)) for k, h in sorted(board.items())}
        J["learning"] = [x for x in S.get("adapt_log", []) if d0 <= x.get("ms", 0) < d1]
        J["record"] = S.get("record", {}).get("all")
        sent = [s["R_ladder"] for s in S["signals"] if s.get("plan_sent") and s.get("status") == "closed" and s.get("R_ladder") is not None]
        J["record_sent"] = dict(n=len(sent), avg_R=round(float(np.mean(sent)), 3) if sent else None, won=sum(r > 0 for r in sent))
        Rs = [s["R_ladder"] for s in sorted(S["signals"], key=lambda s: s.get("closed_ms") or 0) if s.get("status") == "closed" and s.get("R_ladder") is not None]
        streak = 0
        for r in reversed(Rs):
            if r < 0: streak += 1
            else: break
        if streak >= 5:
            J["issues"].append(f"lab: {streak} losing signals in a row")
        stale = [s for s in S["signals"] if s["status"] == "open" and (d1 - s["logged_ms"]) > 3 * 86_400_000]
        if stale:
            J["issues"].append(f"lab: {len(stale)} signals still open after 3 days (scoring problem?)")
    else:
        J["issues"].append("lab: no signals.json")
    hb = sorted((root / "assets").glob("*.json")) if (root / "assets").exists() else []
    for f in hb:
        try:
            a = json.loads(f.read_text())
            if a.get("errors"):
                J["issues"].append(f"desk {f.stem}: {a['errors'][:2]}")
        except Exception:
            pass
    (jd / "journal.jsonl").open("a").write(json.dumps(J, default=str) + "\n")
    L = [f"# Market journal {day}", ""]
    for sym, m in J["markets"].items():
        if m:
            L.append(f"- **{MARKETS[sym]}** {m['change_pct']:+.2f}% (range {m['range_pct']}%, {m['range_vs_20d']}x its 20-day norm); biggest hour {m['biggest_hour']['utc']} UTC "
                     f"({m['biggest_hour']['session']}, {m['biggest_hour']['move_pct']:+.2f}%); most active: {m['active_session']}")
    if J.get("news"):
        L += ["", "**High-impact news:** " + "; ".join(J["news"])]
    sg = J.get("signals")
    if sg:
        L += ["", f"**Signal Lab:** {sg['issued']} signals ({sg['with_plan']} with a trade plan); {len(sg['closed'])} closed:"]
        L += [f"- {x['m']} {x['side']} {x['setup']}: {x['outcome']} {x['R']:+.2f}R. {x['why']}" for x in sg["closed"] if x["R"] is not None]
        if sg["others"]["n"]:
            L.append(f"- other coins (logged, not sent): {sg['others']['n']} closed, avg {sg['others']['avg_R']:+.2f}R")
        if J.get("scoreboard"):
            L += ["", "**Live scoreboard by setup (all markets; 'moments' = separate hours, the real sample size):**"]
            L += [f"- {k}: {v['signals']} signals / {v['moments']} moments, avg {v['avg_R']:+.2f}R" for k, v in J["scoreboard"].items()]
        if J.get("learning"):
            L.append("**Learned:** " + "; ".join(f"{x['cell']} {x.get('frm')}->{x.get('to')}" for x in J["learning"]))
        if J.get("record"):
            L.append(f"**Record so far (all signals, mostly logged only):** {J['record']}")
        rs = J.get("record_sent") or {}
        if rs.get("n"):
            L.append(f"**Signals the owner received with a trade plan:** {rs['n']} closed, {rs['won']} positive, average {rs['avg_R']:+.2f}R")
    bp = Path(state_dir) / "bigpicture" / "latest.json"
    if bp.exists():
        J["bigpicture"] = json.loads(bp.read_text())
        md = Path(state_dir) / "bigpicture" / f"{J['bigpicture']['day']}.md"
        if md.exists():
            L += ["", "**Big picture (week/month play, money flow):**"] + [l for l in md.read_text().splitlines()[2:] if l.strip()]
    mr = Path(state_dir) / "memory" / "RECORD.json"
    if mr.exists():
        J["memory"] = json.loads(mr.read_text())
        L += ["", "**Candle memory (predicts the next hour from look-alike candles + boosting; a mistake model learned from its own wrong calls decides when to make a CALL; information only):**"]
        for sym, r in J["memory"].items():
            x = r.get("latest", {})
            fw = f"{r.get('scored', 0)} scored" + (f", right {r['all_right']:.0%}" if "all_right" in r else "") + \
                 (f"; its CALLS right {r['calls_right']:.0%} of {r['calls_scored']}" if "calls_right" in r else f"; {r.get('calls_scored', 0)} calls scored")
            L.append(f"- {MARKETS.get(sym, sym)}: now {x.get('call')} (P up next hour {x.get('p_up1h')}, P right {x.get('p_right')}); record: {fw}")
        mf = Path(state_dir) / "memory" / "mistakes.csv"
        if mf.exists():
            M = pd.read_csv(mf); M = M[M.bar.astype(str).str[:10] == str(day)]
            if len(M):
                rs = M.why.str.split("; ").explode().str.replace(r"news: .*", "news", regex=True).str.replace(r"shock move .*", "shock move", regex=True)
                L.append(f"- wrong predictions today: {len(M)}; why: " + ", ".join(f"{k} {v}" for k, v in rs.value_counts().head(6).items()))
        uf = Path(state_dir) / "memory" / "UPGRADES.md"
        if uf.exists():
            last = uf.read_text().strip().split("## Self-review")[-1]
            L.append("- latest self-review:" + " ".join(l.strip() for l in last.splitlines()[1:] if l.strip())[:900])
    L += ["", "**Issues for the researcher:** " + ("; ".join(J["issues"]) if J["issues"] else "none")]
    (jd / f"{day}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
