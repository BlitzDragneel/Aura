import sys; sys.path.insert(0,'/home/claude/edge')
from load import *
import pandas as pd
def perp_daily():
    rows = {}
    for part in ['final4_a','final4_b','final4_c','final4_d','final4_young']:
        d, ms = load(part)
        for m in ms:
            t = m['t']*3600; day = (t//86400)*86400
            df = pd.DataFrame({'day':day, 'o':m['o'], 'h':m['h'], 'l':m['l'], 'c':m['c'], 'v':m['v'], 'qv':m['v']*m['c'], 'tbq':(m['tb'] if len(m['tb'])==len(t) else np.full(len(t), np.nan))*m['v']*m['c']})
            g = df.groupby('day').agg(o=('o','first'), h=('h','max'), l=('l','min'), c=('c','last'), qv=('qv','sum'), tbq=('tbq','sum'), n=('c','size'))
            g = g[g.n >= 20]                      # keep days with most hours present
            ft = m['ft']*60; fd = (ft//86400)*86400
            fs = pd.Series(m['fr']).groupby(fd).sum()
            g['fund'] = fs.reindex(g.index).fillna(0.0)   # funding paid by longs to shorts during that UTC day
            g['tbr'] = g.tbq/g.qv
            g['young'] = part == 'final4_young'
            rows[m['sym']] = g
    return rows
if __name__ == '__main__':
    P = perp_daily(); import pickle; pickle.dump(P, open('perp_daily.pkl','wb'))
    first = sorted(int(g.index[0]) for g in P.values()); 
    print('perps', len(P), '| first day range', pd.to_datetime(first[0], unit='s').date(), '->', pd.to_datetime(first[-1], unit='s').date(), '| coin-days', sum(len(g) for g in P.values()))
