"""Panic gate for E31: per hour, each coin's H1 condition (24h return ≤ its own q10) and H3 breadth over all perpetuals."""
import pickle, json, sys, numpy as np, datetime as dt
sys.path.insert(0, '/home/claude/omega/recorder'); from omega_recorder import signals as S
RAW = pickle.load(open('/home/claude/e25/hourly_e26.pkl', 'rb'))
H0 = int(dt.datetime(2023, 5, 1, tzinfo=dt.timezone.utc).timestamp()//3600); H0 -= H0 % 24
H1 = int(dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc).timestamp()//3600)
COINS = json.load(open('/home/claude/omega/plans-new/E31_untouched_coins.json'))['coins']
Ps = {}
for s, x in RAW.items():
    ok = (x['v'] > 0) & (x['h'] >= H0) & (x['h'] < H1)
    if ok.sum() < 24*31: continue
    n = H1 - H0; c = np.full(n, np.nan); h = np.full(n, np.nan); l = np.full(n, np.nan); i = x['h'][ok] - H0
    c[i], h[i], l[i] = x['c'][ok], x['hi'][ok], x['lo'][ok]
    Ps[s] = S.prep(np.arange(H0, H1), c, h, l)
print(len(Ps), 'coins prepared', flush=True)
br = S.breadth_of(Ps.values())
h1 = {s: [int(Ps[s]['idx'][k]) for k in np.where(S.base(Ps[s], 10))[0]] for s in COINS if s in Ps}
pickle.dump(dict(breadth=br, h1=h1), open('e31_gate.pkl', 'wb'))
print('hours with breadth ≥ 20%:', sum(1 for v in br.values() if v >= 0.2), '| H1 hours per coin (median):', int(np.median([len(v) for v in h1.values()])), flush=True)
