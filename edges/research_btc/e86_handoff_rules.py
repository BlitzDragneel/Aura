"""E86: handoff rule families on BTC 15m (plans/E86_handoff_rules_btc.md). One configuration per family."""
import json, sys
import numpy as np, pandas as pd
from libbtc import *  # noqa

MD5 = "856f2ace8ac340265c9883cda7ad3f72"


def families(d, a):
    c, h, l = d.c, d.h, d.l
    hi16 = h.shift(1).rolling(16).max(); lo16 = l.shift(1).rolling(16).min()
    bo_l = c > hi16; bo_s = c < lo16
    out = {}
    def sig(mask_l, mask_s):
        il = np.where(mask_l.fillna(False).values)[0]; is_ = np.where(mask_s.fillna(False).values)[0]
        idx = np.concatenate([il, is_]); sd = np.concatenate([np.ones(len(il)), -np.ones(len(is_))])
        o = np.argsort(idx, kind="stable")
        return idx[o], sd[o].astype(int)
    out["breakout"] = sig(bo_l, bo_s)
    natr = a / c
    pct = natr.rolling(960, min_periods=480).rank(pct=True)
    comp = (pct <= 0.20).astype(float).rolling(8).max().shift(1) > 0
    out["compression"] = sig(bo_l & comp, bo_s & comp)
    # confirmation: bar i+1 also closes beyond level -> signal index = i+1 (entry open of i+3)
    cl = (bo_l & comp).shift(1, fill_value=False) & (c > hi16.shift(1))
    cs = (bo_s & comp).shift(1, fill_value=False) & (c < lo16.shift(1))
    out["compression_conf"] = sig(cl, cs)
    # accepted retest: breakout within prior 8 bars at level Lv (most recent breakout)
    lvl_l = hi16.where(bo_l).shift(1).ffill(limit=7)
    lvl_s = lo16.where(bo_s).shift(1).ffill(limit=7)
    rl = (l <= lvl_l + 0.25 * a) & (c > lvl_l) & ~bo_l
    rs = (h >= lvl_s - 0.25 * a) & (c < lvl_s) & ~bo_s
    out["accepted_retest"] = sig(rl, rs)
    rng = h - l
    clv = (c - l) / rng.replace(0, np.nan)
    fa_s = (h >= hi16 + 0.1 * a) & (c < hi16) & (rng >= 1.5 * a) & (clv <= 0.4)
    fa_l = (l <= lo16 - 0.1 * a) & (c > lo16) & (rng >= 1.5 * a) & (clv >= 0.6)
    out["failed_auction"] = sig(fa_l, fa_s)
    return out


def random_control(d, a, tr, n=200, seed=0):
    """Same count per period and side mix, random entry bars, same engine (overlap allowed)."""
    rng = np.random.default_rng(seed)
    valid = np.where(np.isfinite(a) & np.isfinite(d.c.values))[0]
    t = d.index[valid]
    res = {p: [] for p in P5}
    for p, (x0, x1) in P5.items():
        pool = valid[(t >= x0) & (t < x1)]
        sub = tr[(tr.time >= x0) & (tr.time < x1)]
        k = len(sub)
        if k < 3:
            continue
        sides = sub.side.values
        for _ in range(n):
            si = np.sort(rng.choice(pool[:-20], k, replace=False))
            r = bracket(d, si, rng.permutation(sides), overlap=True, a=a)
            res[p].append(r.net.mean())
    return {p: (float(np.percentile(v, 95)) if v else None) for p, v in res.items()}


def main():
    d = bars("15m")
    a = atr(d).values
    fam = families(d, pd.Series(a, index=d.index))
    out = {}
    for name, (si, sd) in fam.items():
        delay = 2
        tr = bracket(d, si, sd, delay=delay, a=a)
        tr.to_parquet(f"{SCR}/E86_{name}.parquet")
        res = {p: summ(x) for p, x in per(tr, P5).items()}
        res["all"] = summ(tr)
        so = tr[(tr.time >= "2026-09-01") & (tr.time < "2026-11-01")]
        nv = tr[(tr.time >= "2026-11-01")]
        res["sep_oct_2026"] = dict(n=len(so), acct_6bp=round(handoff_account(so, 0.0006), 3),
                                   acct_12bp=round(handoff_account(so, 0.0012), 3), mean_bp=round(so.net.mean() * 1e4, 2) if len(so) else None)
        res["nov_2026"] = dict(n=len(nv), acct_6bp=round(handoff_account(nv, 0.0006), 3) if len(nv) else 0)
        res["acct_6bp_by_period"] = {p: round(handoff_account(x, 0.0006), 2) for p, x in per(tr, P5).items()}
        res["long_short"] = {("long" if s > 0 else "short"): summ(tr[tr.side == s]) for s in (1, -1)}
        res["control_p95_mean_bp"] = {p: (None if v is None else round(v * 1e4, 2))
                                      for p, v in random_control(d, a, tr, n=100).items()}
        bt.log_attempt(MD5, f"E86_{name}", "all", res["all"])
        out[name] = res
        f = res["final"]; v = res["validation"]; di = res["discovery"]
        print(f"{name:18s} disc {di['mean_bp']:7.2f} t{di['t_week']:5.2f} n{di['n']:5d} | val {v['mean_bp']:7.2f} t{v['t_week']:5.2f} n{v['n']:4d} | "
              f"fin {f['mean_bp']:7.2f} t{f['t_week']:5.2f} n{f['n']:5d} | SepOct n{res['sep_oct_2026']['n']} acct {res['sep_oct_2026']['acct_6bp']}% / {res['sep_oct_2026']['acct_12bp']}% | ctrl95 {res['control_p95_mean_bp']}", flush=True)
    json.dump(out, open(f"{ROOT}/edges/results/E86_result.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
