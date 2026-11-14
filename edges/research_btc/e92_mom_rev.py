"""E92 short-horizon daily momentum/reversal with vol targeting (plans/E92_btc_short_mom_rev.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from libbtc import *  # noqa
MD5 = "18e5542b97cda9f3e48592ebb9dea098"


def daily_funding(d):
    f = bt.funding(SYM)
    f.index = pd.DatetimeIndex(f.index).floor("D")
    fd = f.groupby(level=0).sum().reindex(d.index).fillna(0.0003)
    return fd


def series(lr, pos, fd):
    """pos decided at close of d applied to return of d+1."""
    p = pos.shift(1).fillna(0)
    turn = p.diff().abs().fillna(p.abs())
    return p * lr - 0.001 * turn - p * fd


def grid(lr, vol, fd, shift=0):
    out = {}
    for N in (1, 2, 3, 5):
        sig = np.sign(lr.rolling(N).sum())
        if shift:
            sig = pd.Series(np.roll(sig.values, shift), index=sig.index)
        for mode in (1, -1):
            for lo in (False, True):
                s = mode * sig
                if lo:
                    s = s.clip(lower=0)
                pos = s * np.minimum(2, 0.40 / vol)
                out[f"N{N} {'MOM' if mode>0 else 'REV'} {'LO' if lo else 'LS'}"] = series(lr, pos.fillna(0), fd)
    return out


def st(r, P, p):
    a, b = P[p]
    x = r[(r.index >= a) & (r.index < b)].dropna()
    s = curve_stats(x)
    s["mean_bp"] = round(x.mean() * 1e4, 3)
    s["years"] = {int(y): round(v * 1e4, 2) for y, v in x.groupby(x.index.year).mean().items()}
    s["years_pos"] = int(sum(v > 0 for v in s["years"].values()))
    return s


def main():
    d = bars("1d")
    lr = np.log(d.c / d.c.shift(1)).fillna(0)
    vol = lr.rolling(20, min_periods=15).std() * np.sqrt(365)
    fd = daily_funding(d)
    real = grid(lr, vol, fd)
    rows = {}
    best = None
    for k, r in real.items():
        s = st(r, P1, "discovery"); rows[k] = s
        bt.log_attempt(MD5, k, "discovery", dict(mean_bp=s["mean_bp"], t_week=s["nw_t"], sharpe=s["sharpe"]))
        if s["mean_bp"] > 0 and s["years_pos"] >= 3 and (best is None or s["nw_t"] > rows[best]["nw_t"]):
            best = k
    rng = np.random.default_rng(92)
    n = int((d.index < "2024-01-01").sum())
    nulls = []
    for _ in range(200):
        sh = int(rng.integers(90, n - 90))
        g = grid(lr, vol, fd, shift=sh)
        nulls.append(max(st(r, P1, "discovery")["nw_t"] for r in g.values()))
    out = dict(plan="E92", discovery=rows, chosen=best, null_p95=float(np.percentile(nulls, 95)))
    # controls
    out["control_always_long_voltarget"] = {p: st(series(lr, np.minimum(2, 0.4 / vol).fillna(0), fd), P1, p) for p in P1}
    out["buy_hold"] = {p: st(lr, P1, p) for p in P1}
    if best:
        out["real_best_t"] = rows[best]["nw_t"]; out["luck_pass"] = rows[best]["nw_t"] >= out["null_p95"]
        out["validation"] = st(real[best], P1, "validation")
        out["final_info_only"] = st(real[best], P1, "final")
        bt.log_attempt(MD5, best, "validation", dict(mean_bp=out["validation"]["mean_bp"], t_week=out["validation"]["nw_t"]))
        out["verdict"] = "FAIL (luck check)" if not out["luck_pass"] else ("FAIL (validation)" if out["validation"]["nw_t"] < 1.5 else "see final")
    else:
        out["verdict"] = "FAIL (no discovery variant met the bar)"
    json.dump(out, open(f"{ROOT}/edges/results/E92_result.json", "w"), indent=1, default=str)
    for k, v in sorted(rows.items(), key=lambda kv: -kv[1]["nw_t"])[:5]:
        print(k, v["mean_bp"], v["nw_t"], v["sharpe"], v["years"])
    print({k: v for k, v in out.items() if k not in ("discovery",)})


if __name__ == "__main__":
    main()
