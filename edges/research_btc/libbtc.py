"""BTC research bot engine (E86-E99). Conventions: edges/plans/E86_common_btc.md."""
import os, sys, json
import numpy as np, pandas as pd
from numba import njit

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from edges.lib import bt  # noqa
from edges.research1 import lib1  # noqa

SCR = "/tmp/claude-0/-home-user-Aura/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/btc"
os.makedirs(SCR, exist_ok=True)
SYM = "BTCUSDT"
TAKER_SIDE = 0.0005 + 0.0002      # fee + slippage per side
MAKER_SIDE = 0.0002
P5 = {"discovery": ("2022-01-01", "2024-01-01"), "validation": ("2024-01-01", "2025-01-01"),
      "final": ("2025-01-01", "2100-01-01")}
P1 = {"discovery": ("2020-01-01", "2024-01-01"), "validation": ("2024-01-01", "2025-01-01"),
      "final": ("2025-01-01", "2100-01-01")}


def bars(tf):
    if tf in ("5m", "15m", "1h", "4h"):
        d = lib1.load_tf(SYM, tf)
    elif tf == "1d":
        h = lib1.load_tf(SYM, "1h")
        g = h.resample("1D", label="left", closed="left")
        d = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "v": g.v.sum(),
                          "qv": g.qv.sum()})
        d.loc[g.c.count() < 20, ["o", "h", "l", "c"]] = np.nan
    return d


def atr(d, n=14):
    pc = d.c.shift(1)
    tr = np.maximum(d.h - d.l, np.maximum((d.h - pc).abs(), (d.l - pc).abs()))
    return tr.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


# ------------------------------------------------------------------ funding
_F = None


def funding_between(t0, t1, side):
    """Funding cost (fraction of notional) for settlements in (t0, t1]; side +1 long pays rate, -1 short receives.
    Stamps after the funding file ends: 0.0001 charged to longs, 0 to shorts."""
    global _F
    if _F is None:
        f = bt.funding(SYM)
        ts = pd.DatetimeIndex(f.index).as_unit("ns").asi8
        ts = (np.round(ts / 6e10) * 6e10).astype(np.int64)
        _F = (ts, np.concatenate([[0.0], np.cumsum(f.values)]), ts[-1])
    ts, cum, last = _F
    t0 = np.asarray(pd.DatetimeIndex(t0).as_unit("ns").asi8)
    t1 = np.asarray(pd.DatetimeIndex(t1).as_unit("ns").asi8)
    side = np.asarray(side, dtype=float)
    a = np.searchsorted(ts, t0, side="right")
    b = np.searchsorted(ts, t1, side="right")
    s = cum[b] - cum[a]
    # synthetic stamps after the file ends
    eight = 8 * 3600 * 10 ** 9
    lo = np.maximum(t0, last)
    nx = np.where(t1 > last, np.floor((t1 - last) / eight) - np.floor((lo - last) / eight), 0)
    nx = np.maximum(nx, 0)
    syn = np.where(side > 0, nx * 0.0001, 0.0)
    return side * s + syn


# ------------------------------------------------------------------ bracket engine
@njit(cache=True)
def _bracket(o, h, l, c, sig, side, atrv, delay, stop_k, tgt_k, hold, overlap):
    n = len(o)
    m = len(sig)
    ei = np.full(m, -1); xi = np.full(m, -1)
    ep = np.full(m, np.nan); xp = np.full(m, np.nan); mae = np.full(m, np.nan)
    busy = -1
    for k in range(m):
        i = sig[k]
        e = i + delay
        if e >= n or (not overlap and e <= busy):
            continue
        a = atrv[i]
        if not (a > 0) or not (o[e] > 0):
            continue
        s = side[k]
        p0 = o[e]
        st = p0 - s * stop_k * a
        tg = p0 + s * tgt_k * a
        worst = 0.0
        x = -1; px = np.nan
        last = min(n - 1, e + hold - 1)
        bad = False
        for j in range(e, last + 1):
            if not (h[j] > 0):
                bad = True
                break
            if j > e:
                # adverse gap through stop at the open
                if (s > 0 and o[j] <= st) or (s < 0 and o[j] >= st):
                    x = j; px = o[j]
                    adv = s * (o[j] / p0 - 1)
                    worst = min(worst, adv)
                    break
            adv = (l[j] / p0 - 1) if s > 0 else -(h[j] / p0 - 1)
            hit_st = (l[j] <= st) if s > 0 else (h[j] >= st)
            hit_tg = (h[j] >= tg) if s > 0 else (l[j] <= tg)
            if hit_st:
                worst = min(worst, s * (st / p0 - 1))
                x = j; px = st
                break
            worst = min(worst, adv)
            if hit_tg:
                x = j; px = tg
                break
        if bad:
            continue
        if x < 0:
            if last - e + 1 < hold:
                continue  # data ends
            x = last; px = c[last]
        ei[k] = e; xi[k] = x; ep[k] = p0; xp[k] = px; mae[k] = worst
        busy = x
    return ei, xi, ep, xp, mae


def bracket(d, sig_idx, side, delay=2, stop_k=2.0, tgt_k=6.0, hold=16, overlap=False, a=None,
            entry_cost=TAKER_SIDE, exit_cost=TAKER_SIDE):
    if a is None:
        a = atr(d).values
    sig_idx = np.asarray(sig_idx, dtype=np.int64)
    side = np.asarray(side, dtype=np.int64)
    o, h, l, c = (d[k].values.astype(float) for k in "ohlc")
    ei, xi, ep, xp, mae = _bracket(o, h, l, c, sig_idx, side, a, delay, stop_k, tgt_k, hold, overlap)
    ok = ei >= 0
    idx = d.index
    barlen = idx[1] - idx[0]
    tr = pd.DataFrame({"time": idx[ei[ok]], "exit_time": idx[xi[ok]] + barlen, "side": side[ok],
                       "entry": ep[ok], "exit": xp[ok], "mae": mae[ok], "sig": sig_idx[ok],
                       "stopdist": stop_k * a[sig_idx[ok]] / ep[ok]})
    tr["sym"] = SYM
    tr["gross"] = tr.side * (tr.exit / tr.entry - 1)
    tr["fund"] = funding_between(tr.time, tr.exit_time, tr.side)
    tr["net"] = tr.gross - entry_cost - exit_cost - tr.fund
    return tr


def handoff_account(tr, per_side=0.0006, risk=25.0, acct=10000.0):
    """Handoff metric: risk 25 per trade on 10k (size = risk/stopdist, <= 1x notional), cost per side, funding."""
    notional = np.minimum(risk / tr.stopdist.values, acct)
    pnl = notional * (tr.gross.values - 2 * per_side - tr.fund.values)
    return 100 * pnl.sum() / acct


def per(tr, P):
    return {k: tr[(tr.time >= a) & (tr.time < b)] for k, (a, b) in P.items()}


def summ(tr):
    s = bt.summarize(tr)
    s.pop("label", None)
    return s


# ------------------------------------------------------------------ daily stats
def nw_t(x, lags=10):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    n = len(x)
    if n < 20:
        return np.nan
    mu = x.mean(); e = x - mu
    v = (e @ e) / n
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        v += 2 * w * (e[L:] @ e[:-L]) / n
    return float(mu / np.sqrt(v / n)) if v > 0 else np.nan


def curve_stats(r, ann=365):
    r = pd.Series(r).dropna()
    if len(r) < 2:
        return {}
    eq = (1 + r).cumprod()
    dd = float((eq / eq.cummax() - 1).min())
    yrs = len(r) / ann
    cagr = float(eq.iloc[-1] ** (1 / yrs) - 1) if yrs > 0 else np.nan
    sh = float(r.mean() / r.std() * np.sqrt(ann)) if r.std() > 0 else np.nan
    return dict(sharpe=round(sh, 3), cagr=round(cagr, 4), maxdd=round(dd, 4), nw_t=round(nw_t(r), 2), days=len(r))


# ------------------------------------------------------------------ selection / judgement
def fast_t(tr):
    return bt.tstat_weekly(tr) if len(tr) >= 3 else np.nan


def disc_ok(s, nmin, years_need):
    return s.get("n", 0) >= nmin and s.get("mean_bp", -1) > 0 and s.get("years_pos", 0) >= years_need


def judge(md5, plan, trades, null_best, P, nmin=100, years_need=2, final_info=False):
    """trades: {name: DataFrame over all periods}. null_best: array of best discovery t per null run.
    Logs every variant's discovery stats; picks best t; validation; final if validation passes."""
    rows = {}
    best = None
    for nm, tr in trades.items():
        dsc = per(tr, P)["discovery"]
        s = summ(dsc)
        bt.log_attempt(md5, nm, "discovery", s)
        rows[nm] = s
        if disc_ok(s, nmin, years_need) and (best is None or s["t_week"] > rows[best]["t_week"]):
            best = nm
    out = dict(plan=plan, md5=md5, discovery=rows, chosen=best)
    nb = np.asarray([x for x in null_best if x == x])
    out["null_p95"] = float(np.percentile(nb, 95)) if len(nb) else None
    if best is None:
        out["verdict"] = "FAIL (no discovery variant met the bar)"
        return out
    out["real_best_t"] = rows[best]["t_week"]
    out["luck_pass"] = bool(out["null_p95"] is not None and rows[best]["t_week"] >= out["null_p95"])
    pp = per(trades[best], P)
    sv = summ(pp["validation"]); bt.log_attempt(md5, best, "validation", sv); out["validation"] = sv
    vpass = sv.get("n", 0) > 0 and sv["mean_bp"] > 0 and sv["t_week"] >= 1.5
    out["validation_pass"] = bool(vpass)
    if vpass or final_info:
        sf = summ(pp["final"]); bt.log_attempt(md5, best, "final" if vpass else "final_info", sf)
        out["final" if vpass else "final_info_only"] = sf
    if not out["luck_pass"]:
        out["verdict"] = "FAIL (luck check)"
    elif not vpass:
        out["verdict"] = "FAIL (validation)"
    else:
        sf = out["final"]
        allyrs = summ(trades[best])
        ok = (sf["mean_bp"] > 0 and sf["t_week"] >= 2 and (sf["n"] >= 100 or (sf["n"] >= 50 and sf["t_week"] >= 3))
              and allyrs["years_pos"] >= 0.6 * allyrs["years_total"])
        out["all_years"] = allyrs
        out["verdict"] = "PASS" if ok else "FAIL (final)"
    return out
