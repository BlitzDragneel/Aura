import sys, json, gzip, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load
SPLIT = pd.Timestamp('2024-01-01'); END = pd.Timestamp('2026-10-18 23:00')
def hourly15(m):
    t = (m['t']*900)//3600; df = pd.DataFrame({'t':t, 'o':m['o'], 'h':m['h'], 'l':m['l'], 'c':m['c'], 'q':m['v']*m['c'], 'tbq':m['tb']*m['v']*m['c']})
    g = df.groupby('t').agg(o=('o','first'), h=('h','max'), l=('l','min'), c=('c','last'), q=('q','sum'), tbq=('tbq','sum'), n=('c','size')); g = g[g.n >= 3]
    g['tb'] = g.tbq/g.q; g.index = pd.to_datetime(g.index*3600, unit='s'); return g[['o','h','l','c','q','tb']]
MK = {}
for part in ['creed15_1','creed15_2','creed15_3','creed15_4','creed15_5']:
    d, ms = load(part)
    for m in ms: MK[m['sym']] = hourly15(m)
mret = pd.concat({s: np.log(g.c).diff() for s, g in MK.items()}, axis=1).clip(-0.3, 0.3).mean(axis=1)   # equal-weight market, hourly
G = json.loads(gzip.open('/mnt/user-data/uploads/omega-history-gold1h-2026-10-20_json.gz').read())['markets'][0]
s = 10.0**-G['dp']; t = np.cumsum(np.asarray(G['t'], dtype=np.int64)); c = np.cumsum(np.asarray(G['c'], dtype=np.int64))*s; o = c + np.asarray(G['o'], dtype=np.int64)*s
gold = pd.DataFrame({'o':o, 'h':np.maximum(o, c) + np.asarray(G['h'], dtype=np.int64)*s, 'l':np.minimum(o, c) - np.asarray(G['l'], dtype=np.int64)*s, 'c':c}, index=pd.to_datetime(t*3600, unit='s'))
MARKETS = {k: (MK[k], 0.0006) for k in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']}
SESS = {'Asia':range(0, 8), 'London':range(8, 13), 'US':range(13, 21), 'Late':range(21, 24)}
def wk_t(pnl):
    w = pnl.groupby(pnl.index.to_period('W-SUN')).sum(); w = w.reindex(pd.period_range(pnl.index[0], pnl.index[-1], freq='W-SUN'), fill_value=0.0)
    return float(w.mean()/w.std()*np.sqrt(len(w))) if w.std() > 0 else 0.0
def events(sig, H):
    """position for H bars after each signal bar, ignoring signals while holding"""
    pos = np.zeros(len(sig)); k = 0; n = len(sig)
    while k < n:
        if sig[k] != 0: pos[k+1:min(k+1+H, n)] = sig[k]; k += H + 1; continue
        k += 1
    return pos
OUT = {}
for name, (df, cost) in MARKETS.items():
    df = df[df.index <= END].copy(); r = np.log(df.c).diff().fillna(0.0); hr = df.index.hour; yr = df.index.year; per = np.where(df.index < SPLIT, 'a', 'b')
    P = {'name':name, 'from':str(df.index[0].date()), 'to':str(df.index[-1].date()), 'hours':int(len(df)), 'cost':cost}
    # 1-2. hours and sessions
    P['hour_drift_bps'] = [round(float(r[hr == h].mean()*1e4), 2) for h in range(24)]
    P['hour_move_bps'] = [round(float(r[hr == h].abs().mean()*1e4), 1) for h in range(24)]
    P['hour_drift_bps_a'] = [round(float(r[(hr == h) & (per == 'a')].mean()*1e4), 2) for h in range(24)]
    P['hour_drift_bps_b'] = [round(float(r[(hr == h) & (per == 'b')].mean()*1e4), 2) for h in range(24)]
    ses = {}
    for sn, hs in SESS.items():
        y = r[np.isin(hr, list(hs))].groupby(yr[np.isin(hr, list(hs))]).sum()*100
        ses[sn] = dict(byYear={int(k): round(float(v), 1) for k, v in y.items()}, yearsUp=int((y > 0).sum()), years=int(len(y)), perYear=round(float(y.mean()), 1), move_bps=round(float(r[np.isin(hr, list(hs))].abs().mean()*1e4), 1))
    P['sessions'] = ses
    # 3. weekdays (daily sums)
    day = r.groupby(df.index.date).sum(); di = pd.to_datetime(day.index); wd = di.dayofweek
    P['weekday_drift_pct'] = [round(float(day[wd == k].mean()*100), 3) for k in range(7)]; P['weekday_move_pct'] = [round(float(day[wd == k].abs().mean()*100), 2) for k in range(7)]
    # 4. ranges
    pc = df.c.shift(1); tr = np.maximum(df.h - df.l, np.maximum((df.h - pc).abs(), (df.l - pc).abs()))/df.c
    last = df.index >= df.index[-1] - pd.Timedelta(days=90)
    P['atr_h_pct_recent'] = round(float(tr[last].median()*100), 3); P['atr_h_pct_all'] = round(float(tr.median()*100), 3)
    dd = df.resample('1D').agg({'h':'max', 'l':'min', 'c':'last'}).dropna(); P['day_range_pct_recent'] = round(float(((dd.h/dd.l - 1)[dd.index >= dd.index[-1] - pd.Timedelta(days=90)]).median()*100), 2)
    P['weekend_vs_week_move'] = round(float(r[df.index.dayofweek >= 5].abs().mean()/r[df.index.dayofweek < 5].abs().mean()), 2) if name != 'XAUUSD' else None
    # 5-6. after big moves and after 24h breakouts (signed in the move's direction)
    sg = r.rolling(168).std().shift(1); z = r/sg; fwd = lambda Hh: np.log(df.c.shift(-Hh)/df.c)
    def after(mask, sign, Hh):
        x = (fwd(Hh)*sign)[mask].dropna(); xa, xb = x[x.index < SPLIT], x[x.index >= SPLIT]
        return dict(n=int(len(x)), a_bps=round(float(xa.mean()*1e4), 1), b_bps=round(float(xb.mean()*1e4), 1))
    big = z.abs() >= 2.5; P['after_big_4h'] = after(big, np.sign(z), 4); P['after_big_24h'] = after(big, np.sign(z), 24)
    hi24 = df.h.rolling(24).max().shift(1); lo24 = df.l.rolling(24).min().shift(1); bo = np.where(df.c > hi24, 1, np.where(df.c < lo24, -1, 0))
    P['after_breakout_24h'] = after(pd.Series(bo != 0, index=df.index), pd.Series(bo, index=df.index), 24)
    # 7. trend or reversion: variance ratio over 24h, by period
    def vr(x):
        b = x.groupby(np.arange(len(x))//24).sum(); return float(b.var()/(24*x.var())) if x.var() > 0 else None
    P['vr24_a'] = round(vr(r[r.index < SPLIT]), 2); P['vr24_b'] = round(vr(r[r.index >= SPLIT]), 2)
    # 8-10. crypto only
    if name != 'XAUUSD':
        mm = mret.reindex(df.index).fillna(0.0); ok = mm != 0
        P['corr_market'] = round(float(np.corrcoef(r[ok], mm[ok])[0, 1]), 2); P['beta_market'] = round(float(np.cov(r[ok], mm[ok])[0, 1]/mm[ok].var()), 2)
        nxt = r.shift(-1); imb = df.tb - 0.5; okk = imb.notna() & nxt.notna()
        P['imb_next_corr_a'] = round(float(np.corrcoef(imb[okk & (per == 'a')], nxt[okk & (per == 'a')])[0, 1]), 3); P['imb_next_corr_b'] = round(float(np.corrcoef(imb[okk & (per == 'b')], nxt[okk & (per == 'b')])[0, 1]), 3)
        P['day_volume_usd_recent'] = round(float(df.q[last].resample('1D').sum().median()), 0)
    # who trades it when: volume share and aggressive-buying share by session
    P['volume_share_pct'] = {sn: round(float(df.q[np.isin(hr, list(hs))].sum()/df.q.sum()*100), 1) for sn, hs in SESS.items()}
    P['taker_buy_pct'] = {sn: round(float((df.tb[np.isin(hr, list(hs))]*df.q[np.isin(hr, list(hs))]).sum()/df.q[np.isin(hr, list(hs))].sum()*100), 2) for sn, hs in SESS.items()}
    # strategy test
    disc = r.index < SPLIT; sa = {sn: r[np.isin(hr, list(hs)) & disc].mean() for sn, hs in SESS.items()}; best = max(sa, key=sa.get); worst = min(sa, key=sa.get)
    ema = df.c.ewm(span=200, adjust=False).mean()
    pos = {'R1 long best session (' + best + ')':np.where(np.isin(hr, list(SESS[best])), 1.0, 0.0),
           'R2 short worst session (' + worst + ')':np.where(np.isin(hr, list(SESS[worst])), -1.0, 0.0),
           'R3 follow 24h breakout, 24h':events(bo, 24), 'R4 fade 24h breakout, 24h':-events(bo, 24),
           'R5 follow big hour, 4h':events(np.where(z >= 2.5, 1, np.where(z <= -2.5, -1, 0)), 4), 'R6 fade big hour, 4h':-events(np.where(z >= 2.5, 1, np.where(z <= -2.5, -1, 0)), 4),
           'R7 above/below 200h average':np.r_[0.0, np.where(df.c > ema, 1.0, -1.0)[:-1]]}
    res = {}
    for rn, p in pos.items():
        p = pd.Series(p, index=df.index).fillna(0.0); pnl = p*r - p.diff().abs().fillna(0.0)*cost
        a, b = pnl[disc], pnl[~disc]; yb = b.groupby(b.index.year).sum()*100
        res[rn] = dict(t_a=round(wk_t(a), 2), t_b=round(wk_t(b), 2), a_per_year=round(float(a.sum()/((a.index[-1] - a.index[0]).days/365.25)*100), 1), b_per_year=round(float(b.sum()/((b.index[-1] - b.index[0]).days/365.25)*100), 1), b_years={int(k): round(float(v), 1) for k, v in yb.items()}, trades=int((p.diff().abs() > 0).sum()//2))
    pick = max(res, key=lambda k: res[k]['t_a']); R = res[pick]
    passed = R['t_a'] > 0 and R['t_b'] >= 2.40 and all(R['b_years'].get(y, -1) > 0 for y in (2024, 2025, 2026))
    P['strategy'] = dict(rules=res, pick=pick, passed=bool(passed))
    OUT[name] = P
    print(f"\n== {name} {P['from']}→{P['to']} | hourly range {P['atr_h_pct_recent']}% (90d) | daily range {P['day_range_pct_recent']}% | VR24 {P['vr24_a']}/{P['vr24_b']}" + (f" | corr {P['corr_market']} beta {P['beta_market']} | taker-imb→next {P['imb_next_corr_a']}/{P['imb_next_corr_b']}" if name != 'XAUUSD' else ''))
    print('   sessions (log %/yr, years up):', {k: (v['perYear'], f"{v['yearsUp']}/{v['years']}") for k, v in ses.items()})
    print('   after big hour 4h/24h (a|b bps):', (P['after_big_4h']['a_bps'], P['after_big_4h']['b_bps']), (P['after_big_24h']['a_bps'], P['after_big_24h']['b_bps']), 'n', P['after_big_4h']['n'], '| after 24h breakout:', (P['after_breakout_24h']['a_bps'], P['after_breakout_24h']['b_bps']), 'n', P['after_breakout_24h']['n'])
    for rn, v in res.items(): print(f"   {rn:34s} 2020–23 t {v['t_a']:+5.2f} ({v['a_per_year']:+6.1f}%/yr) | 2024–26 t {v['t_b']:+5.2f} ({v['b_per_year']:+6.1f}%/yr) {v['b_years']}" + ('   <= PICKED' if rn == pick else ''))
    print(f"   VERDICT: {pick} → {'PASS' if passed else 'FAIL'}")
json.dump(OUT, open('plans/E14_dossiers.json', 'w'), indent=1)
