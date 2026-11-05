"""E26 accounts per PLAN_E26 + addendum A. Reads e26_tables.pkl (signals and per-coin random-trade results)."""
import pickle, json, numpy as np, pandas as pd, datetime as dt, hashlib, heapq
T = pickle.load(open('e26_tables_nostop.pkl', 'rb')); SIG, COIN = T['SIG'], T['COIN']
HH = lambda s: int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp() // 3600)
MON0 = HH('2020-12-28')                      # a Monday 00:00 UTC
def account(sigs, floor, nmax):
    """sigs sorted by (hour, depth). Returns final equity, booked curve, trades [(entry_h, exit_h, size, net, sym)], skipped."""
    eq = 100.0; seat = max(floor, eq/nmax); week = None; busy = []; book = []; curve = []; trades = []; held = {}; skipped = 0
    by_h = {}
    for s in sigs: by_h.setdefault(s[0], []).append(s)
    for h in sorted(by_h):
        while book and book[0][0] <= h: xh, pnl = heapq.heappop(book); eq += pnl; curve.append((xh, eq))
        busy = [b for b in busy if b[0] > h]; held = {b[1] for b in busy}
        w = (h - MON0)//168
        if w != week: week = w; seat = max(floor, eq/nmax)
        allowed = min(nmax, int(eq // seat)) if eq > 0 else 0
        for s in sorted(by_h[h], key=lambda s: s[2]):            # deepest 24-hour fall first
            t, sym, depth, fill, xh, net, kind = s
            if sym in held or len(busy) >= allowed: skipped += 1; continue
            busy.append((xh if fill is not None else t + 3, sym)); held.add(sym)
            if fill is not None: heapq.heappush(book, (xh, seat*net)); trades.append((fill, xh, seat, net, sym, kind))
    while book: xh, pnl = heapq.heappop(book); eq += pnl; curve.append((xh, eq))
    return eq, curve, trades, skipped
def stats(curve, start=100.0):
    s = pd.Series([e for _, e in curve], index=pd.to_datetime([h*3600 for h, _ in curve], unit='s')); y = s.groupby(s.index.year).last(); prev = start; yrs = {}
    for yr, v in y.items(): yrs[int(yr)] = round((v/prev - 1)*100, 2); prev = v
    dd = float((s/s.cummax().clip(lower=start) - 1).min()*100) if len(s) else 0.0; return yrs, dd
ELIG = {}
def eligible(h):
    if h not in ELIG:
        ELIG[h] = [s for s, (h0, rr, xh) in COIN.items() if 0 <= h - h0 < len(rr) and np.isfinite(rr[h - h0])]
    return ELIG[h]
def random_account(trades, rng):
    eq = 100.0; book = []; open_ = []
    for fill, xh_real, size, net_real, sym_real, kind_real in trades:
        while book and book[0][0] <= fill: x, pnl = heapq.heappop(book); eq += pnl
        open_ = [o for o in open_ if o[0] > fill]; held = {o[1] for o in open_}
        el = eligible(fill)
        for _ in range(20):
            s = el[rng.integers(len(el))]
            if s not in held: break
        h0, rr, xh = COIN[s]; heapq.heappush(book, (int(xh[fill - h0]), size*float(rr[fill - h0]))); open_.append((int(xh[fill - h0]), s))
    while book: x, pnl = heapq.heappop(book); eq += pnl
    return eq
sigs = sorted(SIG, key=lambda s: (s[0], s[2])); OUT = {}
for arm, floor, nmax in (('A 5 USDT seats, up to 20', 5.0, 20), ('B 10 USDT seats, up to 10', 10.0, 10)):
    eq, curve, trades, skipped = account(sigs, floor, nmax); yrs, dd = stats(curve)
    rng = np.random.default_rng(26); RND = np.array([random_account(trades, rng) for _ in range(500)])
    beats = float((RND < eq).mean()*100); gain_years = sum(1 for y in range(2021, 2027) if yrs.get(y, -1) > 0)
    passed = beats >= 97.5 and eq > 100 and dd > -35 and gain_years >= 5
    eq2, curve2, tr2, _ = account([s for s in sigs if s[1] not in ('BTCUSDT', 'ETHUSDT')], floor, nmax)
    nets = np.array([t[3] for t in trades])
    OUT[arm] = dict(final=eq, trades=len(trades), skipped=skipped, years=yrs, maxdd=dd, gain_years=gain_years, random_median=float(np.median(RND)),
                    random_p975=float(np.percentile(RND, 97.5)), beats=beats, passed=bool(passed), without_btc_eth=eq2,
                    trade_mean=float(nets.mean()), trade_median=float(np.median(nets)), winners=float((nets > 0).mean()), worst=float(nets.min()),
                    stops=int(sum(1 for t in trades if t[5] == 'stop')), delisted_exits=int(sum(1 for t in trades if t[5] == 'delisted')))
    print(arm, json.dumps(OUT[arm]), flush=True)
json.dump(OUT, open('E26_nostop_DESCRIPTIVE.json', 'w'), indent=1)
print('result md5', hashlib.md5(open('E26_nostop_DESCRIPTIVE.json', 'rb').read()).hexdigest())
