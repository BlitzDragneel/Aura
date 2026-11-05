"""E25: E22 H1/H3 on every USDT perpetual incl. delisted (PLAN_E25 + Addendum A). Run ONCE."""
import sys, json, numpy as np, pandas as pd, pickle, os
from multiprocessing import Pool
sys.path.insert(0, '/home/claude/omega/research')
from e22_lib import prep, masks, breadth_of, wt
U = [s for s in open('/home/claude/omega/plans-new/E25_universe.txt').read().split()]
H = 3_600_000; LOAD_FROM = pd.Timestamp('2023-10-01').value // 10**6
END_H = pd.Timestamp('2026-10-18 23:00').value // 10**6 // H
A1, B1 = pd.Timestamp('2024-01-01').value // 10**9 // 3600, pd.Timestamp('2026-10-18').value // 10**9 // 3600
def frame(s):
    a = np.load(f'/home/claude/data/um1h/{s}.npy'); a = a[a[:, 0] >= LOAD_FROM]
    if len(a) < 48: return None
    h = (a[:, 0] // H).astype(np.int64)
    df = pd.DataFrame(dict(o=a[:, 1], hi=a[:, 2], lo=a[:, 3], c=a[:, 4], v=a[:, 5]), index=h)
    return df.reindex(np.arange(h.min(), h.max() + 1))
def sanity(df):
    d = df.dropna(); return int(((d.lo > d[['o', 'c']].min(axis=1) + 1e-12) | (d.hi < d[['o', 'c']].max(axis=1) - 1e-12) | (d[['o', 'hi', 'lo', 'c']] <= 0).any(axis=1)).sum())
def work(s):
    df = frame(s)
    if df is None: return s, None, 0, None
    last = int(df.c.last_valid_index()); return s, prep(df), sanity(df), last
def exit_of(c, start, e, delisted, n):
    """Returns (index, haircut) or None (drop). Addendum A rules."""
    j = start + 1
    while j <= min(e, n - 1):
        if not np.isfinite(c[j]):
            k = j
            while k < n and not np.isfinite(c[k]): k += 1
            if k - j > 24 or k >= n:                    # gap > 24 h, or data ends, during the hold
                if k >= n and not delisted: return None
                return j - 1, True
            j = k; continue
        j += 1
    if e < n and np.isfinite(c[e]): return e, False
    if e >= n: return (n - 1, True) if delisted else None
    for k in range(e + 1, min(n, e + 25)):              # exit candle missing, data resumes within 24 h
        if np.isfinite(c[k]): return k, False
    return (e - 1, True) if delisted else None
def run25(P, mask, spec, delisted):
    c, l, idx = P['c'], P['l'], P['idx']; first = int(np.argmax(np.isfinite(c))); out = []; nxt = -1; n = len(c)
    for t in np.where(mask)[0]:
        if t < nxt or t - first < 720 or idx[t] < A1 or idx[t] >= B1: continue
        if spec['mode'] == 'limit':
            if not (P['sig'][t] > 0 and c[t] > 0): continue
            lim = c[t] * np.exp(-spec['k'] * P['sig'][t]); f = None
            for j in range(t + 1, min(n, t + 1 + spec['W'])):
                if l[j] < lim: f = j; break
            if f is None: nxt = t + spec['W']; continue
            ex = exit_of(c, f, f + 24, delisted, n)
            if ex is None: nxt = t + spec['W']; continue
            k, hc = ex; out.append((int(idx[t]), c[k] / lim - 1 - 0.0012 - (0.05 if hc else 0), hc)); nxt = k
        else:
            if not c[t] > 0: continue
            ex = exit_of(c, t, t + 24, delisted, n)
            if ex is None: continue
            k, hc = ex; out.append((int(idx[t]), c[k] / c[t] - 1 - 0.002 - (0.05 if hc else 0), hc)); nxt = k
    return out
if __name__ == '__main__':
    if not os.path.exists('/home/claude/data/e25_prep.pkl'):
        with Pool(os.cpu_count()) as p: R = p.map(work, U, chunksize=4)
        pickle.dump(R, open('/home/claude/data/e25_prep.pkl', 'wb')); print('prepped', len(R)); sys.exit(0)
    R = pickle.load(open('/home/claude/data/e25_prep.pkl', 'rb'))
    bad = sum(r[2] for r in R); total = sum(int(np.isfinite(r[1]['c']).sum()) for r in R if r[1])
    print(f'DATA CHECK (a): {bad} bad candles of {total:,}')
    if bad > total * 1e-4: print('STOP: data check failed'); sys.exit(1)
    Ps = {s: P for s, P, _, last in R if P}; last = {s: lh for s, P, _, lh in R if P}
    deli = {s: last[s] < END_H - 48 for s in Ps}
    BR = breadth_of(Ps.values()); m = 2; bar = 1.96; OUT = {}
    print(f'{len(Ps)} perpetuals ({sum(deli.values())} delisted), 2024-01-01 → 2026-10-18, net of costs; bar t ≥ {bar}')
    for hyp, spec in (('H1', dict(mode='limit', q=10, k=2, W=3, name='H1 limit k2 W3')), ('H3', dict(mode='taker', q=5, b=20, name='H3 q5 breadth≥20%'))):
        tr = []
        for s, P in Ps.items(): tr += [(h, r, hc, s, deli[s]) for h, r, hc in run25(P, masks(P, spec, BR), spec, deli[s])]
        s_ = pd.DataFrame(tr, columns=['h', 'r', 'hc', 'sym', 'del']); mean, t, n = wt(list(zip(s_.h, s_.r)))
        s_['y'] = pd.to_datetime(s_.h * 3600, unit='s').dt.year
        yrs = {int(y): round(float(g.r.mean() * 100), 3) for y, g in s_.groupby('y')}
        passed = t is not None and t >= bar and mean > 0 and all(yrs.get(y, -1) > 0 for y in (2024, 2025, 2026))
        q95 = s_.r.quantile(0.95); nt = s_[s_.r < q95]
        dl = s_[s_['del']]; soon = s_.apply(lambda x: x['del'] and last[x.sym] - x.h <= 90 * 24, axis=1)
        OUT[hyp] = dict(name=spec['name'], n=n, mean=mean, t=t, years=yrs, winners=float((s_.r > 0).mean()), median=float(s_.r.median()),
                        passed=bool(passed), haircut_trades=int(s_.hc.sum()), delisted_n=len(dl), delisted_mean=float(dl.r.mean()) if len(dl) else None,
                        share_delisted_within_90d=float(soon.mean()), without_top5=float(nt.r.mean()), worst10=[round(float(x), 4) for x in s_.r.nsmallest(10)])
        o = OUT[hyp]
        print(f"\n{hyp} {o['name']}: trades {n} | net mean {mean*100:+.3f}% (median {o['median']*100:+.2f}%) | weekly t {t:+.2f} | winners {o['winners']*100:.0f}% | by year {yrs} | {'PASS' if passed else 'FAIL'}")
        print(f"   delisted coins: {o['delisted_n']} trades, mean {o['delisted_mean']*100 if o['delisted_mean'] is not None else float('nan'):+.2f}% | haircut exits {o['haircut_trades']} | trades within 90 d of a delisting {o['share_delisted_within_90d']*100:.1f}% | without best 5%: {o['without_top5']*100:+.3f}% | worst 10 {o['worst10']}")
    json.dump(OUT, open('/home/claude/omega/plans-new/E25_result.json', 'w'), indent=1)
