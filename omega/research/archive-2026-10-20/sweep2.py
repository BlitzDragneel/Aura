import sys, json, time; sys.path.insert(0,'/home/claude/edge')
import engine2 as E
import numpy as np, pandas as pd
ENTRIES = ['donch10','donch20','donch55','ema20_50','ema50_200','rsi2_trend','rsi14_rev','bb_fade','bb_squeeze','keltner','supertrend','macd_trend','insidebar','burst3','burst2','climax','blowoff','sweep_fade','break72_hold','rel_strength','funding_fade','mkt_flush_long']
def sweep(path):
    t0 = time.time(); E.FB.clear(); E.bases()
    with open(path, 'w') as f:
        for e in ENTRIES:
            for flt in E.FILTERS:
                for mg in E.MGMT:
                    T = E.run(e, flt, mg); f.write(json.dumps(dict(entry=e, flt=flt, mg=mg, **E.stat(T))) + '\n')
            f.flush(); print(path, e, round(time.time()-t0), 's', flush=True)
sweep('sweep_real.jsonl')
# null world: every coin's hours shuffled, market index shuffled separately (no trends, no links)
rng = np.random.default_rng(5); SH = {}
for s, u in E.H.items():
    c = u['c']; pc = np.r_[c[0], c[:-1]]; p = rng.permutation(len(c) - 1) + 1
    lr = np.log(c/pc)[p]; cc = np.r_[c[0], c[0]*np.exp(np.cumsum(lr))]; prev = cc[:-1]
    o = np.r_[u['o'][0], prev*(u['o']/pc)[p]]; h = np.r_[u['h'][0], prev*(u['h']/pc)[p]]; l = np.r_[u['l'][0], prev*(u['l']/pc)[p]]
    SH[s] = dict(t=u['t'], c=cc, o=o, h=np.maximum(h, np.maximum(o, cc)), l=np.minimum(l, np.minimum(o, cc)), qv=np.r_[u['qv'][0], u['qv'][p]], fund=np.r_[u['fund'][0], u['fund'][p]])
E.H = SH; mlr = E.MK['lr'][rng.permutation(len(E.MK['lr']))]; midx = np.exp(np.cumsum(mlr))
E.midx = midx; E.mtrend_all = np.where(midx > E.ema(midx, 480), 1, -1); ms = pd.Series(mlr).rolling(168).std().shift(1).values; E.mz_all = mlr/ms
sweep('sweep_null.jsonl')
