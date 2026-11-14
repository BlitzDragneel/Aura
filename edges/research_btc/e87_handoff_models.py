"""E87: handoff learned models + FOMC follow/fade on BTC 15m (plans/E87_handoff_models_btc.md)."""
import json, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from libbtc import *  # noqa
import os
if os.environ.get('NOLOG'):
    bt.log_attempt = lambda *a, **k: None

MD5 = "7d82df2f6f325baffb47e10aed9cb6f4"


def features(d, a):
    c = d.c
    lc = np.log(c)
    X = pd.DataFrame(index=d.index)
    for k in (1, 2, 4, 8, 16, 32, 96):
        X[f"r{k}"] = lc - lc.shift(k)
    X["natr"] = a / c
    X["atr_ratio"] = a / a.rolling(96).mean()
    rng = d.h - d.l
    X["rng_atr"] = rng / a
    X["clv"] = (c - d.l) / rng.replace(0, np.nan)
    for n in (16, 96):
        X[f"dhi{n}"] = (c - d.h.rolling(n).max()) / a
        X[f"dlo{n}"] = (c - d.l.rolling(n).min()) / a
    dc = c.diff()
    up = dc.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-dc.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    X["rsi"] = 100 - 100 / (1 + up / dn)
    X["hour"] = d.index.hour + d.index.minute / 60
    X["dow"] = d.index.dayofweek
    return X


PARAMS = dict(n_estimators=200, learning_rate=0.05, num_leaves=31, min_child_samples=200, subsample=0.8,
              subsample_freq=1, random_state=0, verbose=-1, n_jobs=2)


def main():
    d = bars("15m")
    a = atr(d)
    X = features(d, a)
    fwd = d.c.shift(-16) / d.c - 1
    b = np.maximum(0.0012, 0.5 * a / d.c)
    y3 = pd.Series(np.where(fwd > b, 2, np.where(fwd < -b, 0, 1)), index=d.index).where(fwd.notna())
    ybig = (fwd.abs() > np.maximum(0.004, 2 * a / d.c)).astype(float).where(fwd.notna())
    ok = X.notna().all(axis=1) & y3.notna()
    T = d.index
    tr1 = ok & (T < "2024-01-01") & (T < pd.Timestamp("2024-01-01", tz="UTC") - pd.Timedelta("4h"))
    tr2 = ok & (T < pd.Timestamp("2025-01-01", tz="UTC") - pd.Timedelta("4h"))
    val = X.notna().all(axis=1) & (T >= "2024-01-01") & (T < "2025-01-01")
    fin = X.notna().all(axis=1) & (T >= "2025-01-01")
    res = {}
    # ---------------- A: direction model
    m1 = lgb.LGBMClassifier(objective="multiclass", **PARAMS).fit(X[tr1], y3[tr1])
    pv = m1.predict_proba(X[val])
    m2 = lgb.LGBMClassifier(objective="multiclass", **PARAMS).fit(X[tr2], y3[tr2])
    pf = m2.predict_proba(X[fin])
    thr = np.percentile(np.maximum(pv[:, 0], pv[:, 2]), 98)
    def trades(P, mask):
        idx = np.where(mask.values)[0]
        mx = np.maximum(P[:, 0], P[:, 2])
        sel = mx > thr
        side = np.where(P[:, 2] >= P[:, 0], 1, -1)
        return bracket(d, idx[sel], side[sel], a=a.values)
    tv = trades(pv, val); tf_ = trades(pf, fin)
    # in-sample discovery (information only: fitted on it)
    pdisc = m1.predict_proba(X[ok & tr1]); td = trades(pdisc, ok & tr1)
    res["A_direction"] = dict(threshold=float(thr), discovery_in_sample=summ(td), validation=summ(tv), final=summ(tf_),
                              final_long_short={s: summ(tf_[tf_.side == s]) for s in (1, -1)},
                              sep_oct_2026=dict(n=int(((tf_.time >= "2026-09-01") & (tf_.time < "2026-11-01")).sum()),
                                                acct_6bp=round(handoff_account(tf_[(tf_.time >= "2026-09-01") & (tf_.time < "2026-11-01")]), 3)),
                              acct_6bp=dict(validation=round(handoff_account(tv), 2), final=round(handoff_account(tf_), 2)),
                              val_class_logloss=float(log_loss(y3[val & y3.notna()], m1.predict_proba(X[val & y3.notna()]), labels=[0, 1, 2])))
    tv.to_parquet(f"{SCR}/E87A_val.parquet"); tf_.to_parquet(f"{SCR}/E87A_fin.parquet")
    bt.log_attempt(MD5, "E87A_direction", "validation", res["A_direction"]["validation"])
    bt.log_attempt(MD5, "E87A_direction", "final", res["A_direction"]["final"])
    print("A", json.dumps({k: v for k, v in res["A_direction"].items() if k in ("validation", "final", "sep_oct_2026", "acct_6bp")}, default=str)[:1500], flush=True)
    # ---------------- B: movement timing vs vol/clock control
    okb = X.notna().all(axis=1) & ybig.notna()
    trb1 = okb & tr1; trb2 = okb & tr2
    mb1 = lgb.LGBMClassifier(objective="binary", **PARAMS).fit(X[trb1], ybig[trb1])
    mb2 = lgb.LGBMClassifier(objective="binary", **PARAMS).fit(X[trb2], ybig[trb2])
    def cfeat(m):
        Z = pd.DataFrame({"la": np.log(a / d.c), "la96": np.log(a.rolling(96).mean() / d.c),
                          "lr": np.log(a / a.rolling(96).mean()), "wkend": (d.index.dayofweek >= 5).astype(float)}, index=d.index)
        for h in range(1, 24):
            Z[f"h{h}"] = (d.index.hour == h).astype(float)
        return Z[m]
    c1 = LogisticRegression(max_iter=2000).fit(cfeat(trb1), ybig[trb1])
    c2 = LogisticRegression(max_iter=2000).fit(cfeat(trb2), ybig[trb2])
    vm = okb & (T >= "2024-01-01") & (T < "2025-01-01")
    pm_v = mb1.predict_proba(X[vm])[:, 1]; pc_v = c1.predict_proba(cfeat(vm))[:, 1]
    thm = np.percentile(pm_v, 75); thc = np.percentile(pc_v, 75)
    out = {}
    windows = {"validation_2024": vm, "final_2025_26": okb & (T >= "2025-01-01"),
               "sep_oct_2026": okb & (T >= "2026-09-01") & (T < "2026-11-01"), "nov_2026": okb & (T >= "2026-11-01")}
    for w, m in windows.items():
        yy = ybig[m].values
        if w == "validation_2024":
            pm, pc = pm_v, pc_v
        else:
            pm = mb2.predict_proba(X[m])[:, 1]; pc = c2.predict_proba(cfeat(m))[:, 1]
        out[w] = dict(n=int(m.sum()), base_rate=round(float(yy.mean()), 4),
                      model_watch_rate=round(float(yy[pm > thm].mean()), 4), model_watch_share=round(float((pm > thm).mean()), 3),
                      control_watch_rate=round(float(yy[pc > thc].mean()), 4), control_watch_share=round(float((pc > thc).mean()), 3),
                      logloss_model=round(float(log_loss(yy, pm, labels=[0, 1])), 4), logloss_control=round(float(log_loss(yy, pc, labels=[0, 1])), 4))
        print("B", w, out[w], flush=True)
    res["B_movement_timing"] = out
    bt.log_attempt(MD5, "E87B_model", "final", out["final_2025_26"])
    bt.log_attempt(MD5, "E87B_control", "final", out["final_2025_26"])
    # ---------------- C: FOMC follow / fade
    ds = json.load(open(f"{SCR}/dl/fomc_dates.json"))
    ds = [x for x in ds if x >= "20220101" and x != "20250822"]
    rows = []
    for x in ds:
        t0 = pd.Timestamp(f"{x[:4]}-{x[4:6]}-{x[6:]} 14:00", tz="America/New_York").tz_convert("UTC")
        if t0 not in d.index:
            continue
        i = d.index.get_loc(t0)
        if i + 2 + 16 >= len(d):
            continue
        react = d.c.iloc[i + 1] / d.o.iloc[i] - 1
        e = d.o.iloc[i + 2]; xx = d.c.iloc[i + 2 + 15]
        g = np.sign(react) * (xx / e - 1)
        rows.append(dict(time=d.index[i + 2], date=x, react=react, follow_gross=g, fade_gross=-g))
    ev = pd.DataFrame(rows)
    cost = 2 * TAKER_SIDE
    ev["follow_net"] = ev.follow_gross - cost; ev["fade_net"] = ev.fade_gross - cost
    yrs = ev.groupby(ev.time.dt.year)[["follow_gross", "follow_net", "fade_net"]].mean()
    yrs["n"] = ev.groupby(ev.time.dt.year).size() / 1e4
    res["C_fomc"] = dict(n=len(ev), follow_gross_bp=round(ev.follow_gross.mean() * 1e4, 1),
                         follow_net_bp=round(ev.follow_net.mean() * 1e4, 1), fade_net_bp=round(ev.fade_net.mean() * 1e4, 1),
                         by_year={str(k): v for k, v in (yrs * 1e4).round(1).to_dict(orient="index").items()},
                         y2024_25_follow_gross_bp=round(ev[ev.time.dt.year.isin([2024, 2025])].follow_gross.mean() * 1e4, 1),
                         y2026_follow_gross_bp=round(ev[ev.time.dt.year == 2026].follow_gross.mean() * 1e4, 1),
                         events=ev.assign(time=ev.time.astype(str)).round(5).to_dict(orient="records"))
    for nm in ("follow", "fade"):
        bt.log_attempt(MD5, f"E87C_fomc_{nm}", "all", dict(n=len(ev), mean_bp=float(ev[f"{nm}_net"].mean() * 1e4)))
    print("C", {k: v for k, v in res["C_fomc"].items() if k != "events"}, flush=True)
    json.dump(res, open(f"{ROOT}/edges/results/E87_result.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
