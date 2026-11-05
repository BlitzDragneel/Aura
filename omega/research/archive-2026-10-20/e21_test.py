import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load; from e21_lib import hourly_from, rules, trades, weekly_t
from scipy.stats import norm
C = json.load(open('plans/E21_discovery.json'))['candidates']; m = len(C); bar = float(norm.ppf(1 - 0.05/m)); COST = 0.002
MAJ = {'BTC','ETH','SOL','BNB','XRP','ADA','DOGE','AVAX','LINK','LTC','TRX','DOT','BCH','NEAR','ATOM','UNI','APT','ARB','OP','SUI','FIL','ICP','ETC','XLM','INJ'}
A1, B1 = pd.Timestamp('2024-01-01').value//3600_000_000_000, pd.Timestamp('2026-10-18').value//3600_000_000_000
TR = {c['rule']: [] for c in C}; coins = 0
for part in ['final4_a', 'final4_b', 'final4_c', 'final4_d', 'final4_young']:
    d, ms = load(part); tf = int(d.get('tf', 60))
    for mk in ms:
        if mk['sym'].replace('USDT', '') in MAJ: continue
        df = hourly_from(mk, (mk['t']*tf*60).astype(np.int64)); R = rules(df); coins += 1
        for c in C:
            mask, dr, H = R[c['rule']]; sgn = dr if c['side'] == 'as is' else -dr
            TR[c['rule']] += [(h, r - COST) for h, r in trades(df, mask, sgn, H, A1, B1, min_age=720)]
print(f'tested on {coins} perpetuals (the 25 majors excluded), 2024-01 → 2026-10, after 0.20% round trip; candidates {m}, bar t ≥ {bar:.2f}')
OUT = {}
for c in C:
    tr = TR[c['rule']]; mean, t, n = weekly_t(tr); s = pd.DataFrame(tr, columns=['h', 'r']); s['y'] = pd.to_datetime(s.h*3600, unit='s').dt.year
    yrs = {int(y): round(float(g.r.mean()*100), 3) for y, g in s.groupby('y')}; win = float((s.r > 0).mean()*100)
    passed = t is not None and t >= bar and mean > 0 and all(yrs.get(y, -1) > 0 for y in (2024, 2025, 2026))
    OUT[c['rule']] = dict(side=c['side'], n=n, mean=mean, t=t, years=yrs, winners=win, passed=bool(passed))
    print(f"\n{c['side']}: {c['rule']}  →  buy after the coin's 24-hour return falls into its bottom 10%, hold 24 h" if c['side'] == 'INVERSE' else c['rule'])
    print(f"   trades {n} | net mean per trade {mean*100:+.3f}% | weekly t {t:+.2f} | winners {win:.0f}% | by year (net mean %) {yrs}")
    print('   VERDICT:', 'PASS' if passed else 'FAIL')
json.dump(OUT, open('plans/E21_test.json', 'w'), indent=1)
