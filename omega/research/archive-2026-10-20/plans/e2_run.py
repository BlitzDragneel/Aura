"""Plan E2 (PLAN_E2_gold_hourly.md, md5 a065c880bfa39435532e8c529cd4ad51): run once on the gold hourly file from OMEGA v6.5.84.
usage: python3 e2_run.py <omega-history-gold1h-*.json.gz> [--dry]"""
import sys, json, gzip, hashlib, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); import engine3 as G
path = sys.argv[1]; DRY = '--dry' in sys.argv; raw = open(path, 'rb').read()
print('file', path, 'sha256', hashlib.sha256(raw).hexdigest(), '| DRY RUN (synthetic data, numbers mean nothing)' if DRY else '')
d = json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw); print('file checks:', json.dumps(d.get('checks')))
def decode(m):
    s = 10.0**-m['dp']; t = np.cumsum(np.asarray(m['t'], dtype=np.int64)); c = np.cumsum(np.asarray(m['c'], dtype=np.int64))*s
    o = c + np.asarray(m['o'], dtype=np.int64)*s; h = np.maximum(o, c) + np.asarray(m['h'], dtype=np.int64)*s; l = np.minimum(o, c) - np.asarray(m['l'], dtype=np.int64)*s
    return t, o, h, l, c
class One:   # a single market laid out like engine3.Bars/Book
    def __init__(self, t, o, h, l, c):
        n = len(c); self.t, self.o, self.h, self.l, self.c = t, o, h, l, c; self.fund = np.zeros(n); self.ema = pd.Series(c).ewm(span=20, adjust=False).mean().values
        pc = np.r_[c[0], c[:-1]]; tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc))); self.atr = pd.Series(tr).ewm(alpha=1/14, adjust=False).mean().values
        hi72 = pd.Series(h).rolling(72).max().shift(1).values; lo72 = pd.Series(l).rolling(72).min().shift(1).values; hr = t % 24
        x = np.where((hr >= 13) & (hr <= 20) & (c > hi72), 1, np.where((hr >= 13) & (hr <= 20) & (c < lo72), -1, 0)); x[:200] = 0; x[-2:] = 0
        self.i = np.where(x != 0)[0].astype(np.int64); self.d = x[self.i].astype(np.int64); self.end = np.full(len(self.i), n - 1, dtype=np.int64); self.sa = self.atr[self.i]; self.hr = t[self.i]
        self.order = np.argsort(self.hr, kind='stable').astype(np.int64)
    def run(self, p, flip=None):
        d = self.d if flip is None else self.d*flip; R, xi, ei = G.sim_all(self.o, self.h, self.l, self.c, self.ema, self.fund, self.i, self.end, d, self.sa, p)
        v = ~np.isnan(R); xh = np.where(xi >= 0, self.t[np.maximum(xi, 0)], 0); return R, xh, v
    def acct(self, R, xh, v, a, b): return G.account(self.hr, self.order, xh, np.nan_to_num(R), v, a, b, 0.01, 0)
M = {'M1 owner 5-unit': dict(init=1.0, sc1_frac=0.6, sc1_R=1.0, be_R=1.0, be_to=0.0, add_mode=1, add_size=0.2, add_max=3, add_R=1.0, trail_mode=1, trail_k=3, max_bars=168),
     'M2 new method': dict(entry_mode=1, retest_off=0.5, retest_wait=6, stop_k=3.0, sc1_frac=0.5, sc1_R=1.0, trail_mode=1, trail_k=3.0, max_bars=168)}
res = {}
for mk in d['markets']:
    t, o, h, l, c = decode(mk); X = One(t, o, h, l, c); T0, T1 = int(t[0]), int(t[-1]) + 1
    years = sorted(set(pd.to_datetime(t*3600, unit='s').year)); print(f"\n{mk['sym']}: {len(t)} hours, {pd.to_datetime(t[0]*3600, unit='s').date()} to {pd.to_datetime(t[-1]*3600, unit='s').date()}, {len(X.i)} signals")
    for name, kw in M.items():
        for fee in (0.0005, 0.001):
            p = G.P(fee=fee, **kw); R, xh, v = X.run(p); eq, dd, n, _ = X.acct(R, xh, v, T0, T1)
            ys = []
            for y in years:
                a = int(pd.Timestamp(f'{y}-01-01').value//3600//10**9); b = int(pd.Timestamp(f'{y+1}-01-01').value//3600//10**9); ys.append((y, float(X.acct(R, xh, v, max(a, T0), min(b, T1))[0])))
            line = f"  {name:16s} costs {fee*100:.2f}%/side: 100 -> {eq:7.1f} (fall {dd*100:3.0f}%, {n} trades) | years positive {sum(e > 100 for _, e in ys)}/{len(ys)}"
            if fee == 0.0005:
                rng = np.random.default_rng(1); fl = np.array([X.acct(*X.run(p, flip=rng.choice([-1, 1], size=len(X.d))), T0, T1)[0] for _ in range(200)])
                beat = float(np.mean(fl < eq)*100); passed = eq > 100 and beat >= 97.5 and sum(e > 100 for _, e in ys) >= len(ys)/2
                line += f" | beat {beat:.1f}% of 200 coin-flips | {'PASS' if passed else 'FAIL'}" + (' (gold counts)' if mk['sym'] == 'XAUUSD' else ' (silver: reported only)')
                res[f"{mk['sym']}|{name}"] = dict(end=float(eq), dd=float(dd), n=int(n), beat=beat, years=ys, passed=bool(passed))
            print(line)
json.dump(res, open('E2_result' + ('_DRYRUN' if DRY else '') + '.json', 'w'), indent=1); print('\nsaved', 'E2_result' + ('_DRYRUN' if DRY else '') + '.json')
