import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load
SPLIT = pd.Timestamp('2024-01-01'); END = pd.Timestamp('2026-10-18')
C = {}
for part in ['creed15_2','creed15_3','creed15_4','creed15_5']:
    d, ms = load(part)
    for m in ms:
        ts = pd.to_datetime(m['t']*900, unit='s'); C[m['sym'].replace('USDT', '')] = pd.Series(m['c'], index=ts).resample('1D').last()
P = pd.DataFrame(C).sort_index(); P = P[P.index <= END]
R = np.log(P).diff()                                  # coin daily log returns
age = P.notna().cumsum()
idx_r = R.clip(-0.5, 0.5).mean(axis=1).fillna(0.0); L = np.exp(idx_r.cumsum())
ma200 = L.rolling(200).mean(); r30 = L/L.shift(30) - 1; r7 = L/L.shift(7) - 1; r3 = L/L.shift(3) - 1
vol30 = idx_r.rolling(30).std(); volmed = vol30.rolling(365, min_periods=180).median().shift(1)
state = pd.Series('NORMAL', index=L.index)
state[(L > ma200) & ~((L > ma200) & (r30 >= 0.25)) & (r7 <= -0.08)] = 'CORRECTING'
state[(vol30 < volmed) & (r30.abs() < 0.10) & ~((L > ma200) & (r7 <= -0.08))] = 'CONSOLIDATING'
state[(L > ma200) & (r30 >= 0.25)] = 'BOOMING'
state[(L < ma200) & (r30 <= -0.15)] = 'DEPRESSED'
state[ma200.isna()] = None
# priority: DEPRESSED, BOOMING, CORRECTING, CONSOLIDATING, NORMAL (re-assert in that order)
st2 = pd.Series('NORMAL', index=L.index)
cons = (vol30 < volmed) & (r30.abs() < 0.10); corr = (L > ma200) & (r7 <= -0.08); boom = (L > ma200) & (r30 >= 0.25); dep = (L < ma200) & (r30 <= -0.15)
st2[cons] = 'CONSOLIDATING'; st2[corr] = 'CORRECTING'; st2[boom] = 'BOOMING'; st2[dep] = 'DEPRESSED'; st2[ma200.isna()] = None; state = st2
fwd7 = L.shift(-7)/L - 1
print('index from', L.index[0].date(), 'to', L.index[-1].date(), '| states from', state.dropna().index[0].date())
OUT = {'describe':{}, 'rules':{}}
print('\nPART 1 — what the market did over the next 7 days, by state (2020–23 | 2024–26)')
for s_ in ['DEPRESSED', 'BOOMING', 'CORRECTING', 'CONSOLIDATING', 'NORMAL']:
    row = {}
    for lab, sel in [('a', state.index < SPLIT), ('b', state.index >= SPLIT)]:
        x = fwd7[(state == s_) & sel].dropna(); row[lab] = dict(days=int(len(x)), mean=round(float(x.mean()*100), 2) if len(x) else None, median=round(float(x.median()*100), 2) if len(x) else None, up=round(float((x > 0).mean()*100), 0) if len(x) else None)
    OUT['describe'][s_] = row; a, b = row['a'], row['b']
    print(f"  {s_:13s} days {a['days']:4d} | {b['days']:4d}   next 7d mean {a['mean']}% | {b['mean']}%   median {a['median']}% | {b['median']}%   up {a['up']}% | {b['up']}%")
cur = state.dropna(); print('  latest state:', cur.index[-1].date(), cur.iloc[-1], '| index 30-day', round(float(r30.iloc[-1]*100), 1), '% | 7-day', round(float(r7.iloc[-1]*100), 1), '% | above 200-day:', bool(L.iloc[-1] > ma200.iloc[-1]))
OUT['latest'] = dict(day=str(cur.index[-1].date()), state=cur.iloc[-1], r30=float(r30.iloc[-1]), r7=float(r7.iloc[-1]), above200=bool(L.iloc[-1] > ma200.iloc[-1]))
# PART 2 rules
c3 = P/P.shift(3) - 1; c7 = P/P.shift(7) - 1; hi20 = P.rolling(20).max(); lo20 = P.rolling(20).min(); posr = (P - lo20)/(hi20 - lo20)
days = list(P.index); n = len(days); COST = 0.001
def pick(score, k, largest, d):
    s = score.loc[d]; ok = s.notna() & (age.loc[d] >= 30) & P.loc[d].notna(); s = s[ok]
    return list(s.nlargest(k).index) if largest else list(s.nsmallest(k).index)
RULES = {
 'D1 capitulation bounce (depressed)':   (lambda d: state[d] == 'DEPRESSED' and r3[d] <= -0.10, lambda d: {c: 0.2 for c in pick(c3, 5, False, d)}, 3),
 'D2 relief-rally fade (depressed)':     (lambda d: state[d] == 'DEPRESSED' and r3[d] >= 0.10,  lambda d: {c: -0.2 for c in pick(c3, 5, True, d)}, 3),
 'B1 ride the boom (booming)':           (lambda d: state[d] == 'BOOMING',                      lambda d: {c: 0.2 for c in pick(c7, 5, True, d)}, 7),
 'B2 blow-off fade (booming)':           (lambda d: state[d] == 'BOOMING' and r7[d] >= 0.20,    lambda d: {c: -0.2 for c in pick(c7, 5, True, d)}, 3),
 'C1 buy the correction (correcting)':   (lambda d: state[d] == 'CORRECTING',                   lambda d: (lambda cs: {c: 1.0/len(cs) for c in cs})([c for c in P.columns if pd.notna(P.loc[d, c]) and age.loc[d, c] >= 30]), 7),
 'K1 range reversion (consolidating)':   (lambda d: state[d] == 'CONSOLIDATING',                lambda d: dict([(c, 0.1) for c in pick(posr, 5, False, d)] + [(c, -0.1) for c in pick(posr, 5, True, d)]), 3)}
def wk_t(p):
    w = p.groupby(p.index.to_period('W-SUN')).sum(); w = w.reindex(pd.period_range(p.index[0], p.index[-1], freq='W-SUN'), fill_value=0.0)
    return float(w.mean()/w.std()*np.sqrt(len(w))) if w.std() > 0 else 0.0
print('\nPART 2 — one rule per state (after 0.10% a side). 2020–23 | 2024–26')
for name, (cond, weights, hold) in RULES.items():
    pnl = pd.Series(0.0, index=P.index); k = 0; nsig = {'a':0, 'b':0}
    while k < n - 1:
        d = days[k]
        if state[d] is None or not cond(d): k += 1; continue
        w = weights(d)
        if not w: k += 1; continue
        nsig['a' if d < SPLIT else 'b'] += 1; gross = sum(abs(v) for v in w.values())
        for j in range(1, hold + 1):
            if k + j >= n: break
            dd = days[k + j]; pnl[dd] += sum(v*(R.loc[dd, c] if pd.notna(R.loc[dd, c]) else 0.0) for c, v in w.items())
        pnl[days[min(k + 1, n - 1)]] -= gross*COST; pnl[days[min(k + hold, n - 1)]] -= gross*COST
        k += hold
    a, b = pnl[pnl.index < SPLIT], pnl[pnl.index >= SPLIT]; yrs_a = (a.index[-1] - a.index[0]).days/365.25; yrs_b = (b.index[-1] - b.index[0]).days/365.25
    ta, tb = wk_t(a), wk_t(b); ya, yb = a.sum()/yrs_a*100, b.sum()/yrs_b*100; byy = {int(y): round(float(v*100), 1) for y, v in pnl.groupby(pnl.index.year).sum().items()}
    passed = tb >= 2.40 and yb > 0 and ya > 0
    OUT['rules'][name] = dict(signals=nsig, a_per_year=round(ya, 1), b_per_year=round(yb, 1), t_a=round(ta, 2), t_b=round(tb, 2), by_year=byy, passed=bool(passed))
    print(f"  {name:38s} signals {nsig['a']:3d} | {nsig['b']:3d}   {ya:+6.1f}%/yr (t {ta:+.2f}) | {yb:+6.1f}%/yr (t {tb:+.2f})   {byy}   {'PASS' if passed else 'FAIL'}")
json.dump(OUT, open('plans/E8_states.json', 'w'), indent=1, default=str)
