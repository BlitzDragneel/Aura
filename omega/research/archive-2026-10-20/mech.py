import sys; sys.path.insert(0,'/home/claude/edge')
from load import *
from numpy.lib.stride_tricks import sliding_window_view as sw
COST = 0.002
res = {k: [] for k in ['flush_absorbed','flush_closed_low','sweep_low_reclaimed','break_low_held','sweep_high_rejected','break_high_held']}
for part in ['final4_a','final4_b','final4_c','final4_d','final4_young']:
    d, ms = load(part)
    for m in ms:
        o, h, l, c, v = m['o'], m['h'], m['l'], m['c'], m['v']; n = len(c)
        if n < 24*30 + 200: continue
        lr = np.zeros(n); lr[1:] = np.log(c[1:]/c[:-1])
        sig = np.full(n, np.nan); sig[169:] = sw(lr[1:], 168).std(axis=1, ddof=1)[:n-169]
        medv = np.full(n, np.nan); medv[168:] = np.median(sw(v, 168), axis=1)[:n-168]
        rng = np.where(h - l > 0, h - l, np.nan); cl = (c - l)/rng; z = lr/sig
        hi24 = np.full(n, np.nan); lo24 = np.full(n, np.nan)
        hi24[24:] = sw(h, 24).max(axis=1)[:n-24]; lo24[24:] = sw(l, 24).min(axis=1)[:n-24]   # previous 24 hours, excluding this one
        ok = (np.arange(n) >= 24*30) & (np.arange(n) + 25 < n); big = v >= 3*medv
        def fwd(i, hold): return c[i+hold]/o[i+1] - 1
        for i in np.where(ok & big & (z <= -3) & (cl >= 0.6))[0]: res['flush_absorbed'].append(fwd(i, 12) - COST)
        for i in np.where(ok & big & (z <= -3) & (cl <= 0.2))[0]: res['flush_closed_low'].append(fwd(i, 12) - COST)
        for i in np.where(ok & big & (l < lo24) & (c > lo24))[0]: res['sweep_low_reclaimed'].append(fwd(i, 24) - COST)          # stop-run below the 24h low, closed back above: long
        for i in np.where(ok & big & (c < lo24))[0]: res['break_low_held'].append(-(fwd(i, 24)) - COST)                        # closed below: short the breakdown
        for i in np.where(ok & big & (h > hi24) & (c < hi24))[0]: res['sweep_high_rejected'].append(-(fwd(i, 24)) - COST)      # stop-run above the 24h high, closed back below: short
        for i in np.where(ok & big & (c > hi24))[0]: res['break_high_held'].append(fwd(i, 24) - COST)                          # closed above: long the breakout
lab = {'flush_absorbed':'Flush 3σ down, heavy volume, closed in top 40% (buyers absorbed) -> long 12h',
       'flush_closed_low':'Flush 3σ down, heavy volume, closed in bottom 20% (no buyers yet) -> long 12h',
       'sweep_low_reclaimed':'Swept the 24h low on heavy volume, closed back above -> long 24h',
       'break_low_held':'Broke the 24h low on heavy volume, closed below -> short 24h',
       'sweep_high_rejected':'Swept the 24h high on heavy volume, closed back below (fakeout) -> short 24h',
       'break_high_held':'Broke the 24h high on heavy volume, closed above -> long 24h'}
print('324 perpetuals, hourly; after 0.10% a side (funding not counted). Descriptive only: this history is already used.')
for k, x in res.items():
    x = np.array(x); print(f"{lab[k]:82s} n={len(x):6d} mean {x.mean()*100:+5.2f}% median {np.median(x)*100:+5.2f}% wins {np.mean(x>0)*100:3.0f}%")
