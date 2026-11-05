import sys, json, numpy as np, pandas as pd
def prepare(T):
    T = T.sort_values('h').reset_index(drop=True); groups = [g.index.values for _, g in T.groupby('h', sort=True)]
    hours = np.array(sorted(T.h.unique())); fill = T.fill.values; net = T.net.values; sym = T.sym.values
    sc = np.zeros(len(T))
    for g in groups:
        if len(g) > 1:
            sub = T.loc[g]; sc[g] = (-sub.depth).rank().values + sub.vr.rank().values + sub.liq.rank().values + 1e-6*(-sub.depth).rank().values
    return T, groups, hours, fill, net, sym, sc
def account(T, groups, hours, fill, net, sym, sc, f, rng=None, seats=2):
    eq = 100.0; busy = []; pending = []; curve = [(hours[0], eq)]; ntr = 0
    for gi, g in enumerate(groups):
        h = hours[gi]
        for p in sorted([p for p in pending if p[0] <= h]): eq += p[1]; curve.append((p[0], eq))
        pending = [p for p in pending if p[0] > h]; busy = [b for b in busy if b[0] > h]; free = seats - len(busy)
        if free <= 0: continue
        held = {b[1] for b in busy}; cand = [i for i in g if sym[i] not in held]
        if not cand: continue
        if rng is None: cand = sorted(cand, key=lambda i: -sc[i])
        else: cand = list(rng.permutation(cand))
        for i in cand[:free]:
            if np.isnan(fill[i]): busy.append((h + 3, sym[i]))
            else:
                ex = int(fill[i]) + 24; busy.append((ex, sym[i])); pending.append((ex, f*eq*net[i])); ntr += 1
    for p in sorted(pending): eq += p[1]; curve.append((p[0], eq))
    return eq, curve, ntr
def yearly(curve):
    s = pd.Series([e for _, e in curve], index=pd.to_datetime([h*3600 for h, _ in curve], unit='s')); y = s.groupby(s.index.year).last(); prev = 100.0; out = {}
    for yr, v in y.items(): out[int(yr)] = round((v/prev - 1)*100, 1); prev = v
    dd = float((s/s.cummax() - 1).min()*100); return out, dd
OUT = {}
for name in ['perps', 'dev']:
    T, groups, hours, fill, net, sym, sc = prepare(pd.read_pickle(f'/home/claude/edge/e23_{name}.pkl'))
    for f in (0.25, 0.50):
        eqR, curveR, nR = account(T, groups, hours, fill, net, sym, sc, f); yrs, dd = yearly(curveR)
        runs = 500 if f == 0.25 else 200; rng = np.random.default_rng(23); R = np.array([account(T, groups, hours, fill, net, sym, sc, f, rng)[0] for _ in range(runs)])
        pct = float((R < eqR).mean()*100); passed = name == 'perps' and f == 0.25 and pct >= 95 and eqR > 100 and all(yrs.get(y, -1) > 0 for y in (2024, 2025, 2026))
        OUT[f'{name} f{int(f*100)}'] = dict(final=eqR, trades=nR, years=yrs, maxdd=dd, random_median=float(np.median(R)), random_p95=float(np.percentile(R, 95)), beats_pct=pct, passed=passed if (name == 'perps' and f == 0.25) else None)
        print(f"{'TEST' if name == 'perps' else 'check'} {name:5s} seat {int(f*100)}%: ranked 100 → {eqR:8.1f} ({nR} trades, worst drawdown {dd:.1f}%, by year {yrs}) | random: median {np.median(R):.1f}, 95th pct {np.percentile(R, 95):.1f} | ranked beats {pct:.0f}% of random" + (f"  → {'PASS' if passed else 'FAIL'}" if name == 'perps' and f == 0.25 else ''))
json.dump(OUT, open('plans/E23_result.json', 'w'), indent=1, default=str)
