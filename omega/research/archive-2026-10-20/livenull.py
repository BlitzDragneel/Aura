import sys, json, time; sys.path.insert(0,'/home/claude/edge')
from live import *
CASES = [('break72_hold','us_hours','your method',0.01), ('break72_hold','us_hours','your method',0.02), ('burst3','us_hours','pyramid',0.01), ('burst3','us_hours','pyramid',0.02)]
t0 = time.time(); books = {}
with open('livenull.jsonl','w') as f:
    for ent, flt, m, risk in CASES:
        if (ent, flt) not in books: books[(ent, flt)] = signal_book(ent, flt)
        bk = books[(ent, flt)]
        real, logs, _ = account(bk, METHODS[m], 100.0, risk, t_from=SPLIT_H)
        rng = np.random.default_rng(1); nulls = []
        for k in range(100):
            flip = rng.choice([-1, 1], size=len(bk))
            rb = [(a, b, c, d, int(fl)) for (a, b, c, d, _), fl in zip(bk, flip)]
            eq, _, _ = account(rb, METHODS[m], 100.0, risk, t_from=SPLIT_H); nulls.append(eq)
        # monthly results of the real account, and 6-month accounts started inside the unseen half
        wins = []
        for s0 in [int(x.value//3600//10**9) for x in pd.date_range('2025-07-01', '2026-04-01', freq='MS')]:
            e6, _, _ = account(bk, METHODS[m], 100.0, risk, t_from=s0, t_to=s0 + 24*182); wins.append(e6)
        L = pd.DataFrame(logs); L['mon'] = pd.to_datetime(L.out*3600, unit='s').dt.to_period('M')
        mon = L.groupby('mon').pnl.sum(); start_eq = L.groupby('mon').eq.first() - L.groupby('mon').pnl.first()
        mret = (mon/start_eq).values
        f.write(json.dumps(dict(ent=ent, flt=flt, m=m, risk=risk, real=real, nulls=nulls, win6=wins, mret=list(mret))) + '\n'); f.flush()
        print(ent, m, risk, round(time.time() - t0), 's', flush=True)
