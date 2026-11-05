"""E31 judge (PLAN_E31_creed_upgrade.md, md5 08e44400…): U1 and U2 on 30 more untouched coins, once. Exits replicate the app's
walkExit exactly (stop first in a bar, then target, breakeven from the bar after +1R)."""
import json, gzip, pickle, numpy as np, pandas as pd
D = json.loads(gzip.open('e31_untouched_15m.json.gz').read()); G = pickle.load(open('e31_gate.pkl', 'rb')); BR, HH1 = G['breadth'], {k: set(v) for k, v in G['h1'].items()}
def dec(m):
    S = 10.0**-m['dp']; t = np.cumsum(m['t'])*900; c = np.cumsum(m['c'])*S; o = c + np.array(m['o'])*S
    return pd.DataFrame({'h':np.maximum(o, c) + np.array(m['h'])*S, 'l':np.minimum(o, c) - np.array(m['l'])*S, 'c':c}, index=t)
K = {m['sym']: dec(m) for m in D['markets']}
A0, A1 = pd.Timestamp('2023-10-01').value//10**9, pd.Timestamp('2026-10-01').value//10**9
def trades(path):
    T = json.load(open(path)); rows = []; mism = 0
    for sym, Cn in T['coins'].items():
        df = K[sym]; idx = df.index.values; H, L, Cc = df.h.values, df.l.values, df.c.values
        for tr in Cn['trades']:
            op = tr['t']//1000 - 900
            if not (A0 <= op < A1): continue
            k = np.searchsorted(idx, op)
            if k >= len(idx) or idx[k] != op: continue
            e, s, g, d = tr['entry'], tr['stop'], tr['target'], (1 if tr['d'] == 'L' else -1); R = abs(e - s); stop = s; be = False; px = xb = None
            for j in range(k + 1, min(len(idx), k + 1 + 96*14)):
                if (L[j] <= stop) if d > 0 else (H[j] >= stop): px, xb = stop, j; break
                if (H[j] >= g) if d > 0 else (L[j] <= g): px, xb = g, j; break
                if not be and ((H[j] - e) if d > 0 else (e - L[j]))/R >= 1: stop = e; be = True
            if px is None: continue
            if abs(d*(px - e)/R - tr['r']) > 1e-6: mism += 1
            hh = (op + 900)//3600 - 1                                  # the last hourly candle closed at the decision time
            gate = (hh in HH1.get(sym, ())) or BR.get(hh, 0) >= 0.20
            rows.append(dict(sym=sym, t=pd.Timestamp(op + 900, unit='s'), d=tr['d'], r=tr['r'], cost=tr['c'], gate=gate, bench=d*(Cc[xb] - e)/R))
    X = pd.DataFrame(rows); X['net'] = X.r - X.cost; X['bnet'] = X.bench - X.cost; return X, mism
def wt(s, t):
    w = s.groupby(t.dt.to_period('W')).sum(); return float(w.mean()/w.std()*np.sqrt(len(w))) if len(w) > 2 and w.std() > 0 else 0.0
XT, m1 = trades('e31_taught.json'); XA, m2 = trades('e31_atr.json')
print(f'as-taught buffer: {len(XT)} trades (exit mismatches {m1}); volatility buffer: {len(XA)} trades (mismatches {m2})')
print(f"stop width (cost in R): as taught median {XT.cost.median():.3f}R | volatility buffer median {XA.cost.median():.3f}R")
OUT = {}
for name, X, m, test in [('C0 CREED as taught (reported)', XT, XT.index == XT.index, False), ('U0 volatility buffer, longs, no gate (reported)', XA, XA.d == 'L', False),
                         ('U1 as-taught buffer + longs + panic gate', XT, (XT.d == 'L') & XT.gate, True), ('U2 volatility buffer + longs + panic gate', XA, (XA.d == 'L') & XA.gate, True)]:
    s = X[m]; yrs = s.groupby(s.t.dt.year).net.agg(['mean', 'size']); t = wt(s.net, s.t) if len(s) else 0.0
    ok = test and len(s) > 0 and t >= 1.96 and s.net.mean() > 0 and all(y in yrs.index and yrs.loc[y, 'size'] >= 10 and yrs.loc[y, 'mean'] > 0 for y in (2024, 2025, 2026))
    OUT[name] = dict(n=len(s), net=float(s.net.mean()) if len(s) else None, gross=float(s.r.mean()) if len(s) else None, win=float((s.r > 0).mean()) if len(s) else None, t=t,
                     years={int(y): [round(float(v['mean']), 3), int(v['size'])] for y, v in yrs.iterrows()}, bench_net=float(s.bnet.mean()) if len(s) else None, passed=bool(ok))
    print(f"{name:48s} n {len(s):5d} | net {OUT[name]['net']:+.3f}R gross {OUT[name]['gross']:+.3f}R win {OUT[name]['win']*100:4.1f}% | weekly t {t:+.2f} | {OUT[name]['years']} | same-moment benchmark net {OUT[name]['bench_net']:+.3f}R" + (('  → PASS' if ok else '  → FAIL') if test else ''))
json.dump(OUT, open('/home/claude/omega/plans-new/E31_result.json', 'w'), indent=1)
