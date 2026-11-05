"""PLAN E34 (md5 9693ae6d…): delta-neutral funding harvest. Discovery 2021–2024 picks one variant; final 2025-01 → 2026-09 once."""
import numpy as np, json, re
import engine28 as E
T, N, U, FD = E.T, E.N, E.U, E.FD; SY = list(E.SYMS)
spot = set(json.load(open('spot_usdt_symbols.json')))
def base(s): return re.sub(r'^(1000000|1000|1M)', '', s)
HAS = np.array([(s in spot) or (base(s) in spot) for s in SY])
EL = U & HAS[None, :]                                                  # eligible at the close of day d
FK = np.zeros((T, N), np.float32); FK[1:] = FD[:-1]                   # funding paid during day d, known at its close
A0, A1, B0, B1 = E.DAY('2021-01-01'), E.DAY('2025-01-01'), E.DAY('2025-01-01'), E.DAY('2026-10-01')
def run(k, L, R, m, a, b, luck=False, rng=None):
    cs = np.cumsum(FK, axis=0); ret = np.zeros(T); held = set(); neg = []; nh = 0
    for d in range(a, b):
        if (d - a) % R == 0:
            idx = np.where(EL[d])[0]
            avg = (cs[d, idx] - cs[d - L, idx])/L*365 if d >= L else np.zeros(len(idx))
            if luck: pick = set(rng.choice(idx, size=min(k, len(idx)), replace=False).tolist()) if len(idx) else set()
            else:
                order = np.argsort(-avg); pick = set(int(idx[i]) for i in order[:k] if avg[i] >= m)
            cost = 0.0025*(len(pick - held) + len(held - pick)); held = pick; ret[d] -= cost/(2*k)
        for j in list(held):
            if not E.ALIVE[d, j]: ret[d] -= 0.05/(2*k); held.discard(j); continue
            ret[d] += FD[d, j]/(2*k); nh += 1; neg.append(FD[d, j] < 0)
    return ret, (np.mean(neg) if neg else 0.0), nh
def stats(ret, a, b):
    x = ret[a:b]; w = x[:len(x)//7*7].reshape(-1, 7).sum(1); t = float(w.mean()/w.std(ddof=1)*np.sqrt(len(w))) if w.std() > 0 else 0.0
    r30 = np.convolve(x, np.ones(30), 'valid'); yrs = {}
    for y in range(2021, 2027):
        ya, yb = max(a, E.DAY(f'{y}-01-01')), min(b, E.DAY(f'{y + 1}-01-01'))
        if yb > ya: yrs[y] = round(float(x[ya - a:yb - a].mean()*365*100), 2)
    return dict(yield_pct=float(x.mean()*365*100), t=t, worst30=float(r30.min()*100) if len(r30) else 0.0, years=yrs)
GRID = [(k, L, R, m) for k in (1, 3, 5) for L in (3, 7, 14) for R in (7, 30) for m in (0.10, 0.20)]
res = []
for g in GRID:
    r, neg, nh = run(*g, A0, A1); res.append((stats(r, A0, A1), g, neg))
rng = np.random.default_rng(34); luck = [stats(run(*g, A0, A1, luck=True, rng=rng)[0], A0, A1)['t'] for g in GRID]
print(f'discovery 2021–2024, 36 variants; luck-best t {max(luck):.2f}')
for s, g, neg in sorted(res, key=lambda x: -x[0]['t'])[:6]: print(f'   k{g[0]} L{g[1]} R{g[2]} m{int(g[3]*100)}% | {s["yield_pct"]:+.2f}%/yr on capital (1×) t {s["t"]:.2f} worst 30d {s["worst30"]:+.2f}% | {s["years"]}')
best = max(res, key=lambda x: x[0]['t']); g = best[1]
r, neg, nh = run(*g, B0, B1); F = stats(r, B0, B1)
ok = F['yield_pct'] >= 4 and F['t'] >= 2.0 and all(F['years'].get(y, -1) > 0 for y in (2025, 2026)) and F['worst30'] >= -3
print(f'PICK k{g[0]} L{g[1]} R{g[2]} m{int(g[3]*100)}% → FINAL 2025-01 → 2026-09: {F["yield_pct"]:+.2f}%/yr on capital at 1× ({F["yield_pct"]*4/3:+.2f}% at 2×), t {F["t"]:.2f}, worst 30 days {F["worst30"]:+.2f}%, {F["years"]}; funding negative on {neg*100:.0f}% of held coin-days → {"PASS" if ok else "FAIL"}')
L90 = E.DAY('2026-07-02'); r9, _, _ = run(*g, L90, B1); s9 = r9[L90:B1].mean()
print(f'last 90 days (Jul–Sep 2026): {s9*365*100:+.2f}%/yr = {s9*100:+.4f}% a day = {s9*100*100:+.3f} USDT a day on 100 USDT')
json.dump(dict(discovery=[dict(g=x[1], **x[0]) for x in res], luck_best=max(luck), pick=g, final=F, neg_share=float(neg), passed=bool(ok), last90_daily_pct=float(s9*100)), open('/home/claude/omega/plans-new/E34_result.json', 'w'), indent=1, default=float)
