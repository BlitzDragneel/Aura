import sys; sys.path.insert(0,'/home/claude/edge')
from harvest import *
DAY = 86400
def daily_frame(sym):
    m = M[sym]; ft, fr, pt, pc = series(sym)
    perp0 = int(m['t'][0])*3600; spot0 = int(dt.datetime.fromisoformat(sm['spotYoung'][sym]).replace(tzinfo=dt.UTC).timestamp())
    start = (max(perp0, spot0)//DAY + 1)*DAY; end = (int(m['t'][-1])*3600)//DAY*DAY
    days = np.arange(start, end, DAY)
    if len(days) < 5: return None
    fday = np.array([fr[(ft > d) & (ft <= d + DAY)].sum() for d in days])                 # funding paid to shorts over (d, d+1]
    idx = np.clip(np.searchsorted(pt, days) - 1, 0, len(pc)-1); pd_ = pc[idx]           # premium at each day boundary (last hourly value before)
    return { 'days':days, 'fund':fday, 'prem':pd_, 'age0':start, 'listed':max(perp0, spot0) }
