"""The Recorder: every 15 minutes it saves market facts that nobody archives for free, so they can be studied later.
One CSV per UTC day at <state>/recorder/YYYY-MM-DD.csv, one row per market per run:
  perp price (OKX), spot bid/ask and spread for gold/silver (Swissquote), order-book depth within 0.25/0.5/1% (bids and
  asks, USD, OKX 400 levels), open interest (USD), funding rate, account long/short ratio (BTC), taker buy/sell volume
  over the last 5 minutes (BTC), liquidations in the last 15 minutes (count and USD, longs and shorts, OKX);
  NAS100 / US30: futures price and the last 15m bar's volume (Yahoo).
Nothing here trades. Each source failing is recorded as an empty field, never as a made-up value.
Usage: python -m edges.observer.recorder <state_dir>"""
from __future__ import annotations

import csv
import datetime as dt
import sys
import time
from pathlib import Path

import httpx

OKX = "https://www.okx.com/api/v5"
MK = {"XAUUSD": ("XAU-USDT-SWAP", "XAU-USDT", 0.001, "XAU/USD"), "XAGUSD": ("XAG-USDT-SWAP", "XAG-USDT", 0.01, "XAG/USD"),
      "BTCUSD": ("BTC-USDT-SWAP", "BTC-USDT", 0.01, None)}
YF = {"NAS100": "NQ=F", "US30": "YM=F"}
COLS = ["utc", "market", "price", "spot_bid", "spot_ask", "spot_spread_bp", "bid_025", "ask_025", "bid_05", "ask_05", "bid_1", "ask_1",
        "imb_05", "oi_usd", "funding", "ls_ratio", "taker_buy", "taker_sell", "liq_long_n", "liq_long_usd", "liq_short_n", "liq_short_usd", "volume_15m"]


def j(c, url, **p):
    try:
        r = c.get(url, params=p or None)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def okx_row(c, sym, now_ms):
    inst, fam, ctv, sq = MK[sym]
    row = dict(market=sym)
    b = j(c, f"{OKX}/market/books", instId=inst, sz="400")
    if b and b.get("data"):
        bk = b["data"][0]
        bids = [(float(p), float(q) * ctv) for p, q, *_ in bk["bids"]]
        asks = [(float(p), float(q) * ctv) for p, q, *_ in bk["asks"]]
        if bids and asks:
            mid = (bids[0][0] + asks[0][0]) / 2
            row["price"] = round(mid, 4)
            for pct, k in ((0.0025, "025"), (0.005, "05"), (0.01, "1")):
                row[f"bid_{k}"] = round(sum(p * q for p, q in bids if p >= mid * (1 - pct)))
                row[f"ask_{k}"] = round(sum(p * q for p, q in asks if p <= mid * (1 + pct)))
            s = row["bid_05"] + row["ask_05"]
            row["imb_05"] = round((row["bid_05"] - row["ask_05"]) / s, 4) if s else ""
    o = j(c, f"{OKX}/public/open-interest", instType="SWAP", instId=inst)
    if o and o.get("data"):
        row["oi_usd"] = round(float(o["data"][0].get("oiUsd") or 0))
    f = j(c, f"{OKX}/public/funding-rate", instId=inst)
    if f and f.get("data"):
        row["funding"] = f["data"][0].get("fundingRate")
    lq = j(c, f"{OKX}/public/liquidation-orders", instType="SWAP", uly=fam, state="filled", limit="100")
    if lq and lq.get("data"):
        ln = ls = sn = ss = 0
        for d in lq["data"][0].get("details", []):
            if int(d["ts"]) < now_ms - 900_000:
                continue
            usd = float(d["sz"]) * ctv * float(d["bkPx"])
            if d.get("posSide") == "long":
                ln += 1; ls += usd
            else:
                sn += 1; ss += usd
        row.update(liq_long_n=ln, liq_long_usd=round(ls), liq_short_n=sn, liq_short_usd=round(ss))
    if sym == "BTCUSD":
        r = j(c, f"{OKX}/rubik/stat/contracts/long-short-account-ratio-contract", instId=inst, period="5m", limit="1")
        if r and r.get("data"):
            row["ls_ratio"] = r["data"][0][1]
        t = j(c, f"{OKX}/rubik/stat/taker-volume-contract", instId=inst, period="5m", limit="1")
        if t and t.get("data"):
            row["taker_sell"], row["taker_buy"] = t["data"][0][1], t["data"][0][2]
        tk = j(c, f"{OKX}/market/ticker", instId="BTC-USDT")
        if tk and tk.get("data"):
            bid, ask = float(tk["data"][0]["bidPx"]), float(tk["data"][0]["askPx"])
            row.update(spot_bid=bid, spot_ask=ask, spot_spread_bp=round((ask - bid) / ((ask + bid) / 2) * 1e4, 2))
    if sq:
        a, b2 = sq.split("/")
        q = j(c, f"https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/{a}/{b2}")
        if q:
            pr = (q[0].get("spreadProfilePrices") or [{}])[0]
            if pr.get("bid") and pr.get("ask"):
                row.update(spot_bid=pr["bid"], spot_ask=pr["ask"], spot_spread_bp=round((pr["ask"] - pr["bid"]) / ((pr["ask"] + pr["bid"]) / 2) * 1e4, 2))
    return row


def yahoo_row(c, sym):
    row = dict(market=sym)
    try:
        r = c.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{YF[sym]}", params=dict(range="1d", interval="15m"), headers={"User-Agent": "Mozilla/5.0"})
        res = r.json()["chart"]["result"][0]; q = res["indicators"]["quote"][0]
        idx = [i for i, v in enumerate(q["close"]) if v is not None]
        if len(idx) >= 2:
            i = idx[-2]          # last CLOSED bar
            row.update(price=q["close"][i], volume_15m=q["volume"][i])
    except Exception:
        pass
    return row


def main(state_dir):
    now = dt.datetime.now(dt.timezone.utc)
    now_ms = int(now.timestamp() * 1000)
    c = httpx.Client(timeout=15, headers={"User-Agent": "omega-recorder/1.0"})
    rows = []
    for sym in MK:
        rows.append(okx_row(c, sym, now_ms)); time.sleep(0.3)
    for sym in YF:
        rows.append(yahoo_row(c, sym))
    d = Path(state_dir) / "recorder"; d.mkdir(parents=True, exist_ok=True)
    f = d / f"{now:%Y-%m-%d}.csv"
    new = not f.exists()
    with f.open("a", newline="") as h:
        w = csv.DictWriter(h, fieldnames=COLS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLS} | {"utc": now.strftime("%Y-%m-%d %H:%M")})
    print("recorder:", [(r["market"], r.get("price"), r.get("imb_05"), r.get("liq_long_usd"), r.get("liq_short_usd")) for r in rows])


if __name__ == "__main__":
    main(sys.argv[1])
