"""Order-book liquidity history from Binance's free archives (futures/um/daily/bookDepth): cumulative bid and ask depth
within +-0.2%, 1%, 2%, 3%, 4%, 5% of the price, about every 30 seconds. Aggregated to 5-minute rows (last snapshot in
each 5 minutes) and stored at $OMEGA_DATA/depth/<SYMBOL>_5m.parquet with columns b0.2..b5 (bid notional, USD) and
a0.2..a5 (ask notional). Resumable: days already stored are skipped.
Usage: python -m edges.data.fetch_depth BTCUSDT 2023-01-01 2026-11-14 [--workers 12]"""
import concurrent.futures as cf
import datetime as dt
import io
import os
import sys
import zipfile

import httpx
import pandas as pd

ROOT = os.environ.get("OMEGA_DATA", "/home/user/data")


def day(c, sym, d):
    r = c.get(f"https://data.binance.vision/data/futures/um/daily/bookDepth/{sym}/{sym}-bookDepth-{d}.zip")
    if r.status_code != 200:
        return None
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        x = pd.read_csv(z.open(z.namelist()[0]))
    x["t"] = pd.to_datetime(x.timestamp, utc=True).dt.floor("5min")
    x["k"] = x.percentage.map(lambda p: ("b" if p < 0 else "a") + f"{abs(p):g}")
    w = x.pivot_table(index="t", columns="k", values="notional", aggfunc="last")
    return w


def main(sym, a, b, workers=12):
    out = f"{ROOT}/depth/{sym}_5m.parquet"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    have = pd.read_parquet(out) if os.path.exists(out) else None
    done = set(have.index.normalize().strftime("%Y-%m-%d")) if have is not None else set()
    days = [d.strftime("%Y-%m-%d") for d in pd.date_range(a, b) if d.strftime("%Y-%m-%d") not in done]
    c = httpx.Client(timeout=60)
    parts = []
    with cf.ThreadPoolExecutor(workers) as ex:
        for i, w in enumerate(ex.map(lambda d: day(c, sym, d), days)):
            if w is not None:
                parts.append(w)
            if i % 100 == 0:
                print(sym, i, "/", len(days), flush=True)
    if parts:
        new = pd.concat(parts)
        allx = pd.concat([have, new]) if have is not None else new
        allx = allx[~allx.index.duplicated(keep="last")].sort_index()
        allx.to_parquet(out)
        print("saved", out, len(allx), allx.index[0], allx.index[-1])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
