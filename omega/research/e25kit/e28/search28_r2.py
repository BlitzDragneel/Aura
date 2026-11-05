"""E28 round 2 (discovery only): composites of the two round-1 survivors (size−, funding−) with every feature as a partner,
longer holds, optional BTC-beta-neutral short leg. Same grid on shuffled composites = luck check."""
import numpy as np, json, sys, time
import engine28 as E, features28 as FT
F = FT.F; T, N, U = E.T, E.N, E.U; a, b = E.STAGES['discovery']; MODE = sys.argv[1]; rng = np.random.default_rng(282)
D = range(a - 40, b)
def prank(sig):                                   # percentile rank within the universe each day (0..1), NaN outside
    P = np.full((T, N), np.nan, np.float32)
    for d in D:
        ok = U[d] & np.isfinite(sig[d]); idx = np.where(ok)[0]
        if len(idx) > 1: P[d, idx] = np.argsort(np.argsort(sig[d, idx], kind='stable'), kind='stable')/(len(idx) - 1)
    return P
PR = {f: prank(v) for f, v in F.items()}; print('ranks ready', flush=True)
BETA = np.nan_to_num(F['beta30'], nan=1.0)
PRIM = {'size-': 1 - PR['size'], 'fund1-': 1 - PR['fund1'], 'fund7-': 1 - PR['fund7']}
def weights(score, k, bneu):
    w = np.zeros((T, N), np.float32)
    for d in D:
        x = score[d]; ok = np.isfinite(x); idx = np.where(ok)[0]
        if len(idx) < 2*k: continue
        o = idx[rng.permutation(len(idx))] if MODE == 'luck' else idx[np.argsort(x[ok], kind='stable')]
        lo, hi = o[:k], o[-k:]; w[d, hi] = 0.5/k; s = 0.5/k
        if bneu: bl, bs = BETA[d, hi].mean(), BETA[d, lo].mean(); s = s*np.clip(bl/bs, 0.25, 4) if bs > 0 else s
        w[d, lo] = -s
    return w
out = open(f'round2_{MODE}.jsonl', 'w'); n = 0; t0 = time.time()
for pn, P0 in PRIM.items():
    partners = [(None, 0, 1.0)] + [(f, sg, wt) for f in F for sg in (1, -1) for wt in (0.5, 0.25)]
    for f, sg, wt in partners:
        if f is not None and pn.startswith(f[:4]) and f in ('size', 'fund1', 'fund7'): continue
        sc = P0 if f is None else (1 - wt)*P0 + wt*(PR[f] if sg > 0 else 1 - PR[f])
        for k in (5, 10, 20):
            for bneu in (0, 1):
                w = weights(sc, k, bneu); cs = np.cumsum(w, axis=0, dtype=np.float64)
                for H in (7, 14, 30):
                    W = ((cs - np.vstack([np.zeros((H, N)), cs[:-H]]))/H*E.ALIVE).astype(np.float32)
                    r = E.evaluate(E.pnl(W)); r.update(primary=pn, partner=f, psign=sg, pw=wt, k=k, bneu=bneu, H=H); out.write(json.dumps(r) + '\n'); n += 1
        out.flush()
    print(pn, n, round(time.time() - t0), flush=True)
print('DONE', n, flush=True)
