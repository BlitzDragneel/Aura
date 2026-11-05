import zipfile, io, csv, glob, json, os, hashlib, numpy as np, pickle
fp = hashlib.md5(); old = {}; miss = 0
for d in sorted(glob.glob('zips_old/*')):
    sym = os.path.basename(d); rows = {}; meta = json.load(open(f'{d}/.done')); miss += len(meta['missing'])
    for f in sorted(glob.glob(f'{d}/*.zip')):
        b = open(f, 'rb').read(); fp.update(os.path.basename(f).encode() + hashlib.md5(b).digest()); z = zipfile.ZipFile(io.BytesIO(b))
        for r in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), 'utf-8')):
            if not r or not r[0][:1].isdigit(): continue
            t = int(r[0]); t = t // 1000 if t > 10**14 else t; rows[t // 3_600_000] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]))
    if rows:
        hs = np.array(sorted(rows)); a = np.array([rows[x] for x in hs]); old[sym] = dict(h=hs, o=a[:, 0], hi=a[:, 1], lo=a[:, 2], c=a[:, 3], v=a[:, 4])
new = pickle.load(open('hourly_e25.pkl', 'rb')); allc = {}
for s in sorted(set(old) | set(new)):
    parts = [x for x in (old.get(s), new.get(s)) if x is not None]
    m = {k: np.concatenate([p[k] for p in parts]) for k in ('h', 'o', 'hi', 'lo', 'c', 'v')}
    o = np.argsort(m['h'], kind='stable'); m = {k: v[o] for k, v in m.items()}
    keep = np.r_[m['h'][1:] != m['h'][:-1], True]; allc[s] = {k: v[keep] for k, v in m.items()}
pickle.dump(allc, open('hourly_e26.pkl', 'wb'))
print('old-archive fingerprint', fp.hexdigest(), '| listed-but-missing files', miss)
import datetime as dt
HH = lambda x: int(dt.datetime.fromisoformat(x).replace(tzinfo=dt.timezone.utc).timestamp()//3600)
lt = {s: int(x['h'][x['v'] > 0][-1]) for s, x in allc.items() if (x['v'] > 0).any()}
inwin = [s for s in lt if lt[s] >= HH('2021-01-01')]; dl = [s for s in inwin if lt[s] < HH('2026-10-11')]
import collections
print(len(allc), 'coins with candles;', len(inwin), 'traded at some point from 2021-01-01;', len(dl), 'delisted;', dict(sorted(collections.Counter(dt.datetime.fromtimestamp(lt[s]*3600, dt.UTC).year for s in dl).items())))
