"""Candle memory, live: for each of the owner's five markets, every 15 minutes it describes the last closed candle,
finds the 200 most similar candles in its memory and reports what followed them (P(next candle up), P(next hour up),
P(next 4 hours up), P(big move in 4h), median next-hour move). Every prediction is logged before the outcome and scored
when it is known; every candle whose outcome is known is added to the memory (it learns as it goes).
Backtest (E162): next-hour direction AUC 0.53 BTC / 0.55 gold (PAXG) / 0.52 silver on data it never saw, big-move AUC
0.70-0.75; trading its calls lost after costs. So this is information, not trade signals, until its forward record says
otherwise. Files in <state>/memory/: <SYM>_learned.csv (candles learned live; the seed is edges/memory/seed), predictions.csv, RECORD.json.
Usage: python -m edges.memory.live <state_dir>"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from edges.memory.features import FEATS, describe, outcomes

OKX = {"XAUUSD": "XAU-USDT-SWAP", "XAGUSD": "XAG-USDT-SWAP", "BTCUSD": "BTC-USDT-SWAP"}
YF = {"NAS100": "NQ=F", "US30": "YM=F"}
SEED = Path(__file__).parent / "seed"
K = 200
OUTC = ["up1", "up1h", "up4h", "big4h", "ret1h"]


def bars(c, sym):
    if sym in OKX:
        rows, after = [], None
        for _ in range(10):                      # 1000 candles = ~10 days (volatility rank needs ~3 days of warm-up)
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
        r = c.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{YF[sym]}", params=dict(range="60d", interval="15m"), headers={"User-Agent": "Mozilla/5.0"})
        j = r.json()["chart"]["result"][0]; q = j["indicators"]["quote"][0]
        f = pd.DataFrame(dict(t=np.array(j["timestamp"]) * 1000, o=q["open"], h=q["high"], l=q["low"], c=q["close"])).dropna()
        f = f.iloc[:-1]                          # drop the bar still forming
    f.index = pd.to_datetime(f.t, unit="ms", utc=True)
    return f[["o", "h", "l", "c"]]


def main(state_dir):
    root = Path(state_dir) / "memory"; root.mkdir(parents=True, exist_ok=True)
    c = httpx.Client(timeout=20, headers={"User-Agent": "omega-memory/1.0"})
    pf = root / "predictions.csv"
    P = pd.read_csv(pf, parse_dates=["bar"]) if pf.exists() else pd.DataFrame()
    new_preds, record = [], {}
    for sym in list(OKX) + list(YF):
        try:
            f = bars(c, sym)
        except Exception as e:
            print(sym, "data error", type(e).__name__); continue
        if len(f) < 120:
            continue
        X, Y = describe(f), outcomes(f)
        # memory = fixed seed in the repo + candles learned live (small CSV in state, appended as outcomes become known)
        lf = root / f"{sym}_learned.csv"
        L = pd.read_csv(lf, index_col=0, parse_dates=True) if lf.exists() else pd.DataFrame(columns=FEATS + OUTC)
        S = pd.read_parquet(SEED / f"{sym}.parquet") if (SEED / f"{sym}.parquet").exists() else pd.DataFrame(columns=FEATS + OUTC)
        done = X.join(Y[OUTC]).dropna()
        known = S.index.union(L.index) if len(L) else S.index
        add = done[~done.index.isin(known)].round(5)
        if len(add):
            add.to_csv(lf, mode="a", header=not lf.exists())
            L = pd.concat([L, add])
        M = pd.concat([S, L.astype("float32")]) if len(L) else S
        M = M[M.index >= M.index.max() - pd.Timedelta(days=900)]
        # score older predictions of this market
        if len(P):
            Pm = P[(P.market == sym) & P.actual_up1h.isna()] if "actual_up1h" in P else P[P.market == sym]
            for i, row in Pm.iterrows():
                t = pd.Timestamp(row.bar)
                if t.tzinfo is None:
                    t = t.tz_localize("UTC")
                if t in Y.index and np.isfinite(Y.at[t, "up1h"]):
                    for k in ("up1", "up1h", "up4h", "big4h"):
                        P.at[i, "actual_" + k] = Y.at[t, k]
        # predict the last closed candle
        x = X.dropna().iloc[-1:]
        if len(M) < 2000 or not len(x):
            continue
        mu, sd = M[FEATS].mean(), M[FEATS].std() + 1e-9
        nn = NearestNeighbors(n_neighbors=K).fit(((M[FEATS] - mu) / sd).values)
        _, idx = nn.kneighbors(((x[FEATS] - mu) / sd).values)
        nb = M.iloc[idx[0]]
        bar = x.index[0]
        if len(P) and ((P.market == sym) & (pd.to_datetime(P.bar, utc=True) == bar)).any():
            continue
        new_preds.append(dict(utc=pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M"), market=sym, bar=bar, price=float(f.c.iloc[-1]),
                              p_up1=round(float(nb.up1.mean()), 3), p_up1h=round(float(nb.up1h.mean()), 3), p_up4h=round(float(nb.up4h.mean()), 3),
                              p_big4h=round(float(nb.big4h.mean()), 3), med1h_pct=round(float(nb.ret1h.median() * 100), 3), memory=len(M)))
        time.sleep(0.2)
    if new_preds:
        P = pd.concat([P, pd.DataFrame(new_preds)], ignore_index=True)
    if len(P):
        P.to_csv(pf, index=False)
        for sym, g in P.groupby("market"):
            s = g.dropna(subset=["actual_up1h"]) if "actual_up1h" in g else g.iloc[:0]
            r = dict(predictions=int(len(g)), scored=int(len(s)))
            if len(s) >= 20:
                call = s.p_up1h > 0.5
                r["next_hour_right"] = round(float((call == (s.actual_up1h > 0.5)).mean()), 3)
                conf = s[(s.p_up1h - 0.5).abs() >= 0.08]
                r["confident_calls"] = int(len(conf))
                if len(conf):
                    r["confident_right"] = round(float(((conf.p_up1h > 0.5) == (conf.actual_up1h > 0.5)).mean()), 3)
                big = s[s.p_big4h >= 0.5]
                r["big_move_calls"], r["big_move_came"] = int(len(big)), (round(float(big.actual_big4h.mean()), 3) if len(big) else None)
                r["big_move_base"] = round(float(s.actual_big4h.mean()), 3)
            last = g.iloc[-1]
            r["latest"] = dict(bar=str(last.bar), p_up1=last.p_up1, p_up1h=last.p_up1h, p_up4h=last.p_up4h, p_big4h=last.p_big4h, med1h_pct=last.med1h_pct)
            record[sym] = r
        (root / "RECORD.json").write_text(json.dumps(record, indent=1, default=str))
    print("memory:", {k: (v.get("latest", {}).get("p_up1h"), v.get("scored")) for k, v in record.items()})


if __name__ == "__main__":
    main(sys.argv[1])
