import httpx, zipfile, io, csv, json, gzip, os, time, numpy as np, concurrent.futures as cf
COINS = json.load(open('/home/claude/omega/plans-new/E31_untouched_coins.json'))['coins']
MONTHS = [f'{y}-{m:02d}' for y in (2023, 2024, 2025, 2026) for m in range(1, 13) if '2023-08' <= f'{y}-{m:02d}' <= '2026-09']
c = httpx.Client(timeout=60, limits=httpx.Limits(max_connections=12))
def one(args):
    sym, mo = args; fn = f'k15/{sym}-{mo}.csv'
    if os.path.exists(fn): return 1
    for k in range(4):
        try:
            r = c.get(f'https://data.binance.vision/data/futures/um/monthly/klines/{sym}/15m/{sym}-15m-{mo}.zip')
            if r.status_code == 404: open(fn, 'w').close(); return 0
            if r.status_code == 200:
                z = zipfile.ZipFile(io.BytesIO(r.content)); open(fn, 'wb').write(z.open(z.namelist()[0]).read()); return 1
        except httpx.HTTPError: pass
        time.sleep(1 + 2*k)
    return 0
with cf.ThreadPoolExecutor(12) as ex: got = sum(ex.map(one, [(s, m) for s in COINS for m in MONTHS]))
print('files', got, 'of', len(COINS)*len(MONTHS))
markets = []
for s in COINS:
    rows = []
    for mo in MONTHS:
        fn = f'k15/{s}-{mo}.csv'
        if not os.path.exists(fn): continue
        for x in csv.reader(open(fn)):
            if not x or not x[0][:1].isdigit(): continue
            t = int(x[0]); t = t//1000 if t > 10**14 else t; v = float(x[5])
            if v <= 0: continue                                   # volume-0 candles are missing (addendum B rule)
            rows.append((t//900000, float(x[1]), float(x[2]), float(x[3]), float(x[4]), v, float(x[9])))
    rows.sort(); 
    if not rows: continue
    p = min(r[4] for r in rows); dp = max(0, min(10, 6 - int(np.floor(np.log10(p)))))
    S = 10**dp; T = []; Cc = []; Oo = []; Hh = []; Ll = []; V = []; TB = []; pt = pc = 0
    for (t, o, h, l, cl, v, tbv) in rows:
        ci, oi, hi, li = round(cl*S), round(o*S), round(h*S), round(l*S)
        T.append(t - pt); Cc.append(ci - pc); pt, pc = t, ci; Oo.append(oi - ci); Hh.append(max(0, hi - max(oi, ci))); Ll.append(max(0, min(oi, ci) - li)); V.append(v); TB.append(round(tbv/v*1000))
    markets.append(dict(sym=s, dp=dp, t=T, c=Cc, o=Oo, h=Hh, l=Ll, v=V, tb=TB))
with gzip.open('e31_untouched_15m.json.gz', 'wt') as fh: json.dump(dict(tunit=900, tf=15, src='Binance archive USDT-M 15m (E31)', markets=markets), fh)
print('markets', len(markets), [(m['sym'], len(m['t'])) for m in markets][:5])
