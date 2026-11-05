"""Plan E21's rule library (73 rules) and trade builder, shared by the discovery scan and the test."""
import numpy as np, pandas as pd
def hourly_from(m, tsec):
    df = pd.DataFrame({'h':tsec//3600, 'o':m['o'], 'hi':m['h'], 'lo':m['l'], 'c':m['c'], 'v':m['v']}).groupby('h').agg(o=('o', 'first'), hi=('hi', 'max'), lo=('lo', 'min'), c=('c', 'last'), v=('v', 'sum'))
    return df.reindex(np.arange(df.index.min(), df.index.max() + 1))
def day_thresholds(x, lookback=720, step=24, q=(10, 90)):
    n = len(x); lo = np.full(n, np.nan); hi = np.full(n, np.nan)
    for s in range(lookback, n, step):
        w = x[s - lookback:s]; w = w[np.isfinite(w)]
        if len(w) >= lookback//2: a, b = np.percentile(w, q); lo[s:s + step] = a; hi[s:s + step] = b
    return lo, hi
def rules(df):
    c, h, l, v = df.c, df.hi, df.lo, df.v; hrs = (df.index.values % 24); wd = ((df.index.values//24) + 3) % 7      # 0 = Monday
    r1 = np.log(c/c.shift(1)); sig = r1.rolling(168, min_periods=120).std().shift(1); z = (r1/sig).values; R = {}
    for L in (1, 4, 24, 72):
        rl = np.log(c/c.shift(L)).values; q10, q90 = day_thresholds(rl)
        for H in (1, 4, 24): R[f'F1 momentum up L{L} H{H}'] = (rl >= q90, 1, H); R[f'F1 momentum down L{L} H{H}'] = (rl <= q10, -1, H)
    for N in (24, 72, 168):
        ph = h.rolling(N).max().shift(1).values; pl = l.rolling(N).min().shift(1).values
        for H in (4, 24): R[f'F2 breakout up N{N} H{H}'] = (c.values > ph, 1, H); R[f'F2 breakdown N{N} H{H}'] = (c.values < pl, -1, H)
    for N in (24, 72):
        ph = h.rolling(N).max().shift(1).values; pl = l.rolling(N).min().shift(1).values
        for H in (4, 24): R[f'F3 sweep of high, short N{N} H{H}'] = ((h.values > ph) & (c.values < ph), -1, H); R[f'F3 sweep of low, long N{N} H{H}'] = ((l.values < pl) & (c.values > pl), 1, H)
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean(); rsi = (100 - 100/(1 + up/dn)).values
    for H in (4, 24): R[f'F4 RSI<30 long H{H}'] = (rsi < 30, 1, H); R[f'F4 RSI>70 short H{H}'] = (rsi > 70, -1, H)
    for N in (50, 200):
        ma = c.rolling(N).mean(); R[f'F5 cross above MA{N} long H24'] = (((c > ma) & (c.shift(1) <= ma.shift(1))).values, 1, 24); R[f'F5 cross below MA{N} short H24'] = (((c < ma) & (c.shift(1) >= ma.shift(1))).values, -1, 24)
    med = v.rolling(168, min_periods=120).median().shift(1); spike = (v > 3*med).values
    for H in (4, 24): R[f'F6 volume spike up-hour long H{H}'] = (spike & (r1.values > 0), 1, H); R[f'F6 volume spike down-hour short H{H}'] = (spike & (r1.values < 0), -1, H)
    for H in (4, 24): R[f'F7 3σ up-hour long H{H}'] = (z >= 3, 1, H); R[f'F7 3σ down-hour short H{H}'] = (z <= -3, -1, H)
    for nm, st, H in (('Asia', 0, 8), ('London', 8, 5), ('US', 13, 8), ('Late', 21, 3)): R[f'F8 long through {nm}'] = (hrs == st, 1, H)
    rng = (h.rolling(24).max() - l.rolling(24).min())/c; quiet = (rng < 0.5*rng.rolling(720, min_periods=360).median().shift(1)).values
    lo72 = l.rolling(72).min(); hi72 = h.rolling(72).max(); pos = ((c - lo72)/(hi72 - lo72)).values
    R['F9 quiet, top of range short H24'] = (quiet & (pos >= 0.9), -1, 24); R['F9 quiet, bottom of range long H24'] = (quiet & (pos <= 0.1), 1, 24)
    for k, nm in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']): R[f'F10 long {nm} 00:00 H24'] = ((hrs == 0) & (wd == k), 1, 24)
    return R
def trades(df, mask, d, H, lo_h=None, hi_h=None, min_age=0):
    c = df.c.values; hidx = df.index.values; first = np.argmax(np.isfinite(c)); out = []; nxt = -1
    for t in np.where(np.nan_to_num(mask, nan=0).astype(bool))[0]:
        if t < nxt or t + H >= len(c) or t - first < min_age: continue
        if lo_h is not None and (hidx[t] < lo_h or hidx[t] >= hi_h): continue
        a, b = c[t], c[t + H]
        if not (a > 0 and b > 0): continue
        out.append((hidx[t], d*(b/a - 1))); nxt = t + H
    return out
def weekly_t(tr):
    if len(tr) < 10: return None, None, 0
    s = pd.DataFrame(tr, columns=['h', 'r']); s['w'] = ((s.h//24) + 3)//7; w = s.groupby('w').r.mean()
    return float(s.r.mean()), float(w.mean()/w.std()*np.sqrt(len(w))) if w.std() > 0 else None, len(s)
