"""Plan E10 (PLAN_E10_market_capitulation.md, md5 dd6b6bcc…; addendum B, md5 12a77dea…): run once on creed15_1."""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load
d, ms = load('creed15_1'); C = {}
for m in ms: C[m['sym'].replace('USDT', '')] = pd.Series(m['c'], index=pd.to_datetime(m['t']*900, unit='s')).resample('1D').last()
P = pd.DataFrame(C).sort_index(); P = P[P.index <= pd.Timestamp('2026-10-18')]
R = np.log(P).diff(); idx_r = R.clip(-0.5, 0.5).mean(axis=1).fillna(0.0); L = np.exp(idx_r.cumsum())
ma200 = L.rolling(200).mean(); r30 = L/L.shift(30) - 1; r7 = L/L.shift(7) - 1; r3 = L/L.shift(3) - 1
vol30 = idx_r.rolling(30).std(); volmed = vol30.rolling(365, min_periods=180).median().shift(1)
state = pd.Series('NORMAL', index=L.index)
state[(vol30 < volmed) & (r30.abs() < 0.10)] = 'CONSOLIDATING'; state[(L > ma200) & (r7 <= -0.08)] = 'CORRECTING'
state[(L > ma200) & (r30 >= 0.25)] = 'BOOMING'; state[(L < ma200) & (r30 <= -0.15)] = 'DEPRESSED'; state[ma200.isna()] = None
print('coins', list(P.columns), '| days', len(P), P.index[0].date(), '→', P.index[-1].date(), '| states from', state.dropna().index[0].date())
print('days per state:', state.value_counts().to_dict())
days = list(P.index); n = len(days); pnl = pd.Series(0.0, index=P.index); k = 0; trades = []; COST = 0.001
while k < n - 1:
    dd = days[k]
    if state.iloc[k] != 'DEPRESSED' or not (r3.iloc[k] <= -0.10): k += 1; continue
    coins = [c for c in P.columns if pd.notna(P.iloc[k][c])]; w = 1.0/len(coins); tr = 0.0
    for j in range(1, 4):
        if k + j >= n: break
        g = sum(w*(R.iloc[k + j][c] if pd.notna(R.iloc[k + j][c]) else 0.0) for c in coins); pnl.iloc[k + j] += g; tr += g
    pnl.iloc[min(k + 1, n - 1)] -= COST; pnl.iloc[min(k + 3, n - 1)] -= COST
    trades.append((str(dd.date()), len(coins), round((np.exp(tr - 2*COST) - 1)*100, 2))); k += 3
def wk_t(p):
    w = p.groupby(p.index.to_period('W-SUN')).sum(); w = w.reindex(pd.period_range(p.index[0], p.index[-1], freq='W-SUN'), fill_value=0.0)
    return float(w.mean()/w.std()*np.sqrt(len(w))) if w.std() > 0 else 0.0
S = pd.Timestamp('2024-01-01'); a, b = pnl[pnl.index < S], pnl[pnl.index >= S]; na = sum(1 for x in trades if x[0] < '2024'); nb = len(trades) - na
t_all = wk_t(pnl); yrs = {int(y): round(float((np.exp(v) - 1)*100), 1) for y, v in pnl.groupby(pnl.index.year).sum().items()}
passed = t_all >= 1.65 and pnl.sum() > 0 and (na == 0 or a.sum() > 0) and (nb == 0 or b.sum() > 0)
print(f"\nsignals {len(trades)} (before 2024: {na}, from 2024: {nb}) | winners {sum(1 for x in trades if x[2] > 0)}/{len(trades)} | average trade {np.mean([x[2] for x in trades]):+.2f}%")
print(f"total {(np.exp(pnl.sum()) - 1)*100:+.1f}% | weekly t {t_all:+.2f} | before 2024 {(np.exp(a.sum()) - 1)*100:+.1f}% | from 2024 {(np.exp(b.sum()) - 1)*100:+.1f}% | by year {yrs}")
print('VERDICT:', 'PASS' if passed else 'FAIL'); print('trades (signal day, coins, % after costs):', trades)
json.dump(dict(sha256='5e9fa47e34a6543f73ac6547923fadd3a98fec2a0f5d677cf84a8436cf4ffafb', trades=trades, t=t_all, total_log=float(pnl.sum()), by_year=yrs, passed=bool(passed)), open('plans/E10_result.json', 'w'), indent=1)
