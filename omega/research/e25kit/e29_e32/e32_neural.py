"""PLAN E32 (md5 3a3151c0…): neural network ranking next-day returns; train 2021–23, select on 2024, final once."""
import numpy as np, json, time, sys, warnings; warnings.simplefilter('ignore')
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import Ridge
import engine28 as E, features28 as FT
T, N, U = E.T, E.N, E.U; ST = E.STAGES; a0, b0 = ST['discovery']; a1, b1 = ST['validation']; a2, b2 = ST['final']
names = sorted(FT.F); print(len(names), 'inputs:', names, flush=True)
def prank(x):
    P = np.full((T, N), np.nan, np.float32)
    for d in range(a0 - 5, b2):
        ok = U[d] & np.isfinite(x[d]); idx = np.where(ok)[0]
        if len(idx) > 1: P[d, idx] = np.argsort(np.argsort(x[d, idx], kind='stable'), kind='stable')/(len(idx) - 1)
    return P
X3 = np.stack([np.nan_to_num(prank(FT.F[k]), nan=0.5) for k in names], axis=2)          # T × N × K
Y = prank(np.where(U, E.R1, np.nan))                                                     # next-day return rank (R1[d] = held during d+1)
def rows(a, b, y):
    m = U[a:b] & np.isfinite(y[a:b]); d, j = np.where(m); return X3[a:b][d, j], y[a:b][d, j]
def score(model):
    S = np.full((T, N), np.nan, np.float32)
    for d in range(a1 - 5, b2):
        idx = np.where(U[d])[0]
        if len(idx): S[d, idx] = model.predict(X3[d, idx])
    return S
def band(s, k=10, m=3):
    w = np.zeros((T, N), np.float32); Lg, Sh = [], []
    for d in range(a1 - 5, b2):
        x = s[d]; idx = np.where(np.isfinite(x))[0]
        if len(idx) < 2*m*k: continue
        o = idx[np.argsort(x[idx], kind='stable')]; n = len(o); rk = {j: r for r, j in enumerate(o)}
        Lg = [j for j in Lg if j in rk and rk[j] >= n - m*k]; Sh = [j for j in Sh if j in rk and rk[j] < m*k]
        for j in o[::-1]:
            if len(Lg) >= k: break
            if j not in Lg and j not in Sh: Lg.append(j)
        for j in o:
            if len(Sh) >= k: break
            if j not in Sh and j not in Lg: Sh.append(j)
        w[d, Lg] = 0.5/k; w[d, Sh] = -0.5/k
    return w*E.ALIVE
def longonly(s, k=10):
    w = np.zeros((T, N), np.float32)
    for d in range(a1 - 5, b2):
        x = s[d]; idx = np.where(np.isfinite(x))[0]
        if len(idx) >= k: w[d, idx[np.argsort(x[idx])[-k:]]] = 1.0/k
    return w*E.ALIVE
CFG = [((16,), 1e-4), ((16,), 1e-2), ((32, 16), 1e-4), ((32, 16), 1e-2), ((64, 32), 1e-4), ((64, 32), 1e-2)]
def pipeline(y, tag):
    Xt, yt = rows(a0, b0, y); out = []
    for h, al in CFG:
        t0 = time.time(); m = MLPRegressor(hidden_layer_sizes=h, alpha=al, early_stopping=True, validation_fraction=0.15, max_iter=200, random_state=32).fit(Xt, yt)
        S = score(m); W = band(S); r = E.evaluate(E.pnl(W), 'validation'); out.append((r['t'], h, al, m, S, r)); print(tag, h, al, f"2024 t {r['t']:+.2f} net {r['mean_bp']:+.1f} bp/day", round(time.time() - t0), 's', flush=True)
    return out
MODE = sys.argv[1] if len(sys.argv) > 1 else 'real'
if MODE == 'real':
    res = pipeline(Y, 'real'); best = max(res, key=lambda x: x[0]); t, h, al, m, S, rv = best
    rid = Ridge(alpha=1.0).fit(*rows(a0, b0, Y)); rr = E.evaluate(E.pnl(band(score(rid))), 'validation')
    print(f'ridge (reported): 2024 t {rr["t"]:+.2f} net {rr["mean_bp"]:+.1f}', flush=True)
    print(f'SELECTED {h} alpha {al} (2024 t {t:+.2f}) → FINAL, once:', flush=True)
    P = E.pnl(band(S)); fin = E.evaluate(P, 'final'); lo = E.evaluate(E.pnl(longonly(S)), 'final')
    e = np.cumprod(1 + P['net'][a2:b2]); dd = float((e/np.maximum.accumulate(e) - 1).min())
    ok = fin['t'] >= 2.0 and fin['mean_bp'] > 0 and all(fin['years'].get(y, -1) > 0 for y in (2025, 2026)) and dd > -0.35
    print(json.dumps(dict(final=fin, maxdd=dd, longonly=lo, passed=bool(ok)), default=float)[:1500], flush=True); print('VERDICT', 'PASS' if ok else 'FAIL', flush=True)
    json.dump(dict(selected=dict(hidden=h, alpha=al, val=rv), all_val=[dict(hidden=x[1], alpha=x[2], val=x[5]) for x in res], ridge_val=rr, final=fin, maxdd=dd, longonly=lo, passed=bool(ok)), open('E32_result.json', 'w'), indent=1, default=float)
else:
    rng = np.random.default_rng(int(MODE[-1])); Ys = Y.copy()
    for d in range(a0, b0):
        idx = np.where(np.isfinite(Ys[d]))[0]; Ys[d, idx] = Ys[d, rng.permutation(idx)]
    res = pipeline(Ys, MODE); print('LUCK best 2024 t', max(x[0] for x in res), flush=True)
