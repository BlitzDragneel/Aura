"""E33 judge (PLAN_E33_deleveraging.md, md5 d119dc90…): run once."""
import json, glob, pickle, numpy as np, pandas as pd, datetime as dt
COINS = json.load(open('/home/claude/omega/plans-new/E33_coins.json'))['coins']; RAW = pickle.load(open('/home/claude/e25/hourly_e26.pkl', 'rb'))
A0 = int(dt.datetime(2023, 10, 1, tzinfo=dt.timezone.utc).timestamp()//3600); A1 = int(dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc).timestamp()//3600)
ev = []; cmp = []
for s in COINS:
    oi = {}
    for f in glob.glob(f'oi/{s}/*.json'):
        d = json.load(open(f))
        if d: oi.update({int(k): v for k, v in d.items()})
    x = RAW.get(s)
    if x is None or not oi: continue
    ok = x['v'] > 0; C = dict(zip(x['h'][ok].tolist(), x['c'][ok].tolist()))
    nxt = -1
    for h in range(A0, A1):
        if h < nxt or h not in C or (h - 1) not in C or (h + 4) not in C: continue
        r = np.log(C[h]/C[h - 1])
        if r > -0.05: continue
        o0, o1 = oi.get(h), oi.get(h + 1)                       # OI at the start and the end of hour h
        if not (o0 and o1): continue
        out = np.log(C[h + 4]/C[h]) - 0.002; rec = dict(sym=s, t=pd.Timestamp(h*3600 + 3600, unit='s'), r=r, doi=o1/o0 - 1, net=out)
        if o1/o0 - 1 <= -0.01: ev.append(rec); nxt = h + 4
        else: cmp.append(rec)
E = pd.DataFrame(ev); Cm = pd.DataFrame(cmp)
def wt(s, t):
    w = s.groupby(t.dt.to_period('W')).sum(); w = w.reindex(pd.period_range(t.min(), t.max(), freq='W'), fill_value=0.0); return float(w.mean()/w.std()*np.sqrt(len(w))) if w.std() > 0 else 0.0
def show(nm, X):
    yrs = X.groupby(X.t.dt.year).net.agg(['mean', 'size']); t = wt(X.net, X.t)
    print(f"{nm}: n {len(X)} on {X.sym.nunique()} coins | net {X.net.mean()*1e4:+.1f} bp a trade (median {X.net.median()*1e4:+.1f}, winners {(X.net > 0).mean()*100:.0f}%) | weekly t {t:+.2f} | " + ' '.join(f"{y}: {v['mean']*1e4:+.0f} bp ({int(v['size'])})" for y, v in yrs.iterrows()))
    return t, yrs
t, yrs = show('E33 RULE  fall ≥5% AND open interest −1% or more', E)
show('COMPARE   the same falls, open interest NOT down 1%', Cm)
ok = t >= 2.0 and E.net.mean() > 0 and all(y in yrs.index and yrs.loc[y, 'size'] >= 20 and yrs.loc[y, 'mean'] > 0 for y in (2024, 2025, 2026))
srt = np.sort(E.net.values)[::-1]; k = max(1, len(srt)//20)
print(f"without the best 5% of events: {srt[k:].mean()*1e4:+.1f} bp | worst 5 events: {', '.join(f'{v*1e4:+.0f}' for v in srt[-5:])} bp | top coins by count: {E.sym.value_counts().head(5).to_dict()}")
print('VERDICT:', 'PASS' if ok else 'FAIL')
json.dump(dict(n=len(E), net_bp=float(E.net.mean()*1e4), t=t, years={int(y): [float(v['mean']*1e4), int(v['size'])] for y, v in yrs.iterrows()}, compare_n=len(Cm), compare_net_bp=float(Cm.net.mean()*1e4), passed=bool(ok)), open('/home/claude/omega/plans-new/E33_result.json', 'w'), indent=1)
