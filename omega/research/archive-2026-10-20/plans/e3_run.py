"""Plan E3 (PLAN_E3_gold_structure.md, md5 6713849dcf77ed55b23a7fc4107b9586). usage: python3 e3_run.py <file> [label]"""
import sys, json, gzip, hashlib, numpy as np, pandas as pd
path = sys.argv[1]; label = sys.argv[2] if len(sys.argv) > 2 else 'gold'; raw = open(path, 'rb').read()
print('file sha256', hashlib.sha256(raw).hexdigest())
d = json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)
def decode(m):
    s = 10.0**-m['dp']; t = np.cumsum(np.asarray(m['t'], dtype=np.int64)); c = np.cumsum(np.asarray(m['c'], dtype=np.int64))*s
    o = c + np.asarray(m['o'], dtype=np.int64)*s; h = np.maximum(o, c) + np.asarray(m['h'], dtype=np.int64)*s; l = np.minimum(o, c) - np.asarray(m['l'], dtype=np.int64)*s
    return t, o, h, l, c
out = {}
for m in d['markets']:
    t, o, h, l, c = decode(m); n = len(c); ts = pd.to_datetime(t*3600, unit='s'); hr = t % 24
    r = np.r_[0.0, np.log(c[1:]/c[:-1])]; weeks = pd.period_range(ts[0], ts[-1], freq='W-SUN')
    def judge(name, pnl_by_time, cost, ntr):
        s = pd.Series(pnl_by_time[1], index=pd.to_datetime(np.asarray(pnl_by_time[0])*3600, unit='s'))
        wk = s.groupby(s.index.to_period('W-SUN')).sum().reindex(weeks, fill_value=0.0)
        tval = wk.mean()/wk.std()*np.sqrt(len(wk)) if wk.std() > 0 else 0.0
        yrs = s.groupby(s.index.year).sum(); ypos = int((yrs > 0).sum())
        ann = s.sum()/((t[-1] - t[0])/8766)
        return dict(t=float(tval), total=float(s.sum()), perYear=float(ann), yearsPos=ypos, years={int(k): round(float(v)*100, 1) for k, v in yrs.items()}, trades=int(ntr))
    for cost in (0.0002, 0.0005):
        res = {}
        # H1 overnight drift (and two reported comparisons)
        for nm, held in [('H1 overnight long', ~((hr >= 13) & (hr <= 20))), ('US hours long (reported)', (hr >= 13) & (hr <= 20)), ('hold always (reported)', np.ones(n, bool))]:
            p = held.astype(float); p[0] = 0; ch = np.abs(np.diff(np.r_[0.0, p])); pnl = p*r - ch*cost
            res[nm] = judge(nm, (t, pnl), cost, int(ch.sum()//2))
        # H2 forced-selling rebound
        sg = pd.Series(r).rolling(168).std().shift(1).values; z = r/sg; rg = h - l; cl = np.where(rg > 0, (c - l)/np.where(rg > 0, rg, 1), np.nan)
        tt, pp, k = [], [], 170
        while k < n - 13:
            if z[k] <= -3 and cl[k] >= 0.6: tt.append(t[k+1]); pp.append(np.log(c[k+12]/o[k+1]) - 2*cost); k += 12; continue
            k += 1
        res['H2 forced-selling rebound'] = judge('H2', (tt, pp), cost, len(tt))
        # H3 weekend gap fade
        tt, pp = [], []
        for k in range(1, n - 13):
            if t[k] - t[k-1] >= 40:
                g = np.log(o[k]/c[k-1])
                if abs(g) >= 0.0025: dd = -np.sign(g); tt.append(t[k]); pp.append(dd*np.log(c[k+12]/c[k]) - 2*cost)
        res['H3 weekend gap fade'] = judge('H3', (tt, pp), cost, len(tt))
        out[f"{m['sym']}|{cost}"] = res
        print(f"\n{m['sym']} ({label}), costs {cost*100:.2f}% a side")
        for nm, v in res.items():
            verdict = ''
            if cost == 0.0002 and nm.startswith('H'):
                passed = v['t'] >= 2.13 and v['total'] > 0 and v['yearsPos'] >= 4
                verdict = ' | ' + ('PASS on ' + label if passed else 'FAIL'); v['passed'] = passed
            print(f"  {nm:28s} t {v['t']:+5.2f} | total {v['total']*100:+7.1f}% ({v['perYear']*100:+5.1f}%/yr) | years positive {v['yearsPos']}/{len(v['years'])} {v['years']} | trades {v['trades']}{verdict}")
json.dump(out, open(f'E3_result_{label}.json', 'w'), indent=1); print('\nsaved', f'E3_result_{label}.json')
