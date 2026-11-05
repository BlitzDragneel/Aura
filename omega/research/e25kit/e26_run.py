"""E26 — run ONCE per PLAN_E26 + addendum A. H1 signals from reference_e22 (verbatim e22_lib), E25 exit rules, −10% stop."""
import pickle, json, numpy as np, pandas as pd, datetime as dt, hashlib, sys
import reference_e22 as R
HH = lambda s: int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp() // 3600)
A1, B1, H_END, CUT = HH('2021-01-01'), HH('2026-10-18'), HH('2026-10-19'), HH('2026-10-11')
RAW = pickle.load(open('hourly_e26.pkl', 'rb')); COST = 0.0015; STOP = 0.10; SLIP = 0.001
SIG, COIN = [], {}          # signals; per-coin arrays for random trades
def exits(c, l, o, start, entry, last_i, delisted, n):
    """walk start+1..start+24: stop first; then delisting; then the close at start+24 (or the first close after a gap)."""
    x = start + 24; stp = entry*(1 - STOP); lim_x = min(x, last_i) if delisted else min(x, n - 1)
    for j in range(start + 1, lim_x + 1):
        if np.isfinite(l[j]) and l[j] <= stp: px = min(stp, o[j]) if o[j] > 0 else stp; return px*(1 - SLIP), j, 'stop'
    if delisted and x > last_i: return c[last_i]*0.95, last_i, 'delisted'
    if x >= n: return None
    if np.isfinite(c[x]) and c[x] > 0: return c[x], x, 'normal'
    for j in range(x + 1, n):
        if np.isfinite(c[j]) and c[j] > 0: return c[j], j, 'after_gap'
    return None
for k_, (s, x) in enumerate(RAW.items()):
    ok = x['v'] > 0
    if not ok.any(): continue
    last = int(x['h'][ok][-1])
    if last < A1: continue
    idx = np.arange(int(x['h'][0]), H_END); n = len(idx)
    df = pd.DataFrame(index=idx, columns=['o', 'c', 'hi', 'lo', 'v'], dtype=float)
    df.loc[x['h'][ok], ['o', 'c', 'hi', 'lo', 'v']] = np.c_[x['o'][ok], x['c'][ok], x['hi'][ok], x['lo'][ok], x['v'][ok]]
    P = R.prep(df); c, l, o = P['c'], P['l'], df.o.values; first = int(np.argmax(np.isfinite(c))); last_i = last - idx[0]; delisted = last < CUT
    nxt = -1
    for t in np.where(R.base(P, 10))[0]:
        if t < nxt or t - first < 720 or idx[t] < A1 or idx[t] >= B1 or not (P['sig'][t] > 0 and c[t] > 0): continue
        lim = c[t]*np.exp(-2*P['sig'][t]); f = None
        for j in range(t + 1, min(n, t + 4)):
            if l[j] < lim: f = j; break
        if f is None: SIG.append((int(idx[t]), s, float(P['r24'][t]), None, int(idx[t]) + 3, 0.0, 'unfilled')); nxt = t + 3; continue
        r = exits(c, l, o, f, lim, last_i, delisted, n)
        if r is None: nxt = t + 3; continue
        px, xe, kind = r; SIG.append((int(idx[t]), s, float(P['r24'][t]), int(idx[f]), int(idx[xe]), float(px/lim - 1 - COST), kind)); nxt = f + 24
    # random-trade results for every hour: entry at the close of h (real candle, age ≥ 720), same exit rules
    rr = np.full(n, np.nan, np.float32); xh = np.full(n, -1, np.int32)
    for h in np.where(np.isfinite(c))[0]:
        if h - first < 720 or idx[h] < A1 - 24 or idx[h] >= H_END: continue
        r = exits(c, l, o, h, c[h], last_i, delisted, n)
        if r is not None: rr[h] = r[0]/c[h] - 1 - COST; xh[h] = idx[r[1]]
    COIN[s] = (int(idx[0]), rr, xh)
    if k_ % 100 == 0: print(k_, s, len(SIG), flush=True)
pickle.dump(dict(SIG=SIG, COIN=COIN), open('e26_tables.pkl', 'wb')); print('signals', len(SIG), 'filled', sum(1 for x in SIG if x[3] is not None), flush=True)
