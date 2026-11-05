import numpy as np, pandas as pd
from e21_lib import day_thresholds
def prep(df):
    c, h, l, v = df.c.values, df.hi.values, df.lo.values, df.v.values; r24 = np.log(df.c/df.c.shift(24)).values
    th = {q: day_thresholds(r24, q=(q, 100 - q))[0] for q in (1, 2, 5, 10)}
    sig = np.log(df.c/df.c.shift(1)).rolling(168, min_periods=120).std().shift(1).values
    v24 = df.v.rolling(24).sum(); vmed = v24.rolling(720, min_periods=360).median().shift(1); volok = (v24 > 2*vmed).values
    loc = np.where(h > l, (c - l)/np.where(h > l, h - l, 1), 0.5); return dict(c=c, h=h, l=l, r24=r24, th=th, sig=sig, volok=volok, loc=loc, idx=df.index.values)
def base(P, q): return np.nan_to_num(P['r24'] <= P['th'][q], nan=0).astype(bool) & np.isfinite(P['th'][q])
def run(P, mask, mode, lo_h, hi_h, min_age=0, k=None, W=None):
    c, h, l, idx = P['c'], P['h'], P['l'], P['idx']; first = int(np.argmax(np.isfinite(c))); out = []; nxt = -1; n = len(c)
    for t in np.where(mask)[0]:
        if t < nxt or t - first < min_age or idx[t] < lo_h or idx[t] >= hi_h: continue
        if mode == 'limit':
            if not (P['sig'][t] > 0 and c[t] > 0): continue
            lim = c[t]*np.exp(-k*P['sig'][t]); f = None
            for j in range(t + 1, min(n, t + 1 + W)):
                if l[j] < lim: f = j; break
            if f is None or f + 24 >= n or not (c[f + 24] > 0): nxt = t + W; continue
            out.append((idx[t], c[f + 24]/lim - 1 - 0.0012)); nxt = f + 24
        else:
            if t + 24 >= n or not (c[t] > 0 and c[t + 24] > 0): continue
            out.append((idx[t], c[t + 24]/c[t] - 1 - 0.002)); nxt = t + 24
    return out
def wt(tr):
    if len(tr) < 20: return None, None, len(tr)
    s = pd.DataFrame(tr, columns=['h', 'r']); w = s.groupby(((s.h//24) + 3)//7).r.mean(); return float(s.r.mean()), float(w.mean()/w.std()*np.sqrt(len(w))) if w.std() > 0 else None, len(s)
VARIANTS = [('H1', f'limit k{k} W{W}', dict(mode='limit', q=10, k=k, W=W)) for k in (0.5, 1, 2) for W in (3, 6)] + \
           [('H2', f'q{q}' + (' +volume' if vf else '') + (' +strong close' if cf else ''), dict(mode='taker', q=q, vf=vf, cf=cf)) for q in (5, 2, 1) for vf in (0, 1) for cf in (0, 1)] + \
           [('H3', f'q{q} breadth≥{b}%', dict(mode='taker', q=q, b=b)) for q in (10, 5) for b in (20, 40)]
def masks(P, spec, breadth=None):
    m = base(P, spec['q'])
    if spec.get('vf'): m &= P['volok']
    if spec.get('cf'): m &= (P['loc'] >= 0.5)
    if spec.get('b') is not None: m &= np.array([breadth.get(int(h), 0) >= spec['b']/100 for h in P['idx']])
    return m
def breadth_of(Ps):
    cnt, tot = {}, {}
    for P in Ps:
        m10 = base(P, 10); ok = np.isfinite(P['th'][10]) & np.isfinite(P['r24'])
        for h, a, b in zip(P['idx'][ok], m10[ok], ok[ok]): cnt[h] = cnt.get(h, 0) + int(a); tot[h] = tot.get(h, 0) + 1
    return {h: cnt[h]/tot[h] for h in tot if tot[h] >= 5}
