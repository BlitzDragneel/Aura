import sys; sys.path.insert(0,'/home/claude/edge')
from load import *
import json, datetime as dt
sm = json.load(open('spotmap.json'))
dy, ms = load('final4_young'); M = {m['sym']: m for m in ms}
FEE_RT = 0.0030   # taker both legs, in and out: spot 0.10% x2 + perp 0.05% x2
def series(sym):
    m = M[sym]; ft = m['ft']*60; fr = m['fr']; pt = m['pt']*3600; pc = m['pc_raw']*1e-7
    return ft, fr, pt, pc
def run(sym, start_s, end_s):
    ft, fr, pt, pc = series(sym)
    fsel = (ft > start_s) & (ft <= end_s)
    i0 = np.searchsorted(pt, start_s); i1 = np.searchsorted(pt, end_s) - 1
    if i0 >= len(pt) or i1 <= i0: return None
    fund = fr[fsel].sum(); basis = pc[i0] - pc[i1]     # short perp / long spot gains when the premium shrinks
    worst = (pc[i0:i1+1] - pc[i0]).max()                 # worst mark-to-market from the premium widening
    return { 'fund':fund, 'basis':basis, 'net':fund + basis - FEE_RT, 'days':(pt[i1]-pt[i0])/86400, 'worstBasis':worst, 'negShare': float(np.mean(fr[fsel] < 0)) if fsel.any() else None }
