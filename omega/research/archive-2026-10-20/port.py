import sys; sys.path.insert(0,'/home/claude/edge')
from daily import *
F = {s: daily_frame(s) for s in sm['withspot']}; F = {k:v for k,v in F.items() if v}
def portfolio(min_age=7, thr=0.0, look=3, side_cost=0.0015, cap=0.10, coins=None):
    coins = coins or list(F.keys()); alld = sorted(set(int(x) for f in F.values() for x in f['days']))
    held = {}; out = []
    for d in alld:
        sig = {}
        for s in coins:
            f = F[s]; i = np.searchsorted(f['days'], d)
            if i >= len(f['days']) or f['days'][i] != d or i < max(look, min_age) or i + 1 >= len(f['days']): continue
            sig[s] = (f['fund'][i-look:i].mean() > thr, i)
        new = {s for s, (ok, i) in sig.items() if ok}
        w = min(cap, 1.0/len(new)) if new else 0.0
        pnl = 0.0; fee = 0.0
        for s in new:
            f = F[s]; i = sig[s][1]
            pnl += w*(f['fund'][i] + (f['prem'][i] - f['prem'][i+1]))
            if s not in held: fee += w*side_cost
        for s in set(held) - new: fee += held[s]*side_cost
        held = {s: w for s in new}
        out.append((d, pnl - fee, len(new), w*len(new)))
    return out
def stats(out, capital=1.5):
    r = np.array([x[1] for x in out])/capital; n = len(r)
    eq = np.cumprod(1 + r); dd = np.max(1 - eq/np.maximum.accumulate(eq))
    yrs = {}
    for (d, p, k, g), rr in zip(out, r): y = dt.datetime.fromtimestamp(d, dt.UTC).year; yrs.setdefault(y, []).append(rr)
    return { 'days':n, 'annual':eq[-1]**(365/n) - 1, 'sharpe':r.mean()/r.std()*np.sqrt(365) if r.std() > 0 else 0, 'maxDD':dd, 'avgHeld':np.mean([x[2] for x in out]), 'avgGross':np.mean([x[3] for x in out]),
             'byYear':{y: float(np.prod(1+np.array(v))**(365/len(v)) - 1) for y, v in yrs.items()} }
