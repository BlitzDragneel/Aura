"""Forward paper log of the grade-C watch-list rule "OI-confirmed move" on the gold and silver perps (E143/E144).

Rule (fixed, as tested): on a closed 15-minute bar, if the 4-hour change of open interest has z >= 2 against the last
7 days AND price moved >= 2 ATR14 over those 4 hours, follow the move. Paper trade: entry at the next bar's open,
stop 1.5 ATR, target 3 ATR, closed after 4 hours. NOT a passed rule; E145 failed to replicate it on nine other markets, so treat it as unproven. Logged to see whether it holds up.
Open interest: Binance (as tested) when reachable, else OKX's own XAU/XAG swap (a different venue: labelled).

Usage: python -m edges.watch.oi_move <state_dir>
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

from edges.alerts.notify import send

ASSETS = {"XAU": ("Gold", "XAUUSDT", "XAU-USDT-SWAP", 0.0002), "XAG": ("Silver", "XAGUSDT", "XAG-USDT-SWAP", 0.0004)}
M15 = 900_000


def oi_history(c, sym, okx, have: pd.Series) -> tuple[pd.Series, str]:
    start = int(have.index[-1]) + 1 if len(have) else int(time.time() * 1000) - 8 * 86_400_000
    try:
        rows, t = [], start
        while t < time.time() * 1000 - 300_000 and len(rows) < 3000:
            r = c.get("https://fapi.binance.com/futures/data/openInterestHist", params=dict(symbol=sym, period="5m", limit=500, startTime=t))
            r.raise_for_status()
            d = r.json()
            if not d:
                break
            rows += [(int(x["timestamp"]), float(x["sumOpenInterest"])) for x in d]
            t = rows[-1][0] + 1
        src = "binance"
    except (httpx.HTTPError, KeyError, ValueError):
        rows, end, src = [], None, "okx"
        for _ in range(30):
            p = dict(instId=okx, period="5m", limit="100")
            if end:
                p["end"] = str(end)
            d = c.get("https://www.okx.com/api/v5/rubik/stat/contracts/open-interest-history", params=p).json().get("data") or []
            if not d:
                break
            rows += [(int(x[0]), float(x[2])) for x in d]
            end = int(d[-1][0]) - 1
            if end < start:
                break
            time.sleep(0.25)
    new = pd.Series(dict(rows), dtype=float)
    s = pd.concat([have, new[new.index >= start]]) if len(have) else new
    s = s[~s.index.duplicated()].sort_index()
    return s[s.index >= time.time() * 1000 - 9 * 86_400_000], src


def candles(c, okx):
    d = c.get("https://www.okx.com/api/v5/market/candles", params=dict(instId=okx, bar="15m", limit="300")).json()["data"]
    k = pd.DataFrame([[int(x[0])] + [float(v) for v in x[1:5]] + [x[8]] for x in d], columns=["t", "o", "h", "l", "c", "done"]).sort_values("t")
    return k[k.done == "1"].set_index("t")


def signal(oi: pd.Series, k: pd.DataFrame):
    """Returns dict for the last closed bar, or None when history is too short."""
    g = oi.copy()
    g.index = (g.index + 300_000) // M15 * M15            # known 5 min after its stamp; bar that contains that moment
    g = np.log(g.groupby(level=0).last())
    grid = pd.RangeIndex(int(g.index[0]), int(k.index[-1]) + M15, M15)
    g = g.reindex(grid).ffill()
    doi = g - g.shift(16)
    if doi.notna().sum() < 336:
        return None
    z = (doi - doi.rolling(672, min_periods=336).mean()) / doi.rolling(672, min_periods=336).std()
    tr = pd.concat([k.h - k.l, (k.h - k.c.shift()).abs(), (k.l - k.c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    t = k.index[-1]
    r4, a, zz = k.c.iloc[-1] / k.c.iloc[-17] - 1, atr.iloc[-1], z.get(t, np.nan)
    d = int(np.sign(r4)) if (zz >= 2 and abs(r4) >= 2 * a / k.c.iloc[-1]) else 0
    return dict(bar=int(t), z_oi=round(float(zz), 2) if np.isfinite(zz) else None, r4_pct=round(r4 * 100, 3), atr=float(a), close=float(k.c.iloc[-1]), dir=d)


def step(asset, root: Path, c):
    name, sym, okx, cost = ASSETS[asset]
    w = root / "watch"
    w.mkdir(parents=True, exist_ok=True)
    hf, sf = w / f"oi_{asset}.csv", w / f"oi_move_{asset}.json"
    have = pd.read_csv(hf, index_col=0).oi if hf.exists() else pd.Series(dtype=float)
    oi, src = oi_history(c, sym, okx, have)
    oi.rename("oi").to_csv(hf)
    k = candles(c, okx)
    st = json.loads(sf.read_text()) if sf.exists() else dict(asset=asset, open=None, closed=[], last_bar=0)
    msgs = []
    o = st.get("open")
    if o:  # manage the paper trade on closed bars after its entry
        if o.get("entry") is None:
            nb = k[k.index > o["bar"]]
            if len(nb):
                o["entry"], o["entry_t"] = float(nb.o.iloc[0]), int(nb.index[0])
                o["stop"], o["target"] = o["entry"] - o["dir"] * 1.5 * o["atr"], o["entry"] + o["dir"] * 3 * o["atr"]
        if o.get("entry") is not None:
            for t, b in k[k.index >= o["entry_t"]].iterrows():
                ex = None
                if (o["dir"] == 1 and b.l <= o["stop"]) or (o["dir"] == -1 and b.h >= o["stop"]):
                    ex, why = o["stop"], "stop"
                elif t > o["entry_t"] and ((o["dir"] == 1 and b.h >= o["target"]) or (o["dir"] == -1 and b.l <= o["target"])):
                    ex, why = o["target"], "target"
                elif t >= o["entry_t"] + 16 * M15:
                    ex, why = b.o, "time"
                if ex is not None:
                    o.update(exit=float(ex), exit_t=int(t), why=why, net_pct=round((o["dir"] * (ex - o["entry"]) / o["entry"] - 2 * cost) * 100, 3))
                    st["closed"].append(o)
                    msgs.append(f"🧪 {name} watch-list paper trade closed ({why}): {o['net_pct']:+.2f}% after costs")
                    st["open"] = None
                    break
    sg = signal(oi, k)
    st["last"] = dict(sg or {}, oi_source=src, checked=int(time.time() * 1000))
    if sg and sg["dir"] and st.get("open") is None and sg["bar"] > st.get("last_bar", 0):
        st["open"] = dict(bar=sg["bar"], dir=sg["dir"], atr=sg["atr"], z_oi=sg["z_oi"], r4_pct=sg["r4_pct"], oi_source=src, entry=None)
        side = "BUY" if sg["dir"] == 1 else "SELL"
        msgs.append(f"🧪 {name} WATCH-LIST signal (grade C, paper only, NOT a passed rule; failed on other markets): open interest jumped (z {sg['z_oi']}) while price moved "
                    f"{sg['r4_pct']:+.2f}% in 4h → {side} near {sg['close']:,.2f}, stop {sg['close'] - sg['dir'] * 1.5 * sg['atr']:,.2f}, "
                    f"target {sg['close'] + sg['dir'] * 3 * sg['atr']:,.2f}, 4h max.")
    if sg:
        st["last_bar"] = sg["bar"]
    cl = st["closed"]
    st["record"] = dict(n=len(cl), mean_pct=round(float(np.mean([x["net_pct"] for x in cl])), 3) if cl else None,
                        wins=sum(x["net_pct"] > 0 for x in cl), note="grade C watch list (E143/E144); ~50 closed trades needed for a verdict")
    sf.write_text(json.dumps(st, indent=1))
    return msgs, st


def main(state_dir):
    c = httpx.Client(timeout=20, headers={"User-Agent": "omega-watch/1.0"})
    allm = []
    for a in ASSETS:
        try:
            m, st = step(a, Path(state_dir), c)
            allm += m
            print(a, st["last"], st["record"])
        except Exception as e:  # one asset failing must not stop the other
            print(a, "error", type(e).__name__, str(e)[:200])
    if allm:
        print(send("\n\n".join(allm), c), allm)


if __name__ == "__main__":
    main(sys.argv[1])
