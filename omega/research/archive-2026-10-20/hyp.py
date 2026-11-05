import pickle, numpy as np, pandas as pd
P = pickle.load(open('/home/claude/edge/perp_daily.pkl','rb'))
def frame(col):
    F = pd.DataFrame({s: g[col] for s, g in P.items()}).sort_index(); F.index = pd.to_datetime(F.index.astype('int64'), unit='s'); return F
C = frame('c'); FU = frame('fund').reindex(C.index); QV = frame('qv').reindex(C.index); TB = frame('tbr').reindex(C.index)
R = C.pct_change(fill_method=None)                      # daily close-to-close return
AGE = C.notna().cumsum()                                # days since first close
LIQ = QV.rolling(20, min_periods=10).median().shift(1)   # known before the day
SPLIT = pd.Timestamp('2025-07-01'); COST = 0.001         # per side: 0.05% taker + 0.05% slippage
def tstat_weekly(daily):
    w = daily.resample('W').sum(); w = w[w != 0]
    return (w.mean()/w.std()*np.sqrt(len(w)) if len(w) > 3 and w.std() > 0 else np.nan), len(w)
def report(name, daily):
    out = {}
    for lab, sl in [('train', daily[daily.index < SPLIT]), ('test', daily[daily.index >= SPLIT])]:
        t, nw = tstat_weekly(sl); ann = sl.mean()*365
        out[lab] = (ann, t, nw)
    print(f"{name:52s} TRAIN {out['train'][0]*100:7.1f}%/yr t={out['train'][1]:5.2f} ({out['train'][2]}w) | TEST {out['test'][0]*100:7.1f}%/yr t={out['test'][1]:5.2f} ({out['test'][2]}w)")
    return out
def xs_portfolio(score, hold=7, q=0.2, minliq=5e6, minage=30, sign=+1):
    """weekly long-short: long the lowest score quintile, short the highest (sign=+1); returns daily P&L incl. funding and costs"""
    days = C.index; pnl = pd.Series(0.0, index=days); w_prev = pd.Series(dtype=float)
    reb = days[::hold]
    W = pd.DataFrame(0.0, index=days, columns=C.columns)
    for d in reb:
        s = score.loc[d]; ok = (LIQ.loc[d] >= minliq) & (AGE.loc[d] >= minage) & s.notna() & C.loc[d].notna()
        s = s[ok]
        if len(s) < 20: continue
        k = max(2, int(len(s)*q)); lo = s.nsmallest(k).index; hi = s.nlargest(k).index
        w = pd.Series(0.0, index=C.columns); w[lo] = sign*0.5/k; w[hi] = -sign*0.5/k
        W.loc[d:] = w.values
    Wl = W.shift(1).fillna(0.0)                                       # weights set at close d apply to returns of d+1
    gross = (Wl*R.fillna(0.0)).sum(axis=1) + (-(Wl)*FU.fillna(0.0)).sum(axis=1)   # longs pay funding, shorts receive
    turn = (W - W.shift(1).fillna(0.0)).abs().sum(axis=1)
    return gross - turn*COST
def run_variant(score, sign=-1, hold=7, q=0.2, minliq=5e6, cost=0.001, wins=None, excl_young=False, legs='both'):
    global COST, R
    R0 = R; COST0 = COST
    try:
        COST = cost
        if wins is not None: R = R0.clip(-wins, wins)
        sc = score.copy()
        if excl_young:
            yng = [s for s, g in P.items() if bool(g['young'].iloc[0])]; sc[yng] = np.nan
        days = C.index; W = pd.DataFrame(0.0, index=days, columns=C.columns)
        for d in days[::hold]:
            s = sc.loc[d]; ok = (LIQ.loc[d] >= minliq) & (AGE.loc[d] >= 30) & s.notna() & C.loc[d].notna(); s = s[ok]
            if len(s) < 20: continue
            k = max(2, int(len(s)*q)); lo = s.nsmallest(k).index; hi = s.nlargest(k).index
            w = pd.Series(0.0, index=C.columns)
            if legs in ('both','long'): w[hi if sign < 0 else lo] = 0.5/k
            if legs in ('both','short'): w[lo if sign < 0 else hi] = -0.5/k
            W.loc[d:] = w.values
        Wl = W.shift(1).fillna(0.0)
        gross = (Wl*R.fillna(0.0)).sum(axis=1) + (-(Wl)*FU.fillna(0.0)).sum(axis=1)
        turn = (W - W.shift(1).fillna(0.0)).abs().sum(axis=1)
        return gross - turn*COST, Wl
    finally:
        R = R0; COST = COST0
