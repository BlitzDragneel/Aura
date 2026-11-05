import sys, json, time; sys.path.insert(0,'/home/claude/edge')
from engine2 import *
ENTRIES = ['donch10','donch20','donch55','ema20_50','ema50_200','rsi2_trend','rsi14_rev','bb_fade','bb_squeeze','keltner','supertrend','macd_trend','insidebar','burst3','burst2','climax','blowoff','sweep_fade','break72_hold','rel_strength','funding_fade','mkt_flush_long']
t0 = time.time(); bases(); print('bases', round(time.time()-t0), 's', flush=True)
with open('sweep1.jsonl','w') as f:
    for e in ENTRIES:
        for flt in FILTERS:
            T = run(e, flt, 'T2'); st = stat(T)
            f.write(json.dumps(dict(entry=e, flt=flt, mg='T2', **st)) + '\n'); f.flush()
        print(e, round(time.time()-t0), 's', flush=True)
