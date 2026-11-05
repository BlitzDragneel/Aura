import sys, pickle, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge')
src = open('/home/claude/edge/states.py').read(); ns = {}; exec(src[:src.index('fwd7 = ')], ns)      # E8's state and index, unchanged
state, r3m = ns['state'], ns['r3']
PD = pickle.load(open('/home/claude/edge/perp_daily.pkl', 'rb'))
def frame(col):
    F = pd.DataFrame({s: g[col] for s, g in PD.items()}).sort_index(); F.index = pd.to_datetime(F.index.astype('int64'), unit='s'); return F
C = frame('c'); FU = frame('fund').reindex(C.index); QV = frame('qv').reindex(C.index)
R = np.log(C).diff(); age = C.notna().cumsum(); liq = QV.rolling(20, min_periods=10).median().shift(1); c3 = C/C.shift(3) - 1
days = list(C.index); n = len(days); pnl = pd.Series(0.0, index=C.index); k = 0; trades = []; COST = 0.001
while k < n - 1:
    d = days[k]; st = state.get(d)
    if st != 'DEPRESSED' or not (r3m.get(d, 0) <= -0.10): k += 1; continue
    s = c3.loc[d]; ok = s.notna() & (age.loc[d] >= 30) & (liq.loc[d] >= 5e6) & C.loc[d].notna(); s = s[ok]
    if len(s) < 5: k += 1; continue
    pick = list(s.nsmallest(5).index); w = 0.2; tr = 0.0
    for j in range(1, 4):
        if k + j >= n: break
        dd = days[k + j]; g = sum(w*((R.loc[dd, c] if pd.notna(R.loc[dd, c]) else 0.0) - (FU.loc[dd, c] if pd.notna(FU.loc[dd, c]) else 0.0)) for c in pick); pnl[dd] += g; tr += g
    pnl[days[min(k + 1, n - 1)]] -= COST; pnl[days[min(k + 3, n - 1)]] -= COST; trades.append((str(d.date()), pick, round((tr - 2*COST)*100, 2))); k += 3
def wk_t(p):
    w = p.groupby(p.index.to_period('W-SUN')).sum(); w = w.reindex(pd.period_range(p.index[0], p.index[-1], freq='W-SUN'), fill_value=0.0)
    return float(w.mean()/w.std()*np.sqrt(len(w))) if w.std() > 0 else 0.0
t_all = wk_t(pnl); a = pnl[pnl.index < pd.Timestamp('2024-01-01')]; b = pnl[pnl.index >= pd.Timestamp('2024-01-01')]
na = sum(1 for x in trades if x[0] < '2024'); nb = len(trades) - na
yrs = {int(y): round(float(v*100), 1) for y, v in pnl.groupby(pnl.index.year).sum().items()}
passed = t_all >= 1.65 and pnl.sum() > 0 and (na == 0 or a.sum() > 0) and (nb == 0 or b.sum() > 0)
print(f"perpetuals {C.shape[1]} | signals {len(trades)} (before 2024: {na}, from 2024: {nb})")
print(f"total {pnl.sum()*100:+.1f}% | weekly t {t_all:+.2f} | before 2024 {a.sum()*100:+.1f}% | from 2024 {b.sum()*100:+.1f}% | by year {yrs} | winners {sum(1 for x in trades if x[2] > 0)}/{len(trades)} | avg trade {np.mean([x[2] for x in trades]):+.2f}%")
print('VERDICT:', 'PASS' if passed else 'FAIL'); print('trades:', [(x[0], x[2]) for x in trades])
json.dump(dict(trades=trades, t=t_all, total=float(pnl.sum()), by_year=yrs, passed=bool(passed)), open('plans/E9_result.json', 'w'), indent=1)
