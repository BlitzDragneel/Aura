"""Big picture (daily, first run after 00:20 UTC): the week/month play for the owner's five markets.
Trend over 1, 4 and 12 weeks; price vs its 20-week average; phase (trending vs choppy: 5-day efficiency vs its own
last year); money flow (total stablecoin supply 4-week change - money entering or leaving crypto), Fear & Greed, the
dollar (DXY) and US 10-year yield. Reports what the tested weekly rules say, with their real records (E166: none
passed; best: BTC money-flow rule +0.9%/week 2024-26, t 1.8, but lost in 2023). Description, not signals.
Writes <state>/bigpicture/latest.json, YYYY-MM-DD.md and history.jsonl. Usage: python -m edges.observer.bigpicture <state_dir>"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

YF = {"BTCUSD": "BTC-USD", "XAUUSD": "GC=F", "XAGUSD": "SI=F", "NAS100": "NQ=F", "US30": "YM=F", "DXY": "DX-Y.NYB", "US10Y": "^TNX"}
NAMES = {"BTCUSD": "Bitcoin", "XAUUSD": "Gold", "XAGUSD": "Silver", "NAS100": "Nasdaq 100", "US30": "Dow 30"}


def series(c, tk, rng="2y", iv="1d"):
    j = c.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{tk}", params=dict(range=rng, interval=iv)).json()["chart"]["result"][0]
    s = pd.Series(j["indicators"]["quote"][0]["close"], index=pd.to_datetime(j["timestamp"], unit="s", utc=True)).dropna()
    return s[~s.index.normalize().duplicated(keep="last")] if iv == "1d" else s[~s.index.duplicated()]


def main(state_dir, force=False):
    root = Path(state_dir) / "bigpicture"; root.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc); day = str(now.date())
    if not force and ((root / f"{day}.md").exists() or now.hour == 0 and now.minute < 20):
        return print("bigpicture: done today")
    c = httpx.Client(timeout=25, headers={"User-Agent": "Mozilla/5.0"})
    B = dict(day=day, markets={}, money={}, issues=[])
    for k, tk in YF.items():
        try:
            d = series(c, tk); h = series(c, tk, "60d", "1h")
        except Exception as e:
            B["issues"].append(f"{k}: {type(e).__name__}"); continue
        w = d.resample("W-SUN").last()
        eff_h = (h - h.shift(120)).abs() / h.diff().abs().rolling(120).sum()
        m = dict(price=round(float(d.iloc[-1]), 4), r1w=round(float(d.iloc[-1] / d.iloc[-6] - 1) * 100, 2) if len(d) > 6 else None,
                 r4w=round(float(w.iloc[-1] / w.iloc[-5] - 1) * 100, 2), r12w=round(float(w.iloc[-1] / w.iloc[-13] - 1) * 100, 2),
                 vs20w=round(float(w.iloc[-1] / w.iloc[-20:].mean() - 1) * 100, 2))
        e = eff_h.dropna()
        if len(e) > 200:
            m["phase_eff5d"] = round(float(e.iloc[-1]), 3)
            m["phase"] = "trending" if e.iloc[-1] >= e.quantile(2 / 3) else "choppy (fakeouts likely)" if e.iloc[-1] <= e.quantile(1 / 3) else "mixed"
        m["trend"] = "down" if m["r4w"] < 0 and m["vs20w"] < 0 else "up" if m["r4w"] > 0 and m["vs20w"] > 0 else "turning"
        (B["markets"] if k in NAMES else B["money"])[k] = m
    try:
        st = c.get("https://stablecoins.llama.fi/stablecoincharts/all").json()
        s = pd.Series({pd.Timestamp(int(x["date"]), unit="s", tz="UTC"): x["totalCirculatingUSD"].get("peggedUSD", np.nan) for x in st}).dropna()
        B["money"]["stablecoins"] = dict(total_bn=round(float(s.iloc[-1]) / 1e9, 1), chg_1w_pct=round(float(s.iloc[-1] / s.iloc[-8] - 1) * 100, 2),
                                          chg_4w_pct=round(float(s.iloc[-1] / s.iloc[-29] - 1) * 100, 2), chg_4w_bn=round(float(s.iloc[-1] - s.iloc[-29]) / 1e9, 1))
    except Exception as e:
        B["issues"].append(f"stablecoins: {type(e).__name__}")
    try:
        fg = c.get("https://api.alternative.me/fng/", params=dict(limit=30)).json()["data"]
        B["money"]["fear_greed"] = dict(now=int(fg[0]["value"]), label=fg[0]["value_classification"], four_weeks_ago=int(fg[-1]["value"]))
    except Exception as e:
        B["issues"].append(f"fear&greed: {type(e).__name__}")
    # what the tested weekly rules say (none passed E166; shown with their record)
    sc, btc = B["money"].get("stablecoins"), B["markets"].get("BTCUSD")
    rules = []
    if sc:
        rules.append(f"BTC money-flow rule (stablecoin supply 4w {sc['chg_4w_pct']:+.2f}%): {'DOWN' if sc['chg_4w_pct'] < 0 else 'UP'} next week "
                     "[record: 2019-22 +1.15%/wk, 2023 -0.48%/wk, 2024-26 +0.90%/wk t 1.8; did not pass]")
    if btc and sc:
        agree = np.sign(btc["r12w"]) == np.sign(sc["chg_4w_pct"])
        rules.append(f"BTC momentum + money flow {'AGREE: ' + ('DOWN' if btc['r12w'] < 0 else 'UP') if agree else 'disagree: no view'} "
                     "[record: 2019-22 +1.17%/wk, 2023 -0.28%, 2024-26 +0.45% t 1.1]")
    g, dx = B["markets"].get("XAUUSD"), B["money"].get("DXY")
    if g and dx:
        agree = np.sign(g["r12w"]) == -np.sign(dx["r4w"])
        rules.append(f"Gold momentum + dollar {'AGREE: ' + ('DOWN' if g['r12w'] < 0 else 'UP') if agree else 'disagree: no view'} "
                     "[record: 2019-23 flat, 2024-26 +0.35%/wk t 2.4; did not pass]")
    B["rules"] = rules
    L = [f"# Big picture {day}", ""]
    for k, m in B["markets"].items():
        L.append(f"- **{NAMES[k]}**: {m['trend']} trend; 1w {m['r1w']:+.1f}%, 4w {m['r4w']:+.1f}%, 12w {m['r12w']:+.1f}%, {m['vs20w']:+.1f}% vs 20-week avg; phase {m.get('phase', '?')}")
    mo = B["money"]
    if "stablecoins" in mo:
        s_ = mo["stablecoins"]; L.append(f"- **Money in crypto (stablecoins)**: ${s_['total_bn']}bn, {s_['chg_1w_pct']:+.2f}% this week, {s_['chg_4w_pct']:+.2f}% in 4 weeks ({s_['chg_4w_bn']:+.1f}bn) - {'leaving' if s_['chg_4w_pct'] < 0 else 'entering'}")
    if "fear_greed" in mo:
        L.append(f"- **Fear & Greed**: {mo['fear_greed']['now']} ({mo['fear_greed']['label']}), was {mo['fear_greed']['four_weeks_ago']} four weeks ago")
    for k in ("DXY", "US10Y"):
        if k in mo:
            L.append(f"- **{k}**: 4w {mo[k]['r4w']:+.1f}%, {mo[k]['trend']}")
    L += ["", "**What the tested weekly rules say (none passed the test; shown with their records):**"] + [f"- {r}" for r in rules]
    if B["issues"]:
        L += ["", "Issues: " + "; ".join(B["issues"])]
    (root / f"{day}.md").write_text("\n".join(L) + "\n")
    (root / "latest.json").write_text(json.dumps(B, indent=1))
    (root / "history.jsonl").open("a").write(json.dumps(B) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], "--force" in sys.argv)
