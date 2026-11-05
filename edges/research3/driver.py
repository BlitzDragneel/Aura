"""Generic discovery → luck check → validation → final driver (E63_common_bot3.md)."""
import numpy as np
import pandas as pd
from edges.research3.common import bt, period, tstat, luck_pct, write_result, MD5


def run_grid(coins, feats_fn, variants, shift=0):
    """feats_fn(coin, shift) -> (perp_df, features dict). variants: list of (name, fn(F)->(mask, side), H).
    Returns {name: trades DataFrame (all periods)}."""
    res = {name: [] for name, _, _ in variants}
    for c in coins:
        df, F = feats_fn(c, shift)
        from edges.research3.common import simulate
        for name, fn, H in variants:
            m, s = fn(F)
            m = np.nan_to_num(np.asarray(m, dtype=float), nan=0).astype(bool)
            res[name].append(simulate(df, c, m, s, H))
    return {k: pd.concat(v, ignore_index=True).sort_values("time") if v else pd.DataFrame() for k, v in res.items()}


def disc_table(R, disc_start=None):
    rows = []
    for k, tr in R.items():
        d = period(tr, "discovery", disc_start)
        s = bt.summarize(d, k) if len(d) else dict(label=k, n=0)
        s["t"] = tstat(d) if len(d) >= 3 else np.nan
        rows.append(s)
    return rows


def best_t(rows, min_n=30):
    ts = [r["t"] for r in rows if r.get("n", 0) >= min_n and r["t"] == r["t"]]
    return max(ts) if ts else np.nan


def run_plan(plan, md5key, coins, feats_fn, variants, n_null=200, disc_start=None, seed=0, shift_range=None,
             extra=None):
    md5 = MD5[md5key]
    R = run_grid(coins, feats_fn, variants, 0)
    rows = disc_table(R, disc_start)
    for r in rows:
        bt.log_attempt(md5, f"{plan}:{r['label']}", "discovery", r)
    real_best = best_t(rows)
    rng = np.random.default_rng(seed)
    lo, hi = shift_range
    null = []
    for j in range(n_null):
        k = int(rng.integers(lo, hi))
        null.append(best_t(disc_table(run_grid(coins, feats_fn, variants, k), disc_start)))
    null = np.array(null, dtype=float)
    p95 = float(np.nanpercentile(null, 95))
    pct = luck_pct(real_best, null)
    bt.log_attempt(md5, f"{plan}:luck_check", "discovery", dict(real_best_t=real_best, null_p95=p95, pct=pct,
                                                               n_null=n_null))
    cand = [r for r in rows if r.get("n", 0) >= 30 and r["t"] == r["t"] and r["t"] >= p95
            and r["years_pos"] >= 0.6 * r["years_total"] and r["mean_bp"] > 0]
    cand = sorted(cand, key=lambda r: -r["t"])[:3]
    out = dict(plan=plan, md5=md5, n_variants=len(variants), discovery=rows, luck=dict(real_best_t=real_best,
               null_p95=p95, null_p99=float(np.nanpercentile(null, 99)), pct=pct, n_null=n_null),
               promoted=[r["label"] for r in cand], validation={}, final=None, verdict=None)
    if not cand:
        out["verdict"] = "FAIL: no discovery variant beat the luck check (95th pct of shifted-data best t)" \
            if not (real_best == real_best and real_best >= p95) else "FAIL: luck-check winners failed year/mean screens"
        write_result(plan, out)
        return out, R
    best_v = None
    for r in cand:
        v = period(R[r["label"]], "validation")
        s = bt.summarize(v, r["label"]) if len(v) else dict(label=r["label"], n=0)
        s["t"] = tstat(v) if len(v) >= 3 else np.nan
        bt.log_attempt(md5, f"{plan}:{r['label']}", "validation", s)
        out["validation"][r["label"]] = s
        if s.get("n", 0) > 0 and s["mean_bp"] > 0 and s["t"] >= 1.5 and (best_v is None or s["t"] > best_v[1]):
            best_v = (r["label"], s["t"])
    if best_v is None:
        out["verdict"] = "FAIL: no promoted variant passed VALIDATION (mean > 0, t ≥ 1.5); FINAL not looked at"
        write_result(plan, out)
        return out, R
    name = best_v[0]
    f = period(R[name], "final")
    s = bt.summarize(f, name) if len(f) else dict(label=name, n=0)
    s["t"] = tstat(f) if len(f) >= 3 else np.nan
    bt.log_attempt(md5, f"{plan}:{name}", "final", s)
    out["final"] = s
    out["final_variant"] = name
    allt = R[name]
    ally = allt.groupby(allt.time.dt.year).net.mean()
    out["all_years_pos"] = [int((ally > 0).sum()), int(len(ally))]
    ok = (s.get("n", 0) > 0 and s["mean_bp"] > 0 and s["t"] >= 2.0 and (ally > 0).mean() >= 0.6
          and (s["n"] >= 100 or (s["n"] >= 50 and s["t"] >= 3)) and s["ex_top5pct_bp"] > 0)
    out["verdict"] = "PASS" if ok else "FAIL at FINAL"
    if ok:
        out["leverage"] = bt.leverage_table(allt[allt.time >= pd.Timestamp("2024-01-01", tz="UTC")])
        out["leverage_all"] = bt.leverage_table(allt)
    write_result(plan, out)
    return out, R
