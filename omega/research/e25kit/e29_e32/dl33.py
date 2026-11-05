import httpx, zipfile, io, csv, os, json, time, datetime as dt, concurrent.futures as cf
COINS = json.load(open('/home/claude/omega/plans-new/E33_coins.json'))['coins']
c = httpx.Client(timeout=60, limits=httpx.Limits(max_connections=32))
def days(a, b):
    d = dt.date.fromisoformat(a); e = dt.date.fromisoformat(b)
    while d <= e: yield d.isoformat(); d += dt.timedelta(days=1)
def job(a):
    s, d = a; fn = f'oi/{s}/{d}.json'
    if os.path.exists(fn): return 0
    os.makedirs(f'oi/{s}', exist_ok=True)
    for k in range(4):
        try:
            r = c.get(f'https://data.binance.vision/data/futures/um/daily/metrics/{s}/{s}-metrics-{d}.zip')
            if r.status_code == 404: json.dump(None, open(fn, 'w')); return 1
            if r.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content)); last = {}
                for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), 'utf-8')):
                    if not x or not x[0][:1].isdigit() or not x[2]: continue
                    t = dt.datetime.fromisoformat(x[0]); h = int(t.replace(tzinfo=dt.timezone.utc).timestamp()//3600)
                    if t.minute == 0 and t.second == 0: last[h] = float(x[2])          # OI at each hour's end (the 00:00 snapshot)
                json.dump(last, open(fn, 'w')); return 1
        except Exception: pass
        time.sleep(1 + 2*k)
    return 0
T = [(s, d) for s in COINS for d in days('2023-10-01', '2026-09-30')]; t0 = time.time()
with cf.ThreadPoolExecutor(32) as ex:
    for k, v in enumerate(ex.map(job, T)):
        if k % 5000 == 0: print(k, round(time.time() - t0), flush=True)
print('DONE', len(T), round(time.time() - t0), flush=True)
