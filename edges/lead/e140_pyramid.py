"""E140 gold pyramiding (plan edges/plans/E140_gold_pyramiding.md, md5 791d7764...).
Usage: python3 -m edges.lead.e140_pyramid <XAU_perp_1m.parquet> <PAXG_1m.parquet>"""
import json
import sys

import numpy as np
import pandas as pd

from edges.lib import bt

PLAN = "791d7764069a5bb27bed1f17b6d7d47f"
PER = {"XAU": {"discovery": ("2025-12-01", "2026-06-01"), "validation": ("2026-06-01", "2026-09-01"),
               "final": ("2026-09-01", "2026-11-14")},
       "PAXG": {"discovery": ("2021-01-01", "2024-01-01"), "validation": ("2024-01-01", "2025-01-01"),
                "final": ("2025-01-01", "2025-12-01")}}
VARIANTS = [("SINGLE", 0, 0), ("PYR k0.5 N3", 0.5, 3), ("PYR k0.5 N6", 0.5, 6), ("PYR k1 N3", 1.0, 3), ("PYR k1 N6", 1.0, 6)]
HOLD = 240


def prep(path):
    m = pd.read_parquet(path)[["o", "h", "l", "c"]].astype(float)
    f = m.resample("5min").agg(dict(o="first", h="max", l="min", c="last")).dropna()
    tr = pd.concat([f.h - f.l, (f.h - f.c.shift()).abs(), (f.l - f.c.shift()).abs()], axis=1).max(axis=1)
    f["atr"] = tr.rolling(14).mean()
    f["hh"] = f.h.rolling(12).max().shift(1)
    f["ll"] = f.l.rolling(12).min().shift(1)
    f["sig"] = np.where(f.c > f.hh, 1, np.where(f.c < f.ll, -1, 0))
    return m, f


def walk(O, H, L, i0, d, S, k, N, cost_unit):
    """1-minute walk from index i0 (fill at O[i0]); returns pnl (price units, all units), units_max, worst open pnl, exit idx."""
    if d == 1:
        o, h, l = O, H, L
    else:
        o, h, l = -O, -L, -H
    px = o[i0]
    entries = [px]
    best, stop, nxt = px, px - S, px + k * S if N else np.inf
    worst = 0.0
    end = min(len(o) - 1, i0 + HOLD)
    for j in range(i0, end + 1):
        if j > i0 and o[j] <= stop:            # gap through the stop
            ex = o[j]
            break
        if l[j] <= stop:
            ex = stop
            break
        if j == end:
            ex = o[j]
            break
        while len(entries) <= N and h[j] >= nxt:
            entries.append(nxt)
            nxt += k * S
        worst = min(worst, sum(l[j] - e for e in entries))
        best = max(best, h[j])
        stop = max(stop, best - S)
    pnl = sum(ex - e for e in entries) - cost_unit(px) * len(entries)
    return pnl, len(entries), min(worst, sum(ex - e for e in entries)), j


def run(m, f, k, N, cost_unit, entries):
    """entries: iterable of (5m bar time, direction). One trade open at a time."""
    idx = m.index
    O, H, L = m.o.values, m.h.values, m.l.values
    out, busy_until = [], idx[0]
    for t, d in entries:
        fill_t = t + pd.Timedelta(minutes=5)
        if fill_t < busy_until:
            continue
        i0 = idx.searchsorted(fill_t)
        if i0 >= len(idx) - 2 or (idx[i0] - fill_t) > pd.Timedelta(minutes=10):
            continue
        S = f.atr.at[t]
        if not S > 0:
            continue
        pnl, u, worst, j = walk(O, H, L, i0, d, S, k, N, cost_unit)
        out.append(dict(time=idx[i0], d=d, S=S, pnl=pnl, units=u, worst=worst, R=pnl / S, Rpeak=pnl / (u * S)))
        busy_until = idx[j]
    return pd.DataFrame(out)


def stats(t):
    if len(t) < 3:
        return dict(n=int(len(t)))
    x = t.assign(net=t.R)
    return dict(n=int(len(t)), mean_R=round(float(t.R.mean()), 3), t_week=round(bt.tstat_weekly(x), 2),
                win=round(float((t.R > 0).mean()), 3), mean_Rpeak=round(float(t.Rpeak.mean()), 3),
                avg_units=round(float(t.units.mean()), 2), best_R=round(float(t.R.max()), 1),
                worst_R=round(float(t.R.min()), 1))


def account(t, balance=560.0, oz_per_unit=10.0):
    """The trader's sizing: 0.1 lot (10 oz) per unit, starting balance $560, trades in order."""
    b = balance
    for _, r in t.sort_values("time").iterrows():
        if b + r.worst * oz_per_unit <= 0:
            return dict(end=0.0, wiped=str(r.time.date()))
        b += r.pnl * oz_per_unit
    return dict(end=round(b, 2), wiped=None)


def main(xau_path, paxg_path):
    res = dict(plan="edges/plans/E140_gold_pyramiding.md", md5=PLAN, assets={})
    rng = np.random.default_rng(140)
    for asset, path, cost in (("XAU", xau_path, lambda p: 0.20), ("PAXG", paxg_path, lambda p: 0.001 * p)):
        m, f = prep(path)
        mom = [(t, int(s)) for t, s in f.sig[f.sig != 0].items()]
        # random control: same count per month, random 5m bars and directions
        months = pd.Series([t for t, _ in mom]).dt.to_period("M").value_counts()
        rnd = []
        for per, n in months.items():
            pool = f.index[(f.index.to_period("M") == per) & f.atr.notna().values]
            if len(pool):
                rnd += [(t, int(rng.choice([-1, 1]))) for t in rng.choice(pool, size=min(n, len(pool)), replace=False)]
        rnd.sort()
        A = {}
        for fam, ents in (("M", mom), ("R", rnd)):
            for name, k, N in VARIANTS:
                tr = run(m, f, k, N, cost, ents)
                tr_s = tr.assign(pnl=tr.pnl - tr.units * cost(1) * (0 if asset == "PAXG" else 1),
                                 R=(tr.pnl - tr.units * (0.20 if asset == "XAU" else 0)) / tr.S) if asset == "XAU" else None
                key = f"{fam} {name}"
                A[key] = {}
                for p, (a, b) in PER[asset].items():
                    seg = tr[(tr.time >= a) & (tr.time < b)]
                    st = stats(seg)
                    if tr_s is not None:
                        st["stress_mean_R"] = round(float(tr_s[(tr_s.time >= a) & (tr_s.time < b)].R.mean()), 3)
                    if asset == "XAU" and fam == "M":
                        st["account_560"] = account(seg)
                    A[key][p] = st
                    bt.log_attempt(PLAN, f"E140 {asset} {key}", p, dict(n=st.get("n"), mean_bp=None, t_week=st.get("t_week")))
                print(asset, key, {p: (v.get("n"), v.get("mean_R"), v.get("t_week"), v.get("account_560")) for p, v in A[key].items()}, flush=True)
        res["assets"][asset] = A
    ok = []
    for asset in ("XAU", "PAXG"):
        A = res["assets"][asset]
        best = [n for n, _, N in VARIANTS if N and
                all(A[f"M {n}"][p].get("mean_R", -9) > A["M SINGLE"][p].get("mean_R", -9) and
                    A[f"M {n}"][p].get("mean_R", -9) > A[f"R {n}"][p].get("mean_R", -9) for p in ("validation", "final"))
                and A[f"M {n}"]["final"].get("mean_R", -9) > 0 and (A[f"M {n}"]["final"].get("t_week") or 0) >= 2
                and A[f"M {n}"]["validation"].get("mean_R", -9) > 0 and (A[f"M {n}"]["validation"].get("t_week") or 0) >= 1.5]
        ok.append(f"{asset}: {'PASS ' + ', '.join(best) if best else 'FAIL'}")
    res["verdict"] = "; ".join(ok)
    json.dump(res, open("edges/results/E140_result.json", "w"), indent=1, default=str)
    print(res["verdict"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
