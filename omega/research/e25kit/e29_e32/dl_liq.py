"""Download Binance archive bookDepth (Jan 2023 →) and metrics (2020 →) for 10 coins; keep hourly aggregates only."""
import httpx, zipfile, io, csv, os, json, sys, time, datetime as dt, numpy as np, concurrent.futures as cf
COINS = ['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','DOGEUSDT','ADAUSDT','AVAXUSDT','LINKUSDT','LTCUSDT']
A = 'https://data.binance.vision/data/futures/um/daily/'; c = httpx.Client(timeout=60, limits=httpx.Limits(max_connections=16))
def days(a, b):
    d = dt.date.fromisoformat(a); e = dt.date.fromisoformat(b)
    while d <= e: yield d.isoformat(); d += dt.timedelta(days=1)
def get(u):
    for k in range(4):
        try:
            r = c.get(u)
            if r.status_code in (200, 404): return r
        except httpx.HTTPError: pass
        time.sleep(1 + 2*k)
    return None
def depth_day(sym, d):
    r = get(f'{A}bookDepth/{sym}/{sym}-bookDepth-{d}.zip')
    if r is None or r.status_code != 200: return None
    z = zipfile.ZipFile(io.BytesIO(r.content)); rows = {}
    for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), 'utf-8')):
        if not x or not x[0][:1].isdigit(): continue
        h = int(x[0][11:13]); p = int(round(float(x[1]))); rows.setdefault((h, p), []).append(float(x[3]))      # notional (USDT)
    return {f'{h}|{p}': [float(np.median(v)), float(np.min(v)), len(v)] for (h, p), v in rows.items()}
def metrics_day(sym, d):
    r = get(f'{A}metrics/{sym}/{sym}-metrics-{d}.zip')
    if r is None or r.status_code != 200: return None
    z = zipfile.ZipFile(io.BytesIO(r.content)); out = []
    for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), 'utf-8')):
        if not x or not x[0][:1].isdigit(): continue
        out.append([x[0], *[float(v) if v not in ('', None) else None for v in x[2:]]])
    return out
def job(args):
    kind, sym, d = args; fn = f'{kind}/{sym}/{d}.json'
    if os.path.exists(fn): return 0
    os.makedirs(os.path.dirname(fn), exist_ok=True); v = depth_day(sym, d) if kind == 'depth' else metrics_day(sym, d)
    json.dump(v, open(fn, 'w')); return 1
tasks = [('depth', s, d) for s in COINS for d in days('2023-01-01', '2026-09-30')] + [('metrics', s, d) for s in COINS for d in days('2020-09-01', '2026-09-30')]
print(len(tasks), 'tasks', flush=True); n = 0; t0 = time.time()
with cf.ThreadPoolExecutor(16) as ex:
    for k, v in enumerate(ex.map(job, tasks)):
        n += v
        if k % 2000 == 0: print(time.strftime('%H:%M:%S'), k, 'done,', n, 'new,', round(time.time() - t0), 's', flush=True)
print('ALL DONE', flush=True)
