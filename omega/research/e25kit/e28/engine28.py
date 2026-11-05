"""E28 search engine: daily panel, universe, features, cross-sectional and time-series variants, costs, funding, diagnostics."""
import numpy as np, os, json, datetime as dt
Z = np.load('daily_panel.npz'); O, Hh, L, C, DV, NH = Z['O'], Z['H'], Z['L'], Z['C'], Z['DV'], Z['NH']; LASTD, FIRSTD, DAYS, SYMS = Z['LASTD'], Z['FIRSTD'], Z['days'], Z['syms']
T, N = C.shape; DAY = lambda s: int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp()//86400) - int(DAYS[0])
COST, PEN = 0.001, 0.05
# ---- forward returns: held during day d+1 for a position formed at the close of day d ----
R1 = np.zeros((T, N), np.float32); DEL = np.zeros((T, N), bool)
with np.errstate(invalid='ignore', divide='ignore'):
    nxt = C[1:]/C[:-1] - 1
R1[:-1] = np.nan_to_num(nxt, nan=0.0, posinf=0.0, neginf=0.0)
ALIVE = np.arange(T)[:, None] <= LASTD[None, :]          # no position can be held past a coin's last traded day
for j in range(N):
    ld = LASTD[j]
    if 0 <= ld < T - 8: DEL[ld, j] = True        # a position still held at its last close exits there, 5% against it (once)
# ---- funding: sum of rates paid during day d+1 ----
FD = np.zeros((T, N), np.float32)
if os.path.exists('daily_funding.npy'): FD[:-1] = np.load('daily_funding.npy')[1:]
# ---- universe at the close of day d ----
with np.errstate(invalid='ignore'):
    dvm = np.full((T, N), np.nan, np.float32)
    import warnings; warnings.simplefilter('ignore', RuntimeWarning)
    for d in range(30, T): dvm[d] = np.nanmedian(np.where(NH[d - 29:d + 1] > 0, DV[d - 29:d + 1], np.nan), axis=0)
AGE = (np.arange(T)[:, None] - FIRSTD[None, :]) >= 60
U = (NH == 24) & AGE & np.isfinite(dvm) & np.isfinite(C)
rk = np.full((T, N), np.inf, np.float32)
for d in range(T):
    m = U[d]
    if m.sum(): v = np.where(m, -dvm[d], np.inf); o = np.argsort(v); r = np.empty(N); r[o] = np.arange(N); rk[d] = r
U &= rk < 100
np.save('universe28.npy', U)
STAGES = {'discovery': (DAY('2021-01-01'), DAY('2024-01-01')), 'validation': (DAY('2024-01-01'), DAY('2025-01-01')), 'final': (DAY('2025-01-01'), DAY('2026-10-01'))}
def positions(sig, k, side, H, univ=U):
    """sig: T×N feature (higher = more long). Cohort weights: top-k long, bottom-k short (equal weight, gross 1). Held H days."""
    s = np.where(univ, sig, np.nan); w = np.zeros((T, N), np.float32)
    for d in range(T):
        x = s[d]; ok = np.isfinite(x); n = ok.sum()
        if n < 2*k: continue
        idx = np.where(ok)[0]; o = idx[np.argsort(x[ok])]
        lo, hi = o[:k], o[-k:]
        if side == 'LS': w[d, hi] += 0.5/k; w[d, lo] -= 0.5/k
        elif side == 'L': w[d, hi] += 1.0/k
        elif side == 'S': w[d, lo] -= 1.0/k
    if H == 1: return w*ALIVE
    cs = np.cumsum(w, axis=0, dtype=np.float64)
    W = (cs - np.vstack([np.zeros((H, N)), cs[:-H]]))/H
    return (W*ALIVE).astype(np.float32)
def pnl(W):
    """daily net return series (per unit gross) and parts. W[d] = weights held during day d+1."""
    gross = (W*R1).sum(1); fund = -(W*FD).sum(1); turn = np.abs(np.diff(np.vstack([np.zeros((1, N)), W]), axis=0)).sum(1)
    cost = COST*turn; pen = -PEN*(np.abs(W)*DEL).sum(1)
    net = gross + fund - cost + pen
    return dict(net=net, gross=gross, fund=fund, cost=cost, pen=pen, long=(np.clip(W, 0, None)*R1).sum(1), short=(np.clip(W, None, 0)*R1).sum(1), active=(np.abs(W).sum(1) > 0))
def wt(x, a, b):
    """weekly t-statistic of daily series x over days [a, b)."""
    y = x[a:b]; n = len(y)//7*7; w = y[:n].reshape(-1, 7).sum(1)
    return float(w.mean()/w.std(ddof=1)*np.sqrt(len(w))) if len(w) > 2 and w.std() > 0 else 0.0
def evaluate(P, stage='discovery'):
    a, b = STAGES[stage]; net = P['net'][a:b]; e = np.cumprod(1 + net); dd = float((e/np.maximum.accumulate(e) - 1).min())
    srt = np.sort(net)[::-1]; top = float(srt[:max(1, len(net)//20)].sum()/net.sum()) if net.sum() > 0 else None
    yrs = {}; 
    for y in range(2021, 2027):
        ya, yb = max(a, DAY(f'{y}-01-01')), min(b, DAY(f'{y + 1}-01-01'))
        if yb > ya: yrs[y] = float(P['net'][ya:yb].mean()*1e4)
    return dict(mean_bp=float(net.mean()*1e4), gross_bp=float(P['gross'][a:b].mean()*1e4), cost_bp=float(P['cost'][a:b].mean()*1e4), fund_bp=float(P['fund'][a:b].mean()*1e4),
                pen_bp=float(P['pen'][a:b].mean()*1e4), t=wt(P['net'], a, b), sharpe=float(net.mean()/net.std()*np.sqrt(365)) if net.std() > 0 else 0.0, maxdd=dd,
                long_bp=float(P['long'][a:b].mean()*1e4), short_bp=float(P['short'][a:b].mean()*1e4), active=float(P['active'][a:b].mean()), top5_share=top, years=yrs)
