"""E147 Profit4Life template on random entries + fib pullback (plan md5 bf144f09...)."""
import json, sys, warnings
import numpy as np, pandas as pd
from edges.lib import bt

warnings.filterwarnings("ignore")
PLAN = "bf144f09d478c8201421d300ab1d904f"
PER = {"train": ("2025-12-11", "2026-06-01"), "val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-11-14")}
SL, STEP, NT, SPREAD, MAXB = 10.0, 5.0, 5, 0.20, 1440


def outcome(H, L, C, j, d, px):
    """Walk 1m bars from j. Returns (#targets reached before the stop, exit-by-time close, be_hit after TP1)."""
    hit, be = 0, False
    end = min(len(H) - 1, j + MAXB)
    for q in range(j, end + 1):
        hi, lo = (H[q], L[q]) if d == 1 else (2 * px - L[q], 2 * px - H[q])   # mirror shorts
        stop = px if hit >= 1 else px - SL
        if lo <= stop and not (hit == 0 and q == j and False):
            if hit >= 1:
                be = True
            return hit, None, be, (hit == 0)
        while hit < NT and hi >= px + STEP * (hit + 1):
            hit += 1
        if hit == NT:
            return hit, None, False, False
    last = C[end] if d == 1 else 2 * px - C[end]
    return hit, last - px, False, False


def account(hit, tail, be, stopped):
    """USD per ounce for one signal under three ways of trading it (after spread)."""
    tp1 = (STEP if hit >= 1 else (-SL if stopped else tail)) - SPREAD
    # fifths: each reached target banks STEP*k on one fifth; the rest exits at entry (BE), at -SL (never reached TP1) or at time
    rest = NT - hit
    rest_px = 0.0 if be else (-SL if stopped else (tail if tail is not None else 0.0))
    fifths = (sum(STEP * k for k in range(1, hit + 1)) + rest * rest_px) / NT - SPREAD
    tp5 = (STEP * NT if hit == NT else (-SL if stopped else (tail if tail is not None else -SL))) - SPREAD
    # hold-for-TP5 keeps the original stop: approximated by: if TP5 not reached and price came back to entry after TP1, it is still open ->
    recap = hit * STEP * 10 if hit >= 1 else (-100 if stopped else 0)
    return tp1, fifths, tp5, recap


def run(m, entries):
    H, L, C, idx = m.h.values, m.l.values, m.c.values, m.index
    rows = []
    for j, d, px in entries:
        hit, tail, be, stopped = outcome(H, L, C, j, d, px)
        rows.append((idx[j], hit, *account(hit, tail, be, stopped)))
    return pd.DataFrame(rows, columns=["time", "hit", "tp1", "fifths", "tp5", "recap"])


def summ(t, a, b):
    s = t[(t.time >= a) & (t.time < b)]
    if len(s) < 10:
        return dict(n=int(len(s)))
    o = dict(n=int(len(s)), tp1_first=round(float((s.hit >= 1).mean()), 3), tp5_reached=round(float((s.hit == 5).mean()), 3),
             recap_pips_per_trade=round(float(s.recap.mean()), 1))
    for k in ("tp1", "fifths", "tp5"):
        o[f"usd_{k}"] = round(float(s[k].mean()), 3)
        o[f"t_{k}"] = round(bt.tstat_weekly(s.assign(net=s[k])), 2)
    return o


def main(path):
    m = pd.read_parquet(path)[["o", "h", "l", "c"]].astype(float)
    rng = np.random.default_rng(147)
    ok = np.flatnonzero((m.index.hour >= 7) & (m.index.hour < 20) & (m.index.weekday < 5))[:-MAXB - 5]
    pick = np.sort(rng.choice(ok, 20000, replace=False))
    A = run(m, [(j, int(rng.choice([-1, 1])), m.o.values[j]) for j in pick])
    res = dict(plan="edges/plans/E147_p4l_template.md", md5=PLAN, A_random={p: summ(A, *map(lambda x: pd.Timestamp(x, tz="UTC"), ab)) for p, ab in PER.items()})
    res["A_random"]["all"] = summ(A, pd.Timestamp("2025-01-01", tz="UTC"), pd.Timestamp("2027-01-01", tz="UTC"))
    # a "recap week": 13 gold signals a week drawn at random
    wk = [A.sample(13, random_state=i).recap.sum() for i in range(2000)]
    wins = [(A.sample(13, random_state=i).hit >= 1).mean() for i in range(2000)]
    res["A_random"]["week_of_13"] = dict(median_recap_pips=float(np.median(wk)), p10=float(np.percentile(wk, 10)), p90=float(np.percentile(wk, 90)),
                                         share_of_weeks_positive=round(float(np.mean(np.array(wk) > 0)), 3), median_ticks=round(float(np.median(wins)), 3))
    print("A", json.dumps(res["A_random"], default=str)[:1500], flush=True)
    # B fib pullback
    f = m.resample("15min").agg(dict(o="first", h="max", l="min", c="last")).dropna()
    tr = pd.concat([f.h - f.l, (f.h - f.c.shift()).abs(), (f.l - f.c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().values
    Hf, Lf, Cf = f.h.values, f.l.values, f.c.values
    pos = m.index.searchsorted(f.index + pd.Timedelta("15min"))
    H1, L1 = m.h.values, m.l.values
    res["B_fib"] = {}
    for frac in (0.5, 0.618):
        ents, hours, i = [], [], 20
        while i < len(f) - 10:
            a = atr[i]
            lo8, hi8 = Lf[i - 7:i + 1].min(), Hf[i - 7:i + 1].max()
            d = 0
            if a > 0 and hi8 - lo8 >= 3 * a:
                if Hf[i] >= hi8 and Lf[i - 7:i + 1].argmin() < 7:
                    d = 1
                elif Lf[i] <= lo8 and Hf[i - 7:i + 1].argmax() < 7:
                    d = -1
            if d:
                lvl = hi8 - frac * (hi8 - lo8) if d == 1 else lo8 + frac * (hi8 - lo8)
                j0, j1 = pos[i], min(pos[i] + 120, len(H1) - MAXB - 5)
                fill = None
                for q in range(j0, j1):
                    if (d == 1 and H1[q] >= hi8 + a) or (d == -1 and L1[q] <= lo8 - a):
                        break
                    if (d == 1 and L1[q] <= lvl) or (d == -1 and H1[q] >= lvl):
                        fill = q
                        break
                if fill is not None:
                    ents.append((fill, d, lvl))
                    hours.append(m.index[fill].hour)
                    i += 8
                    continue
            i += 1
        B = run(m, ents)
        ctrl_pick = np.sort(rng.choice(np.flatnonzero(np.isin(m.index.hour, list(set(hours))))[:-MAXB - 5], min(len(ents) * 5, 20000), replace=False))
        Cc = run(m, [(j, int(rng.choice([-1, 1])), m.o.values[j]) for j in ctrl_pick])
        r = {p: summ(B, *map(lambda x: pd.Timestamp(x, tz="UTC"), ab)) for p, ab in PER.items()}
        r["control_final"] = summ(Cc, pd.Timestamp(PER["final"][0], tz="UTC"), pd.Timestamp(PER["final"][1], tz="UTC"))
        res["B_fib"][f"entry {frac}"] = r
        for p in ("val", "final"):
            bt.log_attempt(PLAN, f"E147 fib {frac}", p, dict(n=r[p].get("n"), mean_bp=r[p].get("usd_fifths"), t_week=r[p].get("t_fifths")))
        print("B", frac, json.dumps(r, default=str), flush=True)
    ok = [k for k, r in res["B_fib"].items() if (r["final"].get("usd_fifths") or -1) > 0 and (r["final"].get("t_fifths") or 0) >= 2
          and (r["val"].get("usd_fifths") or -1) > 0 and (r["val"].get("t_fifths") or 0) >= 1.5 and r["final"]["usd_fifths"] > r["control_final"]["usd_fifths"]]
    res["verdict"] = ("PASS " + ", ".join(ok)) if ok else "FAIL (fib pullback); template arithmetic reported"
    json.dump(res, open("edges/results/E147_result.json", "w"), indent=1, default=str)
    print(res["verdict"])


if __name__ == "__main__":
    main(sys.argv[1])
