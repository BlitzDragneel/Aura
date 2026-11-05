import numpy as np, pandas as pd
T = pd.read_pickle('/home/claude/edge/climax_trades.pkl')
EV = [g[['r','fund','mae']].values for _, g in T.groupby('event')]
def run_event(eq, trades, slot, lev, shift):
    """each trade: margin = slot*eq (isolated), notional = lev*margin; liquidated if the dip inside the trade reaches the margin"""
    pnl = 0.0; k = min(len(trades), 20, int(round(1/slot)))
    for r, fund, mae in trades[:k]:
        m = slot*eq
        if mae <= -(1/lev - 0.005): pnl -= m*1.0          # liquidated: lose the margin
        else: pnl += m*lev*(r + shift - fund - 0.002)
    return max(eq + pnl, 0.0)
def sim(slot, lev, shift=0.0, years=5, n=4000, per_year=20, seed=1):
    rng = np.random.default_rng(seed); hit = np.zeros(n, bool); ruin = np.zeros(n, bool); tt = np.full(n, np.nan); finals = np.zeros(n)
    for i in range(n):
        eq = 100.0
        for j in range(years*per_year):
            eq = run_event(eq, EV[rng.integers(len(EV))], slot, lev, shift)
            if eq >= 10000: hit[i] = True; tt[i] = (j+1)/per_year; break
            if eq < 10: ruin[i] = True; break
        finals[i] = eq
    return hit.mean(), ruin.mean(), np.nanmedian(tt) if hit.any() else np.nan, np.median(finals)
