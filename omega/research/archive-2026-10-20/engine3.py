"""Trade-management search: every signal managed by a parameterised method; one-market-at-a-time account from the outcomes."""
import numpy as np, pandas as pd, pickle
from numba import njit
import engine2 as E
# P (params) layout
KEYS = ['entry_mode','retest_off','retest_wait','stop_k','init','add_mode','add_size','add_max','add_R','sc1_frac','sc1_R','sc2_frac','sc2_R',
        'tgt_R','trail_mode','trail_k','trail_min','ema_exit','noprog_bars','noprog_R','max_bars','be_R','be_to','lock1_R','lock1_to','lock2_R','lock2_to','fee']
def P(**kw):
    d = dict(entry_mode=0, retest_off=0.5, retest_wait=6, stop_k=2.0, init=1.0, add_mode=0, add_size=1.0, add_max=0, add_R=1.0, sc1_frac=0.0, sc1_R=1.0, sc2_frac=0.0, sc2_R=2.0,
             tgt_R=0.0, trail_mode=0, trail_k=3.0, trail_min=1.5, ema_exit=0, noprog_bars=0, noprog_R=0.5, max_bars=168, be_R=0.0, be_to=0.0, lock1_R=0.0, lock1_to=0.0, lock2_R=0.0, lock2_to=0.0, fee=0.001)
    d.update(kw); return np.array([float(d[k]) for k in KEYS])
@njit(cache=True)
def sim_all(o, h, l, c, ema, fund, sig_i, sig_end, sig_d, sig_atr, p):
    em, roff, rwait, sk, init, amode, asz, amax, aR, s1f, s1R, s2f, s2R, tgt, tmode, tk, tmin, emax, npb, npR, mxb, beR, beto, l1R, l1to, l2R, l2to, fee = p
    n = len(sig_i); R = np.full(n, np.nan); xi = np.full(n, -1); ei = np.full(n, -1)
    for k in range(n):
        i = sig_i[k]; end = sig_end[k]; d = sig_d[k]; a = sig_atr[k]
        if i + 1 > end: continue
        # entry
        j0 = -1; e = 0.0
        if em == 0: j0 = i + 1; e = o[j0]
        else:
            L = c[i] - d*roff*a
            for j in range(i + 1, min(i + 1 + int(rwait), end + 1)):
                if (d == 1 and l[j] <= L) or (d == -1 and h[j] >= L):
                    j0 = j; e = min(o[j], L) if d == 1 else max(o[j], L); break
        if j0 < 0 or e <= 0: continue
        Rd = sk*a
        if Rd <= 0.001*e: continue
        q = np.zeros(8); pe = np.zeros(8); nl = 1; q[0] = init; pe[0] = e
        pnl = 0.0; cost = init*fee*e/Rd; stop = e - d*Rd; best = e; last = e; adds = 0; s1 = False; s2 = False; done = False; j = j0; mfeR = 0.0
        while j <= end:
            # a pullback add fills before the stop is tested on the same bar (conservative)
            if amode == 2 and adds < amax:
                lv = e - d*0.5*Rd
                if (d == 1 and l[j] <= lv) or (d == -1 and h[j] >= lv):
                    px = min(o[j], lv) if d == 1 else max(o[j], lv)
                    q[nl] = asz; pe[nl] = px; nl += 1; adds += 1; cost += asz*fee*px/Rd
            if (d == 1 and l[j] <= stop) or (d == -1 and h[j] >= stop):
                px = (min(o[j], stop) if d == 1 else max(o[j], stop)) if j > j0 else stop
                for u in range(nl): pnl += q[u]*d*(px - pe[u])/Rd; cost += q[u]*fee*px/Rd
                done = True; break
            if s1f > 0 and not s1:
                lv = e + d*s1R*Rd
                if (d == 1 and h[j] >= lv) or (d == -1 and l[j] <= lv):
                    tot = 0.0
                    for u in range(nl): tot += q[u]
                    rem = s1f*tot
                    for u in range(nl):
                        tk2 = min(q[u], rem); pnl += tk2*d*(lv - pe[u])/Rd; cost += tk2*fee*lv/Rd; q[u] -= tk2; rem -= tk2
                    s1 = True
            if s2f > 0 and not s2:
                lv = e + d*s2R*Rd
                if (d == 1 and h[j] >= lv) or (d == -1 and l[j] <= lv):
                    tot = 0.0
                    for u in range(nl): tot += q[u]
                    rem = s2f*tot
                    for u in range(nl):
                        tk2 = min(q[u], rem); pnl += tk2*d*(lv - pe[u])/Rd; cost += tk2*fee*lv/Rd; q[u] -= tk2; rem -= tk2
                    s2 = True
            if tgt > 0:
                lv = e + d*tgt*Rd
                if (d == 1 and h[j] >= lv) or (d == -1 and l[j] <= lv):
                    for u in range(nl): pnl += q[u]*d*(lv - pe[u])/Rd; cost += q[u]*fee*lv/Rd
                    done = True; break
            if amode == 1 and adds < amax:
                lv = last + d*aR*Rd
                if (d == 1 and h[j] >= lv) or (d == -1 and l[j] <= lv):
                    q[nl] = asz; pe[nl] = lv; nl += 1; adds += 1; last = lv; cost += asz*fee*lv/Rd
                    ns = lv - d*Rd
                    if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
            tot = 0.0
            for u in range(nl): tot += q[u]
            pnl -= d*fund[j]*c[j]/Rd*tot
            best = max(best, h[j]) if d == 1 else min(best, l[j]); mfeR = d*(best - e)/Rd
            if beR > 0 and mfeR >= beR:
                ns = e + d*beto*Rd
                if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
            if l1R > 0 and mfeR >= l1R:
                ns = e + d*l1to*Rd
                if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
            if l2R > 0 and mfeR >= l2R:
                ns = e + d*l2to*Rd
                if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
            if tmode > 0:
                dist = tk if tmode == 1 else max(tmin, tk - 0.5*mfeR)
                ns = best - d*dist*a
                if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
            exit_now = False
            if emax > 0 and j > j0 and ((d == 1 and c[j] < ema[j]) or (d == -1 and c[j] > ema[j])): exit_now = True
            if npb > 0 and j - j0 + 1 == int(npb) and mfeR < npR: exit_now = True
            if j - i >= mxb: exit_now = True
            if exit_now:
                for u in range(nl): pnl += q[u]*d*(c[j] - pe[u])/Rd; cost += q[u]*fee*c[j]/Rd
                done = True; break
            j += 1
        if not done: continue
        R[k] = pnl - cost; xi[k] = j; ei[k] = j0
    return R, xi, ei
@njit(cache=True)
def account(hr, pr_order, xh, R, valid, t_from, t_to, risk, week):
    eq = 100.0; peak = 100.0; dd = 0.0; free = t_from; n = 0; wk_eq = np.full(4000, np.nan)
    for q in range(len(pr_order)):
        k = pr_order[q]; t = hr[k]
        if t < t_from or t < free: continue
        if t >= t_to or eq < 1.0: break
        if not valid[k]: continue
        eq = max(eq*(1.0 + risk*R[k]), 0.0); free = xh[k]; n += 1
        peak = max(peak, eq); dd = max(dd, 1.0 - eq/peak)
        w = int((xh[k] - t_from)//168)
        if 0 <= w < 4000: wk_eq[w] = eq
    return eq, dd, n, wk_eq
class Bars:
    """every series' hourly bars on one long array (built once per process)"""
    def __init__(self, FB=None):
        FB = FB or E.bases(); self.FB = FB; O, Hh, Lw, C, EM, FU, T = [], [], [], [], [], [], []; self.off = {}; off = 0
        for s, F in FB.items():
            n = len(F['c']); self.off[s] = (off, n); O.append(F['o']); Hh.append(F['h']); Lw.append(F['l']); C.append(F['c']); EM.append(F['e20']); FU.append(F['fund']); T.append(F['t']); off += n
        cat = lambda a, t=float: np.concatenate(a).astype(t)
        self.o, self.h, self.l, self.c, self.ema, self.fund, self.t = cat(O), cat(Hh), cat(Lw), cat(C), cat(EM), cat(FU), cat(T, np.int64)
class Book:
    """all signals of one entry + filter on the shared bars"""
    def __init__(self, entry, flt, bars):
        self.b = bars; si, se, sd, sa, sp, sh = [], [], [], [], [], []
        for s, F in bars.FB.items():
            off, n = bars.off[s]
            x = E.apply_filter(E.signal(entry, F), flt, F); x = np.where(F['liq'] & ~np.isnan(F['atr']) & (F['age'] >= 820) & (F['t'] >= E.START_H), x, 0)
            idx = np.where(x != 0)[0]; idx = idx[idx + 2 < n]
            pr = F['vr'][idx] if entry == 'break72_hold' else (-F['z'][idx] if entry == 'climax' else np.abs(F['z'][idx]))
            si.append(idx + off); se.append(np.full(len(idx), off + n - 1)); sd.append(x[idx].astype(np.int64)); sa.append(F['atr'][idx]); sp.append(np.nan_to_num(pr, nan=0.0)); sh.append(F['t'][idx])
        cat = lambda a, t=float: np.concatenate(a).astype(t) if a else np.zeros(0, t)
        self.i, self.end, self.d, self.atr, self.pr, self.hr = cat(si, np.int64), cat(se, np.int64), cat(sd, np.int64), cat(sa), cat(sp), cat(sh, np.int64)
        self.rp = self.atr/np.maximum(self.b.c[self.i], 1e-12)                       # ATR as a share of price at the signal
        self.order = np.lexsort((-self.pr, self.hr)).astype(np.int64)
    def run(self, p, flip=None, bars=None):
        b = bars or self.b; d = self.d if flip is None else self.d*flip
        R, xi, ei = sim_all(b.o, b.h, b.l, b.c, b.ema, b.fund, self.i, self.end, d, self.atr, p)
        valid = ~np.isnan(R); xh = np.where(xi >= 0, b.t[np.maximum(xi, 0)], 0)
        return R, xh, valid
    def acct(self, R, xh, valid, t_from, t_to, risk=0.01, mult=None):
        r = np.nan_to_num(R) if mult is None else np.nan_to_num(R)*mult
        return account(self.hr, self.order, xh, r, valid, t_from, t_to, risk, 0)
