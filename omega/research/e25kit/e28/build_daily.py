import pickle, numpy as np, datetime as dt
RAW = pickle.load(open('hourly_e26.pkl', 'rb'))
D0 = int(dt.datetime(2020, 11, 1, tzinfo=dt.timezone.utc).timestamp()//86400); D1 = int(dt.datetime(2026, 10, 19, tzinfo=dt.timezone.utc).timestamp()//86400)
syms = sorted(s for s, x in RAW.items() if (x['v'] > 0).any()); N, T = len(syms), D1 - D0
f32 = lambda: np.full((T, N), np.nan, np.float32)
O, Hh, L, C, DV, NH = f32(), f32(), f32(), f32(), f32(), np.zeros((T, N), np.int8)
LASTD = np.full(N, -1, np.int32); FIRSTD = np.full(N, -1, np.int32)
for j, s in enumerate(syms):
    x = RAW[s]; ok = x['v'] > 0; h = x['h'][ok]; d = h//24 - D0; m = (d >= 0) & (d < T)
    h, d = h[m], d[m]; o, hi, lo, c, v = x['o'][ok][m], x['hi'][ok][m], x['lo'][ok][m], x['c'][ok][m], x['v'][ok][m]
    if not len(d): continue
    FIRSTD[j] = d[0]; LASTD[j] = d[-1]
    # first and last hour of each day
    starts = np.r_[0, np.where(np.diff(d))[0] + 1]; ends = np.r_[starts[1:] - 1, len(d) - 1]; dd = d[starts]
    O[dd, j] = o[starts]; C[dd, j] = c[ends]; NH[dd, j] = (ends - starts + 1)
    Hh[dd, j] = np.maximum.reduceat(hi, starts); L[dd, j] = np.minimum.reduceat(lo, starts); DV[dd, j] = np.add.reduceat(v*c, starts)
days = np.arange(D0, D1)
first_traded_day = FIRSTD   # listing proxy: first real candle (archive starts 2020-11 for older coins)
np.savez_compressed('daily_panel.npz', O=O, H=Hh, L=L, C=C, DV=DV, NH=NH, LASTD=LASTD, FIRSTD=FIRSTD, days=days, syms=np.array(syms))
print(T, 'days x', N, 'coins; full days', int((NH == 24).sum()), '; coins with a last day before 2026-10-11:', int((LASTD < T - 8).sum()))
