import sys; sys.path.insert(0,'/home/claude/edge')
from engine import *
import pickle
rng = np.random.default_rng(11); SH = {}
for s, u in H.items():
    c = u['c']; pc = np.r_[c[0], c[:-1]]
    rel = np.vstack([np.log(c/pc), u['o']/pc, u['h']/pc, u['l']/pc, u['qv']]).T[1:]
    rel = rel[rng.permutation(len(rel))]
    cc = np.r_[c[0], c[0]*np.exp(np.cumsum(rel[:,0]))]; p = cc[:-1]
    SH[s] = dict(t=u['t'], c=cc, o=np.r_[u['o'][0], p*rel[:,1]], h=np.r_[u['h'][0], p*rel[:,2]], l=np.r_[u['l'][0], p*rel[:,3]], qv=np.r_[u['qv'][0], rel[:,4]])
    SH[s]['h'] = np.maximum(SH[s]['h'], np.maximum(SH[s]['o'], SH[s]['c'])); SH[s]['l'] = np.minimum(SH[s]['l'], np.minimum(SH[s]['o'], SH[s]['c']))
FS = {s: features(u) for s, u in SH.items()}; FS['_H'] = SH
print('SHUFFLED PRICES (same moves, random order: no trends to find). Whole period, 0.10% a side.')
for s in ['S14 Momentum burst', 'S02 Donchian 55 breakout']:
    for m, kw in [('M0 baseline 5R', dict(tgt_R=5.0, max_bars=168)), ('M4 pyramid', dict(tgt_R=0.0, pyr_R=1.0, pyr_max=3, trail_atr=3.0, max_bars=168)), ('M5 your method', dict(tgt_R=0.0, sc_frac=0.6, sc_R=1.0, pyr_R=1.0, pyr_max=3, trail_atr=3.0, max_bars=168))]:
        T = run(s, data=FS, **kw); x = T[:,1]
        print(f"  {s[:3]} {m:16s} n={len(x):6d} {x.mean():+.3f}R ±{x.std()/np.sqrt(len(x)):.3f} | wins {np.mean(x>0)*100:3.0f}% | cost alone ≈ {np.mean(0.002*1.0):.3f} of price", flush=True)
# sizing techniques on the real best combination, second half, from 100 USDT
S3 = pickle.load(open('stage3.pkl','rb'))
T = S3[('S14 Momentum burst', 'M4 pyramid: add each +1R (max 3)')]; T = T[T[:,0] >= SPLIT_H]; T = T[np.argsort(T[:,4])]
print('\nSIZING on S14 + pyramid, second half (Jul 2025 - Oct 2026), trades in order of exit, 100 USDT start:')
def eqrun(rule, base=0.01):
    eq = 100.0; peak = 100.0; dd = 0.0; f = base; low = 100.0
    for r in T[:,1]:
        eq = max(eq*(1 + f*r), 0.0); peak = max(peak, eq); dd = max(dd, 1 - eq/peak if peak > 0 else 1); low = min(low, eq)
        if rule == 'anti': f = min(f*1.5, 0.04) if r > 0 else base
        if rule == 'mart': f = min(f*2, 0.16) if r <= 0 else base
        if eq < 1: break
    return eq, dd, low
for rule, lab in [('fixed','fixed 1% a trade'), ('anti','raise 1.5x after a win (max 4%)'), ('mart','double after a loss (max 16%)')]:
    for base in (0.01, 0.02):
        e, d, lo = eqrun(rule, base)
        print(f"  {lab:34s} base {base*100:.0f}%: end {e:10.2f} USDT | worst fall {d*100:5.1f}% | lowest {lo:8.2f}")
