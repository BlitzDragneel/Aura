"""E35 (new-listing fade) and E36 (pairs mean reversion), PLAN_E35_E36.md (md5 64259a7e…)."""
import numpy as np, json, sys, itertools, warnings; warnings.simplefilter('ignore')
import engine28 as E
T, N, C, Hh, O, DV, NH, FD = E.T, E.N, E.C, E.Hh, E.O, E.DV, E.NH, E.FD; FIRST, LAST = E.FIRSTD, E.LASTD
D = E.DAY; A0, A1, B0, B1 = D('2021-01-01'), D('2025-01-01'), D('2025-01-01'), D('2026-10-01')
MED = np.full((T, N), np.nan)
for d in range(T): MED[d] = np.nanmedian(np.where(NH[max(0, d - 30):d + 1] > 0, DV[max(0, d - 30):d + 1], np.nan), axis=0)
def side_cost(d, j):
    v = MED[d, j]; s = 0.0002 if v >= 1e9 else 0.0005 if v >= 1e8 else 0.0015 if v >= 1e7 else 0.004
    return 0.0005 + s
def wt(entries, a, b):
    """weekly t of trade results grouped by entry week; empty weeks count as 0."""
    nw = (b - a)//7 + 1; w = np.zeros(nw)
    for d, r in entries:
        if a <= d < b: w[(d - a)//7] += r
    return float(w.mean()/w.std(ddof=1)*np.sqrt(nw)) if w.std() > 0 else 0.0
# ───────── E35 new-listing fade ─────────
LIST = [j for j in range(N) if FIRST[j] >= D('2021-01-01')]
def e35(e, H, stop, a, b, luck=None):
    out = []
    for j in LIST:
        d0 = FIRST[j] + e
        if not (a <= d0 < b) or d0 + H >= T: continue
        if luck is not None:
            pool = [x for x in range(N) if FIRST[x] <= d0 - 60 and np.isfinite(C[d0, x]) and NH[d0, x] == 24 and LAST[x] > d0]
            if not pool: continue
            j2 = pool[luck.integers(len(pool))]
        else: j2 = j
        ent = C[d0, j2]
        if not (ent > 0): continue
        cs = side_cost(d0, j2); fund = 0.0; px = None; pen = 0.0
        for t in range(d0 + 1, d0 + H + 1):
            if t > LAST[j2]: px = C[LAST[j2], j2]; pen = 0.05; break
            if stop and Hh[t, j2] >= ent*1.5: px = max(ent*1.5, O[t, j2] if O[t, j2] > 0 else 0)*(1 + cs); break
            fund += FD[t - 1, j2]
            if t == d0 + H: px = C[t, j2]
        if not (px and px > 0):
            last = np.where(np.isfinite(C[d0:d0 + H + 1, j2]))[0]; px = C[d0 + last[-1], j2]
        out.append((d0, 1 - px/ent - 2*cs - pen + fund, E.SYMS[j2]))
    return out
def summ(tr, a, b):
    r = np.array([x[1] for x in tr]); yrs = {}
    for y in range(2021, 2027):
        s = [x[1] for x in tr if D(f'{y}-01-01') <= x[0] < D(f'{y + 1}-01-01')]
        if s: yrs[y] = [round(float(np.mean(s))*100, 2), len(s)]
    k = max(1, len(r)//20); srt = np.sort(r)[::-1]
    return dict(n=len(r), mean_pct=float(r.mean()*100) if len(r) else None, median_pct=float(np.median(r)*100) if len(r) else None, win=float((r > 0).mean()) if len(r) else None,
                t=wt([(x[0], x[1]) for x in tr], a, b), years=yrs, worst_pct=float(r.min()*100) if len(r) else None, without_best5_pct=float(srt[k:].mean()*100) if len(r) > k else None)
MODE = sys.argv[1]
if MODE == 'e35':
    G = [(e, H, s) for e in (1, 3, 7) for H in (14, 30) for s in (False, True)]; rng = np.random.default_rng(35)
    disc = [(summ(e35(*g, A0, A1), A0, A1), g) for g in G]; luck = [summ(e35(*g, A0, A1, luck=rng), A0, A1)['t'] for g in G]
    print(f'E35 listings (first candle ≥ 2021): {len(LIST)}; discovery 12 variants; luck-best t {max(luck):.2f}')
    for s, g in sorted(disc, key=lambda x: -x[0]['t']): print(f"   e{g[0]} H{g[1]} stop {'+50%' if g[2] else 'none':5s} | n {s['n']:4d} mean {s['mean_pct']:+6.2f}% median {s['median_pct']:+6.2f}% win {s['win']*100:4.0f}% t {s['t']:+.2f} worst {s['worst_pct']:+.0f}% | {s['years']}")
    best = max(disc, key=lambda x: x[0]['t']); g = best[1]; F = summ(e35(*g, B0, B1 - g[1]), B0, B1)
    ok = F['n'] > 0 and F['mean_pct'] > 0 and F['t'] >= 2.0 and all(F['years'].get(y, [0, 0])[0] > 0 and F['years'][y][1] >= 10 for y in (2025, 2026))
    print(f"PICK e{g[0]} H{g[1]} stop {g[2]} → FINAL: n {F['n']} mean {F['mean_pct']:+.2f}% median {F['median_pct']:+.2f}% win {F['win']*100:.0f}% t {F['t']:+.2f} worst {F['worst_pct']:+.0f}% without best 5% {F['without_best5_pct']:+.2f}% | {F['years']} → {'PASS' if ok else 'FAIL'}")
    json.dump(dict(discovery=[dict(g=x[1], **x[0]) for x in disc], luck_best=max(luck), pick=g, final=F, passed=bool(ok)), open('/home/claude/omega/plans-new/E35_result.json', 'w'), indent=1, default=float)
# ───────── E36 pairs ─────────
def months(a, b):
    out = []; d = a
    while d < b: out.append(d); d += 30
    return out
lr = np.vstack([np.full((1, N), np.nan), np.diff(np.log(C), axis=0)])
def pairs_for(d, luck=None):
    idx = np.where(E.U[d] & np.isfinite(MED[d]))[0]; top = idx[np.argsort(-MED[d, idx])][:30]
    if luck is not None:
        P = list(itertools.combinations(sorted(top), 2)); return [P[i] for i in luck.choice(len(P), 20, replace=False)]
    R = lr[d - 59:d + 1][:, top]; sc = []
    for i, k in itertools.combinations(range(len(top)), 2):
        x, y = R[:, i], R[:, k]; m = np.isfinite(x) & np.isfinite(y)
        if m.sum() >= 50: sc.append((np.corrcoef(x[m], y[m])[0, 1], top[i], top[k]))
    sc.sort(reverse=True); return [(a_, b_) for _, a_, b_ in sc[:20]]
def e36(Lb, ze, Hm, a, b, luck=None):
    ret = np.zeros(T); openp = {}; active = []; lc = np.log(C)
    for d in range(a, b):
        if (d - a) % 30 == 0: active = pairs_for(d, luck)
        for (pa, pb), st in list(openp.items()):                      # P&L for day d (positions held from the close of d−1)
            ra, rb = C[d, pa]/C[d - 1, pa] - 1, C[d, pb]/C[d - 1, pb] - 1
            if not (np.isfinite(ra) and np.isfinite(rb)) or not (E.ALIVE[d, pa] and E.ALIVE[d, pb]):
                ret[d] -= 0.05*0.5/20; del openp[(pa, pb)]; continue
            lo_, sh_ = (pa, pb) if st['long'] == pa else (pb, pa); rl, rs = (ra, rb) if lo_ == pa else (rb, ra)
            ret[d] += (0.5*rl - 0.5*rs - 0.5*FD[d - 1, lo_] + 0.5*FD[d - 1, sh_])/20; st['days'] += 1
        for (pa, pb) in set(active) | set(openp):
            s = lc[d - Lb + 1:d + 1, pa] - lc[d - Lb + 1:d + 1, pb]
            if not np.isfinite(s).all() or s.std() == 0: continue
            z = (s[-1] - s.mean())/s.std(ddof=1); key = (pa, pb)
            if key in openp:
                st = openp[key]
                if np.sign(z) != st['sign'] or st['days'] >= Hm:
                    ret[d] -= (0.5*side_cost(d, pa) + 0.5*side_cost(d, pb))/20; del openp[key]
            elif key in active and abs(z) >= ze and len(openp) < 20:
                openp[key] = dict(sign=np.sign(z), long=pb if z > 0 else pa, days=0); ret[d] -= (0.5*side_cost(d, pa) + 0.5*side_cost(d, pb))/20
    return ret
def s36(ret, a, b):
    x = ret[a:b]; w = x[:len(x)//7*7].reshape(-1, 7).sum(1); t = float(w.mean()/w.std(ddof=1)*np.sqrt(len(w))) if w.std() > 0 else 0.0
    e = np.cumprod(1 + x); dd = float((e/np.maximum.accumulate(e) - 1).min())
    yrs = {y: round(float(x[max(a, D(f'{y}-01-01')) - a:min(b, D(f'{y + 1}-01-01')) - a].mean()*365*100), 2) for y in range(2021, 2027) if min(b, D(f'{y + 1}-01-01')) > max(a, D(f'{y}-01-01'))}
    return dict(yield_pct=float(x.mean()*365*100), t=t, maxdd=dd, years=yrs)
if MODE == 'e36':
    G = [(Lb, ze, Hm) for Lb in (10, 20) for ze in (1.5, 2.0, 2.5) for Hm in (5, 10)]; rng = np.random.default_rng(36)
    disc = [(s36(e36(*g, A0, A1), A0, A1), g) for g in G]; print('discovery done', flush=True)
    luck = [s36(e36(*g, A0, A1, luck=rng), A0, A1)['t'] for g in G]
    print(f'E36 discovery 12 variants; luck-best t {max(luck):.2f}')
    for s, g in sorted(disc, key=lambda x: -x[0]['t']): print(f"   Lb{g[0]} z{g[1]} Hm{g[2]} | {s['yield_pct']:+6.2f}%/yr t {s['t']:+.2f} dd {s['maxdd']*100:+.0f}% | {s['years']}")
    best = max(disc, key=lambda x: x[0]['t']); g = best[1]; F = s36(e36(*g, B0, B1), B0, B1)
    ok = F['yield_pct'] > 0 and F['t'] >= 2.0 and all(F['years'].get(y, -1) > 0 for y in (2025, 2026)) and F['maxdd'] > -0.25
    print(f"PICK Lb{g[0]} z{g[1]} Hm{g[2]} → FINAL: {F['yield_pct']:+.2f}%/yr t {F['t']:+.2f} dd {F['maxdd']*100:+.0f}% {F['years']} → {'PASS' if ok else 'FAIL'}")
    json.dump(dict(discovery=[dict(g=x[1], **x[0]) for x in disc], luck_best=max(luck), pick=g, final=F, passed=bool(ok)), open('/home/claude/omega/plans-new/E36_result.json', 'w'), indent=1, default=float)
