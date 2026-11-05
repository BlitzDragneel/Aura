"""E25 — run ONCE per PLAN_E25 + addenda A, B, C. Rules from e22_lib (verbatim copy reference_e22.py)."""
import pickle, json, numpy as np, pandas as pd, datetime as dt, hashlib
from scipy.stats import norm
import reference_e22 as R
HH = lambda s: int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp() // 3600)
A1, B1, H_END, CUT = HH('2024-01-01'), HH('2026-10-18'), HH('2026-10-19'), HH('2026-10-11')
EXC = json.load(open('/home/claude/omega/plans-new/E25_exclusions.json'))
RAW = pickle.load(open('hourly_e25.pkl', 'rb'))
Ps, META = {}, {}
for s, x in RAW.items():
    ok = x['v'] > 0
    if not ok.any(): continue
    last = int(x['h'][ok][-1])
    if last < A1: continue
    idx = np.arange(int(x['h'][0]), H_END)
    df = pd.DataFrame(index=idx, columns=['c', 'hi', 'lo', 'v'], dtype=float)
    df.loc[x['h'][ok], ['c', 'hi', 'lo', 'v']] = np.c_[x['c'][ok], x['hi'][ok], x['lo'][ok], x['v'][ok]]     # volume-0 candles stay NaN
    Ps[s] = R.prep(df); META[s] = dict(last=last, delisted=last < CUT, last_i=last - idx[0])
print(len(Ps), 'coins;', sum(m['delisted'] for m in META.values()), 'delisted', flush=True)
BR = R.breadth_of(Ps.values())
def exit_px(c, start, x, M, n):
    lim_x = min(x, M['last_i']) if M['delisted'] else min(x, n - 1)
    run = 0
    for j in range(start + 1, lim_x + 1):                       # gaps longer than 24 hours inside the hold
        if np.isfinite(c[j]) and c[j] > 0: run = 0
        else:
            run += 1
            if run > 24: k = j - run; return c[k]*0.95, 'gap'
    if M['delisted'] and x > M['last_i']: return c[M['last_i']]*0.95, 'delisted'
    if x >= n: return None
    if np.isfinite(c[x]) and c[x] > 0: return c[x], 'normal'
    for j in range(x + 1, n):
        if np.isfinite(c[j]) and c[j] > 0: return c[j], 'after_gap'
    return None
def run(sym, P, mask, spec):
    c, l, idx, M = P['c'], P['l'], P['idx'], META[sym]; first = int(np.argmax(np.isfinite(c))); n = len(c); out = []; nxt = -1
    for t in np.where(mask)[0]:
        if t < nxt or t - first < 720 or idx[t] < A1 or idx[t] >= B1: continue
        if spec['mode'] == 'limit':
            if not (P['sig'][t] > 0 and c[t] > 0): continue
            lim = c[t]*np.exp(-spec['k']*P['sig'][t]); f = None
            for j in range(t + 1, min(n, t + 1 + spec['W'])):
                if l[j] < lim: f = j; break
            if f is None: nxt = t + spec['W']; continue
            entry, start, cost = lim, f, 0.0012
        else:
            if not (c[t] > 0): continue
            entry, start, cost = c[t], t, 0.002
        r = exit_px(c, start, start + 24, M, n)
        if r is None:
            if spec['mode'] == 'limit': nxt = t + spec['W']
            continue
        out.append(dict(sym=sym, h=int(idx[t]), r=float(r[0]/entry - 1 - cost), kind=r[1])); nxt = start + 24
    return out
SPECS = {'H1': dict(mode='limit', q=10, k=2, W=3), 'H3': dict(mode='taker', q=5, b=20)}
bar = float(norm.ppf(1 - 0.05/2)); RES = {}
def summ(tr):
    if not tr: return dict(n=0)
    m, t, n = R.wt([(x['h'], x['r']) for x in tr]); s = pd.DataFrame(tr); s['y'] = pd.to_datetime(s.h*3600, unit='s').dt.year
    return dict(n=n, mean=m, t=t, median=float(s.r.median()), winners=float((s.r > 0).mean()), years={int(y): float(g.r.mean()) for y, g in s.groupby('y')})
for name, spec in SPECS.items():
    tr = []
    for s, P in Ps.items(): tr += run(s, P, R.masks(P, spec, BR), spec)
    S = summ(tr); passed = S['n'] >= 20 and S['t'] is not None and S['t'] >= bar and S['mean'] > 0 and all(S['years'].get(y, -1) > 0 for y in (2024, 2025, 2026))
    rs = sorted(x['r'] for x in tr); k = int(len(rs)*0.05)
    dl = [x for x in tr if META[x['sym']]['delisted']]; soon = [x for x in dl if META[x['sym']]['last'] - x['h'] <= 90*24]
    excl = set(EXC['stable']) | set(EXC['tradfi'])
    RES[name] = dict(main=S, passed=bool(passed), bar=bar,
        kinds={k_: sum(1 for x in tr if x['kind'] == k_) for k_ in ('normal', 'after_gap', 'gap', 'delisted')},
        delisted_coins=summ(dl), trades_on_coins_delisted_within_90d=len(soon), share_within_90d=len(soon)/max(1, len(tr)),
        without_best_5pct=float(np.mean(rs[:len(rs) - k])) if rs else None,
        without_stable_tradfi=summ([x for x in tr if x['sym'] not in excl]),
        survivors_only=summ([x for x in tr if not META[x['sym']]['delisted']]),
        worst10=[(x['sym'], dt.datetime.fromtimestamp(x['h']*3600, dt.UTC).strftime('%Y-%m-%d %H'), round(x['r']*100, 1), x['kind']) for x in sorted(tr, key=lambda x: x['r'])[:10]])
    print(name, json.dumps(RES[name], default=str)[:1500], flush=True)
json.dump(RES, open('E25_result.json', 'w'), indent=1, default=str)
print('result md5', hashlib.md5(open('E25_result.json', 'rb').read()).hexdigest())
