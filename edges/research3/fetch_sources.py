"""Research bot 3 — fetch keyless public data sources into /home/user/data/<name>/.

Usage: python -m edges.research3.fetch_sources <what>   (what = premium | spot | coinbase | dvol | fng | stable | cm | all)
All endpoints are public and keyless (see edges/research3/SOURCES.md for the reachability survey).
"""
import io, json, os, sys, time, zipfile
from concurrent.futures import ThreadPoolExecutor
import httpx
import numpy as np
import pandas as pd

DATA = os.environ.get("OMEGA_DATA", "/home/user/data")
BV = "https://data.binance.vision/data"
CLIENT = httpx.Client(timeout=60, follow_redirects=True)

PREMIUM_COINS = [s[:-8] for s in sorted(os.listdir(f"{DATA}/5m"))] + [
    "EOSUSDT", "XTZUSDT", "ALGOUSDT", "ZECUSDT", "DASHUSDT", "XMRUSDT", "VETUSDT", "NEOUSDT", "IOTAUSDT", "THETAUSDT",
    "COMPUSDT", "SNXUSDT", "MKRUSDT", "SUSHIUSDT", "YFIUSDT", "CRVUSDT", "KSMUSDT", "EGLDUSDT", "MATICUSDT", "FTMUSDT",
    "SANDUSDT", "MANAUSDT", "AXSUSDT", "CHZUSDT", "ICPUSDT", "GALAUSDT", "RUNEUSDT", "ZILUSDT", "QTUMUSDT", "ONTUSDT"]


def months(start="2020-01", end=None):
    end = end or pd.Timestamp.now("UTC").strftime("%Y-%m")
    return [p.strftime("%Y-%m") for p in pd.period_range(start, end, freq="M")]


def _get(url, tries=4):
    for k in range(tries):
        try:
            r = CLIENT.get(url)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r
        except Exception:
            time.sleep(2 * (k + 1))
    return None


def _read_kline_zip(content):
    z = zipfile.ZipFile(io.BytesIO(content))
    raw = z.read(z.namelist()[0]).decode()
    first = raw.split("\n", 1)[0]
    hdr = 0 if first[:1].isalpha() else None
    df = pd.read_csv(io.StringIO(raw), header=hdr)
    df = df.iloc[:, :11]
    df.columns = ["ts", "o", "h", "l", "c", "v", "ct", "qv", "n", "tbv", "tbqv"]
    df["ts"] = df.ts.astype("int64")
    if df.ts.iloc[0] > 1e14:  # microseconds (spot files from 2025 on)
        df["ts"] //= 1000
    return df[["ts", "o", "h", "l", "c", "v", "qv", "n", "tbv", "tbqv"]]


def _monthly_klines(path_fmt, sym, interval, start, outdir):
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/{sym}.parquet"
    parts = []
    for m in months(start):
        r = _get(f"{BV}/{path_fmt.format(sym=sym, iv=interval)}/{sym}-{interval}-{m}.zip")
        if r is not None:
            parts.append(_read_kline_zip(r.content))
    # current month: daily files
    today = pd.Timestamp.now("UTC").normalize()
    cur = today.replace(day=1)
    if parts:
        last = max(p.ts.max() for p in parts)
        d = pd.Timestamp(last, unit="ms", tz="UTC").normalize() + pd.Timedelta(days=1)
        daily_fmt = path_fmt.replace("monthly", "daily")
        while d < today:
            r = _get(f"{BV}/{daily_fmt.format(sym=sym, iv=interval)}/{sym}-{interval}-{d.strftime('%Y-%m-%d')}.zip")
            if r is not None:
                parts.append(_read_kline_zip(r.content))
            d += pd.Timedelta(days=1)
    if not parts:
        open(out + ".empty", "w").close()
        return sym, 0
    df = pd.concat(parts).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    df.to_parquet(out)
    return sym, len(df)


def fetch_premium():
    f = lambda s: _monthly_klines("futures/um/monthly/premiumIndexKlines/{sym}/{iv}", s, "1h", "2020-01",
                                  f"{DATA}/premium_1h")
    with ThreadPoolExecutor(6) as ex:
        for s, n in ex.map(f, PREMIUM_COINS):
            print("premium", s, n, flush=True)


def fetch_spot():
    f = lambda s: _monthly_klines("spot/monthly/klines/{sym}/{iv}", s, "1h", "2020-01", f"{DATA}/spot_1h")
    with ThreadPoolExecutor(4) as ex:
        for s, n in ex.map(f, ["BTCUSDT", "ETHUSDT", "BTCFDUSD", "ETHFDUSD"]):
            print("spot", s, n, flush=True)


def fetch_coinbase(products=("BTC-USD", "ETH-USD"), start="2020-01-01"):
    """Coinbase Exchange public candles, 1h, 300 per request."""
    os.makedirs(f"{DATA}/coinbase_1h", exist_ok=True)
    for p in products:
        rows = []
        t = pd.Timestamp(start, tz="UTC")
        end = pd.Timestamp.now("UTC").floor("h")
        while t < end:
            t2 = min(t + pd.Timedelta(hours=300), end)
            url = (f"https://api.exchange.coinbase.com/products/{p}/candles?granularity=3600"
                   f"&start={t.strftime('%Y-%m-%dT%H:%M:%SZ')}&end={t2.strftime('%Y-%m-%dT%H:%M:%SZ')}")
            r = _get(url)
            if r is not None:
                rows += r.json()
            t = t2
            time.sleep(0.15)
        df = pd.DataFrame(rows, columns=["time", "l", "h", "o", "c", "v"]).drop_duplicates("time").sort_values("time")
        df["ts"] = df.time.astype("int64") * 1000
        df[["ts", "o", "h", "l", "c", "v"]].reset_index(drop=True).to_parquet(f"{DATA}/coinbase_1h/{p}.parquet")
        print("coinbase", p, len(df), flush=True)


def fetch_dvol(currencies=("BTC", "ETH")):
    """Deribit DVOL (30-day implied vol index), hourly, from 2021-03-24."""
    os.makedirs(f"{DATA}/deribit_dvol", exist_ok=True)
    for c in currencies:
        rows = []
        end = int(pd.Timestamp.now("UTC").timestamp() * 1000)
        start = int(pd.Timestamp("2021-03-01", tz="UTC").timestamp() * 1000)
        while True:
            r = _get(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={c}"
                     f"&start_timestamp={start}&end_timestamp={end}&resolution=3600")
            res = r.json()["result"]
            rows += res["data"]
            if not res.get("continuation") or not res["data"]:
                break
            end = res["continuation"]
            time.sleep(0.1)
        df = pd.DataFrame(rows, columns=["ts", "o", "h", "l", "c"]).drop_duplicates("ts").sort_values("ts")
        df.reset_index(drop=True).to_parquet(f"{DATA}/deribit_dvol/{c}.parquet")
        print("dvol", c, len(df), pd.to_datetime(df.ts.min(), unit="ms"), flush=True)


def fetch_fng():
    os.makedirs(f"{DATA}/fear_greed", exist_ok=True)
    d = _get("https://api.alternative.me/fng/?limit=0&format=json").json()["data"]
    df = pd.DataFrame(d)
    df["ts"] = df.timestamp.astype("int64") * 1000
    df["value"] = df.value.astype(int)
    df[["ts", "value"]].sort_values("ts").reset_index(drop=True).to_parquet(f"{DATA}/fear_greed/fng.parquet")
    print("fng", len(df))


def fetch_stable():
    os.makedirs(f"{DATA}/stablecoins", exist_ok=True)
    d = _get("https://stablecoins.llama.fi/stablecoincharts/all").json()
    df = pd.DataFrame({"ts": [int(x["date"]) * 1000 for x in d],
                       "usd": [x.get("totalCirculatingUSD", {}).get("peggedUSD", np.nan) for x in d]})
    df.to_parquet(f"{DATA}/stablecoins/total.parquet")
    print("stable", len(df))


def fetch_cm(assets=("btc", "eth")):
    os.makedirs(f"{DATA}/coinmetrics", exist_ok=True)
    mets = "FlowInExNtv,FlowOutExNtv,SplyExNtv,AdrActCnt,TxCnt,CapMVRVCur,PriceUSD"
    for a in assets:
        rows, url = [], (f"https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets={a}&metrics={mets}"
                         f"&frequency=1d&start_time=2018-01-01&page_size=10000&paging_from=start")
        while url:
            j = _get(url).json()
            rows += j["data"]
            url = j.get("next_page_url")
        df = pd.DataFrame(rows)
        df = df[[c for c in df.columns if not c.endswith("status") and not c.endswith("status-time")]]
        df["ts"] = pd.to_datetime(df.time).astype("int64") // 10 ** 6
        for c in mets.split(","):
            if c in df:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        df.drop(columns=["time", "asset"]).to_parquet(f"{DATA}/coinmetrics/{a}.parquet")
        print("cm", a, len(df))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    jobs = dict(fng=fetch_fng, stable=fetch_stable, cm=fetch_cm, dvol=fetch_dvol, coinbase=fetch_coinbase,
                spot=fetch_spot, premium=fetch_premium)
    for k, f in jobs.items():
        if what in (k, "all"):
            f()
