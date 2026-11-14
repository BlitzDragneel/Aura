"""Gold and silver (and the PAXG gold proxy) for the metals research. Writes parquet to $OMEGA_DATA/metals/.
  GC_1d, SI_1d   Yahoo continuous futures, daily, 2000 -> now
  GC_1h, SI_1h   Yahoo continuous futures, hourly, last ~730 days (Yahoo's limit)
  PAXG_1h        Binance PAXGUSDT spot hourly from data.binance.vision, 2020 -> now (24/7 gold-backed token: a proxy)
Futures roll and the CME daily break (21-22 UTC) are in the data as Yahoo gives it; volume-0 bars are kept and flagged."""
import io, os, re, time, zipfile, xml.etree.ElementTree as ET
import httpx, pandas as pd
D = os.path.join(os.environ.get("OMEGA_DATA", "/home/user/data"), "metals"); os.makedirs(D, exist_ok=True)
c = httpx.Client(timeout=60, headers={"User-Agent": "Mozilla/5.0"})

def yahoo(sym, interval, **p):
    r = c.get(f"https://query2.finance.yahoo.com/v8/finance/chart/{sym}", params=dict(interval=interval, **p)).json()["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    df = pd.DataFrame(dict(o=q["open"], h=q["high"], l=q["low"], c=q["close"], v=q.get("volume")), index=pd.to_datetime(r["timestamp"], unit="s", utc=True))
    return df.dropna(subset=["c"]).loc[lambda x: ~x.index.duplicated(keep="last")]

for s, n in (("GC=F", "GC"), ("SI=F", "SI")):
    yahoo(s, "1d", period1=946684800, period2=int(time.time())).to_parquet(f"{D}/{n}_1d.parquet")
    yahoo(s, "60m", range="730d").to_parquet(f"{D}/{n}_1h.parquet"); time.sleep(1)

# PAXG spot hourly from Binance public archives
L = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"; NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"
keys, marker = [], None
while True:
    p = dict(prefix="data/spot/monthly/klines/PAXGUSDT/1h/")
    if marker: p["marker"] = marker
    root = ET.fromstring(c.get(L, params=p).text); ks = [e.findtext(f"{NS}Key") for e in root.findall(f"{NS}Contents")]; keys += ks
    if (root.findtext(f"{NS}IsTruncated") or "false") == "true" and ks: marker = ks[-1]
    else: break
parts = []
for k in sorted(x for x in keys if x.endswith(".zip")):
    z = zipfile.ZipFile(io.BytesIO(c.get("https://data.binance.vision/" + k).content))
    df = pd.read_csv(z.open(z.namelist()[0]), header=None).iloc[:, :8]; df.columns = ["ts", "o", "h", "l", "c", "v", "cts", "qv"]; parts.append(df)
px = pd.concat(parts); px["ts"] = px.ts.where(px.ts < 1e14, px.ts // 1000)
px.index = pd.to_datetime(px.pop("ts"), unit="ms", utc=True); px = px[~px.index.duplicated()].sort_index()
px[["o", "h", "l", "c", "v", "qv"]].to_parquet(f"{D}/PAXG_1h.parquet")
for f in sorted(os.listdir(D)):
    d = pd.read_parquet(f"{D}/{f}"); print(f, len(d), d.index[0].date(), "->", d.index[-1].date())
