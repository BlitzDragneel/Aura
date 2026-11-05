import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load; from e21_lib import hourly_from, rules, trades, weekly_t
A0, A1, B1 = pd.Timestamp('2020-03-01').value//3600_000_000_000, pd.Timestamp('2024-01-01').value//3600_000_000_000, pd.Timestamp('2026-10-18').value//3600_000_000_000
POOL = {}
for part in ['creed15_1', 'creed15_2', 'creed15_3', 'creed15_4', 'creed15_5']:
    d, ms = load(part)
    for m in ms:
        df = hourly_from(m, (m['t']*900).astype(np.int64)); R = rules(df)
        for name, (mask, dr, H) in R.items():
            P = POOL.setdefault(name, { 'a':[], 'b':[] }); P['a'] += trades(df, mask, dr, H, A0, A1); P['b'] += trades(df, mask, dr, H, A1, B1)
rows = []
for name, P in POOL.items():
    ma, ta, na = weekly_t(P['a']); mb, tb, nb = weekly_t(P['b']); rows.append((name, ma, ta, na, mb, tb, nb))
cands = []
print(f"{'rule':38s} | 2020–23 gross mean, t, trades | 2024–26 gross mean, t, trades")
for name, ma, ta, na, mb, tb, nb in sorted(rows, key=lambda x: -min(abs(x[2] or 0), abs(x[5] or 0))):
    same = ta is not None and tb is not None and np.sign(ta) == np.sign(tb) and abs(ta) >= 2 and abs(tb) >= 2 and abs(ma) >= 0.0025 and abs(mb) >= 0.0025 and np.sign(ma) == np.sign(ta) and np.sign(mb) == np.sign(tb)
    if same: cands.append(dict(rule=name, side='as is' if ta > 0 else 'INVERSE', a=[ma, ta, na], b=[mb, tb, nb]))
    print(f"{name:38s} | {ma*100:+6.3f}% t {ta:+5.2f} n {na:6d} | {mb*100:+6.3f}% t {tb:+5.2f} n {nb:6d}" + ('   <== CANDIDATE (' + ('as is' if ta > 0 else 'INVERSE') + ')' if same else ''))
print(f'\n{len(rows)} rules scanned; candidates: {len(cands)}')
json.dump(dict(rows=rows, candidates=cands), open('plans/E21_discovery.json', 'w'), indent=1)
