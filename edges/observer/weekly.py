"""Weekly review (runs inside the 15-minute workflow; writes once per ISO week, on the first run after Monday 00:30 UTC).
Reads what the bots recorded during the past 7 days and writes <state>/journal/weekly-YYYY-Www.md + weekly.jsonl:
  1. the Signal Lab's live record per setup x trend side (hour-clustered), the five markets and all markets, against the
     backtest prior for the same cell; the record of signals actually sent with a plan; learning changes;
  2. Recorder studies (data nobody archives): liquidation bursts and what price did in the next hour, order-book
     imbalance vs the next hour, gold/silver spot spread by hour, coverage (runs per day);
  3. questions for the research session (cells drifting away from their backtest, recorder effects worth a registered
     test once 4+ weeks exist).
Descriptive only: no live rule changes here (the lab's adapt() and the research session's registered tests do that).
Usage: python -m edges.observer.weekly <state_dir> [--force]"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CORE = ("XAUUSD", "XAGUSD", "BTCUSD", "NAS100", "US30")


def clustered(sig):
    h = {}
    for s in sig:
        h.setdefault(s["logged_ms"] // 3_600_000, []).append(s["R_ladder"])
    cl = [np.mean(v) for v in h.values()]
    if not cl:
        return dict(signals=0, moments=0)
    t = (np.mean(cl) / (np.std(cl, ddof=1) / np.sqrt(len(cl)))) if len(cl) > 2 and np.std(cl, ddof=1) > 0 else None
    return dict(signals=len(sig), moments=len(cl), avg_R=round(float(np.mean(cl)), 3), t=round(float(t), 2) if t is not None else None,
                won=round(float(np.mean([s["R_ladder"] > 0 for s in sig])), 2))


def main(state_dir, force=False):
    root = Path(state_dir); now = dt.datetime.now(dt.timezone.utc)
    iso = now.isocalendar(); tag = f"{iso[0]}-W{iso[1]:02d}"
    jd = root / "journal"; jd.mkdir(parents=True, exist_ok=True)
    out = jd / f"weekly-{tag}.md"
    if not force and (out.exists() or now.weekday() != 0 or now.hour == 0 and now.minute < 30):
        return print("weekly: not due")
    t0 = int((now - dt.timedelta(days=7)).timestamp() * 1000)
    W = dict(week=tag, made=now.isoformat(), lab={}, recorder={}, questions=[])
    L = [f"# Weekly review {tag} (made {now:%Y-%m-%d %H:%M} UTC)", ""]
    lab = root / "siglab" / "signals.json"
    if lab.exists():
        S = json.loads(lab.read_text())
        closed = [s for s in S["signals"] if s.get("status") == "closed" and s.get("R_ladder") is not None and s.get("state") and (s.get("closed_ms") or 0) >= t0]
        try:
            pri = json.loads((Path(__file__).resolve().parents[1] / "siglab" / "priors.json").read_text()).get("history", {})
        except Exception:
            pri = {}
        cells = {}
        for s in closed:
            k = f"{s['setup']} {'with' if s['state'].get('with_trend') else 'against'}"
            cells.setdefault(k, []).append(s)
        L += ["## Signal Lab, last 7 days (all markets; 'moments' = separate hours = real sample size)", "",
              "| setup | signals | moments | avg R | t | won | five markets avg R | backtest avg R (BTC / gold) |", "|---|---|---|---|---|---|---|---|"]
        for k, v in sorted(cells.items()):
            a, c5 = clustered(v), clustered([s for s in v if s["symbol"] in CORE])
            bk = "/".join(str((pri.get(m) or {}).get(k, {}).get("avg_R", "–")) for m in ("BTCUSD", "XAUUSD"))
            W["lab"][k] = dict(all=a, core=c5, backtest=bk)
            L.append(f"| {k} | {a['signals']} | {a['moments']} | {a.get('avg_R')} | {a.get('t')} | {a.get('won')} | {c5.get('avg_R', '–')} | {bk} |")
            if a["moments"] >= 10 and a.get("avg_R") is not None and a["avg_R"] > 0.1:
                W["questions"].append(f"{k}: +{a['avg_R']}R over {a['moments']} moments live this week; backtest {bk}. Worth a registered re-test on fresh data?")
        sent = [s for s in closed if s.get("plan_sent")]
        if sent:
            L.append(f"\n**Signals sent with a trade plan this week:** {clustered(sent)}")
        lg = [x for x in S.get("adapt_log", []) if x.get("ms", 0) >= t0]
        L.append(f"**Learning changes this week:** {lg if lg else 'none'}")
    rec = sorted((root / "recorder").glob("*.csv")) if (root / "recorder").exists() else []
    frames = []
    for f in rec[-8:]:
        try:
            frames.append(pd.read_csv(f))
        except Exception:
            pass
    if frames:
        R = pd.concat(frames); R["utc"] = pd.to_datetime(R.utc, utc=True)
        R = R[R.utc >= pd.Timestamp(now - dt.timedelta(days=7))]
        L += ["", "## Recorder (data nobody archives), last 7 days", ""]
        cov = R.groupby(R.utc.dt.date).utc.nunique()
        L.append(f"Coverage: {int(cov.mean()) if len(cov) else 0} runs per day on average (96 = every 15 minutes).")
        for m, g in R.groupby("market"):
            g = g.sort_values("utc").drop_duplicates("utc").set_index("utc")
            if "price" not in g or g.price.isna().all() or len(g) < 40:
                continue
            nxt = g.price.shift(-4) / g.price - 1          # about 1 hour later
            info = dict(rows=int(len(g)))
            if m in ("XAUUSD", "XAGUSD", "BTCUSD") and g.imb_05.notna().sum() > 30:
                info["imbalance_vs_next_hour_corr"] = round(float(g.imb_05.corr(nxt, method="spearman")), 3)
                liq = g.liq_long_usd.fillna(0) + g.liq_short_usd.fillna(0)
                if (liq > 0).sum() >= 10:
                    big = liq >= liq[liq > 0].quantile(0.9)
                    side = np.sign(g.liq_short_usd.fillna(0) - g.liq_long_usd.fillna(0))   # +1 shorts squeezed, -1 longs flushed
                    after = (side * nxt)[big].dropna()
                    info["liq_bursts"] = int(big.sum())
                    info["after_burst_same_direction_bp"] = round(float(after.mean() * 1e4), 1) if len(after) else None
                if g.spot_spread_bp.notna().sum() > 30:
                    sp = g.spot_spread_bp.groupby(g.index.hour).median()
                    info["spread_bp_widest_hour_utc"] = int(sp.idxmax()); info["spread_bp_median"] = round(float(g.spot_spread_bp.median()), 2)
            W["recorder"][m] = info
            L.append(f"- {m}: {info}")
        W["questions"].append("Recorder effects are descriptive until 4+ weeks exist; then register a test (liquidation bursts, imbalance).")
    mr = root / "memory" / "RECORD.json"
    if mr.exists():
        M = json.loads(mr.read_text()); W["memory"] = M
        L += ["", "## Candle memory forward record (all time; 50% = coin flip, backtest said 52-55%)", "",
              "| market | scored | next hour right | confident right (n) | big-move calls came / base rate |", "|---|---|---|---|---|"]
        for sym, r in M.items():
            L.append(f"| {sym} | {r.get('scored')} | {r.get('next_hour_right', '-')} | {r.get('confident_right', '-')} ({r.get('confident_calls', 0)}) | {r.get('big_move_came', '-')} / {r.get('big_move_base', '-')} |")
        W["questions"].append("Candle memory: is forward next-hour accuracy above 52% with 500+ scored per market? Only then test it as a filter on lab signals (registered plan).")
    L += ["", "## Questions for the research session", ""] + [f"- {q}" for q in W["questions"]]
    out.write_text("\n".join(L) + "\n")
    (jd / "weekly.jsonl").open("a").write(json.dumps(W, default=str) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], "--force" in sys.argv)
