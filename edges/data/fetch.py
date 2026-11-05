"""Shared market-data fetcher for the edge research (Binance USDT-M perpetuals, data.binance.vision).

Writes one parquet per symbol and timeframe to $OMEGA_DATA (default /home/user/data):
  {DATA}/1h/SYM.parquet      all USDT perps incl. delisted, 2020-01 -> latest
  {DATA}/5m/SYM.parquet      the TOP list below, 2022-01 -> latest
  {DATA}/funding/SYM.parquet funding rate history, all USDT perps
Columns (klines): ts (UTC open, ms), o h l c v qv n tbv tbqv.  Volume-0 candles are kept but flagged later by users.
Usage: python3 fetch.py 1h | 5m | funding | all
"""
import concurrent.futures as cf, io, json, os, re, sys, time, zipfile
import xml.etree.ElementTree as ET
import httpx
import pandas as pd

DATA = os.environ.get("OMEGA_DATA", "/home/user/data")
L = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
A = "https://data.binance.vision/"
NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
TOP = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT",
       "DOTUSDT", "TRXUSDT", "BCHUSDT", "NEARUSDT", "ATOMUSDT", "ETCUSDT", "FILUSDT", "APTUSDT", "ARBUSDT", "OPUSDT",
       "SUIUSDT", "INJUSDT", "AAVEUSDT", "UNIUSDT", "1000PEPEUSDT", "WIFUSDT", "TIAUSDT", "SEIUSDT", "XLMUSDT", "HBARUSDT"]
c = httpx.Client(timeout=60, limits=httpx.Limits(max_connections=32))


def get(url, **p):
    for a in range(5):
        try:
            r = c.get(url, params=p or None)
            if r.status_code in (200, 404):
                return r
        except httpx.HTTPError:
            pass
        time.sleep(1 + 2 * a)
    return None


def keys(prefix, delimiter=None):
    out, marker = [], None
    while True:
        p = dict(prefix=prefix)
        if delimiter:
            p["delimiter"] = delimiter
        if marker:
            p["marker"] = marker
        r = get(L, **p)
        root = ET.fromstring(r.text)
        if delimiter:
            ks = [e.findtext(f"{NS}Prefix") for e in root.findall(f"{NS}CommonPrefixes")]
        else:
            ks = [e.findtext(f"{NS}Key") for e in root.findall(f"{NS}Contents")]
        out += ks
        if (root.findtext(f"{NS}IsTruncated") or "false") == "true" and ks:
            marker = root.findtext(f"{NS}NextMarker") or ks[-1]
        else:
            return out


def symbols():
    fn = f"{DATA}/symbols.json"
    if os.path.exists(fn):
        return json.load(open(fn))
    ps = keys("data/futures/um/monthly/klines/", "/")
    syms = sorted(p.rstrip("/").split("/")[-1] for p in ps)
    syms = [s for s in syms if s.endswith("USDT")]
    os.makedirs(DATA, exist_ok=True)
    json.dump(syms, open(fn, "w"))
    return syms


KCOLS = ["ts", "o", "h", "l", "c", "v", "close_ts", "qv", "n", "tbv", "tbqv", "ignore"]


def read_zip(content, cols):
    z = zipfile.ZipFile(io.BytesIO(content))
    raw = z.read(z.namelist()[0])
    first = raw[:200].decode(errors="ignore")
    header = 0 if re.match(r"^[a-zA-Z_]", first) else None
    df = pd.read_csv(io.BytesIO(raw), header=header)
    df = df.iloc[:, : len(cols)]
    df.columns = cols[: df.shape[1]]
    return df


def klines(sym, tf, start="2020-01"):
    out = f"{DATA}/{tf}/{sym}.parquet"
    if os.path.exists(out):
        return sym, "skip"
    os.makedirs(f"{DATA}/{tf}", exist_ok=True)
    ks = [k for k in keys(f"data/futures/um/monthly/klines/{sym}/{tf}/") if k.endswith(".zip")]
    months = {re.search(r"(\d{4}-\d{2})\.zip$", k).group(1): k for k in ks}
    want = [months[m] for m in sorted(months) if m >= start]
    last = max(months) if months else "0000-00"
    # current month (not yet in monthly files): daily files
    if last >= "2026-09":
        dks = [k for k in keys(f"data/futures/um/daily/klines/{sym}/{tf}/{sym}-{tf}-2026-1") if k.endswith(".zip")]
        want += [k for k in dks if re.search(r"(\d{4}-\d{2})-\d{2}\.zip$", k).group(1) > last]
    parts = []
    for k in want:
        r = get(A + k)
        if r is None or r.status_code != 200:
            continue
        try:
            parts.append(read_zip(r.content, KCOLS))
        except Exception:
            continue
    if not parts:
        open(out + ".empty", "w").write("no data")
        return sym, 0
    df = pd.concat(parts, ignore_index=True).drop(columns=["close_ts", "ignore"], errors="ignore")
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["ts"]).astype({"ts": "int64"})
    # some files use microseconds (2025+ spot); futures are ms but normalise anyway
    df.loc[df.ts > 10**14, "ts"] //= 1000
    df = df.drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    df.to_parquet(out, index=False)
    return sym, len(df)


def funding(sym):
    out = f"{DATA}/funding/{sym}.parquet"
    if os.path.exists(out):
        return sym, "skip"
    os.makedirs(f"{DATA}/funding", exist_ok=True)
    ks = [k for k in keys(f"data/futures/um/monthly/fundingRate/{sym}/") if k.endswith(".zip")]
    parts = []
    for k in ks:
        r = get(A + k)
        if r is None or r.status_code != 200:
            continue
        try:
            parts.append(read_zip(r.content, ["ts", "interval_h", "rate"]))
        except Exception:
            continue
    if not parts:
        open(out + ".empty", "w").write("no data")
        return sym, 0
    df = pd.concat(parts, ignore_index=True)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna().astype({"ts": "int64"}).drop_duplicates("ts").sort_values("ts")
    df.to_parquet(out, index=False)
    return sym, len(df)


def run(fn, syms, workers):
    with cf.ThreadPoolExecutor(workers) as ex:
        for i, (s, n) in enumerate(ex.map(fn, syms)):
            if i % 25 == 0:
                print(time.strftime("%H:%M:%S"), fn.__name__ if hasattr(fn, "__name__") else "", i, len(syms), s, n,
                      flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    syms = symbols()
    print("symbols", len(syms), flush=True)
    if what in ("5m", "all"):
        run(lambda s: klines(s, "5m", "2022-01"), [s for s in TOP if s in syms], 8)
        print("5m DONE", flush=True)
    if what in ("1h", "all"):
        run(lambda s: klines(s, "1h", "2020-01"), syms, 16)
        print("1h DONE", flush=True)
    if what in ("funding", "all"):
        run(funding, syms, 16)
        print("funding DONE", flush=True)
    print("ALL DONE", flush=True)
