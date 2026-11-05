import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load; from e21_lib import hourly_from; from e22_lib import prep, run, wt, VARIANTS, masks, breadth_of
A0, A1, B1 = [pd.Timestamp(x).value//3600_000_000_000 for x in ('2020-03-01', '2024-01-01', '2026-10-18')]
Ps = []
for part in ['creed15_1', 'creed15_2', 'creed15_3', 'creed15_4', 'creed15_5']:
    d, ms = load(part)
    for m in ms: Ps.append(prep(hourly_from(m, (m['t']*900).astype(np.int64))))
BR = breadth_of(Ps); keep = {}
print(f"{'hyp':3s} {'variant':28s} | 2020–23 net mean, t, n | 2024–26 net mean, t, n")
for hyp, name, spec in VARIANTS:
    A, B = [], []
    for P in Ps:
        mk = masks(P, spec, BR); kw = dict(k=spec.get('k'), W=spec.get('W'))
        A += run(P, mk, spec['mode'], A0, A1, **kw); B += run(P, mk, spec['mode'], A1, B1, **kw)
    ma, ta, na = wt(A); mb, tb, nb = wt(B); q = all(x is not None for x in (ta, tb)) and ma > 0 and mb > 0 and ta >= 2 and tb >= 2
    f = lambda m, t, n: f"{m*100:+.3f}% t {t:+.2f} n {n}" if t is not None else f"n {n}"
    print(f"{hyp:3s} {name:28s} | {f(ma, ta, na):26s} | {f(mb, tb, nb):26s}" + ('  <== qualifies' if q else ''))
    if q and (hyp not in keep or min(ta, tb) > keep[hyp]['score']): keep[hyp] = dict(name=name, spec=spec, score=min(ta, tb), a=[ma, ta, na], b=[mb, tb, nb])
print('\nKEPT for the test:', {h: v['name'] for h, v in keep.items()} or 'none')
json.dump(keep, open('plans/E22_kept.json', 'w'), indent=1, default=str)
