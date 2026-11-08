"""Live UpScout / DownScout: predict every hour, score every prediction 24 h later, publish SCOUTS.md.

State dir (default $OMEGA_BOTS_HOME/../scouts or ./scouts_state):
  predictions.csv  one row per coin per hour: probabilities, flags, and (after 24 h) the outcome
  SCOUTS.md        the public scoreboard: forward AUC, hit rates of flagged calls vs base rate, paper P&L of flags
Candles come from the same providers as the Live API (Binance futures -> OKX -> Gate), closed bars only.
Usage: python -m edges.scouts.live [state_dir]
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "omega", "live_api"))
from omega_live.providers import Crypto, Http, ProviderError  # noqa: E402

from edges.scouts.model import features, H  # noqa: E402

MODELS = os.environ.get("SCOUT_MODELS") if os.path.exists(os.path.join(os.environ.get("SCOUT_MODELS", "/nonexistent"), "meta.json")) \
    else os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
TARGETS = ("up_move", "down_move", "turn_up", "turn_down")
COST = 0.0014  # round trip for liquid coins (2 x (0.05% taker + 0.02% slippage))


def candles(cx, sym, n=500):
    k = cx.klines(sym, "1h", n)
    df = pd.DataFrame([c for c in k["candles"] if c["closed"]])
    df.index = pd.to_datetime(df.pop("t"), unit="ms", utc=True)
    return df[["o", "h", "l", "c", "v", "qv"]], k["source"]


def predict(state):
    import lightgbm as lgb
    meta = json.load(open(os.path.join(MODELS, "meta.json")))
    boosters = {t: lgb.Booster(model_file=os.path.join(MODELS, f"{t}.txt")) for t in TARGETS}
    cx = Crypto(Http())
    btc, src = candles(cx, "BTCUSDT")
    rows, bars = [], {"BTCUSDT": btc}
    for s in meta["coins"]:
        try:
            d = btc if s == "BTCUSDT" else candles(cx, s)[0]
        except (ProviderError, ValueError, KeyError):
            continue
        bars[s] = d
        if len(d) < 400:
            continue
        F = features(d, btc)
        x = F.iloc[[-1]][meta["features"]]
        lr = np.log(d.c).diff()
        sig24 = float(lr.rolling(168, min_periods=100).std().iloc[-1] * np.sqrt(H))
        r = dict(time=F.index[-1].isoformat(), sym=s, close=float(d.c.iloc[-1]), sig24=sig24, source=src)
        for t in TARGETS:
            p = float(boosters[t].predict(x)[0])
            r[f"p_{t}"] = round(p, 4)
            r[f"flag_{t}"] = int(p >= meta["thresholds"][t])
        rows.append(r)
    new = pd.DataFrame(rows)
    f = os.path.join(state, "predictions.csv")
    old = pd.read_csv(f) if os.path.exists(f) else pd.DataFrame()
    allp = pd.concat([old, new], ignore_index=True).drop_duplicates(["time", "sym"], keep="first")
    return allp, bars, meta


def score(allp, bars):
    """Fill outcomes for predictions whose 24 h window has closed (using the fetched candles)."""
    for col in ("fwd", "y_up_move", "y_down_move"):
        if col not in allp:
            allp[col] = np.nan
    now = max(d.index[-1] for d in bars.values())
    for i, r in allp[allp.fwd.isna()].iterrows():
        t = pd.Timestamp(r.time)
        t2 = t + pd.Timedelta(hours=H)
        d = bars.get(r.sym)
        if d is None or t2 > now or t2 not in d.index:
            continue
        fwd = float(np.log(d.c.loc[t2] / r.close))
        allp.loc[i, "fwd"] = fwd
        allp.loc[i, "y_up_move"] = float(fwd >= r.sig24)
        allp.loc[i, "y_down_move"] = float(fwd <= -r.sig24)
    return allp


def board(allp, meta, state):
    from sklearn.metrics import roc_auc_score
    s = allp.dropna(subset=["fwd"])
    lines = [f"# UpScout / DownScout — forward record", "",
             f"Updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}. Predictions so far: {len(allp)}; "
             f"scored (24 h passed): {len(s)}. Models trained to {meta['trained_to'][:10]}. "
             "Every prediction is written before its outcome is known. Information only: no bot trades these.", ""]
    if len(s) >= 50:
        lines += ["| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |",
                  "|---|---|---|---|---|---|"]
        for t, y, sgn in (("up_move", "y_up_move", 1), ("down_move", "y_down_move", -1)):
            try:
                auc = roc_auc_score(s[y], s[f"p_{t}"]) if s[y].nunique() > 1 else float("nan")
            except ValueError:
                auc = float("nan")
            fl = s[s[f"flag_{t}"] == 1]
            pnl = (sgn * (np.exp(fl.fwd) - 1) - COST).mean() * 1e4 if len(fl) else float("nan")
            lines.append(f"| {'UpScout' if t == 'up_move' else 'DownScout'} | {auc:.3f} | {len(fl)} | "
                         f"{fl[y].mean():.1%} | {s[y].mean():.1%} | {pnl:+.0f} bp/trade |" if len(fl) else
                         f"| {'UpScout' if t == 'up_move' else 'DownScout'} | {auc:.3f} | 0 | – | {s[y].mean():.1%} | – |")
        lines += ["", "Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate "
                  "over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26)."]
    else:
        lines.append("Not enough scored predictions yet (needs 50+; the first are scored 24 hours after they are made).")
    last = allp[allp.time == allp.time.max()].sort_values("p_up_move", ascending=False)
    lines += ["", f"## Latest call ({allp.time.max()[:16]} UTC)", "",
              "| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |", "|---|---|---|---|---|---|"]
    for _, r in last.iterrows():
        fl = " ".join(n for n, k in (("UP", "flag_up_move"), ("DOWN", "flag_down_move"), ("TURN↑", "flag_turn_up"),
                                     ("TURN↓", "flag_turn_down")) if r[k] == 1)
        lines.append(f"| {r.sym} | {r.p_up_move:.0%} | {r.p_down_move:.0%} | {r.p_turn_up:.0%} | {r.p_turn_down:.0%} | {fl} |")
    open(os.path.join(state, "SCOUTS.md"), "w").write("\n".join(lines) + "\n")


def main():
    state = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "scouts_state")
    os.makedirs(state, exist_ok=True)
    allp, bars, meta = predict(state)
    allp = score(allp, bars)
    allp.to_csv(os.path.join(state, "predictions.csv"), index=False)
    board(allp, meta, state)
    print(open(os.path.join(state, "SCOUTS.md")).read()[:1500])


if __name__ == "__main__":
    main()
