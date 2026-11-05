"""E30 (PLAN_E30_liquidity.md, md5 e84fdd70…). usage: python3 e30.py depth|metrics"""
import json, glob, os, sys, pickle, numpy as np, pandas as pd, datetime as dt
COINS = ['BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT','XRPUSDT','DOGEUSDT','ADAUSDT','AVAXUSDT','LINKUSDT','LTCUSDT']; COST = 0.002
RAW = pickle.load(open('/home/claude/e25/hourly_e26.pkl', 'rb'))
def price(sym):
    x = RAW[sym]; ok = x['v'] > 0; return pd.Series(x['c'][ok], index=pd.to_datetime(x['h'][ok]*3600, unit='s'))
def wt(s):
    w = s.groupby(s.index.to_period('W')).sum(); return float(w.mean()/w.std()*np.sqrt(len(w))) if len(w) > 2 and w.std() > 0 else 0.0
def events(sig, fwd, H):
    """non-overlapping trades per coin: sig ∈ {−1,0,1} at hour close, return = sig × forward H-hour log return − costs"""
    out = []; nxt = None
    for t, s in sig[sig != 0].items():
        if nxt is not None and t < nxt: continue
        f = fwd.get(t)
        if f is None or not np.isfinite(f): continue
        out.append((t, s*f - COST)); nxt = t + pd.Timedelta(hours=H)
    return out
def pctl(x, w=720):
    return x.rolling(w, min_periods=w//2).rank(pct=True)
def run_grid(feats, P, stages, specs, luck=False, rng=None):
    res = []
    for sp in specs:
        tr = []
        for c in COINS:
            if c not in feats: continue
            f = feats[c][sp['feat']]; pr = P[c]; fw = np.log(pr.shift(-sp['H'])/pr)
            q = pctl(f); sig = pd.Series(np.where(q >= 0.9, 1, np.where(q <= 0.1, -1, 0))*sp['sign'], index=f.index)
            if sp.get('cond') is not None: sig = sp['cond'](feats[c], pr)
            if luck: sig = pd.Series(rng.permutation(sig.values), index=sig.index)
            tr += events(sig, fw, sp['H'])
        S = pd.Series([r for _, r in tr], index=pd.DatetimeIndex([t for t, _ in tr])).sort_index()
        row = dict(sp, n=len(S))
        for nm, (a, b) in stages.items():
            s = S[(S.index >= a) & (S.index < b)]; row[nm] = dict(n=len(s), mean_bp=float(s.mean()*1e4) if len(s) else None, t=wt(s) if len(s) > 10 else 0.0, years={int(y): float(v*1e4) for y, v in s.groupby(s.index.year).mean().items()})
        row.pop('cond', None); res.append(row)
    return res
MODE = sys.argv[1]; rng = np.random.default_rng(30)
P = {c: price(c) for c in COINS}
if MODE == 'depth':
    feats = {}
    for c in COINS:
        rec = []
        for f in sorted(glob.glob(f'depth/{c}/*.json')):
            d = json.load(open(f)); day = os.path.basename(f)[:10]
            if not d: continue
            for k, v in d.items():
                h, p = k.split('|'); rec.append((pd.Timestamp(day) + pd.Timedelta(hours=int(h)), int(p), v[0]))
        df = pd.DataFrame(rec, columns=['t', 'p', 'n']).pivot_table(index='t', columns='p', values='n').sort_index()
        df.index = df.index + pd.Timedelta(hours=1)                    # an hour's median is known at the hour's end (= that hour's close)
        F = pd.DataFrame(index=df.index)
        for k in (1, 2, 5): F[f'imb{k}'] = (df[-k] - df[k])/(df[-k] + df[k])
        F['thin'] = (df[-1] + df[1])/((df[-1] + df[1]).rolling(720, min_periods=240).median())
        pr = P[c].reindex(F.index - pd.Timedelta(hours=1)); pr.index = F.index      # the kline that closes at the same time
        feats[c] = F; P[c] = pr
    pickle.dump(feats, open('depth_feats.pkl', 'wb'))
    ST = {'discovery': (pd.Timestamp('2023-01-01'), pd.Timestamp('2025-01-01')), 'final': (pd.Timestamp('2025-01-01'), pd.Timestamp('2026-10-01'))}
    # L1 size: rank correlation of thinness (inverse: 1/thin = thinner) with the next-24h absolute move
    L1 = {}
    for nm, (a, b) in ST.items():
        cs = []
        for c in COINS:
            f = feats[c]; pr = P[c]; mv = np.log(pr.shift(-24)/pr).abs(); m = (f.index >= a) & (f.index < b)
            x = pd.concat([-f.thin[m], mv[m]], axis=1).dropna()
            if len(x) > 200: cs.append(float(x.corr(method='spearman').iloc[0, 1]))
        L1[nm] = dict(per_coin=[round(v, 3) for v in cs], mean=float(np.mean(cs)), positive=int(sum(v > 0 for v in cs)))
    specs = [dict(feat=f'imb{k}', H=H, sign=sg) for k in (1, 2, 5) for H in (1, 4, 24) for sg in (1, -1)]
    DISC = {'discovery': ST['discovery']}
    real = run_grid(feats, P, DISC, specs); luck = run_grid(feats, P, DISC, specs, luck=True, rng=rng)
    lb = max(x['discovery']['t'] for x in luck); pick = max(real, key=lambda x: x['discovery']['t'])
    fin = run_grid(feats, P, {'final': ST['final']}, [dict(feat=pick['feat'], H=pick['H'], sign=pick['sign'])])[0]['final']
    f = fin; passed = f['t'] >= 2.0 and (f['mean_bp'] or 0) > 0 and all(f['years'].get(y, -1) > 0 for y in (2025, 2026))
    json.dump(dict(L1=L1, L2_discovery=real, L2_luck=luck, L2_pick=pick, L2_final=fin, L2_passed=bool(passed)), open('E30_depth.json', 'w'), indent=1, default=str)
    print('L1 thin book → bigger next-24h move (rank corr, per coin):', {k: (round(v['mean'], 3), f"{v['positive']}/10 positive") for k, v in L1.items()})
    print(f'L2 discovery, 18 variants; luck-best t {lb:.2f}')
    for x in sorted(real, key=lambda x: -x['discovery']['t'])[:6]: print(f"  {x['feat']} H{x['H']:<2d} sign {x['sign']:+d} | disc n {x['discovery']['n']} {x['discovery']['mean_bp']:+.1f} bp t {x['discovery']['t']:+.2f} {x['discovery']['years']}")
    print(f"L2 PICK {pick['feat']} H{pick['H']} sign {pick['sign']:+d} → FINAL n {f['n']} {f['mean_bp']:+.1f} bp t {f['t']:+.2f} {f['years']} → {'PASS' if passed else 'FAIL'}")
if MODE == 'metrics':
    feats = {}
    for c in COINS:
        rec = []
        for f in sorted(glob.glob(f'metrics/{c}/*.json')):
            d = json.load(open(f))
            if d: rec += d
        if not rec: continue
        df = pd.DataFrame(rec, columns=['t', 'oi', 'oiv', 'ttc', 'tt', 'acc', 'taker']); df['t'] = pd.to_datetime(df.t); df = df.drop_duplicates('t').set_index('t').sort_index()
        h = df.resample('1h', label='right', closed='right').last()           # value at each hour's end
        pr = P[c]; pr.index = pr.index + pd.Timedelta(hours=1)                  # the kline that closes at that hour's end
        F = pd.DataFrame(index=h.index); F['oi_chg'] = h.oi.pct_change(); F['ret1'] = np.log(pr/pr.shift(1)).reindex(h.index); F['tt'] = h.tt; F['acc'] = h.acc
        feats[c] = F; P[c] = pr.reindex(h.index)
    pickle.dump(feats, open('metrics_feats.pkl', 'wb'))
    ST = {'discovery': (pd.Timestamp('2020-09-01'), pd.Timestamp('2024-01-01')), 'validation': (pd.Timestamp('2024-01-01'), pd.Timestamp('2025-01-01')), 'final': (pd.Timestamp('2025-01-01'), pd.Timestamp('2026-10-01'))}
    def dl(x, y, side):
        def f(F, pr):
            m = (F.ret1 <= -x) & (F.oi_chg <= -y) if side > 0 else (F.ret1 >= x) & (F.oi_chg <= -y)
            return pd.Series(np.where(m.fillna(False), side, 0), index=F.index)
        return f
    L4 = [dict(feat='oi_chg', H=H, sign=1, x=x, y=y, cond=dl(x, y, 1)) for x in (0.02, 0.03, 0.05) for y in (0.005, 0.01, 0.02) for H in (4, 24)]
    L5 = [dict(feat=f, H=24, sign=-1) for f in ('tt', 'acc')] + [dict(feat=f, H=24, sign=1) for f in ('tt', 'acc')]
    OUT = {}
    for fam, specs in (('L4', L4), ('L5', L5)):
        disc = run_grid(feats, P, {'discovery': ST['discovery']}, specs); luck = run_grid(feats, P, {'discovery': ST['discovery']}, specs, luck=True, rng=rng)
        lb = max(x['discovery']['t'] for x in luck); pick_i = int(np.argmax([x['discovery']['t'] for x in disc])); pk = disc[pick_i]; sp = specs[pick_i]
        val = run_grid(feats, P, {'validation': ST['validation']}, [sp])[0]['validation']; fin = None; passed = False
        if val['t'] >= 1.65 and (val['mean_bp'] or 0) > 0:
            fin = run_grid(feats, P, {'final': ST['final']}, [sp])[0]['final']; passed = fin['t'] >= 2.0 and fin['mean_bp'] > 0 and all(fin['years'].get(y, -1) > 0 for y in (2025, 2026))
        OUT[fam] = dict(discovery=disc, luck_best=lb, pick=pk, validation=val, final=fin, passed=bool(passed))
        print(f'{fam}: {len(specs)} variants; luck-best discovery t {lb:.2f}')
        for x in sorted(disc, key=lambda x: -x['discovery']['t'])[:5]: print(f"   {x.get('feat')} x{x.get('x', '')} y{x.get('y', '')} H{x['H']} sign {x['sign']:+d} | disc n {x['discovery']['n']} {x['discovery']['mean_bp'] if x['discovery']['mean_bp'] is None else round(x['discovery']['mean_bp'], 1)} bp t {x['discovery']['t']:+.2f} {x['discovery']['years']}")
        print(f"   PICK → VALIDATION 2024: n {val['n']} {val['mean_bp']} bp t {val['t']:+.2f}" + (f" → FINAL: n {fin['n']} {fin['mean_bp']:+.1f} bp t {fin['t']:+.2f} {fin['years']}" if fin else ' → not promoted (validation bar not met)') + f" → {'PASS' if passed else 'FAIL'}")
    json.dump(OUT, open('E30_metrics.json', 'w'), indent=1, default=str)
