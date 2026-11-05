"""Plan E13 (PLAN_E13_market_watch.md, md5 4390a4e4…; addendum A, md5 14a3500…). usage: python3 e13_run.py <file> [<file> …] [--dry]
Without --dry it refuses files below the plan's minimum. --dry only checks the code paths; its numbers mean nothing."""
import sys, json, hashlib, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from mwload import load_watch
paths = [a for a in sys.argv[1:] if not a.startswith('--')]; DRY = '--dry' in sys.argv; COST = 0.001
for pth in paths: print('file sha256', hashlib.sha256(open(pth, 'rb').read()).hexdigest(), pth.split('/')[-1])
if DRY: print('DRY RUN: numbers mean nothing')
Ws = [load_watch(pth) for pth in paths]; W = Ws[0]; d = W['meta']
for X in Ws[1:]:                                                   # merge minute by minute; a minute counts once
    for sym, df in X['coins'].items(): W['coins'][sym] = W['coins'][sym].combine_first(df) if sym in W['coins'] else df
    W['market'] = W['market'].combine_first(X['market'])
    for sym, P in X['meta']['pos'].items():
        old = d['pos'].setdefault(sym, {'oi':[]}); seen = {r[0] for r in old.get('oi', [])}; old['oi'] = sorted(old.get('oi', []) + [r for r in P.get('oi', []) if r[0] not in seen])
if 'BTCUSDT' not in W['coins']: print('days with BTC live data in >= 80% of minutes: 0 | total live BTC minutes: 0 (no minute rows at all)'); print('NOT RUN: below the plan minimum (5 such days). The file is noted as too short.'); sys.exit(0)
EX0, EX1 = pd.Timestamp('2026-10-21 01:00'), pd.Timestamp('2026-10-21 08:59')     # explored night, excluded (addendum A)
for sym in W['coins']: W['coins'][sym].loc[(W['coins'][sym].index >= EX0) & (W['coins'][sym].index <= EX1)] = np.nan
W['market'].loc[(W['market'].index >= EX0) & (W['market'].index <= EX1)] = np.nan
btc = W['coins']['BTCUSDT']; live = ((btc.sC > 0) | (btc.pC > 0)).groupby(btc.index.floor('D')).sum()
good_days = int((live >= 0.8*1440).sum()); print('days with BTC live data in >= 80% of minutes:', good_days, '| total live BTC minutes:', int(live.sum()))
if good_days < 5 and not DRY: print('NOT RUN: below the plan minimum (5 such days). The file is noted as too short.'); sys.exit(0)
def full(df):
    i = pd.date_range(df.index.min().floor('min'), df.index.max().floor('min'), freq='min'); return df.reindex(i)
def tclust(times, x):
    s = pd.Series(np.asarray(x, float), index=pd.to_datetime(times)).groupby(lambda t: t.floor('h')).mean()
    return (float(s.mean()/s.std()*np.sqrt(len(s))) if len(s) > 2 and s.std() > 0 else None), len(s)
res = {}
# Q1 (long liquidations after a fall → long) and Q4 (short liquidations after a rise → short)
def flushes(side):
    ev = []
    for sym, df in W['coins'].items():
        f = full(df); p = f.pC; liq = f.liqL if side == 'L' else f.liqS; nz = liq[liq > 0]
        if len(nz) < 5: continue
        thr = 10*nz.median(); mv = p/p.shift(15) - 1; cond = (mv <= -0.01) if side == 'L' else (mv >= 0.01); sgn = 1 if side == 'L' else -1
        oi = d['pos'].get(sym, {}).get('oi') or []; ois = pd.Series([r[1] for r in oi], index=pd.to_datetime([r[0] for r in oi], unit='ms')).sort_index() if oi else None
        last = None
        for t in f.index[(liq >= thr) & cond]:
            if last is not None and (t - last) < pd.Timedelta(minutes=60): continue
            k = f.index.get_loc(t)
            if k + 61 >= len(f) or not (p.iloc[k+1] > 0) or not (p.iloc[k+61] > 0): continue
            out = sgn*(p.iloc[k+61]/p.iloc[k+1] - 1) - COST; grp = 'N'
            if ois is not None and len(ois):
                a = ois.asof(t); b = ois.asof(t - pd.Timedelta(minutes=15))
                if a > 0 and b > 0 and a/b - 1 <= -0.005: grp = 'F'
            ev.append((t, sym, grp, out)); last = t
    return pd.DataFrame(ev, columns=['t', 'sym', 'grp', 'out'])
allev = []
for q, side in (('Q1', 'L'), ('Q4', 'S')):
    E = flushes(side); allev.append(E)
    for g in ('F', 'N'):
        x = E[E.grp == g]; tt, nh = tclust(x.t, x.out) if len(x) else (None, 0)
        res[q + '_' + g] = dict(n=int(len(x)), mean=float(x.out.mean()) if len(x) else None, t=tt, hours=nh)
    F_, N_ = res[q + '_F'], res[q + '_N']; res[q + '_pass'] = bool(F_['n'] >= 30 and F_['mean'] is not None and F_['mean'] > 0 and (F_['t'] or 0) >= 1.65 and (N_['mean'] is None or F_['mean'] > N_['mean']))
    print(f"{q} {'liquidation flushes (longs)' if side == 'L' else 'short squeezes'}: falling OI n={F_['n']} mean={F_['mean']} t={F_['t']} | other n={N_['n']} mean={N_['mean']} | {'PASS' if res[q + '_pass'] else 'FAIL / not enough events'}")
A = pd.concat(allev) if allev else pd.DataFrame(columns=['t', 'out'])
if len(A):
    thin = A.t.dt.hour.isin(list(range(21, 24)) + list(range(0, 8)))
    res['Q5'] = dict(thin_n=int(thin.sum()), thin_mean=float(A.out[thin].mean()) if thin.any() else None, busy_n=int((~thin).sum()), busy_mean=float(A.out[~thin].mean()) if (~thin).any() else None)
else: res['Q5'] = dict(thin_n=0, busy_n=0)
print('Q5 thin hours (21:00–08:00 UTC) vs busy hours, reversal outcome:', res['Q5'])
# Q2 absorption on the tape
tr = []
for sym, df in W['coins'].items():
    f = full(df); p = f.pC; imb = (f.pBuy - f.pSell)/(f.pBuy + f.pSell); r1 = p/p.shift(1) - 1
    if imb.notna().sum() < 100: continue
    hi, lo = imb.quantile(0.95), imb.quantile(0.05); k = 0; n = len(f)
    while k < n - 17:
        s = -1 if (imb.iloc[k] >= hi and r1.iloc[k] <= 0) else (1 if (imb.iloc[k] <= lo and r1.iloc[k] >= 0) else 0)
        if s and p.iloc[k+1] > 0 and p.iloc[k+16] > 0: g = s*(p.iloc[k+16]/p.iloc[k+1] - 1); tr.append((f.index[k], sym, s, g, g - COST)); k += 16; continue
        k += 1
T = pd.DataFrame(tr, columns=['t', 'sym', 'd', 'gross', 'net'])
tt, nh = tclust(T.t, T.net) if len(T) else (None, 0)
res['Q2'] = dict(n=int(len(T)), gross=float(T.gross.mean()) if len(T) else None, net=float(T.net.mean()) if len(T) else None, t=tt, hours=nh); res['Q2_pass'] = bool(len(T) and T.net.mean() > 0 and (tt or 0) >= 1.65)
print(f"Q2 absorption: trades={res['Q2']['n']} gross={res['Q2']['gross']} net={res['Q2']['net']} t={tt} | {'PASS' if res['Q2_pass'] else 'FAIL'}")
# Q3 Coinbase vs Binance
m = full(W['market']); cb, bn, cu = m.cbBTC, m.bnBTC, m.cbUSDT
rc, rb = np.log(cb).diff(), np.log(bn).diff(); ok = rc.notna() & rb.shift(-1).notna(); ok2 = rb.notna() & rc.shift(-1).notna()
def corr_t(a, b):
    a, b = a.dropna(), b.reindex(a.dropna().index).dropna(); a = a.reindex(b.index); n = len(a)
    if n < 10: return None, None, n
    r = float(np.corrcoef(a, b)[0, 1]); return r, r*np.sqrt((n - 2)/max(1 - r*r, 1e-12)), n
lead = corr_t(rc[ok], rb.shift(-1)[ok]); lag = corr_t(rb[ok2], rc.shift(-1)[ok2])
prem = cb/(bn*cu.where(cu > 0, 1.0)) - 1; fwd = bn.shift(-60)/bn - 1; pc = corr_t(prem, fwd)
res['Q3'] = dict(lead=lead[0], lead_t=lead[1], lag=lag[0], n=lead[2], premium_vs_next60=pc[0], premium_n=pc[2]); res['Q3_coinbase_leads'] = bool(lead[0] is not None and lag[0] is not None and lead[0] - lag[0] >= 0.05 and (lead[1] or 0) >= 3)
print(f"Q3 Coinbase→Binance next minute r={lead[0]} (t {lead[1]}, n {lead[2]}) | Binance→Coinbase r={lag[0]} | premium vs next 60 min r={pc[0]} (n {pc[2]}) | Coinbase leads: {res['Q3_coinbase_leads']}")
json.dump(res, open('E13_result' + ('_DRYRUN' if DRY else '') + '.json', 'w'), indent=1, default=str)
