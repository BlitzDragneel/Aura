"""E43 funding-settlement windows, E44 US cash-open, E45 turn-of-month (10 majors). usage: python run_timing.py E43 [R]"""
import sys, time, pickle
import numpy as np, pandas as pd
from lib1 import *  # noqa
from searchkit import WeekAgg

MAJ = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "LTCUSDT"]


def trades_at(d, tf, sym, q24, t_in, t_out, side):
    """Enter at the open of the bar starting t_in, exit at the close of the bar ending t_out (taker both)."""
    bar = pd.Timedelta(minutes=TFMIN[tf])
    t_in = pd.DatetimeIndex(t_in); t_out = pd.DatetimeIndex(t_out); side = np.asarray(side, float)
    if len(t_in) == 0:
        return None
    i = d.index.get_indexer(t_in); j = d.index.get_indexer(t_out - bar)
    ok = (i >= 0) & (j >= i)
    i, j, side, t_in, t_out = i[ok], j[ok], side[ok], t_in[ok], t_out[ok]
    o, c, h, l = d.o.values, d.c.values, d.h.values, d.l.values
    e, x = o[i], c[j]
    ok = np.isfinite(e) & np.isfinite(x) & (e > 0)
    i, j, side, t_in, t_out, e, x = i[ok], j[ok], side[ok], t_in[ok], t_out[ok], e[ok], x[ok]
    if len(i) == 0:
        return None
    flat = np.empty(2 * len(i), dtype=np.int64); flat[0::2] = i; flat[1::2] = j + 1
    lp = np.append(l, np.nan); hp = np.append(h, np.nan)
    lmin = np.fmin.reduceat(lp, flat)[0::2]; hmax = np.fmax.reduceat(hp, flat)[0::2]
    mae = np.where(side > 0, lmin / e - 1, 1 - hmax / e)
    gross = side * (x / e - 1)
    cost = bt.round_trip_cost(np.nan_to_num(q24[i], nan=0.0), "taker", "taker")
    held = (t_out - t_in).total_seconds().values / 3600
    fund = np.where(held > 8, funding_paid(sym, t_in.as_unit("ms").asi8, t_out.as_unit("ms").asi8), 0.0) * side
    return pd.DataFrame(dict(time=t_in, sym=sym, exit_time=t_out, gross=gross, cost=cost, fund=fund,
                             net=gross - cost - fund, mae=mae, side=side))


# ------------------------------------------------------------------ E43
E43V = [(w, k) for w in (30, 60, 120) for k in ("PRE-HIGH", "PRE-LOW", "POST-HIGH", "POST-LOW", "PRE-ALL", "POST-ALL")]


def e43_events(sym):
    f = bt.funding(sym)
    t = pd.DatetimeIndex(f.index).as_unit("ns").round("5min")
    r = f.values
    s = pd.Series(r, index=t)
    s = s[~s.index.duplicated()]
    prev = s.shift(1)
    roll = s.rolling("90D", min_periods=100)
    p90 = roll.quantile(0.9).shift(1); p10 = roll.quantile(0.1).shift(1)
    high = (prev >= p90) & (prev > 0.0001); low = (prev <= p10) & (prev < 0)
    return pd.DataFrame(dict(high=high.values, low=low.values), index=s.index)


def e43_specs(ev, S):
    """ev: events frame; S: anchor times (same length). returns list per variant of (t_in, t_out, side)."""
    out = []
    for (w, kind) in E43V:
        W = pd.Timedelta(minutes=w)
        if kind.startswith("PRE"):
            if kind == "PRE-HIGH": m, sd = ev.high.values, -1
            elif kind == "PRE-LOW": m, sd = ev.low.values, 1
            else: m, sd = np.ones(len(ev), bool), 1
            out.append((S[m] - W, S[m], np.full(m.sum(), sd)))
        else:
            if kind == "POST-HIGH": m, sd = ev.high.values, 1
            elif kind == "POST-LOW": m, sd = ev.low.values, -1
            else: m, sd = np.ones(len(ev), bool), 1
            out.append((S[m], S[m] + W, np.full(m.sum(), sd)))
    return out


# ------------------------------------------------------------------ E44
E44V = [(mode, hold, cond) for mode in ("FOLLOW", "FADE") for hold in (30, 120, 390) for cond in ("all", "big")]


def ny_open_utc(days):
    loc = pd.DatetimeIndex([pd.Timestamp(f"{dd.date()} 09:30", tz="America/New_York") for dd in days])
    return loc.tz_convert("UTC").as_unit("ns")


def e44_specs(d, A):
    """A: anchor UTC times (one per weekday). pre from 00:00 UTC to A."""
    day0 = A.floor("D")
    i0 = d.index.get_indexer(day0); ia = d.index.get_indexer(A - pd.Timedelta(minutes=5))
    ok = (i0 >= 0) & (ia >= 0)
    pre = np.full(len(A), np.nan)
    pre[ok] = np.log(d.c.values[ia[ok]] / d.o.values[i0[ok]])
    sp = pd.Series(pre).rolling(30, min_periods=20).std().shift(1).values
    out = []
    for (mode, hold, cond) in E44V:
        m = np.isfinite(pre) & (pre != 0)
        if cond == "big":
            m &= np.abs(pre) >= np.nan_to_num(sp, nan=np.inf)
        sd = np.sign(pre[m]) * (1 if mode == "FOLLOW" else -1)
        out.append((A[m], A[m] + pd.Timedelta(minutes=hold), sd))
    return out


# ------------------------------------------------------------------ E45
E45V = [(N, M) for N in (1, 2, 3) for M in (1, 3)]


def e45_specs(months, anchor_day=1):
    """months: month starts (UTC). anchor = day `anchor_day` of each month (1 = real turn of month)."""
    out = []
    for (N, M) in E45V:
        A = months + pd.Timedelta(days=anchor_day - 1)
        out.append((A - pd.Timedelta(days=N), A + pd.Timedelta(days=M), np.ones(len(A))))
    return out


def main(plan, R):
    names = {"E43": [f"w{w} {k}" for w, k in E43V], "E44": [f"{m} hold{h} {c}" for m, h, c in E44V],
             "E45": [f"N{n} M{m}" for n, m in E45V]}[plan]
    nv = len(names); tf = "1h" if plan == "E45" else "5m"
    a, _ = bt.PERIODS["discovery"]
    w0 = int((pd.Timestamp(a).value + 3 * 86400 * 10**9) // (7 * 86400 * 10**9)); w1 = w0 + 215
    agg = WeekAgg((R, nv), w0, w1); rng = np.random.default_rng(int(plan[1:]))
    real = {i: [] for i in range(nv)}
    disc_end = pd.Timestamp(bt.PERIODS["discovery"][1], tz="UTC")
    # shared random anchors for E44 / E45 (same for all coins)
    if plan == "E44":
        days = pd.date_range("2022-01-01", "2026-12-31", freq="D", tz="UTC"); days = days[days.dayofweek < 5]
        A_real = ny_open_utc(days)
        rand_off = rng.integers(72, 216, size=(R, len(days)))  # 06:00..18:00 in 5-min steps
    if plan == "E45":
        months = pd.date_range("2020-01-01", "2026-12-01", freq="MS", tz="UTC").as_unit("ns")
        rand_day = rng.integers(4, 26, size=R)
    for s in MAJ:
        d = load_tf(s, tf); q24 = qv24(d, tf)
        if plan == "E43":
            ev = e43_events(s); S = ev.index
            specs = e43_specs(ev, S)
            dmask = S < disc_end; evd = ev[dmask]; Sd = S[dmask]
        elif plan == "E44":
            specs = e44_specs(d, A_real)
        else:
            specs = e45_specs(months)
        for i, (ti, to, sd) in enumerate(specs):
            tr = trades_at(d, tf, s, q24, ti, to, sd)
            if tr is not None:
                real[i].append(tr)
        for rep in range(R):
            if plan == "E43":
                Sr = Sd.floor("D") + pd.to_timedelta(rng.integers(0, 288, len(Sd)) * 5, unit="min")
                rs = e43_specs(evd, Sr)
            elif plan == "E44":
                Ar = days.as_unit("ns") + pd.to_timedelta(rand_off[rep] * 5, unit="min")
                Ar = Ar[Ar < disc_end]
                rs = e44_specs(d, Ar)
            else:
                mm = months[months < disc_end]
                rs = e45_specs(mm, int(rand_day[rep]))
            for i, (ti, to, sd) in enumerate(rs):
                agg.add((rep, i), trades_at(d, tf, s, q24, ti, to, sd))
        print(s, flush=True)
    real = {i: (pd.concat(v, ignore_index=True) if v else pd.DataFrame()) for i, v in real.items()}
    pickle.dump(dict(names=names, real=real, luck=agg.stats()), open(f"{SCR}/{plan}_stage1.pkl", "wb"))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 100)
