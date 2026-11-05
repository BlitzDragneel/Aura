"""E23: build the signal table (one row per H1 signal, with fill result and selection features) for a set of files."""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/edge'); from load import load; from e21_lib import hourly_from; from e22_lib import prep, base
def table(parts, unit, lo_h, hi_h, min_age):
    rows = []
    for part in parts:
        d, ms = load(part); mult = unit if unit else int(d.get('tf', 60))*60
        for mk in ms:
            df = hourly_from(mk, (mk['t']*mult).astype(np.int64)); P = prep(df); c, l, idx, n = P['c'], P['l'], P['idx'], len(P['c'])
            v24 = df.v.rolling(24).sum(); vr = (v24/v24.rolling(720, min_periods=360).median().shift(1)).values; liq = (df.c*df.v).rolling(24).sum().values
            first = int(np.argmax(np.isfinite(c))); nxt = -1
            for t in np.where(base(P, 10))[0]:
                if t < nxt or t - first < min_age or idx[t] < lo_h or idx[t] >= hi_h or not (P['sig'][t] > 0 and c[t] > 0): continue
                lim = c[t]*np.exp(-2*P['sig'][t]); f = None
                for j in range(t + 1, min(n, t + 4)):
                    if l[j] < lim: f = j; break
                if f is not None and (f + 24 >= n or not (c[f + 24] > 0)): continue
                net = (c[f + 24]/lim - 1 - 0.0012 - 0.0003) if f is not None else None
                rows.append(dict(sym=mk['sym'], h=int(idx[t]), fill=None if f is None else int(idx[f]), net=net, depth=float(P['r24'][t]), vr=float(vr[t]) if np.isfinite(vr[t]) else 0.0, liq=float(liq[t]) if np.isfinite(liq[t]) else 0.0))
                nxt = (f + 24) if f is not None else t + 3
    return pd.DataFrame(rows)
H = lambda x: pd.Timestamp(x).value//3600_000_000_000
if sys.argv[1] == 'dev': T = table(['creed15_1', 'creed15_2', 'creed15_3', 'creed15_4', 'creed15_5'], 900, H('2020-03-01'), H('2026-10-18'), 720)
else: T = table(['final4_a', 'final4_b', 'final4_c', 'final4_d', 'final4_young'], None, H('2024-01-01'), H('2026-10-18'), 720)
T.to_pickle(f'/home/claude/edge/e23_{sys.argv[1]}.pkl'); print(sys.argv[1], len(T), 'signals,', int(T.fill.notna().sum()), 'filled, coins', T.sym.nunique())
