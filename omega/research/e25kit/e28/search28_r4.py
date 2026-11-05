"""E28 round 4 (discovery only): daily LIMIT-entry rules. At the close of day d, rank coins by a 'fallen' measure; a limit order
m×σ30 below the close (longs) / above it (shorts), valid all of day d+1; filled if day d+1 trades through it; exit at the close of
d+1 (X1) or d+2 (X2). Costs: maker 0.02% in, taker 0.05% + 0.05% slippage out = 0.12%. Funding for the days held. Capital split
into k slots per day; unfilled slots stay in cash. Ranked by the weakest discovery year. MODE luck: coins picked at random."""
import numpy as np, json, sys
import engine28 as E, features28 as FT
F = FT.F; T, N, U = E.T, E.N, E.U; C, Hh, L, NH = E.C, E.Hh, E.L, E.NH; a, b = E.STAGES['discovery']; MODE = sys.argv[1]
rng = np.random.default_rng(284); SIG30 = F['vol30']; COST = 0.0012
STAGE_END = E.STAGES[sys.argv[2]][1] if len(sys.argv) > 2 else b
def cohort(order_fn, k, m, X, side):
    """returns daily series (by exit day) of capital-weighted net return, plus fills per day."""
    ser = np.zeros(T); fills = np.zeros(T)
    for d in range(a - 5, min(STAGE_END, T - 3)):
        cand = order_fn(d)
        if cand is None or len(cand) == 0: continue
        sel = cand[:k]; tot = 0.0; nf = 0
        for j in sel:
            s = SIG30[d, j]
            if not (s > 0) or not (C[d, j] > 0): continue
            if side == 'L':
                lim = C[d, j]*np.exp(-m*s); ok = NH[d + 1, j] > 0 and L[d + 1, j] < lim
            else:
                lim = C[d, j]*np.exp(m*s); ok = NH[d + 1, j] > 0 and Hh[d + 1, j] > lim
            if not ok: continue
            ex = d + X; px = C[ex, j]; pen = 0.0
            if E.LASTD[j] < ex or not (px > 0):                      # delisted (or no candle) before the exit: last close, −5%
                lastc = C[min(E.LASTD[j], ex), j] if E.LASTD[j] >= d + 1 else lim; px = lastc if lastc > 0 else lim; pen = 0.05
            r = px/lim - 1
            if side == 'S': r = -r
            fund = -E.FD[d + 1:d + X + 1, j].sum()*(1 if side == 'L' else -1)   # FD[t] = funding during day t+1
            tot += r - COST - pen + fund; nf += 1
        ser[min(d + X, T - 1)] += tot/k/X; fills[d] = nf
    return ser, fills
def evaluate(ser, fills):
    r = dict(mean_bp=float(ser[a:b].mean()*1e4), t=E.wt(ser, a, b), fill_days=float((fills[a:b] > 0).mean()), fills_per_day=float(fills[a:b].mean()))
    yrs = {y: float(ser[max(a, E.DAY(f'{y}-01-01')):E.DAY(f'{y + 1}-01-01')].mean()*1e4) for y in (2021, 2022, 2023)}
    e = np.cumprod(1 + ser[a:b]); r.update(years=yrs, worst_year=min(yrs.values()), maxdd=float((e/np.maximum.accumulate(e) - 1).min())); return r
feats = ['ret1', 'zret1', 'ret3', 'res1', 'ret7', 'intraday', 'clv']
out = open(f'round4_{MODE}.jsonl', 'w'); n = 0
for fn in feats + ['all']:
    for side in ('L', 'S'):
        sgn = 1 if side == 'L' else -1                            # longs: most fallen first; shorts: most risen first
        def order_fn(d, fn=fn, sgn=sgn):
            idx = np.where(U[d])[0]
            if len(idx) == 0: return None
            if fn == 'all' or MODE == 'luck': return rng.permutation(idx)
            x = F[fn][d, idx]; ok = np.isfinite(x); idx = idx[ok]; return idx[np.argsort(sgn*x[ok], kind='stable')]
        for k in ((3, 5, 10, 20) if fn != 'all' else (100,)):
            for m in (0.5, 1.0, 1.5, 2.0, 3.0):
                for X in (1, 2):
                    ser, fl = cohort(order_fn, k, m, X, side); r = evaluate(ser, fl); r.update(feature=fn, side=side, k=k, m=m, X=X); out.write(json.dumps(r) + '\n'); n += 1
    out.flush(); print(fn, n, flush=True)
print('DONE', n, flush=True)
