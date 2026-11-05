import numpy as np, pandas as pd, pickle
from numba import njit
H = pickle.load(open('/home/claude/edge/hourly2024.pkl','rb'))
SPLIT_H = int(np.datetime64('2025-07-01T00:00').astype('datetime64[h]').astype(int))
START_H = int(np.datetime64('2024-01-01T00:00').astype('datetime64[h]').astype(int))
def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().values
@njit(cache=True)
def supertrend_dir(h, l, c, atr, mult):
    n = len(c); up = np.zeros(n); dn = np.zeros(n); d = np.ones(n, np.int8)
    for i in range(n):
        mid = (h[i] + l[i])/2; bu = mid + mult*atr[i]; bl = mid - mult*atr[i]
        if i == 0 or np.isnan(atr[i]): up[i] = bu; dn[i] = bl; continue
        up[i] = bu if (bu < up[i-1] or c[i-1] > up[i-1]) else up[i-1]
        dn[i] = bl if (bl > dn[i-1] or c[i-1] < dn[i-1]) else dn[i-1]
        d[i] = 1 if c[i] > up[i-1] else (-1 if c[i] < dn[i-1] else d[i-1])
    return d
def features(u):
    o, h, l, c, qv = u['o'], u['h'], u['l'], u['c'], u['qv']; n = len(c)
    pc = np.r_[c[0], c[:-1]]; tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = pd.Series(tr).ewm(alpha=1/14, adjust=False).mean().values
    e20, e50, e200 = ema(c, 20), ema(c, 50), ema(c, 200)
    s = pd.Series(c); d = s.diff(); g = d.clip(lower=0).ewm(alpha=1/2, adjust=False).mean(); ls = (-d.clip(upper=0)).ewm(alpha=1/2, adjust=False).mean()
    rsi2 = (100 - 100/(1 + g/ls.replace(0, np.nan))).fillna(50).values
    m20 = s.rolling(20).mean().values; sd20 = s.rolling(20).std().values; bu, bl = m20 + 2*sd20, m20 - 2*sd20; bw = (bu - bl)/m20
    bwlow = pd.Series(bw).rolling(120).min().values
    dh20 = pd.Series(h).rolling(20).max().shift(1).values; dl20 = pd.Series(l).rolling(20).min().shift(1).values
    dh55 = pd.Series(h).rolling(55).max().shift(1).values; dl55 = pd.Series(l).rolling(55).min().shift(1).values
    hi24 = pd.Series(h).rolling(24).max().shift(1).values; lo24 = pd.Series(l).rolling(24).min().shift(1).values
    macd = ema(c, 12) - ema(c, 26); sig = ema(macd, 9)
    st = supertrend_dir(h, l, c, atr, 3.0)
    lr = np.r_[0, np.diff(np.log(c))]; sg = pd.Series(lr).rolling(168).std().shift(1).values; z = lr/sg
    medv = pd.Series(qv).rolling(168).median().shift(1).values; vol3 = qv >= 3*medv
    rng = np.where(h - l > 0, h - l, np.nan); cl = (c - l)/rng
    liq = pd.Series(qv).rolling(480, min_periods=240).sum().values/20 >= 5e6
    sh = lambda x: np.r_[x[0], x[:-1]]
    S = {}
    S['S01 Donchian 20 breakout'] = np.where(c > dh20, 1, np.where(c < dl20, -1, 0))
    S['S02 Donchian 55 breakout'] = np.where(c > dh55, 1, np.where(c < dl55, -1, 0))
    S['S03 EMA 20/50 cross'] = np.where((e20 > e50) & (sh(e20) <= sh(e50)), 1, np.where((e20 < e50) & (sh(e20) >= sh(e50)), -1, 0))
    S['S04 Trend pullback to EMA20'] = np.where((e50 > e200) & (l <= e20) & (c > e20) & (sh(c) > sh(e20)), 1, np.where((e50 < e200) & (h >= e20) & (c < e20) & (sh(c) < sh(e20)), -1, 0))
    S['S05 RSI(2) dip with trend'] = np.where((rsi2 < 10) & (c > e200), 1, np.where((rsi2 > 90) & (c < e200), -1, 0))
    S['S06 Bollinger fade'] = np.where(c < bl, 1, np.where(c > bu, -1, 0))
    S['S07 Bollinger squeeze breakout'] = np.where((sh(bw) <= sh(bwlow)*1.05) & (c > bu), 1, np.where((sh(bw) <= sh(bwlow)*1.05) & (c < bl), -1, 0))
    S['S08 Supertrend flip'] = np.where((st == 1) & (sh(st) == -1), 1, np.where((st == -1) & (sh(st) == 1), -1, 0))
    S['S09 MACD cross with trend'] = np.where((macd > sig) & (sh(macd) <= sh(sig)) & (c > e200), 1, np.where((macd < sig) & (sh(macd) >= sh(sig)) & (c < e200), -1, 0))
    S['S10 Keltner breakout'] = np.where(c > e20 + 2*atr, 1, np.where(c < e20 - 2*atr, -1, 0))
    ib = (sh(h) < sh(sh(h))) & (sh(l) > sh(sh(l)))
    S['S11 Inside bar breakout'] = np.where(ib & (c > sh(sh(h))), 1, np.where(ib & (c < sh(sh(l))), -1, 0))
    S['S12 Climax reversal (long)'] = np.where((z <= -3) & vol3 & (cl >= 0.6), 1, 0)
    S['S13 Sweep and reclaim (fade)'] = np.where(vol3 & (l < lo24) & (c > lo24), 1, np.where(vol3 & (h > hi24) & (c < hi24), -1, 0))
    S['S14 Momentum burst'] = np.where((z >= 3) & vol3 & (cl >= 0.6), 1, np.where((z <= -3) & vol3 & (cl <= 0.4), -1, 0))
    S['S15 Donchian 20 with trend'] = np.where((c > dh20) & (c > e200), 1, np.where((c < dl20) & (c < e200), -1, 0))
    valid = liq & ~np.isnan(atr) & (np.arange(n) >= 220) & (u['t'] >= START_H)
    for k in S: S[k] = np.where(valid, S[k], 0).astype(np.int8)
    return S, atr
@njit(cache=True)
def simulate(t, o, h, l, c, atr, sig, stop_atr, tgt_R, trail_atr, be_R, sc_frac, sc_R, pyr_R, pyr_max, max_bars, cost):
    n = len(c); out = np.zeros((n, 5)); k = 0; i = 0
    while i < n - 2:
        d = sig[i]
        if d == 0: i += 1; continue
        e = o[i+1]; R = stop_atr*atr[i]
        if R <= 0.001*e or e <= 0: i += 1; continue
        stop = e - d*R; units = 1.0; avg_pnl = 0.0; open_u = np.empty(8); open_e = np.empty(8); nu = 1; open_u[0] = 1.0; open_e[0] = e
        last_add = e; adds = 0; scaled = False; best = e; ncost = 0.0; j = i + 1; done = False; maxu = 1.0
        while j < n and not done:
            # 1. stop first (conservative)
            hit = (l[j] <= stop) if d == 1 else (h[j] >= stop)
            if hit:
                px = min(o[j], stop) if d == 1 else max(o[j], stop)
                for q in range(nu): avg_pnl += open_u[q]*d*(px - open_e[q])/R; ncost += open_u[q]
                done = True; break
            # 2. partial take-profit
            if sc_frac > 0 and not scaled:
                lvl = e + d*sc_R*R
                if (h[j] >= lvl) if d == 1 else (l[j] <= lvl):
                    rem = sc_frac
                    for q in range(nu):
                        take = min(open_u[q], rem); avg_pnl += take*d*(lvl - open_e[q])/R; ncost += take; open_u[q] -= take; rem -= take
                    scaled = True
            # 3. full target
            if tgt_R > 0:
                lvl = e + d*tgt_R*R
                if (h[j] >= lvl) if d == 1 else (l[j] <= lvl):
                    for q in range(nu): avg_pnl += open_u[q]*d*(lvl - open_e[q])/R; ncost += open_u[q]
                    done = True; break
            # 4. pyramid: add a unit each time price moves pyr_R*R beyond the last add
            if pyr_R > 0 and adds < pyr_max:
                lvl = last_add + d*pyr_R*R
                if (h[j] >= lvl) if d == 1 else (l[j] <= lvl):
                    open_u[nu] = 1.0; open_e[nu] = lvl; nu += 1; adds += 1; last_add = lvl; ncost += 1.0
                    ns = lvl - d*R
                    if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
            tot = 0.0
            for q in range(nu): tot += open_u[q]
            if tot > maxu: maxu = tot
            # 5. stop updates for the next bar: breakeven, trailing
            best = max(best, h[j]) if d == 1 else min(best, l[j])
            if be_R > 0 and d*(best - e) >= be_R*R:
                if (d == 1 and e > stop) or (d == -1 and e < stop): stop = e
            if trail_atr > 0:
                ns = best - d*trail_atr*atr[i]
                if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
            if j - i >= max_bars:
                for q in range(nu): avg_pnl += open_u[q]*d*(c[j] - open_e[q])/R; ncost += open_u[q]
                done = True; break
            j += 1
        if not done: break
        cR = cost*e/R                                  # cost per unit per side, in R
        out[k, 0] = t[i]; out[k, 1] = avg_pnl - cR*(ncost + 1.0); out[k, 2] = maxu; out[k, 3] = j - i; out[k, 4] = t[j]
        k += 1; i = j
    return out[:k]
FEAT = {}
def feats():
    if not FEAT:
        for s, u in H.items(): FEAT[s] = features(u)
    return FEAT
def run(strategy, stop_atr=2.0, tgt_R=2.0, trail_atr=0.0, be_R=0.0, sc_frac=0.0, sc_R=1.0, pyr_R=0.0, pyr_max=0, max_bars=72, cost=0.001, data=None):
    F = feats() if data is None else data; rows = []
    for s, u in (H.items() if data is None else data['_H'].items()):
        S, atr = F[s]
        r = simulate(u['t'], u['o'], u['h'], u['l'], u['c'], atr, S[strategy], stop_atr, tgt_R, trail_atr, be_R, sc_frac, sc_R, pyr_R, pyr_max, max_bars, cost)
        if len(r): rows.append(r)
    return np.vstack(rows) if rows else np.zeros((0, 5))
def summ(T):
    if len(T) == 0: return dict(n=0)
    a, b = T[T[:,0] < SPLIT_H], T[T[:,0] >= SPLIT_H]
    f = lambda x: (len(x), x[:,1].mean() if len(x) else np.nan, x[:,1].std()/np.sqrt(len(x)) if len(x) > 1 else np.nan, np.mean(x[:,1] > 0) if len(x) else np.nan)
    return dict(first=f(a), second=f(b))
