import zipfile, io, csv, glob, json, os, hashlib, numpy as np, pickle
END = 1760745600 // 3600 + 24*0      # placeholder
import datetime as dt
h = lambda s: int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp() // 3600)
H_END = h('2026-10-19'); H_DELIST = h('2026-10-11')
fp = hashlib.md5(); out = {}; info = {}
for d in sorted(glob.glob('zips/*')):
    sym = os.path.basename(d); rows = {}
    meta = json.load(open(f'{d}/.done'))
    for f in sorted(glob.glob(f'{d}/*.zip')):
        b = open(f, 'rb').read(); fp.update(os.path.basename(f).encode() + hashlib.md5(b).digest())
        z = zipfile.ZipFile(io.BytesIO(b))
        for r in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), 'utf-8')):
            if not r or not r[0][:1].isdigit(): continue
            t = int(r[0]); t = t // 1000 if t > 10**14 else t; hh = t // 3_600_000
            if hh < H_END: rows[hh] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]))
    if not rows: info[sym] = dict(rows=0, missing=meta['missing']); continue
    hs = np.array(sorted(rows)); a = np.array([rows[x] for x in hs])
    out[sym] = dict(h=hs, o=a[:, 0], hi=a[:, 1], lo=a[:, 2], c=a[:, 3], v=a[:, 4])
    span = int(hs[-1] - hs[0] + 1)
    info[sym] = dict(rows=len(hs), first=int(hs[0]), last=int(hs[-1]), holes=span - len(hs), delisted=bool(hs[-1] < H_DELIST), missing=meta['missing'])
pickle.dump(out, open('hourly_e25.pkl', 'wb'))
json.dump(dict(data_md5=fp.hexdigest(), info=info), open('coverage.json', 'w'))
have = [s for s in info if info[s]['rows']]; dl = [s for s in have if info[s]['delisted']]
start24 = h('2024-01-01')
inwin = [s for s in have if info[s]['last'] >= start24]
print('data fingerprint', fp.hexdigest())
print(len(info), 'symbols;', len(have), 'with hourly data 2023-10 → 2026-10-18;', len(inwin), 'trading at some point from 2024-01-01;')
print(' of those', sum(1 for s in inwin if info[s]['delisted']), 'delisted before 2026-10-11;', sum(1 for s in inwin if not info[s]['delisted']), 'still trading')
print('listed-but-missing monthly files:', sum(len(info[s]['missing']) for s in info), '| coins with internal holes:', sum(1 for s in have if info[s]['holes'] > 0))
