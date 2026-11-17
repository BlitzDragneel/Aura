"""Candle memory, live (E162 -> E163). Every 15 minutes, for the owner's five markets:
1. adds the newly closed 15m candles to its memory (it never forgets a candle);
2. scores its earlier predictions; for every WRONG one it writes down why (close vote, unfamiliar situation, shock move,
   called against the 24h move, high volatility, news, session) in mistakes.csv;
3. retrains itself on all the memory (look-alike candles + gradient boosting) and predicts the candle that just closed:
   P(next candle up), P(next hour up), P(next 4h up), P(big move in 4h), median next-hour move;
4. asks its MISTAKE MODEL - trained on its own past rights and wrongs (a walk-forward replay, then every live result) -
   how likely this call is to be right, and makes a CALL only when that is >= the threshold its weekly self-review set
   and the situation is not one the review blocked; otherwise "no call".
Information only (not trade signals) until the forward record passes the registered test.
Files in <state>/memory/: <SYM>_bars.csv (candles after the seed), <SYM>_calls.csv (every prediction with the numbers
the mistake model learns from), predictions.csv (readable log), mistakes.csv (why each wrong call was wrong),
RECORD.json, config.json (set by the self-review), UPGRADES.md (what the self-review changed and why).
Usage: python -m edges.memory.live <state_dir>"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

from edges.memory.features import RICH, describe_rich, outcomes
from edges.memory.model import META, mistake_model, p_right, predict, why_wrong

OKX = {"XAUUSD": "XAU-USDT-SWAP", "XAGUSD": "XAG-USDT-SWAP", "BTCUSD": "BTC-USDT-SWAP"}
YF = {"NAS100": "NQ=F", "US30": "YM=F"}
SEED = Path(__file__).parent / "seed"
DEFAULT = dict(threshold=0.55, blocked=[])


def fetch(c, sym):
    if sym in OKX:
        rows, after = [], None
        for _ in range(10):                      # ~1000 candles
            p = dict(instId=OKX[sym], bar="15m", limit="100")
            if after:
                p["after"] = after
            d = c.get("https://www.okx.com/api/v5/market/history-candles", params=p).json().get("data") or []
            if not d:
                break
            rows += [(int(k[0]), *map(float, k[1:5])) for k in d if k[8] == "1"]
            after = d[-1][0]; time.sleep(0.15)
        f = pd.DataFrame(rows, columns=["t", "o", "h", "l", "c"]).drop_duplicates("t").sort_values("t")
    else:
        r = c.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{YF[sym]}", params=dict(range="60d", interval="15m"),
                  headers={"User-Agent": "Mozilla/5.0"})
        j = r.json()["chart"]["result"][0]; q = j["indicators"]["quote"][0]
        f = pd.DataFrame(dict(t=np.array(j["timestamp"]) * 1000, o=q["open"], h=q["high"], l=q["low"], c=q["close"])).dropna()
        f = f[f.t % 900_000 == 0].iloc[:-1]      # whole 15m candles, drop the one still forming
    f.index = pd.to_datetime(f.t, unit="ms", utc=True)
    return f[["o", "h", "l", "c"]].astype(float)


def news_now(state):
    """High-impact USD events from the alerts calendar cache: {hour-floor timestamp: title}."""
    try:
        cal = json.loads((state / "alerts" / "calendar.json").read_text())
        ev = cal.get("events", cal) if isinstance(cal, dict) else cal
        out = {}
        for e in ev:
            if str(e.get("impact", "")).lower().startswith("high") and e.get("country") == "USD":
                out[pd.Timestamp(e["date"]).tz_convert("UTC")] = e.get("title", "event")
        return out
    except Exception:
        return {}


def main(state_dir):
    state = Path(state_dir); root = state / "memory"; root.mkdir(parents=True, exist_ok=True)
    cfg_f = root / "config.json"
    CFG = json.loads(cfg_f.read_text()) if cfg_f.exists() else {}
    c = httpx.Client(timeout=20, headers={"User-Agent": "omega-memory/2.0"})
    news = news_now(state)
    pf, mf = root / "predictions.csv", root / "mistakes.csv"
    if pf.exists() and ",call," not in pf.open().readline():
        pf.rename(root / "predictions_v1.csv")          # the first version's log (different columns) is kept aside
    for old in root.glob("*_learned.csv"):              # v1 memory files; v2 keeps raw candles in <SYM>_bars.csv
        old.unlink()
    record = {}
    for sym in list(OKX) + list(YF):
        try:
            fresh = fetch(c, sym)
        except Exception as e:
            print(sym, "data error", type(e).__name__); continue
        cfg = {**DEFAULT, **CFG.get(sym, {})}
        # 1. memory of candles: seed + every candle seen since
        seed = pd.read_parquet(SEED / f"{sym}_15m.parquet").astype(float) if (SEED / f"{sym}_15m.parquet").exists() else fresh.iloc[:0]
        bf = root / f"{sym}_bars.csv"
        B = pd.read_csv(bf, index_col=0, parse_dates=True) if bf.exists() else fresh.iloc[:0]
        if len(B) and B.index.tz is None:
            B.index = B.index.tz_localize("UTC")
        new = fresh[(fresh.index > max(seed.index.max() if len(seed) else fresh.index[0] - pd.Timedelta("1D"),
                                       B.index.max() if len(B) else pd.Timestamp(0, tz="UTC")))]
        if len(new):
            new.round(6).to_csv(bf, mode="a", header=not bf.exists()); B = pd.concat([B, new])
        f = pd.concat([seed, B])
        f = f[~f.index.duplicated(keep="last")].sort_index()
        f = f[f.index >= f.index.max() - pd.Timedelta(days=1100)]
        if len(f) < 3000:
            print(sym, "memory too small", len(f)); continue
        X, Y = describe_rich(f), outcomes(f)
        okX = X[RICH].notna().all(axis=1)
        # 2. score earlier predictions, explain the wrong ones
        cf = root / f"{sym}_calls.csv"
        C = pd.read_csv(cf, index_col=0, parse_dates=True) if cf.exists() else pd.DataFrame()
        if len(C):
            if C.index.tz is None:
                C.index = C.index.tz_localize("UTC")
            todo = C.index[C["right"].isna() & C.index.isin(Y.index[Y.up1h.notna()])] if "right" in C else []
            typical = float(Y.ret1h.abs().median())
            expl = []
            for t in todo:
                C.at[t, "right"] = float((C.at[t, "p_up1h"] > 0.5) == (Y.at[t, "up1h"] > 0.5))
                C.at[t, "actual_ret1h"] = Y.at[t, "ret1h"]
                for k in ("up1", "up4h", "big4h"):
                    C.at[t, "actual_" + k] = Y.at[t, k]
                if C.at[t, "right"] == 0:
                    row = C.loc[t].copy(); row["bar"] = t
                    expl.append(dict(market=sym, bar=t, call=C.at[t, "call"], p_up1h=round(C.at[t, "p_up1h"], 3),
                                     p_right=round(float(C.at[t, "p_right"]), 3), move_pct=round(Y.at[t, "ret1h"] * 100, 3), why=why_wrong(row, typical)))
            if expl:
                pd.DataFrame(expl).to_csv(mf, mode="a", header=not mf.exists(), index=False)
        # 3. retrain on all memory, predict the last closed candle
        last = X.index[okX][-1]
        if len(C) and last in C.index:
            record[sym] = summary(C); continue
        mem = okX & Y.up1h.notna() & (X.index < last - pd.Timedelta("5h"))
        P = predict(X[mem], Y[mem], X.loc[[last]])
        # 4. mistake model: its own past rights and wrongs (replay + live)
        # (the indices have no long replay yet: until they have 3000 scored of their own they borrow the record of
        # gold, silver and Bitcoin - the numbers are in ATR units so they carry across markets)
        own = SEED / f"{sym}_history.parquet"
        H = [pd.read_parquet(own)] if own.exists() else [pd.read_parquet(x) for x in sorted(SEED.glob("*_history.parquet"))]
        if len(C) and "right" in C:
            H.append(C.dropna(subset=["right"])[RICH + META + ["right"]])
        H = pd.concat(H) if H else pd.DataFrame()
        mm = mistake_model(H) if len(H) else None
        P["unfamiliar"] = float(P.dist.iloc[0] >= cfg.get("dist_p80", H.dist.quantile(0.8) if len(H) else np.inf))
        P["p_right"] = p_right(mm, P)
        pr = P.p_right.iloc[0]; up = P.p_up1h.iloc[0]
        blocked = [b for b in cfg["blocked"] if condition(P.iloc[0], b, news)]
        call = ("UP" if up > 0.5 else "DOWN") if (np.isfinite(pr) and pr >= cfg["threshold"] and not blocked) else "no call"
        P["call"] = call
        P["news"] = news.get(last.floor("h"), "")
        P["price"] = float(f.c.iloc[-1])
        P["right"] = np.nan
        C = pd.concat([C, P[RICH + META + ["p_up1", "p_up1h", "p_up4h", "p_big4h", "med1h_pct", "p_right", "call", "news", "price", "unfamiliar", "right"]]])
        C.to_csv(cf)
        pd.DataFrame([dict(utc=pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M"), market=sym, bar=last, price=P.price.iloc[0],
                           call=call, p_right=round(pr, 3) if np.isfinite(pr) else None, p_up1=round(P.p_up1.iloc[0], 3), p_up1h=round(up, 3),
                           p_up4h=round(P.p_up4h.iloc[0], 3), p_big4h=round(P.p_big4h.iloc[0], 3), med1h_pct=round(P.med1h_pct.iloc[0], 3),
                           blocked="; ".join(blocked), memory=int(mem.sum()))]).to_csv(pf, mode="a", header=not pf.exists(), index=False)
        record[sym] = summary(C)
        print(sym, call, round(up, 3), round(pr, 3) if np.isfinite(pr) else None, flush=True)
    if record:
        old = json.loads((root / "RECORD.json").read_text()) if (root / "RECORD.json").exists() else {}
        old = {k: v for k, v in old.items() if isinstance(v, dict) and "calls" in v}
        (root / "RECORD.json").write_text(json.dumps({**old, **record}, indent=1, default=str))


def condition(row, b, news):
    """Conditions the self-review can block (named the same as in mistakes.csv)."""
    h = pd.Timestamp(row.name).hour
    return {"close vote": row.margin < 0.05, "unfamiliar": row.get("unfamiliar") == 1, "against 24h move": np.sign(row.r96) != np.sign(row.p_up1h - 0.5),
            "high volatility": row.volp >= 2 / 3, "news hour": pd.Timestamp(row.name).floor("h") in news,
            "session Asia": h < 7, "session London": 7 <= h < 13, "session New York": 13 <= h < 20, "session late": h >= 20,
            "weekend": row.wkend > 0}.get(b, False)


def summary(C):
    s = C.dropna(subset=["right"]) if "right" in C else C.iloc[:0]
    calls = s[s.call != "no call"] if len(s) else s
    r = dict(predictions=int(len(C)), scored=int(len(s)), calls=int((C.call != "no call").sum()), calls_scored=int(len(calls)))
    if len(s) >= 20:
        r["all_right"] = round(float(s.right.mean()), 3)
        r["big_move_calls"] = int((s.p_big4h >= 0.5).sum())
        r["big_move_came"] = round(float(s[s.p_big4h >= 0.5].actual_big4h.mean()), 3) if (s.p_big4h >= 0.5).any() else None
        r["big_move_base"] = round(float(s.actual_big4h.mean()), 3)
    if len(calls) >= 10:
        r["calls_right"] = round(float(calls.right.mean()), 3)
    last = C.iloc[-1]
    r["latest"] = dict(bar=str(C.index[-1]), call=last.call, p_right=None if pd.isna(last.p_right) else round(float(last.p_right), 3),
                       p_up1h=round(float(last.p_up1h), 3), p_big4h=round(float(last.p_big4h), 3), med1h_pct=round(float(last.med1h_pct), 3))
    return r


if __name__ == "__main__":
    main(sys.argv[1])
