"""E29 judge (PLAN_E29_creed_improved.md, md5 03874f64…): C2 and C5 on the 30 untouched coins, once."""
import json, gzip, sys, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/omega/research'); from load import load
_, ms = load('creed15_1'); B = [m for m in ms if m['sym'] == 'BTCUSDT'][0]; BT = pd.Series(B['c'], index=B['t']*900); BT = BT[~BT.index.duplicated()]
D = json.loads(gzip.open('e29_untouched_15m.json.gz').read())
def dec(m):
    S = 10.0**-m['dp']; t = np.cumsum(m['t'])*900; c = np.cumsum(m['c'])*S; o = c + np.array(m['o'])*S
    return pd.DataFrame({'o':o, 'h':np.maximum(o, c) + np.array(m['h'])*S, 'l':np.minimum(o, c) - np.array(m['l'])*S, 'c':c}, index=t)
K = {m['sym']: dec(m) for m in D['markets']}
T = json.load(open('e29_trades.json')); rows = []; mism = 0
A0, A1 = pd.Timestamp('2023-10-01').value//10**9, pd.Timestamp('2026-10-01').value//10**9
for sym, Cn in T['coins'].items():
    df = K[sym]; idx = df.index.values; H, L, Cc = df.h.values, df.l.values, df.c.values
    for tr in Cn['trades']:
        op = tr['t']//1000 - 900
        if not (A0 <= op < A1): continue
        k = np.searchsorted(idx, op)
        if k >= len(idx) or idx[k] != op: continue
        e, s, g, d = tr['entry'], tr['stop'], tr['target'], (1 if tr['d'] == 'L' else -1); R = abs(e - s); stop = s; be = False; px = None; xb = None
        for j in range(k + 1, min(len(idx), k + 1 + 96*14)):
            hs = L[j] <= stop if d > 0 else H[j] >= stop; ht = H[j] >= g if d > 0 else L[j] <= g
            if hs: px, xb = stop, j; break
            if ht: px, xb = g, j; break
            if not be and ((H[j] - e) if d > 0 else (e - L[j]))/R >= 1: stop = e; be = True
        if px is None: continue                                     # the replay skips trades without an exit too
        r = d*(px - e)/R
        if abs(r - tr['r']) > 1e-6: mism += 1
        b = BT.get(op); b0 = BT.get(op - 86400); b24 = np.log(b/b0) if b and b0 else np.nan
        rows.append(dict(sym=sym, t=pd.Timestamp(op + 900, unit='s'), d=tr['d'], r=tr['r'], cost=tr['c'], btc24=b24, bench=d*(Cc[xb] - e)/R, bars=xb - k))
X = pd.DataFrame(rows); X['net'] = X.r - X.cost; X['bnet'] = X.bench - X.cost
print(f'trades {len(X)} on {X.sym.nunique()} coins, {X.t.min().date()} → {X.t.max().date()}; exit replication mismatches: {mism} of {len(X)}')
def wt(s, t):
    w = s.groupby(t.dt.to_period('W')).sum(); return float(w.mean()/w.std()*np.sqrt(len(w))) if len(w) > 2 and w.std() > 0 else 0.0
OUT = {}
for name, m in [('C0 as taught (reported)', X.index == X.index), ('C2 longs, BTC 24h ≤ −1%', (X.d == 'L') & (X.btc24 <= -0.01)), ('C5 longs, BTC 24h ≤ −2%', (X.d == 'L') & (X.btc24 <= -0.02))]:
    s = X[m]; yrs = s.groupby(s.t.dt.year).net.agg(['mean', 'size']); t = wt(s.net, s.t)
    ok = name[:2] != 'C0' and t >= 1.96 and s.net.mean() > 0 and all(y in yrs.index and yrs.loc[y, 'size'] >= 20 and yrs.loc[y, 'mean'] > 0 for y in (2024, 2025, 2026))
    OUT[name] = dict(n=len(s), net=float(s.net.mean()), gross=float(s.r.mean()), win=float((s.r > 0).mean()), t=t, years={int(y): [round(float(v['mean']), 3), int(v['size'])] for y, v in yrs.iterrows()},
                     bench_net=float(s.bnet.mean()), bench_t=wt(s.bnet, s.t), passed=bool(ok))
    print(f"{name:26s} n {len(s):5d} | net {s.net.mean():+.3f}R gross {s.r.mean():+.3f}R win {(s.r>0).mean()*100:4.1f}% | weekly t {t:+.2f} | years {OUT[name]['years']} | benchmark (same coin, same hold) net {s.bnet.mean():+.3f}R t {OUT[name]['bench_t']:+.2f}" + ('' if name[:2] == 'C0' else ('  → PASS' if ok else '  → FAIL')))
json.dump(OUT, open('/home/claude/omega/plans-new/E29_result.json', 'w'), indent=1)
