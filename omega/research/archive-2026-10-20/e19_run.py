"""Plan E19 (PLAN_E19_simulator_v2.md): the path simulator v2 on 20 unseen coins, run once."""
import sys, json, time, numpy as np, pandas as pd
from numba import njit, prange
sys.path.insert(0, '/home/claude/edge'); from load import load
LAM, N, KS = 0.94, 5000, (0.5, 1.0); ALPHA, BETA = 0.06, 0.93; CAL_END = pd.Timestamp('2024-01-01'); TEST_END = pd.Timestamp('2026-10-18')
COINS = {}
for part in ['creed15_2', 'creed15_3', 'creed15_4', 'creed15_5']:
  d, ms = load(part)
  for m in ms:
    df = pd.DataFrame({'h':(m['t']*900)//3600, 'o':m['o'], 'hi':m['h'], 'lo':m['l'], 'c':m['c']}).groupby('h').agg(o=('o', 'first'), hi=('hi', 'max'), lo=('lo', 'min'), c=('c', 'last'))
    idx = np.arange(df.index.min(), df.index.max() + 1); df = df.reindex(idx); COINS[m['sym'].replace('USDT', '')] = df
@njit(parallel=True, cache=True)
def simulate(z, u, dd, s, lam, v0, h0, B, N, seed, om, al, be):
    n = v0.shape[0]; K = B.shape[1]; q = np.empty((n, 6)); pu = np.zeros((n, K)); pd_ = np.zeros((n, K)); pf = np.zeros((n, K)); L = z.shape[0]
    for o in prange(n):
        np.random.seed(seed + o); fin = np.empty(N)
        for p in range(N):
            lp = 0.0; v = v0[o]; done = np.zeros(K, np.int64); tu = np.zeros(K, np.int64); td = np.zeros(K, np.int64)
            for j in range(24):
                sc = np.sqrt(v)*s[(h0[o] + j) % 24]; i = np.random.randint(0, L); hi = lp + sc*u[i]; lo = lp + sc*dd[i]
                for k in range(K):
                    up = hi >= B[o, k]; dn = lo <= -B[o, k]
                    if up: tu[k] = 1
                    if dn: td[k] = 1
                    if done[k] == 0:
                        if dn: done[k] = 2
                        elif up: done[k] = 1
                r = sc*z[i]; lp += r; v = om[o] + al*r*r + be*v
            fin[p] = lp
            for k in range(K):
                pu[o, k] += tu[k]; pd_[o, k] += td[k]; pf[o, k] += 1 if done[k] == 1 else 0
        fs = np.sort(fin); qs = (0.005, 0.05, 0.25, 0.75, 0.95, 0.995)
        for a in range(6): q[o, a] = fs[min(N - 1, int(qs[a]*N))]
        for k in range(K): pu[o, k] /= N; pd_[o, k] /= N; pf[o, k] /= N
    return q, pu, pd_, pf
def realized(df, T, B):
    c0 = df.c.values[T]; H = np.log(df.hi.values[T+1:T+25]/c0); Lw = np.log(df.lo.values[T+1:T+25]/c0); R = np.log(df.c.values[T+24]/c0); out = []
    for b in B:
        tu = int(H.max() >= b); td = int(Lw.min() <= -b); uf = 0
        for j in range(24):
            if Lw[j] <= -b: break
            if H[j] >= b: uf = 1; break
        out.append((tu, td, uf))
    return R, out
t0 = time.time(); REC = []; BASE = []; NORMAL = []
for name, df in COINS.items():
    c, hi, lo = df.c.values, df.hi.values, df.lo.values; cp = np.r_[np.nan, c[:-1]]
    r = np.log(c/cp); uh = np.log(hi/cp); dl = np.log(lo/cp); hours = (df.index.values % 24); ts = pd.to_datetime(df.index.values*3600, unit='s')
    v = np.empty(len(r)); seed = np.nanvar(r[1:501]); v[0] = seed
    for t in range(1, len(r)): v[t] = LAM*v[t-1] + (1 - LAM)*r[t-1]**2 if np.isfinite(r[t-1]) else v[t-1]
    cal = (ts < CAL_END) & np.isfinite(r) & np.isfinite(uh) & np.isfinite(dl) & (np.arange(len(r)) > 600)
    s = np.array([np.sqrt(np.mean((r[cal & (hours == h)]**2)/v[cal & (hours == h)])) for h in range(24)])
    sc = np.sqrt(v)*s[hours]; z = r[cal]/sc[cal]; u = uh[cal]/sc[cal]; dd = dl[cal]/sc[cal]; mz = z.mean(); z, u, dd = z - mz, u - mz, dd - mz
    def origins(lo_ts, hi_ts):
        out = []
        for T in np.where((hours == 0) & (ts >= lo_ts) & (ts < hi_ts))[0]:
            if T + 25 <= len(c) and np.all(np.isfinite(c[T:T+25])) and np.all(np.isfinite(hi[T+1:T+25])) and np.all(np.isfinite(lo[T+1:T+25])) and T + 1 < len(v): out.append(T)
        return out
    for T in origins(pd.Timestamp('2020-03-01'), CAL_END):
        B = [k*np.sqrt(24*v[T+1]) for k in KS]; R, ev = realized(df, T, B); BASE.append([e for x in ev for e in x])
    OT = origins(CAL_END, TEST_END); q = np.zeros((0, 6)); allq = {}; 
    groups = {}
    for T in OT: groups.setdefault((ts[T].year, (ts[T].month - 1)//3), []).append(T)
    res = {}
    for (yy, qq), TT in groups.items():
        q0 = pd.Timestamp(year=yy, month=3*qq + 1, day=1); win = (ts < q0) & (ts >= q0 - pd.Timedelta(hours=17520)) & np.isfinite(r) & np.isfinite(uh) & np.isfinite(dl) & (np.arange(len(r)) > 600)
        if win.sum() < 4000: continue
        sq = np.array([np.sqrt(np.mean((r[win & (hours == h)]**2)/v[win & (hours == h)])) for h in range(24)]); scq = np.sqrt(v)*sq[hours]
        zq = r[win]/scq[win]; uq = uh[win]/scq[win]; dq = dl[win]/scq[win]; mq = zq.mean(); zq, uq, dq = zq - mq, uq - mq, dq - mq
        v0 = np.array([v[T+1] for T in TT]); h0 = np.array([(hours[T] + 1) % 24 for T in TT], dtype=np.int64); Bm = np.array([[k*np.sqrt(24*v[T+1]) for k in KS] for T in TT])
        om = np.array([0.01*np.nanmedian(v[max(0, T - 8760):T]) for T in TT])
        qq_, pu, pdn, pf = simulate(zq, uq, dq, sq, LAM, v0, h0, Bm, N, 19, om, ALPHA, BETA)
        for i, T in enumerate(TT): res[T] = (qq_[i], [[pu[i, k], pdn[i, k], pf[i, k]] for k in range(len(KS))], Bm[i])
    OT = sorted(res)
    sd_cal = np.nanstd(r[cal])
    for T in OT:
        qv, pv, Bv = res[T]; R, ev = realized(df, T, Bv); REC.append(dict(coin=name, R=R, q=qv.tolist(), p=pv, y=[list(e) for e in ev]))
        NORMAL.append((R, sd_cal*np.sqrt(24)))
print(f'simulated {len(REC)} origins × {N} paths in {time.time() - t0:.0f} s')
# (a) coverage
def cov(rows):
    R = np.array([x['R'] for x in rows]); Q = np.array([x['q'] for x in rows]); return { '50%':float(np.mean((R >= Q[:, 2]) & (R <= Q[:, 3]))), '90%':float(np.mean((R >= Q[:, 1]) & (R <= Q[:, 4]))), '99%':float(np.mean((R >= Q[:, 0]) & (R <= Q[:, 5]))) }
pooled = cov(REC); per = {c: cov([x for x in REC if x['coin'] == c]) for c in COINS}; nom = { '50%':0.5, '90%':0.9, '99%':0.99 }
a_ok = all(abs(pooled[k] - nom[k]) <= 0.02 for k in nom) and all(abs(per[c][k] - nom[k]) <= 0.04 for c in per for k in nom)
print('\n(a) COVERAGE of the real 24-hour move (target 50 / 90 / 99%):'); print(f"   pooled: {pooled['50%']*100:.1f} / {pooled['90%']*100:.1f} / {pooled['99%']*100:.1f}")
bad = [c for c in per if any(abs(per[c][k] - nom[k]) > 0.04 for k in nom)]; print('   coins outside ±4 points:', {c: [round(per[c][k]*100, 1) for k in nom] for c in bad} or 'none')
from scipy.stats import norm
NR = np.array([x[0] for x in NORMAL]); NS = np.array([x[1] for x in NORMAL]); ncov = {k: float(np.mean(np.abs(NR) <= norm.ppf(0.5 + nom[k]/2)*NS)) for k in nom}
print(f"   comparison, normal model with constant volatility: {ncov['50%']*100:.1f} / {ncov['90%']*100:.1f} / {ncov['99%']*100:.1f}")
# (b) calibration
names = []; [names.extend([f'touch-up k={k}', f'touch-down k={k}', f'up-first k={k}']) for k in KS]
P = np.array([[e for kk in x['p'] for e in kk] for x in REC]); Y = np.array([[e for kk in x['y'] for e in kk] for x in REC]); base = np.array(BASE).mean(axis=0)
b_ok = True; print('\n(b) CALIBRATION (expected calibration error ≤ 0.02 and Brier better than the baseline):')
for j, nmj in enumerate(names):
    p, y = P[:, j], Y[:, j]; bins = np.minimum((p*10).astype(int), 9); ece = sum(np.sum(bins == b)/len(p)*abs(y[bins == b].mean() - p[bins == b].mean()) for b in range(10) if np.any(bins == b))
    brier = np.mean((p - y)**2); bb = np.mean((base[j] - y)**2); skill = 1 - brier/bb; ok = ece <= 0.02 and skill > 0; b_ok &= ok
    print(f"   {nmj:16s} predicted {p.mean()*100:5.1f}% | happened {y.mean()*100:5.1f}% | ECE {ece:.3f} | Brier skill vs baseline {skill*100:+.1f}% | {'ok' if ok else 'FAIL'}")
# (c) tails
R = np.array([x['R'] for x in REC]); Q = np.array([x['q'] for x in REC]); tail = float(np.mean((R < Q[:, 0]) | (R > Q[:, 5]))); c_ok = 0.004 <= tail <= 0.02
print(f'\n(c) TAILS: real moves beyond the simulated 99% range: {tail*100:.2f}% (pass 0.4–2.0%)')
passed = a_ok and b_ok and c_ok; print('\nVERDICT:', 'PASS' if passed else 'FAIL', f'(coverage {"ok" if a_ok else "FAIL"}, calibration {"ok" if b_ok else "FAIL"}, tails {"ok" if c_ok else "FAIL"})')
json.dump(dict(pooled=pooled, per=per, normal=ncov, tail=tail, passed=bool(passed), origins=len(REC)), open('plans/E19_result.json', 'w'), indent=1)
