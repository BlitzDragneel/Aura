"""E22 H1 and H3, ported line for line from the research code (e22_lib.py, e21_lib.day_thresholds) for a forward PAPER record.
The only live addition: trades whose fill window or 24-hour hold has not finished yet are reported as pending/open instead of
being dropped. Closed trades must equal the research engine's (tests/test_signals.py checks this on synthetic data).
Thresholds step every 24 bars from the first bar, as in research; series built here always start at 00:00 UTC, so the steps
fall at UTC midnight."""
import numpy as np
import pandas as pd

H1 = dict(name="H1 limit k2 W3", mode="limit", q=10, k=2.0, W=3, cost=0.0012)
H3 = dict(name="H3 q5 breadth>=20%", mode="taker", q=5, b=20, cost=0.002)

def day_thresholds(x, lookback=720, step=24, q=(10, 90)):
    n = len(x); lo = np.full(n, np.nan); hi = np.full(n, np.nan)
    for s in range(lookback, n, step):
        w = x[s - lookback:s]; w = w[np.isfinite(w)]
        if len(w) >= lookback // 2: a, b = np.percentile(w, q); lo[s:s + step] = a; hi[s:s + step] = b
    return lo, hi

def _roll_std(x, w, minp):
    return pd.Series(x).rolling(w, min_periods=minp).std().values

def prep(hours, c, h, l):
    """hours: consecutive hour numbers (epoch hours), NaN where a candle is missing."""
    c = np.asarray(c, float); h = np.asarray(h, float); l = np.asarray(l, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        r24 = np.full(len(c), np.nan); r24[24:] = np.log(c[24:] / c[:-24])
        r1 = np.full(len(c), np.nan); r1[1:] = np.log(c[1:] / c[:-1])
    th = {q: day_thresholds(r24, q=(q, 100 - q))[0] for q in (5, 10)}
    sig = np.full(len(c), np.nan); sig[1:] = _roll_std(r1, 168, 120)[:-1]
    return dict(c=c, h=h, l=l, r24=r24, th=th, sig=sig, idx=np.asarray(hours, np.int64))

def base(P, q):
    return np.nan_to_num(P["r24"] <= P["th"][q], nan=0).astype(bool) & np.isfinite(P["th"][q])

def breadth_of(Ps):
    cnt, tot = {}, {}
    for P in Ps:
        m10 = base(P, 10); ok = np.isfinite(P["th"][10]) & np.isfinite(P["r24"])
        for hr, a in zip(P["idx"][ok], m10[ok]):
            hr = int(hr); cnt[hr] = cnt.get(hr, 0) + int(a); tot[hr] = tot.get(hr, 0) + 1
    return {hr: cnt[hr] / tot[hr] for hr in tot if tot[hr] >= 5}

def mask(P, spec, breadth=None):
    m = base(P, spec["q"])
    if spec.get("b") is not None:
        m &= np.array([breadth.get(int(hr), 0) >= spec["b"] / 100 for hr in P["idx"]], bool)
    return m

def run(P, m, spec, lo_h, hi_h, min_age=720, live=False):
    """Returns trades as dicts. With live=False this is exactly research run(): unfinished trades are dropped."""
    c, h, l, idx = P["c"], P["h"], P["l"], P["idx"]
    fin = np.isfinite(c)
    if not fin.any(): return []
    first = int(np.argmax(fin)); out = []; nxt = -1; n = len(c)
    for t in np.where(m)[0]:
        if t < nxt or t - first < min_age or idx[t] < lo_h or idx[t] >= hi_h: continue
        if spec["mode"] == "limit":
            if not (P["sig"][t] > 0 and c[t] > 0): continue
            lim = c[t] * np.exp(-spec["k"] * P["sig"][t]); f = None
            for j in range(t + 1, min(n, t + 1 + spec["W"])):
                if l[j] < lim: f = j; break
            if f is None:
                if live and t + spec["W"] >= n:
                    out.append(dict(signal_h=int(idx[t]), status="pending", limit=float(lim)))
                nxt = t + spec["W"]; continue
            if f + 24 >= n:
                if live: out.append(dict(signal_h=int(idx[t]), status="open", entry=float(lim), fill_h=int(idx[f]), exit_due_h=int(idx[f]) + 24))
                nxt = t + spec["W"]; continue
            if not (c[f + 24] > 0): nxt = t + spec["W"]; continue
            out.append(dict(signal_h=int(idx[t]), status="closed", entry=float(lim), fill_h=int(idx[f]), exit_h=int(idx[f + 24]),
                            exit=float(c[f + 24]), net=float(c[f + 24] / lim - 1 - spec["cost"])))
            nxt = f + 24
        else:
            if t + 24 >= n:
                if live and c[t] > 0: out.append(dict(signal_h=int(idx[t]), status="open", entry=float(c[t]), exit_due_h=int(idx[t]) + 24))
                continue
            if not (c[t] > 0 and c[t + 24] > 0): continue
            out.append(dict(signal_h=int(idx[t]), status="closed", entry=float(c[t]), exit_h=int(idx[t + 24]), exit=float(c[t + 24]),
                            net=float(c[t + 24] / c[t] - 1 - spec["cost"])))
            nxt = t + 24
    return out

def dense(rows, first_h=None, last_h=None):
    """k1h rows (t ms, h, l, c) -> consecutive-hour arrays starting at 00:00 UTC, NaN for missing candles."""
    if not rows: return None
    hrs = np.array([r["t"] // 3_600_000 for r in rows], np.int64)
    a = int(first_h if first_h is not None else hrs.min()); a -= a % 24
    b = int(last_h if last_h is not None else hrs.max())
    n = b - a + 1; c = np.full(n, np.nan); h = np.full(n, np.nan); l = np.full(n, np.nan)
    for r, hr in zip(rows, hrs):
        if a <= hr <= b: i = hr - a; c[i], h[i], l[i] = r["c"], r["h"], r["l"]
    return np.arange(a, b + 1, dtype=np.int64), c, h, l

def forward_record(series, forward_start_h, now_h):
    """series: {sym: (hours, c, h, l)}. Replays H1 and H3 from forward_start (stateless, so a restart can't corrupt it)."""
    Ps = {s: prep(*v) for s, v in series.items()}
    br = breadth_of(Ps.values())
    out = []
    for spec in (H1, H3):
        for s, P in Ps.items():
            for tr in run(P, mask(P, spec, br), spec, forward_start_h, now_h + 1, live=True):
                tr.update(sym=s, rule=spec["name"]); out.append(tr)
    return sorted(out, key=lambda x: (x["signal_h"], x["sym"])), br

def summary(trades):
    closed = [t["net"] for t in trades if t["status"] == "closed"]
    res = {}
    for rule in sorted({t["rule"] for t in trades}):
        r = [t["net"] for t in trades if t["rule"] == rule and t["status"] == "closed"]
        res[rule] = dict(closed=len(r), open=sum(1 for t in trades if t["rule"] == rule and t["status"] != "closed"),
                         mean=float(np.mean(r)) if r else None, winners=float(np.mean(np.array(r) > 0)) if r else None)
    return res
