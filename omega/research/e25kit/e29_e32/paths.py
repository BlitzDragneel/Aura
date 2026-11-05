"""Path diagnosis of CREED's on-time setups (diag_part*.json from creed_diag.js, the app's own engine) on the creed15 files."""
import json, sys, glob, numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/omega/research'); from load import load
COST = 0.0012                                                     # 0.06% a side, as CREED's replay
bars = {}
for p in ['creed15_1', 'creed15_3', 'creed15_4', 'creed15_5']:
    d, ms = load(p)
    for m in ms:
        t = m['t']*900                                            # bar open, seconds (tf 15)
        df = pd.DataFrame({'o':m['o'], 'h':m['h'], 'l':m['l'], 'c':m['c'], 'v':m['v'], 'tb':m['tb']}, index=t)
        df = df[~df.index.duplicated()].sort_index(); bars[m['sym']] = df
btc = bars['BTCUSDT']
rows = []
for f in sorted(glob.glob('diag_part*.json')):
    D = json.load(open(f))
    for sym, C in D['coins'].items():
        df = bars[sym]; T = df.index.values; O, Hh, L, Cc, V, TB = (df[k].values for k in ('o', 'h', 'l', 'c', 'v', 'tb'))
        tr = np.maximum(Hh - L, np.maximum(np.abs(Hh - np.r_[Cc[0], Cc[:-1]]), np.abs(L - np.r_[Cc[0], Cc[:-1]])))
        atr = pd.Series(tr).rolling(96).mean().values                # 1-day average 15-min true range
        atrp = pd.Series(atr/Cc).rolling(96*90, min_periods=96*30).rank(pct=True).values   # volatility regime: percentile over 90 days
        vmed = pd.Series(V).rolling(96*7, min_periods=96).median().values
        bt = btc.c.reindex(df.index).values
        for tr_ in C['trades']:
            dec_open = tr_['t']//1000 - 900; k = np.searchsorted(T, dec_open)
            if k >= len(T) or T[k] != dec_open: continue
            e, s, g, d = tr_['entry'], tr_['stop'], tr_['target'], (1 if tr_['d'] == 'L' else -1); R = abs(e - s)
            if not (R > 0): continue
            hi, lo, cl = Hh[k + 1:k + 1 + 96*14], L[k + 1:k + 1 + 96*14], Cc[k + 1:k + 1 + 96*14]
            fav = (hi - e)/R if d > 0 else (e - lo)/R; adv = (e - lo)/R if d > 0 else (hi - e)/R
            stop_i = np.argmax(adv >= 1) if (adv >= 1).any() else None
            def first(x): return int(np.argmax(fav >= x)) if (fav >= x).any() else None
            rrT = abs(g - e)/R; tgt_i = first(rrT)
            mfe_before_stop = float(fav[:stop_i + 1].max()) if stop_i is not None else float(fav.max())
            raw = (rrT if (tgt_i is not None and (stop_i is None or tgt_i < stop_i)) else (-1.0 if stop_i is not None else float(d*(cl[-1] - e)/R)))
            si = k - (tr_['i'] - tr_['sbar'])                        # sweep bar index in the coin's series
            sweep_depth = abs(tr_['sx'] - tr_['lvl'])/atr[k] if tr_['lvl'] and atr[k] > 0 else np.nan
            b24 = np.log(bt[k]/bt[k - 96]) if k >= 96 and bt[k] > 0 and bt[k - 96] > 0 else np.nan
            c24 = np.log(Cc[k]/Cc[k - 96]) if k >= 96 else np.nan
            rows.append(dict(sym=sym, t=pd.Timestamp(dec_open + 900, unit='s'), d=tr_['d'], kind=tr_['k'], r=tr_['r'], cost=COST*e/R, rr=rrT,
                risk_pct=R/e*100, risk_atr=R/atr[k] if atr[k] > 0 else np.nan, sweep_depth_atr=sweep_depth, z=tr_.get('z'),
                vol_x=V[si]/vmed[si] if 0 <= si < len(V) and vmed[si] > 0 else np.nan, tb=TB[si] if 0 <= si < len(TB) else np.nan,
                volreg=atrp[k], btc24=b24*d if b24 == b24 else np.nan, coin24=c24*d if c24 == c24 else np.nan, hour=pd.Timestamp(dec_open + 900, unit='s').hour,
                wd=pd.Timestamp(dec_open + 900, unit='s').dayofweek, mfe=float(fav.max()), mfe_bs=mfe_before_stop, mae=float(adv.max()),
                hit1=first(1) is not None and (stop_i is None or first(1) < stop_i), hit2=first(2) is not None and (stop_i is None or first(2) < stop_i),
                hit3=first(3) is not None and (stop_i is None or first(3) < stop_i), tgt=tgt_i is not None and (stop_i is None or tgt_i < stop_i),
                raw=raw, bars_to_stop=stop_i, struct=tr_['sr'], why=tr_['w']))
X = pd.DataFrame(rows); X.to_pickle('creed_paths.pkl'); print(len(X), 'trades with paths;', X.sym.nunique(), 'coins;', X.t.min().date(), '→', X.t.max().date())
