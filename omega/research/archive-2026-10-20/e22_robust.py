import sys, json, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load; from e21_lib import hourly_from; from e22_lib import prep, run, wt, masks
A1, B1 = [pd.Timestamp(x).value//3600_000_000_000 for x in ('2024-01-01', '2026-10-18')]
spec = json.load(open('plans/E22_kept.json'))['H1']['spec']; rows = []
for part in ['final4_a', 'final4_b', 'final4_c', 'final4_d', 'final4_young']:
    d, ms = load(part); tf = int(d.get('tf', 60))
    for mk in ms:
        P = prep(hourly_from(mk, (mk['t']*tf*60).astype(np.int64)))
        for h, r in run(P, masks(P, spec), 'limit', A1, B1, min_age=720, k=spec['k'], W=spec['W']): rows.append((mk['sym'], h, r))
T = pd.DataFrame(rows, columns=['sym', 'h', 'r']); FUND = 0.0003
print(f"H1 on the 324 perpetuals: {len(T)} trades on {T.sym.nunique()} coins")
m0, t0, _ = wt(list(zip(T.h, T.r))); m1, t1, _ = wt(list(zip(T.h, T.r - FUND)))
print(f"1. funding of 0.03% a day charged to every trade: net {m0*100:+.3f}% → {m1*100:+.3f}% a trade, t {t0:.2f} → {t1:.2f}")
cut = T.r.quantile(0.95); T2 = T[T.r < cut]; m2, t2, _ = wt(list(zip(T2.h, T2.r - FUND))); print(f"2. without the best 5% of trades (and with funding): {m2*100:+.3f}% a trade, t {t2:.2f}")
pc = T.groupby('sym').r.mean(); big = T.groupby('sym').r.size() >= 20; print(f"3. coins with 20+ trades: {int(big.sum())}; of those, net positive: {int((pc[big] > 0).sum())} ({(pc[big] > 0).mean()*100:.0f}%)")
T['d'] = T.h//24; daily = (T.groupby('d').r.mean() - FUND).reindex(range(int(T.d.min()), int(T.d.max()) + 1), fill_value=0.0)
eq = (1 + daily*0.10).cumprod(); dd = (eq/eq.cummax() - 1).min(); yrs = (len(daily))/365.25
print(f"4. an account putting 10% of equity into each day's average H1 trade: ×{eq.iloc[-1]:.2f} over {yrs:.1f} years ({(eq.iloc[-1]**(1/yrs) - 1)*100:+.1f}%/yr), worst drawdown {dd*100:.1f}%, daily Sharpe×√365 {daily.mean()/daily.std()*np.sqrt(365):.2f}")
print(f"   days with at least one trade: {(T.groupby('d').size() > 0).sum()} of {len(daily)}; trades per active day, median {int(T.groupby('d').size().median())}")
json.dump(dict(funding=[m1, t1], no_top5=[m2, t2], coins_pos=float((pc[big] > 0).mean())), open('plans/E22_robust.json', 'w'), indent=1)
