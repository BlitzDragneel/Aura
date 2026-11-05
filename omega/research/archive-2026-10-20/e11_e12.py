import sys, json, numpy as np, pandas as pd
from numba import njit
sys.path.insert(0, '/home/claude/edge'); from load import load
d, ms = load('creed15_1'); HR = {}
for m in ms:
    if m['sym'] not in ('BTCUSDT', 'ETHUSDT'): continue
    tb = np.where(m['tb'] >= 0, m['tb'], np.nan); df = pd.DataFrame({'t':(m['t']*900)//3600, 'o':m['o'], 'h':m['h'], 'l':m['l'], 'c':m['c'], 'v':m['v'], 'bv':tb*m['v']})
    g = df.groupby('t').agg(o=('o','first'), h=('h','max'), l=('l','min'), c=('c','last'), v=('v','sum'), bv=('bv','sum')); g['tb'] = g.bv/g.v; g.index = pd.to_datetime(g.index*3600, unit='s'); HR[m['sym']] = g
S = pd.Timestamp('2024-01-01')
def wk_t(p):
    w = p.groupby(p.index.to_period('W-SUN')).sum(); w = w.reindex(pd.period_range(p.index[0], p.index[-1], freq='W-SUN'), fill_value=0.0)
    return float(w.mean()/w.std()*np.sqrt(len(w))) if w.std() > 0 else 0.0
# ── E11 absorption ──
COST = 0.0005; rows = []
for sym, g in HR.items():
    r = np.log(g.c).diff(); hi = g.tb.rolling(720, min_periods=360).quantile(0.95).shift(1); lo = g.tb.rolling(720, min_periods=360).quantile(0.05).shift(1)
    sig = np.where((g.tb >= hi) & (r <= 0), -1, np.where((g.tb <= lo) & (r >= 0), 1, 0)); o, c, idx = g.o.values, g.c.values, g.index; k = 0; n = len(g)
    while k < n - 5:
        if sig[k] != 0 and np.isfinite(o[k+1]) and np.isfinite(c[k+4]): rows.append((idx[k+1], sym, int(sig[k]), sig[k]*np.log(c[k+4]/o[k+1]) - 2*COST)); k += 4; continue
        k += 1
T = pd.DataFrame(rows, columns=['t', 'sym', 'd', 'pnl']).set_index('t').sort_index()
pnl = T.pnl.groupby(level=0).sum()
full = pd.Series(0.0, index=pd.date_range(min(g.index[0] for g in HR.values()), max(g.index[-1] for g in HR.values()), freq='h')); full.loc[pnl.index] += pnl.values
a, b = T[T.index < S], T[T.index >= S]; t_all = wk_t(full); passed = t_all >= 2.0 and T.pnl.sum() > 0 and a.pnl.sum() > 0 and b.pnl.sum() > 0
print('E11 ABSORPTION (BTC+ETH, hourly, 0.05% a side)')
print(f"  trades {len(T)} | mean {T.pnl.mean()*100:+.3f}% | winners {np.mean(T.pnl > 0)*100:.0f}% | total {T.pnl.sum()*100:+.1f}% | weekly t {t_all:+.2f} | before 2024 {a.pnl.sum()*100:+.1f}% ({len(a)}) | from 2024 {b.pnl.sum()*100:+.1f}% ({len(b)})")
for dd, lab in [(-1, 'buy absorption → short'), (1, 'sell absorption → long')]:
    x = T[T.d == dd]; print(f"    {lab:24s} n {len(x):4d} mean {x.pnl.mean()*100:+.3f}% | before 2024 {x[x.index < S].pnl.mean()*100:+.3f}% | from 2024 {x[x.index >= S].pnl.mean()*100:+.3f}%")
for sym in HR: x = T[T.sym == sym]; print(f"    {sym}: n {len(x)} mean {x.pnl.mean()*100:+.3f}%")
print('  VERDICT:', 'PASS' if passed else 'FAIL')
# ── E12 stop-outs ──
@njit(cache=True)
def scan(o, h, l, c, atr, lo24, hi24, step):
    n = len(c); out = []
    for i in range(30, n - 74, step):
        a = atr[i]
        if not (a > 0): continue
        e = o[i+1]
        for d in (1, -1):
            for mode in (0, 1):
                if mode == 0:
                    stop = lo24[i] - 0.1*a if d == 1 else hi24[i] + 0.1*a; dist = (e - stop)*d
                    if dist < 0.5*a or dist > 3*a: continue
                else:
                    dist = 1.5*a; stop = e - d*dist
                hit = -1
                for j in range(i+1, i+49):
                    if (d == 1 and l[j] <= stop) or (d == -1 and h[j] >= stop): hit = j; break
                rec = 0
                if hit >= 0:
                    tgt = e + d*dist
                    for j in range(hit+1, hit+25):
                        if (d == 1 and h[j] >= tgt) or (d == -1 and l[j] <= tgt): rec = 1; break
                out.append((i, d, mode, 1 if hit >= 0 else 0, rec))
    return out
def prep(g):
    o, h, l, c = g.o.values, g.h.values, g.l.values, g.c.values; pc = np.r_[c[0], c[:-1]]; tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = pd.Series(tr).ewm(alpha=1/14, adjust=False).mean().values; lo24 = pd.Series(l).rolling(24).min().values; hi24 = pd.Series(h).rolling(24).max().values
    return o, h, l, c, atr, lo24, hi24
def rates(res):
    R = np.array(res, dtype=float); out = {}
    for mode in (0, 1):
        x = R[R[:, 2] == mode]; hit = x[x[:, 3] == 1]; out[mode] = (len(x), x[:, 3].mean(), hit[:, 4].mean() if len(hit) else np.nan, x, hit)
    return out
rng = np.random.default_rng(12); real = {}; null = {0:[], 1:[]}; real_rows = {}
for sym, g in HR.items():
    g = g.dropna(subset=['o','h','l','c']); P = prep(g); res = scan(*P, 4); real[sym] = rates(res); real_rows[sym] = (np.array(res, dtype=float), g.index)
    c = g.c.values; pc = np.r_[c[0], c[:-1]]
    for k in range(20):
        p = rng.permutation(len(c) - 1) + 1; lr = np.log(c/pc)[p]; cc = np.r_[c[0], c[0]*np.exp(np.cumsum(lr))]; prev = cc[:-1]
        oo = np.r_[g.o.values[0], prev*(g.o.values/pc)[p]]; hh = np.r_[g.h.values[0], prev*(g.h.values/pc)[p]]; ll = np.r_[g.l.values[0], prev*(g.l.values/pc)[p]]
        hh = np.maximum(hh, np.maximum(oo, cc)); ll = np.minimum(ll, np.minimum(oo, cc)); sh = pd.DataFrame({'o':oo, 'h':hh, 'l':ll, 'c':cc})
        rr = rates(scan(*prep(sh), 4)); [null[m].append(rr[m][2]) for m in (0, 1)]
print('\nE12 STOP-OUTS (BTC+ETH, entries every 4 h, both directions)')
names = {0:'OBVIOUS (beyond the 24 h low/high)', 1:'FIXED (1.5 ATR)'}; eff = {}
for mode in (0, 1):
    n = sum(real[s][mode][0] for s in real); hitr = np.mean(np.concatenate([real[s][mode][3][:, 3] for s in real])); rec = np.concatenate([real[s][mode][4][:, 4] for s in real]).mean()
    nul = np.mean(null[mode]); eff[mode] = rec - nul
    print(f"  {names[mode]:36s} entries {n:6d} | stop hit within 48 h {hitr*100:4.1f}% | after a stop-out, went 1R my way within 24 h: real {rec*100:4.1f}% vs shuffled {nul*100:4.1f}% (range {min(null[mode])*100:.1f}–{max(null[mode])*100:.1f}%)")
hunt = eff[0] - eff[1]
# bootstrap by week over the real stopped trades
wk = {}; 
for s, (R, idx) in real_rows.items():
    weeks = idx[R[:, 0].astype(int)].to_period('W-SUN').astype(str)
    for (row, w) in zip(R, weeks):
        if row[3] == 1: wk.setdefault(w, {0:[], 1:[]})[int(row[2])].append(row[4])
W = list(wk.keys()); B = []; nul0, nul1 = np.mean(null[0]), np.mean(null[1])
for _ in range(2000):
    pick = rng.choice(len(W), len(W)); a0 = [x for i in pick for x in wk[W[i]][0]]; a1 = [x for i in pick for x in wk[W[i]][1]]
    if a0 and a1: B.append((np.mean(a0) - nul0) - (np.mean(a1) - nul1))
lo, hi = np.percentile(B, [2.5, 97.5])
print(f"  hunt effect (obvious minus fixed, each against shuffled): {hunt*100:+.2f} points, 95% interval {lo*100:+.2f} to {hi*100:+.2f} → {'EVIDENCE of hunting' if lo > 0 else ('obvious stops recover LESS than chance' if hi < 0 else 'no evidence of hunting')}")
json.dump(dict(e11=dict(trades=len(T), mean=float(T.pnl.mean()), t=t_all, passed=bool(passed)), e12=dict(eff_obvious=float(eff[0]), eff_fixed=float(eff[1]), hunt=float(hunt), ci=[float(lo), float(hi)])), open('plans/E11_E12_result.json', 'w'), indent=1)
