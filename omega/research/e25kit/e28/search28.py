"""E28 round 1: cross-sectional sorts on discovery only, plus the same grid on shuffled features (luck check)."""
import numpy as np, json, sys, time
import engine28 as E, features28 as FT
F = FT.F; T, N, U = E.T, E.N, E.U; a, b = E.STAGES['discovery']
rng = np.random.default_rng(28); MODE = sys.argv[1]           # 'real' or 'luck'
def orders(sig):
    out = []
    for d in range(T):
        if d < a - 10 or d >= b: out.append(None); continue
        x = sig[d]; ok = U[d] & np.isfinite(x); idx = np.where(ok)[0]
        if MODE == 'luck': idx_sorted = rng.permutation(idx)
        else: idx_sorted = idx[np.argsort(x[ok], kind='stable')]
        out.append(idx_sorted)
    return out
def weights(od, k, side, sign):
    w = np.zeros((T, N), np.float32)
    for d, o in enumerate(od):
        if o is None or len(o) < 2*k: continue
        if sign < 0: o = o[::-1]
        lo, hi = o[:k], o[-k:]
        if side in ('LS', 'L'): w[d, hi] += (0.5 if side == 'LS' else 1.0)/k
        if side in ('LS', 'S'): w[d, lo] -= (0.5 if side == 'LS' else 1.0)/k
    return w
out = open(f'round1_{MODE}.jsonl', 'w'); n = 0; t0 = time.time()
for fname, sig in F.items():
    od = orders(sig)
    for sign in (1, -1):
        for k in (5, 10, 20):
            for side in ('LS', 'L', 'S'):
                w = weights(od, k, side, sign)
                for H in (1, 3, 7):
                    if H == 1: W = w*E.ALIVE
                    else:
                        cs = np.cumsum(w, axis=0, dtype=np.float64); W = ((cs - np.vstack([np.zeros((H, N)), cs[:-H]]))/H*E.ALIVE).astype(np.float32)
                    r = E.evaluate(E.pnl(W)); r.update(feature=fname, sign=sign, k=k, side=side, H=H); out.write(json.dumps(r) + '\n'); n += 1
    out.flush(); print(fname, n, round(time.time() - t0), flush=True)
print('DONE', n, flush=True)
