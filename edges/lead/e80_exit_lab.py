"""E80 exit lab (plan edges/plans/E80_exit_lab.md, md5 692056019fe930932c937abeefafe28f).

Entries come from edges/bots/backtest.run (the parity-checked rule code). For every filled entry the next 72 hourly bars
are stored relative to the entry price; a numba kernel applies each exit variant to all trades at once.
Simplification (stated): the trade set is the one the original exit produced (one position per coin at a time); a
different hold would change which overlapping signals are taken only marginally.
Usage: python3 -m edges.lead.e80_exit_lab build|discover|luck|judge
"""
import itertools
import json
import os
import sys
import time

import numba
import numpy as np
import pandas as pd

from edges.lib import bt
from edges.bots import backtest as B

OUT = "/home/user/data/e80"
HMAX = 72
HOLDS = (6, 12, 24, 48, 72)
TPS = (0.0, 0.02, 0.04, 0.08)
SLS = (0.0, 0.05, 0.10, 0.20)
TRS = ((0.0, 0.0), (0.03, 0.03), (0.06, 0.04))
GRID = list(itertools.product(HOLDS, TPS, SLS, TRS))
PLAN = "692056019fe930932c937abeefafe28f"


def paths_for(trades, limit_entry):
    """Arrays [n, HMAX] of o/h/l/c relative to entry (bar 0 = the entry bar) and cumulative funding."""
    n = len(trades)
    O = np.full((n, HMAX), np.nan, np.float32); Hh = O.copy(); Ll = O.copy(); C = O.copy(); F = np.zeros((n, HMAX), np.float32)
    for sym, g in trades.groupby("sym"):
        d = B.load_coin(sym, "1h")[0]
        idx = d.index
        o, h, l, c = (d[k].values for k in ("o", "h", "l", "c"))
        try:
            fs = bt.funding(sym)
        except (FileNotFoundError, OSError):
            fs = None
        pos = idx.get_indexer(pd.DatetimeIndex(g.entry_time))
        for row, p, e in zip(g.index, pos, g.entry.values):
            if p < 0:
                continue
            q = min(len(c), p + HMAX)
            k = q - p
            O[row, :k] = o[p:q] / e; Hh[row, :k] = h[p:q] / e; Ll[row, :k] = l[p:q] / e; C[row, :k] = c[p:q] / e
            if fs is not None and len(fs):
                ends = idx[p:q] + pd.Timedelta(hours=1)
                cum = fs.cumsum()
                base = cum[cum.index <= idx[p]]
                b0 = base.iloc[-1] if len(base) else 0.0
                vals = cum.reindex(ends, method="ffill").fillna(b0).values - b0
                F[row, :k] = vals
    if limit_entry:  # the limit filled inside bar 0: only the part of bar 0 after the fill is unknown -> use the close
        Hh[:, 0] = np.minimum(Hh[:, 0], np.maximum(1.0, C[:, 0]))  # no TP inside the fill bar (conservative)
    return O, Hh, Ll, C, F


@numba.njit(cache=True)
def apply_exit(O, H, L, C, F, slip, entry_cost, hold, tp, sl, arm, trail, maker, taker):
    n = O.shape[0]
    net = np.full(n, np.nan)
    mae = np.zeros(n)
    for i in range(n):
        peak = 1.0
        armed = False
        worst = 0.0
        ex = np.nan
        kind = 0  # 0 time/trail taker, 1 tp maker
        last = -1
        pending_trail = False
        for k in range(hold):
            if np.isnan(C[i, k]):
                continue
            last = k
            if pending_trail:            # trailing stop decided on the previous close: exit at this open
                ex = O[i, k]; kind = 0
                break
            lo = L[i, k]
            if lo - 1.0 < worst:
                worst = lo - 1.0
            if sl > 0.0 and lo <= 1.0 - sl:
                ex = O[i, k] if (k > 0 and O[i, k] < 1.0 - sl) else 1.0 - sl
                kind = 0
                break
            if tp > 0.0 and H[i, k] >= 1.0 + tp:
                ex = 1.0 + tp; kind = 1
                break
            if C[i, k] > peak:
                peak = C[i, k]
            if arm > 0.0:
                if peak >= 1.0 + arm:
                    armed = True
                if armed and C[i, k] <= peak * (1.0 - trail):
                    pending_trail = True
        if np.isnan(ex):
            if last < 0:
                continue
            ex = C[i, last]; kind = 0
        k_end = last if last >= 0 else 0
        exit_cost = maker if kind == 1 else taker + slip[i]
        net[i] = (ex - 1.0) - entry_cost[i] - exit_cost - F[i, k_end]
        mae[i] = worst
    return net, mae


def load(rule):
    z = np.load(f"{OUT}/{rule}.npz", allow_pickle=True)
    meta = pd.read_parquet(f"{OUT}/{rule}_trades.parquet")
    return z, meta


def build():
    os.makedirs(OUT, exist_ok=True)
    for rule, lim in (("climax_a", False), ("panic_h1", True)):
        t0 = time.time()
        tr, info = B.run(rule, start="2020-01-01")
        tr = tr[tr.status == "filled"].reset_index(drop=True)
        O, Hh, Ll, C, F = paths_for(tr, lim)
        slip = bt.slippage(tr.qv24.values).astype(np.float64)
        ecost = (np.full(len(tr), bt.MAKER) if lim else bt.TAKER + slip).astype(np.float64)
        np.savez(f"{OUT}/{rule}.npz", O=O, H=Hh, L=Ll, C=C, F=F, slip=slip, ecost=ecost)
        tr[["sym", "entry_time", "entry", "qv24", "net"]].to_parquet(f"{OUT}/{rule}_trades.parquet")
        print(rule, len(tr), f"{time.time() - t0:.0f}s", flush=True)
    random_build()


def random_build(reps=30, seed=7):
    """Random-entry trades for the luck check: same coins and count as climax/H1 discovery, random hours, market entry."""
    rng = np.random.default_rng(seed)
    for rule in ("climax_a", "panic_h1"):
        _, meta = load(rule)
        disc = meta[meta.entry_time < "2024-01-01"]
        n = min(len(disc), 8000)
        for r in range(reps):
            samp = disc.sample(n, random_state=int(rng.integers(1e9)))
            rows = []
            for sym, g in samp.groupby("sym"):
                d = B.load_coin(sym, "1h")[0]
                d = d[(d.index < "2024-01-01") & (d.o > 0)]
                if len(d) < 200:
                    continue
                pick = rng.integers(0, len(d) - HMAX - 1, size=len(g))
                for p in pick:
                    rows.append(dict(sym=sym, entry_time=d.index[p], entry=float(d.o.values[p]), qv24=float(g.qv24.iloc[0])))
            rt = pd.DataFrame(rows)
            O, Hh, Ll, C, F = paths_for(rt, False)
            slip = bt.slippage(rt.qv24.values).astype(np.float64)
            np.savez(f"{OUT}/rand_{rule}_{r}.npz", O=O, H=Hh, L=Ll, C=C, F=F, slip=slip, ecost=bt.TAKER + slip,
                     t=rt.entry_time.values.astype("datetime64[ns]").astype(np.int64))
            print("random", rule, r, len(rt), flush=True)


def evaluate(z, times, mask, v):
    hold, tp, sl, (arm, trail) = v
    net, mae = apply_exit(z["O"][mask], z["H"][mask], z["L"][mask], z["C"][mask], z["F"][mask], z["slip"][mask],
                          z["ecost"][mask], hold, tp, sl, arm, trail, bt.MAKER, bt.TAKER)
    df = pd.DataFrame(dict(time=pd.to_datetime(times[mask]).tz_localize("UTC") if getattr(pd.to_datetime(times[mask]), "tz", None) is None else pd.to_datetime(times[mask]),
                           net=net, mae=mae, sym="x")).dropna(subset=["net"])
    return df


def best_of_grid(z, times, mask, log=None, rule=""):
    rows = []
    for v in GRID:
        df = evaluate(z, times, mask, v)
        s = bt.summarize(df)
        rows.append((v, s))
        if log:
            bt.log_attempt(PLAN, f"E80 {rule} H{v[0]} TP{v[1]} SL{v[2]} TR{v[3]}", "discovery", s)
    ok = [(v, s) for v, s in rows if s.get("n", 0) >= 300 and s.get("t_week") == s.get("t_week")]
    return max(ok, key=lambda x: x[1]["t_week"]) if ok else (None, None), rows


def discover():
    res = {}
    for rule in ("climax_a", "panic_h1"):
        z, meta = load(rule)
        times = meta.entry_time.values
        mask = (meta.entry_time < "2024-01-01").values
        (v, s), rows = best_of_grid(z, times, mask, log=True, rule=rule)
        orig = (12, 0.0, 0.0, (0.0, 0.0)) if rule == "climax_a" else (24, 0.0, 0.0, (0.0, 0.0))
        so = dict(rows)[orig] if orig in dict(rows) else None
        top = sorted(rows, key=lambda x: -(x[1].get("t_week") or -99))[:8]
        res[rule] = dict(best=dict(variant=v, stats=s), original=dict(variant=orig, stats=so),
                         top8=[dict(variant=a, t=b.get("t_week"), mean_bp=b.get("mean_bp"), n=b.get("n")) for a, b in top])
        print(rule, "BEST", v, s["mean_bp"], s["t_week"], s["n"], "| ORIGINAL", so["mean_bp"], so["t_week"], flush=True)
    json.dump(res, open(f"{OUT}/discovery.json", "w"), default=str, indent=1)


def luck():
    res = {}
    for rule in ("climax_a", "panic_h1"):
        bests = []
        r = 0
        while os.path.exists(f"{OUT}/rand_{rule}_{r}.npz"):
            z = np.load(f"{OUT}/rand_{rule}_{r}.npz")
            times = pd.to_datetime(z["t"], utc=True).values
            (v, s), _ = best_of_grid(z, times, np.ones(len(times), bool))
            bests.append(s["t_week"] if s else np.nan)
            r += 1
        res[rule] = dict(random_best_t=bests, p95=float(np.nanpercentile(bests, 95)))
        print(rule, "random best t p95", res[rule]["p95"], flush=True)
    json.dump(res, open(f"{OUT}/luck.json", "w"), indent=1)


def judge(period):
    disc = json.load(open(f"{OUT}/discovery.json"))
    out = {}
    for rule in ("climax_a", "panic_h1"):
        z, meta = load(rule)
        a, b = bt.PERIODS[period]
        mask = ((meta.entry_time >= a) & (meta.entry_time < b)).values
        best = disc[rule]["best"]["variant"]; orig = disc[rule]["original"]["variant"]
        best = (best[0], best[1], best[2], tuple(best[3]))
        orig = (orig[0], orig[1], orig[2], tuple(orig[3]))
        sb = bt.summarize(evaluate(z, meta.entry_time.values, mask, best))
        so = bt.summarize(evaluate(z, meta.entry_time.values, mask, orig))
        bt.log_attempt(PLAN, f"E80 {rule} chosen {best}", period, sb)
        out[rule] = dict(chosen=dict(variant=best, stats=sb), original=dict(variant=orig, stats=so))
        print(period, rule, "chosen", best, sb["mean_bp"], sb["t_week"], sb["n"], "| original", so["mean_bp"], so["t_week"], flush=True)
    json.dump(out, open(f"{OUT}/{period}.json", "w"), default=str, indent=1)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "build":
        build()
    elif cmd == "random":
        random_build()
    elif cmd == "discover":
        discover()
    elif cmd == "luck":
        luck()
    else:
        judge(cmd)
