import sys, json, pickle; sys.path.insert(0,'/home/claude/edge')
import numpy as np
import engine2 as E
import live as L
EV0 = int(np.datetime64('2025-07-01T00:00').astype('datetime64[h]').astype(int)); EV1 = int(np.datetime64('2025-10-01T00:00').astype('datetime64[h]').astype(int))
full = E.H
# 40 perpetuals: the 30 most traded in the window plus 10 others, each with 1000 warm-up hours and 220 hours after
cand = []
for s, u in full.items():
    if s.startswith('M:'): continue
    k0 = np.searchsorted(u['t'], EV0); k1 = np.searchsorted(u['t'], EV1)
    if k0 < 1000 or k1 + 220 > len(u['t']): continue
    cand.append((u['qv'][k0:k1].sum(), s))
cand.sort(reverse=True); rng = np.random.default_rng(3)
pick = [s for _, s in cand[:30]] + list(rng.choice([s for _, s in cand[30:]], 10, replace=False))
sub = {}
for s in pick:
    u = full[s]; k0 = np.searchsorted(u['t'], EV0) - 1000; k1 = np.searchsorted(u['t'], EV1) + 220
    sub[s] = {k: (v[k0:k1] if hasattr(v, '__len__') and len(v) == len(u['t']) else v) for k, v in u.items()}
    sub[s]['first'] = int(u['t'][0])            # the research counts age from the start of its series
E.H = sub; E.FB.clear()
# the research 'age' is the index inside the series: shift it so the subset keeps the full-series age
for s in pick:
    F = E.base(sub[s]); F['age'] = F['age'] + (np.searchsorted(full[s]['t'], EV0) - 1000); E.FB[s] = F
ref = {}
for key, ent, m in [('A', 'break72_hold', 'your method'), ('B', 'burst3', 'pyramid')]:
    bk = L.signal_book(ent, 'us_hours')
    eq, logs, curve = L.account(bk, L.METHODS[m], start=100.0, risk=0.01, t_from=EV0, t_to=EV1)
    ref[key] = dict(end=eq, trades=[dict(sym=x['sym'], hr=x['hr'], out=x['out'], R=x['R'], pnl=x['pnl'], eq=x['eq'], why=x['why'], adds=x['adds']) for x in logs])
    print(key, ent, m, 'trades', len(logs), 'end', round(eq, 4))
fx = dict(ev0=EV0, ev1=EV1, coins=[dict(sym=s, h0=int(sub[s]['t'][0]), first=sub[s]['first'], o=sub[s]['o'].tolist(), h=sub[s]['h'].tolist(), l=sub[s]['l'].tolist(), c=sub[s]['c'].tolist(), qv=sub[s]['qv'].tolist(), fund=sub[s]['fund'].tolist()) for s in pick], ref=ref)
json.dump(fx, open('/home/claude/omega48/fixtures/bdesk40.json', 'w')); print('fixture coins', len(pick))
