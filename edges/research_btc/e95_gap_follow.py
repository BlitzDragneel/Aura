"""E95 CME gap FOLLOW (plans/E95_btc_cme_gap_follow.md). One configuration."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from libbtc import *  # noqa
from e88_weekend import events, mk
MD5 = "284b07db4f3a01e4a4f52b44918574b6"


def rule(d, shift=0, g=0.01, H=24):
    o, h, l, c = (d[k].values for k in "ohlc")
    n = len(d)
    vt, fri, reo, mon = events(d, shift)
    rows = []; busy = -1
    for f in fri:
        k = np.searchsorted(reo, f + 1)
        if k >= len(reo) or reo[k] - f >= 60:
            continue
        r = reo[k]
        if r <= busy or r + H >= n or not (c[f] > 0 and o[r] > 0 and c[r + H - 1] > 0):
            continue
        gap = o[r] / c[f] - 1
        if abs(gap) < g:
            continue
        s = 1 if gap > 0 else -1
        lo = np.nanmin(l[r:r + H]); hi = np.nanmax(h[r:r + H])
        rows.append((r, r + H - 1, s, o[r], c[r + H - 1], (lo / o[r] - 1) if s > 0 else -(hi / o[r] - 1), False))
        busy = r + H - 1
    return mk(d, rows, TAKER_SIDE, None)


def main():
    d = bars("1h")
    tr = rule(d)
    rng = np.random.default_rng(95)
    nulls = []
    for s in rng.choice(np.arange(12, 157), 150):
        t = per(rule(d, int(s)), P1)["discovery"]
        nulls.append(fast_t(t) if len(t) >= 10 else np.nan)
    pp = per(tr, P1)
    out = dict(plan="E95", md5=MD5, rule="|gap|>=1% follow, 24h", discovery=summ(pp["discovery"]))
    nb = np.array([x for x in nulls if x == x])
    out["null_p95"] = float(np.percentile(nb, 95)); out["luck_pass"] = bool(out["discovery"]["t_week"] >= out["null_p95"])
    bt.log_attempt(MD5, "GAP FOLLOW g0.01 H24", "discovery", out["discovery"])
    out["validation"] = summ(pp["validation"]); bt.log_attempt(MD5, "GAP FOLLOW g0.01 H24", "validation", out["validation"])
    v = out["validation"]
    vpass = v["n"] > 0 and v["mean_bp"] > 0 and v["t_week"] >= 1.5
    out["validation_pass"] = bool(vpass)
    if out["luck_pass"] and vpass:
        out["final"] = summ(pp["final"]); bt.log_attempt(MD5, "GAP FOLLOW g0.01 H24", "final", out["final"])
        f = out["final"]
        ok = f["mean_bp"] > 0 and ((f["n"] >= 100 and f["t_week"] >= 2) or (f["n"] >= 50 and f["t_week"] >= 3))
        out["verdict"] = "PASS" if ok else "FAIL (final)"
    else:
        out["verdict"] = "FAIL (luck check)" if not out["luck_pass"] else "FAIL (validation)"
        out["final_info_only"] = summ(pp["final"]); bt.log_attempt(MD5, "GAP FOLLOW g0.01 H24", "final_info", out["final_info_only"])
    tr.to_parquet(f"{SCR}/E95_trades.parquet")
    json.dump(out, open(f"{ROOT}/edges/results/E95_result.json", "w"), indent=1, default=str)
    print(json.dumps(out, indent=0, default=str)[:3000])


if __name__ == "__main__":
    main()
