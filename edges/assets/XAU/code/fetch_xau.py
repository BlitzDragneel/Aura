"""Fetch for the gold bot (E100+): PAXGUSDT spot 15m (2020->), XAUUSDT USD-M perp 15m/1h + funding (Dec 2025->),
Yahoo daily DX-Y.NYB (US dollar index), ^IRX (13-week T-bill yield), ^TNX. Writes to /home/user/data/metals/."""
import io, zipfile, time, xml.etree.ElementTree as ET, httpx, pandas as pd
D = "/home/user/data/metals"
c = httpx.Client(timeout=60, headers={"User-Agent": "Mozilla/5.0"})
L = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
def keys(prefix):
    out, marker = [], None
    while True:
        p = dict(prefix=prefix); 
        if marker: p["marker"] = marker
        root = ET.fromstring(c.get(L, params=p).text); ks = [e.findtext(f"{NS}Key") for e in root.findall(f"{NS}Contents")]; out += ks
        if (root.findtext(f"{NS}IsTruncated") or "false") == "true" and ks: marker = ks[-1]
        else: return [k for k in out if k.endswith(".zip")]
def grab(ks, cols):
    parts = []
    for k in sorted(ks):
        z = zipfile.ZipFile(io.BytesIO(c.get("https://data.binance.vision/" + k).content))
        df = pd.read_csv(z.open(z.namelist()[0]), header=None)
        if not str(df.iloc[0, 0]).replace(".", "").isdigit(): df = df.iloc[1:]
        df = df.iloc[:, :len(cols)]; df.columns = cols; parts.append(df.astype(float))
    return pd.concat(parts)
def klines(prefix_m, prefix_d, out):
    ks = keys(prefix_m); months = {k.split("-")[-2] + k.split("-")[-1][:2] for k in ks}
    kd = [k for k in keys(prefix_d) if k.split("-")[-3] + k.split("-")[-2] not in months] if prefix_d else []
    px = grab(ks + kd, ["ts", "o", "h", "l", "c", "v", "cts", "qv"])
    px["ts"] = px.ts.where(px.ts < 1e14, px.ts // 1000)
    px.index = pd.to_datetime(px.pop("ts").astype("int64"), unit="ms", utc=True); px = px[~px.index.duplicated()].sort_index()
    px[["o", "h", "l", "c", "v", "qv"]].to_parquet(f"{D}/{out}.parquet"); print(out, len(px), px.index[0], px.index[-1], flush=True)
klines("data/spot/monthly/klines/PAXGUSDT/15m/", None, "PAXG_15m")
for tf in ("15m", "1h"):
    klines(f"data/futures/um/monthly/klines/XAUUSDT/{tf}/", f"data/futures/um/daily/klines/XAUUSDT/{tf}/", f"XAUUSDT_perp_{tf}")
fk = keys("data/futures/um/monthly/fundingRate/XAUUSDT/")
if fk:
    f = grab(fk, ["ts", "interval", "rate"]); f.index = pd.to_datetime(f.ts.astype("int64"), unit="ms", utc=True)
    f[["rate"]].sort_index().to_parquet(f"{D}/XAUUSDT_funding.parquet"); print("funding", len(f))
for s, n in (("DX-Y.NYB", "DXY_1d"), ("^IRX", "IRX_1d"), ("^TNX", "TNX_1d")):
    r = c.get(f"https://query2.finance.yahoo.com/v8/finance/chart/{s}", params=dict(interval="1d", period1=946684800, period2=int(time.time()))).json()["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    df = pd.DataFrame(dict(o=q["open"], h=q["high"], l=q["low"], c=q["close"]), index=pd.to_datetime(r["timestamp"], unit="s", utc=True)).dropna(subset=["c"])
    df[~df.index.duplicated(keep="last")].to_parquet(f"{D}/{n}.parquet"); print(n, len(df), df.index[0], df.index[-1]); time.sleep(1)
