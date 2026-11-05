"""Plan E15 (PLAN_E15_forex.md): the five forex majors one by one, rules exactly as plan E14 (anatomy_top5.py / dossier_top5.py
code, unchanged), costs 0.015% a side, the pick = highest weekly t before 2024 among all eleven rules, judged ONCE on
2024-01-01 → end: pass if t ≥ 2.33 and positive in 2024, 2025 and 2026. Forex has no volume: S1's volume condition is off
(as E14 did for gold). Run once."""
import sys, json, gzip, hashlib, numpy as np, pandas as pd
P = '/mnt/user-data/uploads/omega-history-metals-fx1h-2026-10-23_json.gz'; print('sha256', hashlib.sha256(open(P, 'rb').read()).hexdigest())
SPLIT = pd.Timestamp('2024-01-01'); COST = 0.00015; SESS = {'Asia':range(0, 8), 'London':range(8, 13), 'US':range(13, 21), 'Late':range(21, 24)}
def dec(G):
    s = 10.0**-G['dp']; t = np.cumsum(np.asarray(G['t'], dtype=np.int64)); c = np.cumsum(np.asarray(G['c'], dtype=np.int64))*s; o = c + np.asarray(G['o'], dtype=np.int64)*s
    return pd.DataFrame({'o':o, 'h':np.maximum(o, c) + np.asarray(G['h'], dtype=np.int64)*s, 'l':np.minimum(o, c) - np.asarray(G['l'], dtype=np.int64)*s, 'c':c}, index=pd.to_datetime(t*3600, unit='s'))
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
D = json.loads(gzip.open(P).read()); OUT = {}
for G in D['markets']:
    name = G['sym']
    if name not in ('EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'): continue
    df = dec(G); df = df[~df.index.duplicated()].sort_index(); r = np.log(df.c).diff().fillna(0.0); hr = df.index.hour; disc = df.index < SPLIT
    sg = r.rolling(168).std().shift(1); z = r/sg
    hi24 = df.h.rolling(24).max().shift(1); lo24 = df.l.rolling(24).min().shift(1); bo = np.where(df.c > hi24, 1, np.where(df.c < lo24, -1, 0)); ema = df.c.ewm(span=200, adjust=False).mean()
    sa = {sn: r[np.isin(hr, list(hs)) & disc].mean() for sn, hs in SESS.items()}; best = max(sa, key=sa.get); worst = min(sa, key=sa.get)
    zz = np.where(z >= 2.5, 1, np.where(z <= -2.5, -1, 0))
    pos = {'R1 long best session (' + best + ')':np.where(np.isin(hr, list(SESS[best])), 1.0, 0.0), 'R2 short worst session (' + worst + ')':np.where(np.isin(hr, list(SESS[worst])), -1.0, 0.0),
           'R3 follow 24h breakout, 24h':events(bo, 24), 'R4 fade 24h breakout, 24h':-events(bo, 24), 'R5 follow big hour, 4h':events(zz, 4), 'R6 fade big hour, 4h':-events(zz, 4),
           'R7 above/below 200h average':np.r_[0.0, np.where(df.c > ema, 1.0, -1.0)[:-1]]}
    rg = df.h - df.l; cl = np.where(rg > 0, (df.c - df.l)/rg.replace(0, np.nan), np.nan); volok = np.ones(len(df), bool)
    s1 = np.where((z >= 3).values & volok & (cl <= 0.4), -1, 0); s2 = np.where((df.h > hi24).values & (df.c < hi24).values, -1, 0)
    lo72 = df.l.rolling(72).min().shift(1); below = (df.c < ema).values; s4 = np.where((df.c < lo72).values & below, -1, 0)
    o13 = pd.Series(np.where(hr == 13, (df.o < ema.shift(1)).astype(float), np.nan), index=df.index).groupby(df.index.date).transform('max').fillna(0).values
    s3 = np.where((o13 > 0) & np.isin(hr, list(SESS['US'])), -1.0, 0.0)
    pos.update({'S1 blow-off short, 12h':events(s1, 12), 'S2 failed breakout short, 24h':events(s2, 24), 'S3 downtrend US-hours short':s3, 'S4 breakdown in downtrend, 24h':events(s4, 24)})
    res = {}
    for rn, p in pos.items():
        p = pd.Series(p, index=df.index).fillna(0.0); pn = p*r - p.diff().abs().fillna(0.0)*COST; a, b = pn[disc], pn[~disc]; yb = b.groupby(b.index.year).sum()*100
        res[rn] = dict(t_a=round(wk_t(a), 2), t_b=round(wk_t(b), 2), a_yr=round(peryr(a), 2), b_yr=round(peryr(b), 2), b_years={int(k): round(float(v), 2) for k, v in yb.items()}, trades=int((p.diff().abs() > 0).sum()//2))
    pick = max(res, key=lambda k: res[k]['t_a']); R = res[pick]; passed = R['t_a'] > 0 and R['t_b'] >= 2.33 and all(R['b_years'].get(y, -1) > 0 for y in (2024, 2025, 2026))
    OUT[name] = dict(frm=str(df.index[0])[:10], to=str(df.index[-1])[:13], hours=len(df), rules=res, pick=pick, passed=bool(passed))
    print(f"\n== {name} {OUT[name]['frm']} → {OUT[name]['to']} ({len(df)} hours)")
    for rn, v in res.items(): print(f"   {rn:32s} before 2024 t {v['t_a']:+5.2f} ({v['a_yr']:+6.2f}%/yr) | 2024→ t {v['t_b']:+5.2f} ({v['b_yr']:+6.2f}%/yr) {v['b_years']}" + ('  <= PICKED' if rn == pick else ''))
    print(f"   VERDICT: {pick} → {'PASS' if passed else 'FAIL'}")
json.dump(OUT, open('plans/E15_result.json', 'w'), indent=1)
