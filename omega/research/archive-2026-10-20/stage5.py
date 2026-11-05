import sys; sys.path.insert(0,'/home/claude/edge')
import numpy as np, pickle
from engine import SPLIT_H
S3 = pickle.load(open('stage3.pkl','rb'))
def account(T, f0, rule, slots=5, start=100.0):
    T = T[np.argsort(T[:,0])]; ev = []
    eq = start; peak = start; dd = 0.0; f = f0; open_ = []; taken = []
    for row in T:
        t_in, R, units, bars, t_out = row
        # settle trades that closed before this entry
        open_.sort(key=lambda x: x[0])
        while open_ and open_[0][0] <= t_in:
            _, stake, r = open_.pop(0); eq = max(eq + stake*r, 0.0); taken.append(r); peak = max(peak, eq); dd = max(dd, 1 - eq/peak)
            if rule == 'anti': f = min(f*1.5, 4*f0) if r > 0 else f0
            if rule == 'mart': f = min(f*2, 16*f0) if r <= 0 else f0
        if len(open_) >= slots or eq < 5: continue
        open_.append((t_out, f*eq, R))
    for _, stake, r in sorted(open_): eq = max(eq + stake*r, 0.0); taken.append(r); peak = max(peak, eq); dd = max(dd, 1 - eq/peak)
    return eq, dd, np.array(taken)
for name in [('S14 Momentum burst','M4 pyramid: add each +1R (max 3)'), ('S14 Momentum burst','M5 your method: close 60% + pyramid'), ('S14 Momentum burst','M0 stop + 5R target (baseline)')]:
    T = S3[name]; R = T[:,1]
    print(f"\n{name[0]} + {name[1]} — trade outcomes in R (whole period): median {np.median(R):+.2f}, 99th pct {np.percentile(R,99):+.1f}, best {R.max():+.1f}; share of profit from top 1% of trades {R[R >= np.percentile(R,99)].sum()/max(R[R>0].sum(),1e-9)*100:.0f}% of all gains")
    for half, sel in [('1st half', T[:,0] < SPLIT_H), ('2nd half', T[:,0] >= SPLIT_H)]:
        for f0 in (0.02, 0.05):
            line = []
            for rule in ('fixed', 'anti', 'mart'):
                eq, dd, tk = account(T[sel], f0, rule)
                line.append(f"{rule:5s} end {eq:9.0f} (fall {dd*100:3.0f}%)")
            print(f"  {half} risk {f0*100:.0f}%: " + ' | '.join(line) + f" | trades taken {len(tk)}")
