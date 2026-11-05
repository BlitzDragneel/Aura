import sys; sys.path.insert(0,'/home/claude/edge')
from engine2 import *
try:
    from sklearn.ensemble import HistGradientBoostingRegressor as GB; HAVE = True
except Exception: HAVE = False
PRE = ['z','vr','cl','r24','m24','mz','atrpct','f24','exz','hour','mtrend','trendhtf','dist_hi72','dist_lo72']
def trades(entry, flt, mg):
    T, syms = run(entry, flt, mg, keep=True); FB = bases(); rows = []
    for (t0, R, d, i, j, rp), s in zip(T, syms):
        F = FB[s]; i, j = int(i), int(j)
        mkt = d*np.log(midx[F['mi'][j]]/midx[F['mi'][min(i+1, j)]])          # market move during the trade, in the trade's direction
        coin = d*np.log(F['c'][j]/F['o'][i+1]); own = coin - mkt                  # the coin's own part
        x = [F[k][i] if k in F else np.nan for k in PRE[:11]] + [1.0 if F['c'][i] > F['e800'][i] else -1.0, np.log(F['c'][i]/F['hi72'][i]), np.log(F['c'][i]/F['lo72'][i])]
        x = [v*d if k in ('z','r24','m24','mz','f24','exz','mtrend','trendhtf','dist_hi72','dist_lo72') else v for k, v in zip(PRE, x)]   # signed in the trade's direction
        rows.append([t0, R, d, mkt/rp, own/rp] + x)
    return pd.DataFrame(rows, columns=['t','R','d','mkt','own'] + PRE).replace([np.inf, -np.inf], np.nan).dropna()
def r2(y, p): return 1 - np.sum((y - p)**2)/np.sum((y - y.mean())**2)
for entry, flt, mg in [('burst3','none','T5'), ('donch20','none','T2'), ('sweep_fade','none','T2'), ('climax','none','T2')]:
    D = trades(entry, flt, mg); a, b = D[D.t < SPLIT_H], D[D.t >= SPLIT_H]
    y = D.R.clip(-3, 10)
    print(f"\n=== {entry} ({mg}): {len(D)} trades")
    # 1. after entry: how much of each result is the market's move and how much the coin's own move
    for col, lab in [('mkt','the whole market moved during the trade'), ('own','the coin moved on its own')]:
        c = np.corrcoef(D[col].clip(-10, 10), y)[0,1]; print(f"  explained by '{lab}': {c*c*100:4.0f}% of the variation in results")
    c2 = np.linalg.lstsq(np.c_[np.ones(len(D)), D[['mkt','own']].clip(-10,10)], y, rcond=None)[0]
    print(f"  both together: {r2(y, np.c_[np.ones(len(D)), D[['mkt','own']].clip(-10,10)] @ c2)*100:4.0f}%  (the rest is the stop/target path)")
    # 2. before entry: fit on the 1st half, predict the 2nd half
    Xa, Xb = a[PRE].values, b[PRE].values; ya, yb = a.R.clip(-3, 10).values, b.R.clip(-3, 10).values
    mu, sd = Xa.mean(0), Xa.std(0) + 1e-12; A = np.c_[np.ones(len(Xa)), (Xa - mu)/sd]; B = np.c_[np.ones(len(Xb)), (Xb - mu)/sd]
    w = np.linalg.lstsq(A, ya, rcond=None)[0]; p = B @ w
    print(f"  everything known BEFORE entry (14 measures), linear, fitted on 1st half -> 2nd half: explains {r2(yb, p)*100:+.1f}%")
    if HAVE:
        g = GB(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=100).fit(Xa, ya); pg = g.predict(Xb)
        q = pd.qcut(pg, 10, labels=False, duplicates='drop'); top = yb[q == q.max()].mean(); bot = yb[q == q.min()].mean()
        print(f"  same with a machine-learning model: explains {r2(yb, pg)*100:+.1f}% | its best 10% of trades {top:+.3f}R vs worst 10% {bot:+.3f}R vs all {yb.mean():+.3f}R")
    # 3. can the market's move after entry (the main cause) be predicted before entry?
    ma, mb = a.mkt.clip(-10,10).values, b.mkt.clip(-10,10).values; w2 = np.linalg.lstsq(A, ma, rcond=None)[0]
    print(f"  predicting the market's move during the trade from before-entry measures: explains {r2(mb, B @ w2)*100:+.1f}% on the 2nd half")
    # which before-entry measures mattered in both halves (same sign, both meaningful)
    keep = []
    for k in PRE:
        ca = np.corrcoef(a[k], a.R.clip(-3,10))[0,1]; cb = np.corrcoef(b[k], b.R.clip(-3,10))[0,1]
        if np.sign(ca) == np.sign(cb) and abs(ca) > 0.02 and abs(cb) > 0.02: keep.append(f"{k} ({ca:+.2f}/{cb:+.2f})")
    print('  before-entry measures with the same direction in both halves (correlation 1st/2nd):', ', '.join(keep) if keep else 'none')
