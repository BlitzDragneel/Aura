import sys; sys.path.insert(0,'/home/claude/edge')
from load import *
import pickle
def candidates():
    out = []; hourly = {}
    for part in ['final4_a','final4_b','final4_c','final4_d','final4_young']:
        d, ms = load(part)
        for m in ms:
            t = m['t']; o, h, l, c, v = m['o'], m['h'], m['l'], m['c'], m['v']; n = len(t)
            if n < 24*30 + 200: continue
            lr = np.zeros(n); lr[1:] = np.log(c[1:]/c[:-1])
            # sigma and median volume of the 168 hours BEFORE each hour
            sig = np.full(n, np.nan); medv = np.full(n, np.nan)
            from numpy.lib.stride_tricks import sliding_window_view as sw
            W = sw(lr[1:], 168).std(axis=1, ddof=1); sig[169:] = W[:n-169]
            V = np.median(sw(v, 168), axis=1); medv[168:] = V[:n-168]
            rng = h - l; cl = np.where(rng > 0, (c - l)/np.where(rng > 0, rng, 1), 0.5)
            z = lr/sig
            idx = np.where((z <= -3) & (v >= 3*medv) & (cl >= 0.6) & (np.arange(n) >= 24*30) & (np.arange(n) + 13 < n))[0]
            ft = m['ft']*60; fr = m['fr']
            for i in idx:
                e = o[i+1]; x = c[i+12]                       # in at the next open, out 12 hours later
                ts, te = (t[i+1])*3600, (t[i+12]+1)*3600
                fund = fr[(ft >= ts) & (ft < te)].sum()
                mae = l[i+1:i+13].min()/e - 1; mfe = h[i+1:i+13].max()/e - 1
                out.append((int(t[i]), m['sym'], float(z[i]), float(x/e - 1), float(fund), float(mae), float(mfe)))
            hourly[m['sym']] = None
    return out
if __name__ == '__main__':
    cand = candidates(); pickle.dump(cand, open('climax_cand.pkl','wb'))
    print('raw signals', len(cand))
