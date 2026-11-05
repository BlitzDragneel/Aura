import sys, json, time; sys.path.insert(0,'/home/claude/edge')
from live import *
STRATS = [('burst3','us_hours'), ('burst3','mkt_trend'), ('break72_hold','us_hours'), ('climax','none')]
H0 = START_H + 820; months = pd.date_range('2024-02-01', '2026-04-01', freq='MS')
starts = [int(m.value//3600//10**9) for m in months]
def dd(curve):
    v = np.array([x[1] for x in curve]); pk = np.maximum.accumulate(v); return float(np.max(1 - v/np.maximum(pk, 1e-9)))
t0 = time.time()
with open('livegrid.jsonl','w') as f:
    for ent, flt in STRATS:
        bk = signal_book(ent, flt)
        meths = ['climax 12h'] if ent == 'climax' else ['your method', 'pyramid', 'fixed 2R target']
        for mname in meths:
            for risk in (0.01, 0.02, 0.05, 0.10):
                for start in (100.0, 10.0):
                    eq, logs, curve = account(bk, METHODS[mname], start=start, risk=risk, t_from=SPLIT_H)
                    f.write(json.dumps(dict(kind='second_half', ent=ent, flt=flt, m=mname, risk=risk, start=start, end=eq, dd=dd(curve), n=len(logs),
                        bumped=int(sum(l['bumped'] for l in logs)), liq=int(sum(l['why'] == 'liquidated' for l in logs)))) + '\n')
                    for s0 in starts:
                        t1 = s0 + 24*182
                        eq, logs, curve = account(bk, METHODS[mname], start=start, risk=risk, t_from=s0, t_to=t1)
                        f.write(json.dumps(dict(kind='window', s0=s0, ent=ent, flt=flt, m=mname, risk=risk, start=start, end=eq, dd=dd(curve), n=len(logs))) + '\n')
                f.flush()
            print(ent, flt, mname, round(time.time() - t0), 's', flush=True)
