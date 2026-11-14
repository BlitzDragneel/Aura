"""E96 movement-watch windows + stop-entry breakout (plans/E96_btc_watch_breakout.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from numba import njit
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from libbtc import *  # noqa
from e87_handoff_models import features, PARAMS
MD5 = "2da1f15f1d5749bbdb8ab728730b2838"


@njit(cache=True)
def sim(o, h, l, c, a, flag, m, tgt_on, W, H):
    n = len(c); out = np.empty((n // 4 + 1, 6)); k = 0; t = 0
    while t < n - W - H - 2:
        if not flag[t] or not (a[t] > 0):
            t += 1; continue
        bs = c[t] + m * a[t]; ss = c[t] - m * a[t]; A = a[t]
        j0 = -1; s = 0; fp = 0.0; both = False
        for j in range(t + 1, t + 1 + W):
            if not (h[j] > 0):
                break
            up = h[j] >= bs; dn = l[j] <= ss
            if up or dn:
                j0 = j
                if up and dn:
                    both = True; s = 1; fp = max(o[j], bs)
                elif up:
                    s = 1; fp = max(o[j], bs)
                else:
                    s = -1; fp = min(o[j], ss)
                break
        if j0 < 0:
            t += W; continue
        st = fp - s * 2 * A; tg = fp + s * 6 * A
        x = -1; px = 0.0; worst = 0.0
        if both:
            x = j0; px = st; worst = -2 * A / fp
        else:
            last = j0 + H
            for q in range(j0, last + 1):
                if not (h[q] > 0):
                    x = -2; break
                if q > j0 and ((s > 0 and o[q] <= st) or (s < 0 and o[q] >= st)):
                    x = q; px = o[q]; worst = min(worst, s * (o[q] / fp - 1)); break
                if (s > 0 and l[q] <= st) or (s < 0 and h[q] >= st):
                    x = q; px = st; worst = min(worst, s * (st / fp - 1)); break
                worst = min(worst, (l[q] / fp - 1) if s > 0 else -(h[q] / fp - 1))
                if tgt_on and q > j0 and ((s > 0 and h[q] >= tg) or (s < 0 and l[q] <= tg)):
                    x = q; px = tg; break
            if x == -1:
                x = last; px = c[last]
        if x >= 0 and px > 0:
            out[k, 0] = j0; out[k, 1] = x; out[k, 2] = s; out[k, 3] = fp; out[k, 4] = px; out[k, 5] = worst
            k += 1
            t = x + 1
        else:
            t = j0 + 1
    return out[:k]


def to_tr(rows, d):
    idx = d.index; bar = idx[1] - idx[0]
    tr = pd.DataFrame({"time": idx[rows[:, 0].astype(int)], "exit_time": idx[rows[:, 1].astype(int)] + bar,
                       "side": rows[:, 2].astype(int), "entry": rows[:, 3], "exit": rows[:, 4], "mae": rows[:, 5]})
    tr["sym"] = SYM
    tr["gross"] = tr.side * (tr.exit / tr.entry - 1)
    tr["fund"] = funding_between(tr.time, tr.exit_time, tr.side)
    tr["net"] = tr.gross - 2 * TAKER_SIDE - tr.fund
    return tr


def main():
    d = bars("15m")
    a = atr(d)
    X = features(d, a)
    fwd = d.c.shift(-16) / d.c - 1
    y = (fwd.abs() > np.maximum(0.004, 2 * a / d.c)).astype(float).where(fwd.notna())
    Z = pd.DataFrame({"la": np.log(a / d.c), "la96": np.log(a.rolling(96).mean() / d.c),
                      "lr": np.log(a / a.rolling(96).mean()), "wkend": (d.index.dayofweek >= 5).astype(float)}, index=d.index)
    for hh in range(1, 24):
        Z[f"h{hh}"] = (d.index.hour == hh).astype(float)
    T = d.index
    okx = X.notna().all(axis=1) & Z.notna().all(axis=1)
    lab = okx & y.notna()
    def ts(s): return pd.Timestamp(s, tz="UTC")
    cut = pd.Timedelta("4h")
    folds = [  # (train mask, score mask)
        (lab & (T >= ts("2023-01-01")) & (T < ts("2024-01-01") - cut), okx & (T < ts("2023-01-01"))),
        (lab & (T < ts("2023-01-01") - cut), okx & (T >= ts("2023-01-01")) & (T < ts("2024-01-01"))),
        (lab & (T < ts("2024-01-01") - cut), okx & (T >= ts("2024-01-01")) & (T < ts("2025-01-01"))),
        (lab & (T < ts("2025-01-01") - cut), okx & (T >= ts("2025-01-01")))]
    pm = pd.Series(np.nan, index=T); pc = pd.Series(np.nan, index=T)
    for trm, scm in folds:
        mdl = lgb.LGBMClassifier(objective="binary", **PARAMS).fit(X[trm], y[trm])
        pm[scm] = mdl.predict_proba(X[scm])[:, 1]
        lr_ = LogisticRegression(max_iter=2000).fit(Z[trm], y[trm])
        pc[scm] = lr_.predict_proba(Z[scm])[:, 1]
    flags = {}
    for nm, p in (("MODEL", pm), ("CONTROL", pc)):
        thr = p.rolling(2880, min_periods=960).quantile(0.75)
        flags[nm] = (p > thr).fillna(False).values
    o, h, l, c, av = d.o.values, d.h.values, d.l.values, d.c.values, a.values
    def grid(F):
        out = {}
        for m in (0.5, 1.0):
            for ex in ("BRACKET", "TIME"):
                for g in ("MODEL", "CONTROL"):
                    out[f"m{m} {ex} {g}"] = to_tr(sim(o, h, l, c, av, F[g], m, ex == "BRACKET", 4, 16), d)
        return out
    real = grid(flags)
    rng = np.random.default_rng(96)
    pool = np.where((T < ts("2024-01-01")) & np.isfinite(pm.values))[0]
    nulls = []
    for i in range(200):
        F = {}
        for g, f in flags.items():
            ff = np.zeros(len(f), dtype=np.bool_); ff[rng.choice(pool, int(f[pool].sum()), replace=False)] = True; F[g] = ff
        r = grid(F)
        tt = [fast_t(per(t, P5)["discovery"]) for t in r.values() if len(per(t, P5)["discovery"]) >= 100 and per(t, P5)["discovery"].net.mean() > 0]
        nulls.append(max(tt) if tt else 0.0)
    out = judge(MD5, "E96", real, nulls, P5, nmin=100, years_need=2, final_info=True)
    out["all_rows_by_period"] = {k: {p: {kk: s.get(kk) for kk in ("n", "mean_bp", "t_week")} for p, s in ((p, summ(x)) for p, x in per(t, P5).items())} for k, t in real.items()}
    json.dump(out, open(f"{ROOT}/edges/results/E96_result.json", "w"), indent=1, default=str)
    for k, v in out["all_rows_by_period"].items():
        print(f"{k:22s}", v)
    print({k: v for k, v in out.items() if k not in ("discovery", "all_rows_by_period")})


if __name__ == "__main__":
    main()
