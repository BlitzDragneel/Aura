import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load; from e21_lib import hourly_from; from e22_lib import prep, run, wt, masks, breadth_of
from scipy.stats import norm
K = json.load(open('plans/E22_kept.json')); m = len(K); bar = float(norm.ppf(1 - 0.05/m))
A1, B1 = [pd.Timestamp(x).value//3600_000_000_000 for x in ('2024-01-01', '2026-10-18')]
Ps = []
for part in ['final4_a', 'final4_b', 'final4_c', 'final4_d', 'final4_young']:
    d, ms = load(part); tf = int(d.get('tf', 60))
    for mk in ms: Ps.append(prep(hourly_from(mk, (mk['t']*tf*60).astype(np.int64))))
BR = breadth_of(Ps); print(f'{len(Ps)} perpetuals, 2024-01 → 2026-10, net of costs; {m} variants, bar t ≥ {bar:.2f}'); OUT = {}
for hyp, kv in K.items():
    spec = kv['spec']; tr = []
    for P in Ps: tr += run(P, masks(P, spec, BR), spec['mode'], A1, B1, min_age=720, k=spec.get('k'), W=spec.get('W'))
    mean, t, n = wt(tr); s = pd.DataFrame(tr, columns=['h', 'r']); s['y'] = pd.to_datetime(s.h*3600, unit='s').dt.year
    yrs = {int(y): round(float(g.r.mean()*100), 3) for y, g in s.groupby('y')}; win = float((s.r > 0).mean()*100); med = float(s.r.median()*100)
    passed = t is not None and t >= bar and mean > 0 and all(yrs.get(y, -1) > 0 for y in (2024, 2025, 2026))
    OUT[hyp] = dict(name=kv['name'], n=n, mean=mean, t=t, years=yrs, winners=win, median=med, passed=bool(passed))
    print(f"\n{hyp} {kv['name']}: trades {n} | net mean {mean*100:+.3f}% (median {med:+.2f}%) | weekly t {t:+.2f} | winners {win:.0f}% | by year {yrs} | {'PASS' if passed else 'FAIL'}")
json.dump(OUT, open('plans/E22_test.json', 'w'), indent=1)
