import sys; sys.path.insert(0,'/home/claude/edge')
from engine2 import *
def clustered(T, sel):
    x = T[sel]; wk = (x[:,0]//(24*7)).astype(int); s = pd.Series(x[:,1]).groupby(wk).sum(); n = pd.Series(1, index=range(len(x))).groupby(wk).sum()
    m = s.mean(); se = s.std()/np.sqrt(len(s)); return m/se, len(s)          # weekly P&L sums: trades in the same week share the market's luck
def account(T, f0=0.02, slots=5, start=100.0):
    T = T[np.lexsort((-np.abs(T[:,1]*0), T[:,0]))]; eq = start; peak = start; dd = 0; op = []; got = []
    for row in T:
        op.sort(key=lambda x: x[0])
        while op and op[0][0] <= row[0]:
            _, st, r = op.pop(0); eq = max(eq + st*r, 0); got.append(r); peak = max(peak, eq); dd = max(dd, 1 - eq/peak)
        if len(op) < slots and eq >= 5: op.append((row[0] + (row[4] - row[3]), f0*eq, row[1]))
    for _, st, r in sorted(op): eq = max(eq + st*r, 0); got.append(r)
    return eq, dd, np.array(got)
for e, flt, mg in [('burst3','us_hours','PY'), ('burst3','mkt_trend','PY'), ('break72_hold','us_hours','PY'), ('burst3','none','PY')]:
    T = run(e, flt, mg); a, b = T[:,0] < SPLIT_H, T[:,0] >= SPLIT_H
    ta, wa = clustered(T, a); tb, wb = clustered(T, b)
    lo, sh_ = T[:,2] == 1, T[:,2] == -1
    q = pd.Series(T[:,1]).groupby(pd.to_datetime(T[:,0]*3600, unit='s').to_period('Q')).agg(['mean','size'])
    print(f"\n{e} + {flt} + {mg}: weekly-clustered t: 1st {ta:.2f} ({wa} weeks) | 2nd {tb:.2f} ({wb} weeks)")
    print(f"  longs {T[b & lo][:,1].mean():+.3f}R (n {int((b&lo).sum())}) | shorts {T[b & sh_][:,1].mean():+.3f}R (n {int((b&sh_).sum())}) in the 2nd half")
    print('  by quarter:', ' '.join(f"{str(k)}:{v['mean']:+.2f}" for k, v in q.iterrows()))
    R = T[:,1]; print(f"  top 1% of trades = {R[R >= np.percentile(R, 99)].sum()/R[R > 0].sum()*100:.0f}% of all gains | median trade {np.median(R):+.2f}R")
    for half, sel in [('1st', a), ('2nd', b)]:
        eq, dd, got = account(T[sel]); print(f"  100 USDT, 5 positions, 2% risk, {half} half: end {eq:7.1f} USDT | worst fall {dd*100:3.0f}% | trades taken {len(got)}, mean {got.mean():+.3f}R")
