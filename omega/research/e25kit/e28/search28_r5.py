"""E28 round 5 (discovery only): time-series timing of BTC, ETH and a top-10 basket from market-wide gauges.
Each gauge is ranked against its own previous 365 days (≥ 180) — causal. Position for day d+1 from the rank at the close of d:
long-short (top q → +1, bottom q → −1), long-only or short-only; sign ±; held H days (overlapping, averaged).
Costs 0.10%/side on position changes, funding paid/received. Ranked by weakest discovery year. MODE luck: each gauge's history
is circularly shifted by a random offset (keeps its rhythm, breaks any link to future prices)."""
import numpy as np, json, sys
import engine28 as E, features28 as FT
F = FT.F; T, N, U = E.T, E.N, E.U; a, b = E.STAGES['discovery']; MODE = sys.argv[1]; rng = np.random.default_rng(285); STAGE_END = E.STAGES[sys.argv[2]][1] if len(sys.argv) > 2 else b
SY = list(E.SYMS); iB, iE = SY.index('BTCUSDT'), SY.index('ETHUSDT')
def med(x): return np.nanmedian(np.where(U, x, np.nan), axis=1)
r1 = F['ret1']
G = {'fund_med':med(F['fund1']), 'fund7_med':med(F['fund7']), 'fund_btc':F['fund1'][:, iB], 'breadth_up':np.nanmean(np.where(U, (r1 > 0).astype(float), np.nan), axis=1),
     'above_ma30':np.nanmean(np.where(U, (F['ma30'] > 0).astype(float), np.nan), axis=1), 'dispersion':np.nanstd(np.where(U, r1, np.nan), axis=1),
     'mkt_ret1':med(r1), 'mkt_ret3':med(F['ret3']), 'mkt_ret7':med(F['ret7']), 'mkt_ret30':med(F['ret30']), 'btc_vol7':F['vol7'][:, iB], 'btc_ret7':F['ret7'][:, iB],
     'btc_vs_alts7':F['ret7'][:, iB] - med(F['ret7']), 'mkt_range':med(F['range1']), 'dv_surge':med(F['dvsurge7'])}
def prank(x):
    out = np.full(T, np.nan)
    for d in range(T):
        w = x[max(0, d - 365):d]; w = w[np.isfinite(w)]
        if len(w) >= 180 and np.isfinite(x[d]): out[d] = (w < x[d]).mean()
    return out
# asset daily returns held during d+1 (R1 row d), funding during d+1
top10 = np.zeros((T, N), bool)
for d in range(T):
    idx = np.where(U[d])[0]
    if len(idx): top10[d, idx[np.argsort(-E.DV[d, idx])[:10]]] = True
ASSET = {'BTC':(E.R1[:, iB].astype(float), E.FD[:, iB].astype(float)), 'ETH':(E.R1[:, iE].astype(float), E.FD[:, iE].astype(float)),
         'TOP10':((E.R1*top10).sum(1)/np.maximum(top10.sum(1), 1), (E.FD*top10).sum(1)/np.maximum(top10.sum(1), 1))}
def run(rank, q, mode, sign, H, asset):
    s = np.zeros(T)
    s[rank >= 1 - q] = 1; s[rank <= q] = -1
    if mode == 'L': s[s < 0] = 0
    if mode == 'S': s[s > 0] = 0
    s *= sign; s[~np.isfinite(rank)] = 0
    if H > 1: s = np.convolve(s, np.ones(H)/H)[:T]           # overlapping: average of the last H signals
    r, f = ASSET[asset]; turn = np.abs(np.diff(np.r_[0, s]))
    ser = s*r - s*f - 0.001*turn
    return ser, float((s != 0).mean())
def ev(ser, inmkt):
    yrs = {y: float(ser[max(a, E.DAY(f'{y}-01-01')):E.DAY(f'{y + 1}-01-01')].mean()*1e4) for y in (2021, 2022, 2023)}
    e = np.cumprod(1 + ser[a:b]); return dict(mean_bp=float(ser[a:b].mean()*1e4), t=E.wt(ser, a, b), years=yrs, worst_year=min(yrs.values()), maxdd=float((e/np.maximum.accumulate(e) - 1).min()), in_market=inmkt)
out = open(f'round5_{MODE}.jsonl', 'w'); n = 0
for g, x in G.items():
    if MODE == 'luck': x = np.roll(x, int(rng.integers(200, T - 200)))
    rk = prank(np.asarray(x, float))
    for asset in ASSET:
        for mode in ('LS', 'L', 'S'):
            for sign in (1, -1):
                for q in (0.1, 0.2, 0.3, 0.5):
                    if mode != 'LS' and q == 0.5: pass
                    for H in (1, 3, 7):
                        ser, im = run(rk, q, mode, sign, H, asset); r = ev(ser, im); r.update(gauge=g, asset=asset, mode=mode, sign=sign, q=q, H=H); out.write(json.dumps(r) + '\n'); n += 1
    out.flush(); print(g, n, flush=True)
print('DONE', n, flush=True)
