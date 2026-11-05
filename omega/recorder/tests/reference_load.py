# VERBATIM copy of research load.dec_market
import numpy as np
def cum(a): return np.cumsum(np.asarray(a, dtype=np.int64))
def dec_market(m, tf):
    dp = m['dp']; s = 10.0**-dp
    t = cum(m['t']); c = cum(m['c'])*s
    o_off = np.asarray(m['o'], dtype=np.int64)*s; h_off = np.asarray(m['h'], dtype=np.int64)*s; l_off = np.asarray(m['l'], dtype=np.int64)*s
    o = c + o_off; hi = np.maximum(o, c) + h_off; lo = np.minimum(o, c) - l_off
    out = { 'sym':m['sym'], 'src':m.get('src'), 't':t, 'o':o, 'h':hi, 'l':lo, 'c':c, 'v':np.asarray(m['v'], dtype=float), 'tb':np.asarray(m.get('tb') or [], dtype=float)/1000.0 }
    if isinstance(m.get('fund'), dict) and m['fund'].get('t'):
        out['ft'] = cum(m['fund']['t']); out['fr'] = np.asarray(m['fund']['r'], dtype=float)*1e-7
    if isinstance(m.get('prem'), dict) and m['prem'].get('t'):
        out['pt'] = cum(m['prem']['t']); out['pc_raw'] = np.asarray(m['prem']['c'], dtype=float)
    return out
