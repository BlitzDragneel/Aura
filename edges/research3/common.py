"""Shared engine for bot-3 plans (E63–E69). Conventions: edges/plans/E63_common_bot3.md."""
import json, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from edges.lib import bt  # noqa: E402

DATA = bt.DATA
ROOT = bt.ROOT
MD5 = json.load(open(os.path.join(ROOT, "research3", "plan_md5.json")))
DEFAULT_FUND = 0.0001


def perp(sym):
    """1h perp frame + qv24 + hourly funding array aligned to the index (rate at the hour it settles)."""
    df = bt.load(sym, "1h")
    df = df[~df.index.duplicated()]
    full = pd.date_range(df.index[0], df.index[-1], freq="h", tz="UTC")
    df = df.reindex(full)
    df["qv24"] = df.qv.fillna(0).rolling(24, min_periods=1).sum().shift(1)
    F = pd.Series(0.0, index=df.index)
    try:
        f = bt.funding(sym)
        f.index = f.index.floor("h")
        f = f[~f.index.duplicated()]
        f = f[(f.index >= df.index[0]) & (f.index <= df.index[-1])]
        F.loc[f.index] = f.values
        first, last = (f.index.min(), f.index.max()) if len(f) else (df.index[-1], df.index[0])
    except FileNotFoundError:
        first, last = df.index[-1], df.index[0]
    hrs = df.index.hour
    miss = ((df.index < first) | (df.index > last)) & np.isin(hrs, [0, 8, 16])
    df["rtc"] = bt.round_trip_cost(df.qv24.fillna(0).clip(lower=0).values)
    df["fund"] = F.values
    df["fund_missing"] = miss
    return df


def simulate(df, sym, entry_mask, side, H, entry="taker", exit="taker"):
    """entry_mask: bool array (len df) = enter at OPEN of this bar. side: scalar or array (+1/-1). H hours.
    One position at a time. Returns DataFrame time, exit_time, sym, net, gross, mae, side."""
    o, h, l = df.o.values, df.h.values, df.l.values
    qv24, F, Fm = df.qv24.values, df.fund.values, df.fund_missing.values
    rtc = df.rtc.values
    idx = df.index
    n = len(o)
    side_arr = np.broadcast_to(np.asarray(side), (n,)) if np.ndim(side) == 0 else np.asarray(side)
    out = []
    nxt = -1
    for i in np.flatnonzero(entry_mask):
        if i < nxt or i + H >= n:
            continue
        e, x = o[i], o[i + H]
        if not (e > 0 and x > 0):
            continue
        s = side_arr[i]
        if s == 0:
            continue
        hh, ll = h[i:i + H], l[i:i + H]
        if s > 0:
            mae = np.nanmin(ll) / e - 1
        else:
            mae = -(np.nanmax(hh) / e - 1)
        gross = s * (x / e - 1)
        cost = rtc[i] if (entry == "taker" and exit == "taker") else float(bt.round_trip_cost(max(qv24[i], 0), entry, exit))
        fund = 0.0
        if H > 8:
            fund = s * F[i:i + H].sum()
            if s > 0:
                fund += DEFAULT_FUND * Fm[i:i + H].sum()
        out.append((idx[i], idx[i + H], sym, gross - cost - fund, gross, mae, s))
        nxt = i + H
    return pd.DataFrame(out, columns=["time", "exit_time", "sym", "net", "gross", "mae", "side"])


def period(tr, p, start=None):
    a, b = bt.PERIODS[p]
    if start is not None and p == "discovery":
        a = max(pd.Timestamp(a, tz="UTC"), pd.Timestamp(start, tz="UTC"))
    if len(tr) == 0:
        return tr
    a, b = pd.Timestamp(a), pd.Timestamp(b)
    a = a if a.tzinfo else a.tz_localize("UTC")
    b = b if b.tzinfo else b.tz_localize("UTC")
    return tr[(tr.time >= a) & (tr.time < b)]


def tstat(tr):
    if len(tr) < 3:
        return np.nan
    return bt.tstat_weekly(tr)


def circ_shift(series, k):
    """Circularly shift the VALUES of a time-indexed series by k positions (index fixed)."""
    v = series.values
    return pd.Series(np.roll(v, k), index=series.index)


def luck_pct(real_best, null):
    null = np.asarray([x for x in null if x == x])
    return float((null < real_best).mean()) if len(null) else np.nan


def write_result(plan, obj):
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    with open(os.path.join(ROOT, "results", f"{plan}_result.json"), "w") as f:
        json.dump(obj, f, indent=1, default=str)
