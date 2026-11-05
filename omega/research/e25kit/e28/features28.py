"""Features at the close of day d (only data up to d). Higher value = 'more long' for sign +1; each is also tried with sign −1."""
import numpy as np, warnings; warnings.simplefilter('ignore')
import engine28 as E
C, O, Hh, L, DV, T, N = E.C, E.O, E.Hh, E.L, E.DV, E.T, E.N
lc = np.log(C); r = np.vstack([np.full((1, N), np.nan), np.diff(lc, axis=0)])         # daily log return of day d
def lag(x, k): return np.vstack([np.full((k, x.shape[1]), np.nan), x[:-k]])
def roll(x, k, f):
    out = np.full((T, N), np.nan, np.float32)
    for d in range(k - 1, T): out[d] = f(x[d - k + 1:d + 1], axis=0)
    return out
F = {}
for k in (1, 2, 3, 5, 7, 14, 30, 60): F[f'ret{k}'] = lc - lag(lc, k)                 # past k-day return
mkt = np.nanmedian(np.where(E.U, r, np.nan), axis=1)[:, None]                          # market (median coin) daily return
F['vol7'] = roll(r, 7, np.nanstd); F['vol30'] = roll(r, 30, np.nanstd); F['volratio'] = F['vol7']/F['vol30']
F['range1'] = (Hh - L)/C; F['range_rel'] = F['range1']/roll(np.nan_to_num((Hh - L)/C, nan=np.nan), 30, np.nanmean)
F['clv'] = (C - L)/(Hh - L)                                                            # where the day closed in its range
F['intraday'] = np.log(C/O)
F['dvsurge1'] = DV/roll(DV, 30, np.nanmedian); F['dvsurge7'] = roll(DV, 7, np.nanmean)/roll(DV, 30, np.nanmedian)
F['ma7'] = C/roll(C, 7, np.nanmean) - 1; F['ma30'] = C/roll(C, 30, np.nanmean) - 1
F['max30'] = roll(r, 30, np.nanmax); F['min30'] = roll(r, 30, np.nanmin)
F['pos30'] = (C - roll(L, 30, np.nanmin))/(roll(Hh, 30, np.nanmax) - roll(L, 30, np.nanmin))
mu = roll(r, 30, np.nanmean); sd = F['vol30']; F['skew30'] = (roll(r**3, 30, np.nanmean) - 3*mu*sd**2 - mu**3)/sd**3            # skewness of the last 30 days
b = 'BTCUSDT' in list(E.SYMS) and list(E.SYMS).index('BTCUSDT'); rb = r[:, b:b + 1]
cov = roll(r*rb, 30, np.nanmean) - roll(r, 30, np.nanmean)*roll(np.repeat(rb, N, 1), 30, np.nanmean); F['beta30'] = cov/(roll(np.repeat(rb, N, 1), 30, np.nanstd)**2)
BC = np.cumsum(np.nan_to_num(rb), axis=0)                                            # BTC cumulative log return
for k in (1, 3, 7, 30): F[f'res{k}'] = F[f'ret{k}'] - F['beta30']*(BC - lag(BC, k))   # the coin's own move, net of its BTC beta
F['size'] = np.log(roll(DV, 30, np.nanmedian))                                        # liquidity / size
F['age'] = np.log1p(np.arange(T)[:, None] - E.FIRSTD[None, :]).astype(np.float32)
F['zret1'] = r/F['vol30']                                                              # yesterday's move in its own sigmas
if E.FD.any():
    FDn = np.zeros((T, N), np.float32); FDn[1:] = E.FD[:-1]                            # funding paid during day d (known at its close)
    F['fund1'] = FDn; F['fund7'] = roll(FDn, 7, np.nanmean)
for k in list(F): F[k] = np.where(np.isfinite(F[k]), F[k], np.nan).astype(np.float32)
