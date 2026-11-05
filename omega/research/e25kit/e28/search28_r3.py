"""E28 round 3 (discovery only): executable single-portfolio versions of the survivors, for a 100 USDT account (k ≤ 10 per side)."""
import numpy as np, json, sys
import engine28 as E, features28 as FT
F = FT.F; T, N, U = E.T, E.N, E.U; a, b = E.STAGES['discovery']; MODE = sys.argv[1]; rng = np.random.default_rng(283); D = range(a - 40, b)
def prank(sig):
    P = np.full((T, N), np.nan, np.float32)
    for d in D:
        ok = U[d] & np.isfinite(sig[d]); idx = np.where(ok)[0]
        if len(idx) > 1:
            v = rng.permutation(len(idx)).astype(np.float32) if MODE == 'luck' else np.argsort(np.argsort(sig[d, idx], kind='stable'), kind='stable')
            P[d, idx] = v/(len(idx) - 1)
    return P
Rf1, Rf7, Rsz = 1 - prank(F['fund1']), 1 - prank(F['fund7']), 1 - prank(F['size'])
SIG = {'A fund1 0.75 + size 0.25': 0.75*Rf1 + 0.25*Rsz, 'B size': Rsz, 'C fund7': Rf7, 'D fund1 0.5 + size 0.5': 0.5*Rf1 + 0.5*Rsz}
def rebal_every(s, k, R):
    w = np.zeros((T, N), np.float32); cur = None
    for d in D:
        if cur is None or (d - a) % R == 0:
            x = s[d]; idx = np.where(np.isfinite(x))[0]
            if len(idx) >= 2*k: o = idx[np.argsort(x[idx], kind='stable')]; cur = (o[-k:], o[:k])
        if cur is not None:
            hi, lo = [j for j in cur[0] if U[d, j]], [j for j in cur[1] if U[d, j]]      # a coin that left the universe is closed
            if hi: w[d, hi] = 0.5/k
            if lo: w[d, lo] = -0.5/k
    return w*E.ALIVE
def band(s, k, m):
    w = np.zeros((T, N), np.float32); L, S = [], []
    for d in D:
        x = s[d]; idx = np.where(np.isfinite(x))[0]
        if len(idx) < 2*m*k: continue
        o = idx[np.argsort(x[idx], kind='stable')]; n = len(o); rank = {j: r for r, j in enumerate(o)}
        L = [j for j in L if j in rank and rank[j] >= n - m*k]; S = [j for j in S if j in rank and rank[j] < m*k]   # keep while inside the band
        for j in o[::-1]:
            if len(L) >= k: break
            if j not in L and j not in S: L.append(j)
        for j in o:
            if len(S) >= k: break
            if j not in S and j not in L: S.append(j)
        w[d, L] = 0.5/k; w[d, S] = -0.5/k
    return w*E.ALIVE
out = open(f'round3_{MODE}.jsonl', 'w'); n = 0
for nm, s in SIG.items():
    for k in (5, 10):
        for R in (1, 3, 7, 14):
            P = E.pnl(rebal_every(s, k, R)); r = E.evaluate(P); r.update(sig=nm, impl=f'rebuild every {R}d', k=k, trade_days=float((np.abs(np.diff(rebal_every(s, k, R)[a:b], axis=0)).sum(1) > 1e-9).mean())); out.write(json.dumps(r) + '\n'); n += 1
        for m in (2, 3, 4):
            W = band(s, k, m); P = E.pnl(W); r = E.evaluate(P); r.update(sig=nm, impl=f'daily band x{m}', k=k, trade_days=float((np.abs(np.diff(W[a:b], axis=0)).sum(1) > 1e-9).mean())); out.write(json.dumps(r) + '\n'); n += 1
print('DONE', n)
