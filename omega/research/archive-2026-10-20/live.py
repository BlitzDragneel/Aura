"""Live-account simulator: one market at a time, several units in that market, Binance USD-M rules."""
import sys; sys.path.insert(0,'/home/claude/edge')
from engine2 import *
FEE = 0.001; MIN_NOTIONAL = 5.0; MAX_LEV = 20.0; MAINT = 0.005
def signal_book(entry, flt):
    """every eligible signal: (hour, priority, sym, i, direction)"""
    book = []
    for s, F in bases().items():
        x = apply_filter(signal(entry, F), flt, F); x = np.where(F['liq'] & ~np.isnan(F['atr']) & (F['age'] >= 820) & (F['t'] >= START_H), x, 0)
        for i in np.where(x != 0)[0]:
            if i + 2 >= len(F['c']): continue
            pr = abs(F['z'][i]) if not np.isnan(F['z'][i]) else 0.0
            if entry == 'break72_hold': pr = F['vr'][i]
            if entry == 'climax': pr = -F['z'][i]
            book.append((int(F['t'][i]), float(pr), s, int(i), int(x[i])))
    book.sort(key=lambda r: (r[0], -r[1])); return book
def trade(F, i, d, eq, risk, M):
    """play one trade bar by bar in USDT. M: method dict. Returns (new equity, log dict, exit hour)"""
    o, h, l, c, fund, atr = F['o'], F['h'], F['l'], F['c'], F['fund'], F['atr']
    e = o[i+1]; Rd = M['stop_atr']*atr[i]
    if Rd <= 0.001*e: return eq, None, int(F['t'][i+1])
    base_notional = risk*eq/(Rd/e)                         # notional at which a full stop-out loses risk*eq
    lots = []; fees = 0.0; fundpaid = 0.0; bumped = False
    def open_lot(px, size):
        nonlocal fees, bumped
        notional = size*base_notional
        if notional < MIN_NOTIONAL: notional = MIN_NOTIONAL; bumped = True
        tot = sum(q*px for q, _ in lots)
        if tot + notional > MAX_LEV*max(eq_now(px), 0):    # margin cap
            notional = MAX_LEV*max(eq_now(px), 0) - tot
            if notional < MIN_NOTIONAL: return False
        lots.append([notional/px, px]); fees += notional*FEE; return True
    def upnl(px): return sum(d*q*(px - p) for q, p in lots)
    def eq_now(px): return eq - fees - fundpaid + upnl(px) + realized[0]
    realized = [0.0]
    def close_qty(qty, px):
        nonlocal fees
        while qty > 1e-12 and lots:
            q, p = lots[0]; take = min(q, qty); realized[0] += d*take*(px - p); fees += take*px*FEE; lots[0][0] -= take; qty -= take
            if lots[0][0] <= 1e-12: lots.pop(0)
    for sz in M['init']: open_lot(e, sz)
    if not lots: return eq, None, int(F['t'][i+1])
    stop = e - d*Rd; best = e; last_add = e; adds = 0; scaled = False; j = i + 1; why = 'time'
    while j < len(c):
        gap = o[j]                                                        # only a gap at the open can jump past both the stop and the liquidation price
        if eq_now(gap) <= MAINT*sum(q*gap for q, _ in lots):
            realized[0] = -(eq - fees - fundpaid) + realized[0]*0; lots.clear(); why = 'liquidated'; break
        if (l[j] <= stop) if d == 1 else (h[j] >= stop):
            px = min(o[j], stop) if d == 1 else max(o[j], stop); close_qty(sum(q for q, _ in lots), px); why = 'stop'; break
        if M.get('hold'):                                                 # fixed holding period (climax rule)
            if j - i >= M['hold']: close_qty(sum(q for q, _ in lots), c[j]); why = 'time'; break
        if M.get('sc_frac') and not scaled:
            lv = e + d*M['sc_R']*Rd
            if (h[j] >= lv) if d == 1 else (l[j] <= lv):
                close_qty(M['sc_frac']*sum(q for q, _ in lots), lv); scaled = True
                if M.get('be_after_scale'): stop = e if (d == 1 and e > stop) or (d == -1 and e < stop) else stop
        if M.get('tgt_R'):
            lv = e + d*M['tgt_R']*Rd
            if (h[j] >= lv) if d == 1 else (l[j] <= lv): close_qty(sum(q for q, _ in lots), lv); why = 'target'; break
        if M.get('pyr_R') and adds < M['pyr_max']:
            lv = last_add + d*M['pyr_R']*Rd
            if (h[j] >= lv) if d == 1 else (l[j] <= lv):
                if open_lot(lv, M['add_size']):
                    adds += 1; last_add = lv; ns = lv - d*Rd
                    if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
        fundpaid += d*sum(q for q, _ in lots)*c[j]*fund[j]
        best = max(best, h[j]) if d == 1 else min(best, l[j])
        if M.get('trail_atr'):
            ns = best - d*M['trail_atr']*atr[i]
            if (d == 1 and ns > stop) or (d == -1 and ns < stop): stop = ns
        if j - i >= M['max_bars']: close_qty(sum(q for q, _ in lots), c[j]); why = 'time'; break
        j += 1
    if lots: close_qty(sum(q for q, _ in lots), c[min(j, len(c)-1)])
    new = max(eq + realized[0] - fees - fundpaid, 0.0)
    return new, dict(pnl=new - eq, R=(new - eq)/(risk*eq) if eq > 0 else 0, why=why, adds=adds, bumped=bumped, fees=fees, fund=fundpaid), int(F['t'][min(j, len(c)-1)])
def account(book, M, start=100.0, risk=0.02, t_from=START_H, t_to=10**9, slots=1):
    FB = bases(); eq = start; free_at = [t_from]*slots; logs = []; curve = [(t_from, eq)]
    k = 0; n = len(book)
    while k < n:
        hr, pr, s, i, d = book[k]
        if hr < t_from: k += 1; continue
        if hr >= t_to or eq < 1.0: break
        slot = min(range(slots), key=lambda z: free_at[z])
        if hr < free_at[slot]: k += 1; continue                        # busy: this setup is skipped
        new, lg, out = trade(FB[s], i, d, eq if slots == 1 else eq/slots*slots, risk, M)
        if lg is None: k += 1; continue
        eq = new; free_at[slot] = out; lg.update(sym=s, hr=hr, out=out, eq=eq); logs.append(lg); curve.append((out, eq)); k += 1
    return eq, logs, curve
METHODS = {
 'pyramid':        dict(init=[1.0], stop_atr=2.0, trail_atr=3.0, pyr_R=1.0, pyr_max=3, add_size=1.0, max_bars=168),
 'your method':    dict(init=[0.2]*5, stop_atr=2.0, trail_atr=3.0, sc_frac=0.6, sc_R=1.0, be_after_scale=True, pyr_R=1.0, pyr_max=3, add_size=0.2, max_bars=168),
 'fixed 2R target':dict(init=[1.0], stop_atr=2.0, tgt_R=2.0, max_bars=72),
 'climax 12h':     dict(init=[1.0], stop_atr=4.0, hold=12, max_bars=13),
}
