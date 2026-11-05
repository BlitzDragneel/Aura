import sys, json, gzip, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load
SPLIT = pd.Timestamp('2024-01-01'); END = pd.Timestamp('2026-10-18 23:00')
def hourly15(m):
    t = (m['t']*900)//3600; df = pd.DataFrame({'t':t, 'o':m['o'], 'h':m['h'], 'l':m['l'], 'c':m['c'], 'q':m['v']*m['c']})
    g = df.groupby('t').agg(o=('o','first'), h=('h','max'), l=('l','min'), c=('c','last'), q=('q','sum'), n=('c','size')); g = g[g.n >= 3]; g.index = pd.to_datetime(g.index*3600, unit='s'); return g[['o','h','l','c','q']]
MK = {}
d, ms = load('creed15_2')
for m in ms: MK[m['sym']] = hourly15(m)
G = json.loads(gzip.open('/mnt/user-data/uploads/omega-history-gold1h-2026-10-20_json.gz').read())['markets'][0]
s = 10.0**-G['dp']; t = np.cumsum(np.asarray(G['t'], dtype=np.int64)); c = np.cumsum(np.asarray(G['c'], dtype=np.int64))*s; o = c + np.asarray(G['o'], dtype=np.int64)*s
gold = pd.DataFrame({'o':o, 'h':np.maximum(o, c) + np.asarray(G['h'], dtype=np.int64)*s, 'l':np.minimum(o, c) - np.asarray(G['l'], dtype=np.int64)*s, 'c':c, 'q':np.nan}, index=pd.to_datetime(t*3600, unit='s'))
MARKETS = {'XAUUSD':(gold, 0.0002, 0.03), 'DOGEUSDT':(MK['DOGEUSDT'], 0.001, 0.10), 'LINKUSDT':(MK['LINKUSDT'], 0.001, 0.10), 'LTCUSDT':(MK['LTCUSDT'], 0.001, 0.10), 'ADAUSDT':(MK['ADAUSDT'], 0.001, 0.10), 'AVAXUSDT':(MK['AVAXUSDT'], 0.001, 0.10)}
SESS = {'Asia':range(0, 8), 'London':range(8, 13), 'US':range(13, 21), 'Late':range(21, 24)}
def wk_t(p):
    w = p.groupby(p.index.to_period('W-SUN')).sum(); w = w.reindex(pd.period_range(p.index[0], p.index[-1], freq='W-SUN'), fill_value=0.0)
    return float(w.mean()/w.std()*np.sqrt(len(w))) if w.std() > 0 else 0.0
def peryr(p): return float(p.sum()/max((p.index[-1] - p.index[0]).days/365.25, 1e-9)*100)
def events(sig, H):
    pos = np.zeros(len(sig)); k = 0; n = len(sig)
    while k < n:
        if sig[k] != 0: pos[k+1:min(k+1+H, n)] = sig[k]; k += H + 1; continue
        k += 1
    return pos
def zigzag(c, th):
    """swing points: a leg ends when price reverses by at least th (fraction) from the leg's extreme"""
    hi_i = lo_i = 0; hi = lo = c[0]; trend = 0; piv = []
    for i in range(1, len(c)):
        x = c[i]
        if trend == 0:
            if x > hi: hi, hi_i = x, i
            if x < lo: lo, lo_i = x, i
            if x >= lo*(1 + th): piv.append((lo_i, lo)); trend = 1; hi, hi_i = x, i
            elif x <= hi*(1 - th): piv.append((hi_i, hi)); trend = -1; lo, lo_i = x, i
        elif trend == 1:
            if x > hi: hi, hi_i = x, i
            elif x <= hi*(1 - th): piv.append((hi_i, hi)); trend = -1; lo, lo_i = x, i
        else:
            if x < lo: lo, lo_i = x, i
            elif x >= lo*(1 + th): piv.append((lo_i, lo)); trend = 1; hi, hi_i = x, i
    return piv
OUT = {}
for name, (df, cost, th) in MARKETS.items():
    df = df[df.index <= END].copy(); r = np.log(df.c).diff().fillna(0.0); hr = df.index.hour; A = {}
    day = df.c.resample('1D').last().dropna(); dr = np.log(day).diff().dropna()
    A['up_hours_pct'] = round(float((r > 0).mean()*100), 1); A['up_days_pct'] = round(float((dr > 0).mean()*100), 1)
    A['avg_up_hour_bps'] = round(float(r[r > 0].mean()*1e4), 1); A['avg_down_hour_bps'] = round(float(r[r < 0].mean()*1e4), 1)
    A['worst1pct_hour_pct'] = round(float(r.quantile(0.01)*100), 2); A['best1pct_hour_pct'] = round(float(r.quantile(0.99)*100), 2)
    A['worst_hour'] = [round(float(r.min()*100), 1), str(r.idxmin())[:13]]; A['best_hour'] = [round(float(r.max()*100), 1), str(r.idxmax())[:13]]
    c24 = np.log(df.c).diff(24); A['worst_24h'] = [round(float((np.exp(c24.min()) - 1)*100), 1), str(c24.idxmin())[:10]]; A['best_24h'] = [round(float((np.exp(c24.max()) - 1)*100), 1), str(c24.idxmax())[:10]]
    A['skew_hourly'] = round(float(r.skew()), 2)
    # swings
    cv = df.c.values; idx = df.index; piv = zigzag(cv, th); legs = []
    for (i0, p0), (i1, p1) in zip(piv[:-1], piv[1:]): legs.append(('down' if p1 < p0 else 'up', (p1/p0 - 1)*100, (idx[i1] - idx[i0]).total_seconds()/3600, idx[i0]))
    for kind in ('down', 'up'):
        L = [x for x in legs if x[0] == kind]
        A[kind + '_legs'] = dict(n=len(L), median_pct=round(float(np.median([x[1] for x in L])), 1) if L else None, median_hours=round(float(np.median([x[2] for x in L])), 0) if L else None,
                                 biggest_pct=round(float((min if kind == 'down' else max)([x[1] for x in L])), 1) if L else None, longest_days=round(float(max([x[2] for x in L])/24), 0) if L else None)
    A['swing_threshold_pct'] = th*100
    # volatility after big down vs big up hours
    sg = r.rolling(168).std().shift(1); z = r/sg; base = r.abs().mean(); nxt = r.abs().rolling(24).mean().shift(-24)
    A['vol_after_big_down_x'] = round(float(nxt[z <= -2.5].mean()/base), 2); A['vol_after_big_up_x'] = round(float(nxt[z >= 2.5].mean()/base), 2)
    A['big_down_by_session_pct'] = {k: round(float((np.isin(hr[z <= -2.5], list(v))).mean()*100), 0) for k, v in SESS.items()}
    A['big_up_by_session_pct'] = {k: round(float((np.isin(hr[z >= 2.5], list(v))).mean()*100), 0) for k, v in SESS.items()}
    # direction split of plan E5's two-sided rules
    hi24 = df.h.rolling(24).max().shift(1); lo24 = df.l.rolling(24).min().shift(1); bo = np.where(df.c > hi24, 1, np.where(df.c < lo24, -1, 0)); ema = df.c.ewm(span=200, adjust=False).mean()
    zz = np.where(z >= 2.5, 1, np.where(z <= -2.5, -1, 0))
    two = {'R3 follow 24h breakout':events(bo, 24), 'R4 fade 24h breakout':-events(bo, 24), 'R5 follow big hour':events(zz, 4), 'R6 fade big hour':-events(zz, 4), 'R7 200h average':np.r_[0.0, np.where(df.c > ema, 1.0, -1.0)[:-1]]}
    split = {}
    for rn, p in two.items():
        p = pd.Series(p, index=df.index); ch = p.diff().abs().fillna(0.0)*cost; res = {}
        for side, msk in [('long', p > 0), ('short', p < 0)]:
            pn = (p*r).where(msk, 0.0) - ch.where(msk | (p.shift(1) > 0 if side == 'long' else p.shift(1) < 0), 0.0)
            res[side] = dict(a=round(peryr(pn[pn.index < SPLIT]), 1), b=round(peryr(pn[pn.index >= SPLIT]), 1), tb=round(wk_t(pn[pn.index >= SPLIT]), 2))
        split[rn] = res
    A['e5_direction_split'] = split
    # short-only rules
    rg = df.h - df.l; cl = np.where(rg > 0, (df.c - df.l)/rg.replace(0, np.nan), np.nan)
    volok = (df.q >= 3*df.q.rolling(168).median().shift(1)).values if name != 'XAUUSD' else np.ones(len(df), bool)
    s1 = np.where((z >= 3).values & volok & (cl <= 0.4), -1, 0)
    s2 = np.where((df.h > hi24).values & (df.c < hi24).values, -1, 0)
    lo72 = df.l.rolling(72).min().shift(1); below = (df.c < ema).values
    s4 = np.where((df.c < lo72).values & below, -1, 0)
    o13 = pd.Series(np.where(hr == 13, (df.o < ema.shift(1)).astype(float), np.nan), index=df.index).groupby(df.index.date).transform('max').fillna(0).values
    s3 = np.where((o13 > 0) & np.isin(hr, list(SESS['US'])), -1.0, 0.0)
    S = {'S1 blow-off short, 12h':events(s1, 12), 'S2 failed breakout short, 24h':events(s2, 24), 'S3 downtrend US-hours short':s3, 'S4 breakdown in downtrend, 24h':events(s4, 24)}
    res = {}
    for rn, p in S.items():
        p = pd.Series(p, index=df.index).fillna(0.0); pn = p*r - p.diff().abs().fillna(0.0)*cost; a, b = pn[pn.index < SPLIT], pn[pn.index >= SPLIT]; yb = b.groupby(b.index.year).sum()*100
        res[rn] = dict(t_a=round(wk_t(a), 2), t_b=round(wk_t(b), 2), a_yr=round(peryr(a), 1), b_yr=round(peryr(b), 1), b_years={int(k): round(float(v), 1) for k, v in yb.items()}, trades=int((p.diff().abs() > 0).sum()//2))
    pick = max(res, key=lambda k: res[k]['t_a']); R = res[pick]; passed = R['t_a'] > 0 and R['t_b'] >= 2.40 and all(R['b_years'].get(y, -1) > 0 for y in (2024, 2025, 2026))
    A['shorts'] = dict(rules=res, pick=pick, passed=bool(passed)); OUT[name] = A
    print(f"\n== {name}: up hours {A['up_hours_pct']}%, up days {A['up_days_pct']}% | avg up hour {A['avg_up_hour_bps']} bp, down {A['avg_down_hour_bps']} bp | 1% tails {A['worst1pct_hour_pct']}% / +{A['best1pct_hour_pct']}% | skew {A['skew_hourly']}")
    print(f"   worst hour {A['worst_hour']}, best {A['best_hour']} | worst 24h {A['worst_24h']}, best {A['best_24h']}")
    print(f"   swings ≥{th*100:.0f}%: falls {A['down_legs']} | rallies {A['up_legs']}")
    print(f"   volatility next 24h after big drop ×{A['vol_after_big_down_x']}, after big rise ×{A['vol_after_big_up_x']} | big drops by session {A['big_down_by_session_pct']} | big rises {A['big_up_by_session_pct']}")
    for rn, v in split.items(): print(f"   E5 {rn:24s} long: {v['long']['a']:+6.1f}%/yr | {v['long']['b']:+6.1f}%/yr (t {v['long']['tb']:+.2f})   short: {v['short']['a']:+6.1f} | {v['short']['b']:+6.1f} (t {v['short']['tb']:+.2f})   [2020–23 | 2024–26]")
    for rn, v in res.items(): print(f"   {rn:32s} 2020–23 t {v['t_a']:+5.2f} ({v['a_yr']:+6.1f}%/yr) | 2024–26 t {v['t_b']:+5.2f} ({v['b_yr']:+6.1f}%/yr) {v['b_years']} trades {v['trades']}" + ('  <= PICKED' if rn == pick else ''))
    print(f"   SHORT VERDICT: {pick} → {'PASS' if passed else 'FAIL'}")
json.dump(OUT, open('plans/E7_anatomy.json', 'w'), indent=1)
