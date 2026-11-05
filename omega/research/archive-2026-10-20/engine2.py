import numpy as np, pandas as pd, pickle
from numba import njit
H = pickle.load(open('/home/claude/edge/hourly2024f.pkl','rb')); MK = pickle.load(open('/home/claude/edge/market.pkl','rb'))
SPLIT_H = int(np.datetime64('2025-07-01T00:00').astype('datetime64[h]').astype(int)); START_H = int(np.datetime64('2024-01-01T00:00').astype('datetime64[h]').astype(int))
def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().values
def roll(x, n, f): return getattr(pd.Series(x).rolling(n), f)().values
@njit(cache=True)
def st_dir(h, l, c, atr, mult):
    n = len(c); up = np.zeros(n); dn = np.zeros(n); d = np.ones(n, np.int8)
    for i in range(n):
        mid = (h[i] + l[i])/2; bu = mid + mult*atr[i]; bl = mid - mult*atr[i]
        if i == 0 or np.isnan(atr[i]): up[i] = bu; dn[i] = bl; continue
        up[i] = bu if (bu < up[i-1] or c[i-1] > up[i-1]) else up[i-1]
        dn[i] = bl if (bl > dn[i-1] or c[i-1] < dn[i-1]) else dn[i-1]
        d[i] = 1 if c[i] > up[i-1] else (-1 if c[i] < dn[i-1] else d[i-1])
    return d
mlr = MK['lr']; midx = MK['idx']; mema = ema(midx, 480); mtrend_all = np.where(midx > mema, 1, -1)
msig = pd.Series(mlr).rolling(168).std().shift(1).values; mz_all = mlr/msig
def base(u):
    o, h, l, c, qv = u['o'], u['h'], u['l'], u['c'], u['qv']; n = len(c); sh = lambda x: np.r_[x[0], x[:-1]]
    pc = sh(c); tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc))); atr = pd.Series(tr).ewm(alpha=1/14, adjust=False).mean().values
    s = pd.Series(c); d = s.diff()
    def rsi(k):
        g = d.clip(lower=0).ewm(alpha=1/k, adjust=False).mean(); ls = (-d.clip(upper=0)).ewm(alpha=1/k, adjust=False).mean()
        return (100 - 100/(1 + g/ls.replace(0, np.nan))).fillna(50).values
    F = dict(o=o, h=h, l=l, c=c, t=u['t'], fund=u['fund'], atr=atr, e20=ema(c,20), e50=ema(c,50), e200=ema(c,200), e800=ema(c,800), rsi2=rsi(2), rsi14=rsi(14))
    m20 = roll(c,20,'mean'); sd20 = roll(c,20,'std'); F['bu'], F['bl'] = m20 + 2*sd20, m20 - 2*sd20; F['bw'] = 4*sd20/m20; F['bwlow'] = roll(F['bw'],120,'min')
    for k in (10, 20, 55): F[f'dh{k}'] = np.r_[np.nan, roll(h,k,'max')[:-1]]; F[f'dl{k}'] = np.r_[np.nan, roll(l,k,'min')[:-1]]
    for k in (24, 72): F[f'hi{k}'] = np.r_[np.nan, roll(h,k,'max')[:-1]]; F[f'lo{k}'] = np.r_[np.nan, roll(l,k,'min')[:-1]]
    macd = ema(c,12) - ema(c,26); F['macd'], F['msig'] = macd, ema(macd, 9); F['st'] = st_dir(h, l, c, atr, 3.0)
    lr = np.r_[0, np.diff(np.log(c))]; sg = np.r_[np.nan, roll(lr,168,'std')[:-1]]; F['z'] = lr/sg
    medv = np.r_[np.nan, roll(qv,168,'median')[:-1]]; F['vr'] = qv/medv
    rng = np.where(h - l > 0, h - l, np.nan); F['cl'] = (c - l)/rng
    F['liq'] = np.r_[np.zeros(479), np.convolve(qv, np.ones(480), 'valid')]/20 >= 5e6
    mi = np.clip(np.searchsorted(MK['t'], u['t']), 0, len(MK['t'])-1); F['mtrend'] = mtrend_all[mi]; F['mz'] = mz_all[mi]; F['mi'] = mi
    F['hour'] = (u['t'] % 24).astype(np.int64)
    F['atrpct'] = pd.Series(atr/c).rolling(720, min_periods=240).rank(pct=True).values
    r24 = np.r_[np.zeros(24), np.log(c[24:]/c[:-24])]; m24 = np.r_[np.zeros(24), np.log(midx[mi][24:]/midx[mi][:-24])]
    ex = r24 - m24; F['exz'] = ex/np.r_[np.nan, roll(ex,720,'std')[:-1]]; F['r24'] = r24; F['m24'] = m24
    F['f24'] = np.r_[np.zeros(23), np.convolve(u['fund'], np.ones(24), 'valid')]
    F['age'] = np.arange(n); F['sh'] = sh
    return F
def signal(name, F):
    c, h, l, sh = F['c'], F['h'], F['l'], F['sh']; Z = np.zeros(len(c), np.int8)
    w = lambda up, dn: np.where(up, 1, np.where(dn, -1, 0))
    if name == 'donch20': x = w(c > F['dh20'], c < F['dl20'])
    elif name == 'donch55': x = w(c > F['dh55'], c < F['dl55'])
    elif name == 'donch10': x = w(c > F['dh10'], c < F['dl10'])
    elif name == 'ema20_50': e, f = F['e20'], F['e50']; x = w((e > f) & (sh(e) <= sh(f)), (e < f) & (sh(e) >= sh(f)))
    elif name == 'ema50_200': e, f = F['e50'], F['e200']; x = w((e > f) & (sh(e) <= sh(f)), (e < f) & (sh(e) >= sh(f)))
    elif name == 'rsi2_trend': x = w((F['rsi2'] < 10) & (c > F['e200']), (F['rsi2'] > 90) & (c < F['e200']))
    elif name == 'rsi14_rev': r = F['rsi14']; x = w((r < 30) & (sh(r) >= 30), (r > 70) & (sh(r) <= 70))
    elif name == 'bb_fade': x = w(c < F['bl'], c > F['bu'])
    elif name == 'bb_squeeze': q = sh(F['bw']) <= sh(F['bwlow'])*1.05; x = w(q & (c > F['bu']), q & (c < F['bl']))
    elif name == 'keltner': x = w(c > F['e20'] + 2*F['atr'], c < F['e20'] - 2*F['atr'])
    elif name == 'supertrend': s = F['st']; x = w((s == 1) & (sh(s) == -1), (s == -1) & (sh(s) == 1))
    elif name == 'macd_trend': m, g = F['macd'], F['msig']; x = w((m > g) & (sh(m) <= sh(g)) & (c > F['e200']), (m < g) & (sh(m) >= sh(g)) & (c < F['e200']))
    elif name == 'insidebar': ib = (sh(h) < sh(sh(h))) & (sh(l) > sh(sh(l))); x = w(ib & (c > sh(sh(h))), ib & (c < sh(sh(l))))
    elif name == 'burst3': x = w((F['z'] >= 3) & (F['vr'] >= 3) & (F['cl'] >= 0.6), (F['z'] <= -3) & (F['vr'] >= 3) & (F['cl'] <= 0.4))
    elif name == 'burst2': x = w((F['z'] >= 2) & (F['vr'] >= 2) & (F['cl'] >= 0.6), (F['z'] <= -2) & (F['vr'] >= 2) & (F['cl'] <= 0.4))
    elif name == 'climax': x = w((F['z'] <= -3) & (F['vr'] >= 3) & (F['cl'] >= 0.6), np.zeros(len(c), bool))
    elif name == 'blowoff': x = w(np.zeros(len(c), bool), (F['z'] >= 3) & (F['vr'] >= 3) & (F['cl'] <= 0.4))
    elif name == 'sweep_fade': v = F['vr'] >= 3; x = w(v & (l < F['lo24']) & (c > F['lo24']), v & (h > F['hi24']) & (c < F['hi24']))
    elif name == 'break72_hold': v = F['vr'] >= 2; x = w(v & (c > F['hi72']), v & (c < F['lo72']))
    elif name == 'rel_strength': e = F['exz']; x = w((e >= 2) & (sh(e) < 2), (e <= -2) & (sh(e) > -2))
    elif name == 'funding_fade': f = F['f24']; x = w((f < -0.0015) & (sh(f) >= -0.0015), (f > 0.0015) & (sh(f) <= 0.0015))
    elif name == 'mkt_flush_long': x = w((F['mz'] <= -3) & (F['cl'] >= 0.5), np.zeros(len(c), bool))
    else: raise ValueError(name)
    return x
FILTERS = ['none', 'mkt_trend', 'htf_trend', 'us_hours', 'high_vol', 'low_vol']
def apply_filter(x, flt, F):
    if flt == 'none': return x
    if flt == 'mkt_trend': return np.where(x == F['mtrend'], x, 0)
    if flt == 'htf_trend': d = np.where(F['c'] > F['e800'], 1, -1); return np.where(x == d, x, 0)
    if flt == 'us_hours': return np.where((F['hour'] >= 13) & (F['hour'] <= 20), x, 0)
    if flt == 'high_vol': return np.where(F['atrpct'] >= 0.5, x, 0)
    if flt == 'low_vol': return np.where(F['atrpct'] < 0.5, x, 0)
@njit(cache=True)
def simulate(t, o, h, l, c, fund, atr, sig, stop_atr, tgt_R, trail_atr, be_R, sc_frac, sc_R, pyr_R, pyr_max, max_bars, cost):
    n = len(c); out = np.zeros((n, 6)); k = 0; i = 0
    while i < n - 2:
        d = sig[i]
        if d == 0: i += 1; continue
        e = o[i+1]; R = stop_atr*atr[i]
        if R <= 0.001*e or e <= 0: i += 1; continue
        stop = e - d*R; pnl = 0.0; ou = np.zeros(8); oe = np.zeros(8); nu = 1; ou[0] = 1.0; oe[0] = e
        last_add = e; adds = 0; scaled = False; best = e; ncost = 0.0; j = i + 1; done = False; fpaid = 0.0
        while j < n:
            hit = (l[j] <= stop) if d == 1 else (h[j] >= stop)
            if hit:
                px = min(o[j], stop) if d == 1 else max(o[j], stop)
                for q in range(nu): pnl += ou[q]*d*(px - oe[q])/R; ncost += ou[q]
                done = True; break
            if sc_frac > 0 and not scaled:
                lv = e + d*sc_R*R
                if (h[j] >= lv) if d == 1 else (l[j] <= lv):
                    rem = sc_frac
                    for q in range(nu):
                        tk = min(ou[q], rem); pnl += tk*d*(lv - oe[q])/R; ncost += tk; ou[q] -= tk; rem -= tk
                    scaled = True
            if tgt_R > 0:
                lv = e + d*tgt_R*R
                if (h[j] >= lv) if d == 1 else (l[j] <= lv):
                    for q in range(nu): pnl += ou[q]*d*(lv - oe[q])/R; ncost += ou[q]
                    done = True; break
            if pyr_R > 0 and adds < pyr_max:
                lv = last_add + d*pyr_R*R
                if (h[j] >= lv) if d == 1 else (l[j] <= lv):
                    ou[nu] = 1.0; oe[nu] = lv; nu += 1; adds += 1; last_add = lv; ncost += 1.0
                    ns = lv - d*R
                    if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
            tot = 0.0
            for q in range(nu): tot += ou[q]
            fp = d*fund[j]*c[j]/R*tot; pnl -= fp; fpaid += fp            # longs pay positive funding, shorts receive it
            best = max(best, h[j]) if d == 1 else min(best, l[j])
            if be_R > 0 and d*(best - e) >= be_R*R:
                if (d == 1 and e > stop) or (d == -1 and e < stop): stop = e
            if trail_atr > 0:
                ns = best - d*trail_atr*atr[i]
                if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
            if j - i >= max_bars:
                for q in range(nu): pnl += ou[q]*d*(c[j] - oe[q])/R; ncost += ou[q]
                done = True; break
            j += 1
        if not done: break
        out[k, 0] = t[i]; out[k, 1] = pnl - cost*e/R*(ncost + 1.0); out[k, 2] = d; out[k, 3] = i; out[k, 4] = j; out[k, 5] = R/e
        k += 1; i = j
    return out[:k]
MGMT = {'T2': dict(stop_atr=2.0, tgt_R=2.0, max_bars=72), 'T5': dict(stop_atr=2.0, tgt_R=5.0, max_bars=168), 'TR': dict(stop_atr=2.0, trail_atr=3.0, max_bars=168),
        'PY': dict(stop_atr=2.0, trail_atr=3.0, pyr_R=1.0, pyr_max=3, max_bars=168), 'YM': dict(stop_atr=2.0, trail_atr=3.0, pyr_R=1.0, pyr_max=3, sc_frac=0.6, sc_R=1.0, max_bars=168),
        'T1': dict(stop_atr=1.0, tgt_R=1.0, max_bars=24)}
FB = {}
def bases():
    if not FB:
        for s, u in H.items(): FB[s] = base(u)
    return FB
def run(entry, flt='none', mg='T2', keep=False):
    kw = dict(stop_atr=2.0, tgt_R=0.0, trail_atr=0.0, be_R=0.0, sc_frac=0.0, sc_R=1.0, pyr_R=0.0, pyr_max=0, max_bars=72, cost=0.001); kw.update(MGMT[mg]); rows = []; syms = []
    for s, F in bases().items():
        x = apply_filter(signal(entry, F), flt, F); x = np.where(F['liq'] & ~np.isnan(F['atr']) & (F['age'] >= 820) & (F['t'] >= START_H), x, 0).astype(np.int8)
        if not x.any(): continue
        r = simulate(F['t'], F['o'], F['h'], F['l'], F['c'], F['fund'], F['atr'], x, kw['stop_atr'], kw['tgt_R'], kw['trail_atr'], kw['be_R'], kw['sc_frac'], kw['sc_R'], kw['pyr_R'], kw['pyr_max'], kw['max_bars'], kw['cost'])
        if len(r): rows.append(r); syms += [s]*len(r)
    T = np.vstack(rows) if rows else np.zeros((0, 6))
    return (T, syms) if keep else T
def stat(T):
    out = {}
    for lab, sel in [('a', T[:,0] < SPLIT_H), ('b', T[:,0] >= SPLIT_H)]:
        x = T[sel][:,1]; out[lab] = (int(len(x)), float(x.mean()) if len(x) else 0.0, float(x.std()/np.sqrt(len(x))) if len(x) > 1 else 9.0)
    return out
