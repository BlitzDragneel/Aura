"""E142 movement forecast + WATCH-armed breakouts (plan edges/plans/E142_movement_forecast.md, md5 5f8d4899...).
Usage: python3 -m edges.lead.e142_movement <XAU_perp_1m.parquet> <PAXG_1m.parquet>"""
import json
import sys
import warnings

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from edges.lib import bt

warnings.filterwarnings("ignore")
PLAN = "5f8d489939aeb81694b0ee76beeecc08"
SETS = {
    "BTC": dict(per=("2022-01-01", "2024-01-01", "2025-01-01", "2026-11-04"), costs={"base": 0.0007}, reach=("pct", [0.005, 0.01])),
    "GOLD": dict(per=("2025-12-11", "2026-06-01", "2026-09-01", "2026-11-14"), costs={"base": 0.0002, "tight": 0.000025}, reach=("usd", [4.0, 7.0])),
    "PAXG": dict(per=("2021-01-01", "2024-01-01", "2025-01-01", "2025-12-01"), costs={"base": 0.0010}, reach=("pct", [0.001, 0.00175])),
}
HZ = {"4h": 16, "8h": 32}
CTRL = ["rv24", "atrp", "hs", "hc", "wd"]


def bars15(fine):
    agg = dict(o="first", h="max", l="min", c="last", v="sum")
    if "tbv" in fine:
        agg["tbv"] = "sum"
    return fine.resample("15min").agg(agg).dropna(subset=["c"])


def features(f):
    c, lr = f.c, np.log(f.c).diff()
    tr = pd.concat([f.h - f.l, (f.h - c.shift()).abs(), (f.l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    X = pd.DataFrame(index=f.index)
    for k in (1, 4, 16, 96):
        X[f"r{k}"] = c / c.shift(k) - 1
    X["atrp"] = atr / c
    X["rv4"], X["rv24"], X["rv7d"] = lr.rolling(16).std(), lr.rolling(96).std(), lr.rolling(672).std()
    X["rv4_24"], X["rv24_7d"] = X.rv4 / X.rv24, X.rv24 / X.rv7d
    X["barr"] = (f.h - f.l) / atr
    h24, l24 = f.h.rolling(96).max(), f.l.rolling(96).min()
    X["pos24"] = (c - l24) / (h24 - l24)
    X["dhi"], X["dlo"] = (h24 - c) / atr, (c - l24) / atr
    X["comp"] = (f.h.rolling(16).max() - f.l.rolling(16).min()) / (h24 - l24)
    hr = f.index.hour + f.index.minute / 60
    X["hs"], X["hc"], X["wd"] = np.sin(2 * np.pi * hr / 24), np.cos(2 * np.pi * hr / 24), f.index.weekday
    X["volr"] = f.v / f.v.rolling(96).mean()
    if "tbv" in f:
        X["tb1"] = f.tbv / f.v.replace(0, np.nan)
        X["tb16"] = f.tbv.rolling(16).sum() / f.v.rolling(16).sum().replace(0, np.nan)
    return X, atr


def targets(f, atr, reach):
    c = f.c
    Y = pd.DataFrame(index=f.index)
    for name, n in HZ.items():
        fh = f.h[::-1].rolling(n).max()[::-1].shift(-1)
        fl = f.l[::-1].rolling(n).min()[::-1].shift(-1)
        Y[f"size_{name}"] = np.log((fh - fl) / c)
        mv = c.shift(-n) / c - 1
        Y[f"big_{name}"] = (mv.abs() > np.maximum(0.004, 2 * atr / c)).astype(float).where(mv.notna())
        Y[f"dir_{name}"] = (mv > 0).astype(float).where(mv.notna())
        Y[f"last_{name}"] = np.log((f.h.rolling(n).max() - f.l.rolling(n).min()) / c)
    day = f.index.floor("D")
    g = f.groupby(day)
    rh = g.h.transform(lambda s: s[::-1].cummax()[::-1].shift(-1))
    rl = g.l.transform(lambda s: s[::-1].cummin()[::-1].shift(-1))
    Y["size_day"] = np.log(((rh - rl) / c).where(rh > rl))
    mv = g.c.transform("last") / c - 1
    last_bar = f.index == pd.Series(f.index, index=f.index).groupby(day).transform("max").values
    mv = mv.where(~last_bar)
    Y["big_day"] = (mv.abs() > np.maximum(0.004, 2 * atr / c)).astype(float).where(mv.notna())
    Y["dir_day"] = (mv > 0).astype(float).where(mv.notna())
    # reach: +X before -X within 8h (15m bars; both in one bar = unknown)
    kind, xs = reach
    H, L, C = f.h.values, f.l.values, c.values
    for x in xs:
        dist = C * x if kind == "pct" else np.full(len(C), x)
        res = np.full(len(C), np.nan)
        done = np.zeros(len(C), bool)
        for k in range(1, 33):
            hk, lk = np.roll(H, -k), np.roll(L, -k)
            up, dn = hk >= C + dist, lk <= C - dist
            new = ~done & (up | dn)
            res[new & up & ~dn] = 1.0
            res[new & dn & ~up] = 0.0
            done |= new
        res[~done] = 0.0  # neither reached = not an "up first"
        res[-33:] = np.nan
        both = np.isnan(res)
        Y[f"reach_{x:g}"] = res
        Y.loc[both, f"reach_{x:g}"] = np.nan
    return Y


def fit(Xtr, ytr, Xva, yva, clf):
    P = dict(n_estimators=300, learning_rate=0.03, num_leaves=31, min_child_samples=100, subsample=0.8,
             subsample_freq=1, colsample_bytree=0.8, verbose=-1, n_jobs=3, random_state=142)
    m = (lgb.LGBMClassifier if clf else lgb.LGBMRegressor)(**P)
    m.fit(Xtr, ytr, eval_set=[(Xva, yva)], callbacks=[lgb.early_stopping(30, verbose=False)])
    return (lambda X: m.predict_proba(X)[:, 1]) if clf else m.predict


def week_t(x, idx):
    w = pd.Series(x, index=idx).groupby(pd.Grouper(freq="W")).sum()
    w = w[w != 0]
    return float(w.mean() / (w.std() / np.sqrt(len(w)))) if len(w) > 2 and w.std() > 0 else np.nan


def simulate(fine, sig_pos, atr, cost_free=True, Hlev=None, Llev=None, dirs=None, fade=False, arm=None, hold=None):
    """sig_pos: fine index right after each signal bar closes. Break mode (Hlev/Llev) or market mode (dirs)."""
    O, Hh, Ll, idx = fine.o.values, fine.h.values, fine.l.values, fine.index
    out, busy, skipped, n = [], -1, 0, len(O)
    for i in range(len(sig_pos)):
        i0 = sig_pos[i]
        if i0 <= busy or i0 >= n - hold - arm - 2 or not atr[i] > 0:
            continue
        if dirs is None:
            up = np.flatnonzero(Hh[i0:i0 + arm] >= Hlev[i])
            dn = np.flatnonzero(Ll[i0:i0 + arm] <= Llev[i])
            ju, jd = (up[0] if len(up) else 10 ** 9), (dn[0] if len(dn) else 10 ** 9)
            if ju == jd == 10 ** 9:
                continue
            if ju == jd:
                skipped += 1
                continue
            j = i0 + min(ju, jd)
            d = 1 if ju < jd else -1
            px = max(Hlev[i], O[j]) if d == 1 else min(Llev[i], O[j])
            if fade:
                d = -d
            first = j  # entry inside bar j: only the stop is checked on that bar (conservative)
        else:
            d, j = int(dirs[i]), i0
            if d == 0:
                continue
            px, first = O[j], -1
        stop, tgt = px - d * 1.5 * atr[i], px + d * 3 * atr[i]
        ex = None
        for q in range(j, j + hold + 1):
            hi, lo = Hh[q], Ll[q]
            if q == j + hold:
                ex = O[q]
                break
            if (d == 1 and lo <= stop) or (d == -1 and hi >= stop):
                ex = stop
                break
            if q != first and ((d == 1 and hi >= tgt) or (d == -1 and lo <= tgt)):
                ex = tgt
                break
        out.append((idx[j], d * (ex - px) / px))
        busy = q
    t = pd.DataFrame(out, columns=["time", "gross"])
    return t, skipped


def tstats(t, cost, a, b):
    s = t[(t.time >= a) & (t.time < b)]
    if len(s) < 5:
        return dict(n=int(len(s)))
    s = s.assign(net=s.gross - 2 * cost)
    return dict(n=int(len(s)), mean_bp=round(float(s.net.mean() * 1e4), 2), gross_bp=round(float(s.gross.mean() * 1e4), 2),
                t_week=round(bt.tstat_weekly(s), 2), win=round(float((s.net > 0).mean()), 3),
                per_day=round(len(s) / max(1, (s.time.max() - s.time.min()).days), 2))


def run(name, fine, cfg, res):
    f = bars15(fine)
    X, atr = features(f)
    Y = targets(f, atr, cfg["reach"])
    a0, a1, a2, a3 = [pd.Timestamp(x, tz="UTC") for x in cfg["per"]]
    ok = X.notna().all(axis=1)
    seg = {"train": ok & (f.index >= a0) & (f.index < a1), "val": ok & (f.index >= a1) & (f.index < a2),
           "final": ok & (f.index >= a2) & (f.index < a3)}
    feats = list(X.columns)
    R = dict(forecast={}, trades={}, bars={k: int(v.sum()) for k, v in seg.items()})
    preds = {}
    for tgt in [c for c in Y.columns if not c.startswith("last_")]:
        clf = not tgt.startswith("size")
        m = {k: v & Y[tgt].notna() & np.isfinite(Y[tgt]) for k, v in seg.items()}
        if m["train"].sum() < 2000 or m["final"].sum() < 500:
            continue
        yf = Y[tgt][m["final"]]
        row = dict(n_final=int(m["final"].sum()))
        for label, cols in (("model", feats), ("control", CTRL)):
            p = fit(X.loc[m["train"], cols], Y[tgt][m["train"]], X.loc[m["val"], cols], Y[tgt][m["val"]], clf)
            pf, pv = p(X.loc[m["final"], cols]), p(X.loc[m["val"], cols])
            if label == "model":
                preds[tgt] = (pd.Series(p(X.loc[ok, cols]), index=X.index[ok]), pv)
            if clf:
                row[f"auc_{label}"] = round(float(roc_auc_score(yf, pf)), 4)
                thr = np.quantile(pv, 0.75)
                row[f"top25_rate_{label}"] = round(float(yf[pf >= thr].mean()), 4)
                row[f"top25_share_{label}"] = round(float((pf >= thr).mean()), 3)
                row["err_" + label] = -(yf * np.log(np.clip(pf, 1e-6, 1)) + (1 - yf) * np.log(np.clip(1 - pf, 1e-6, 1)))
            else:
                row[f"mae_{label}"] = round(float(np.abs(yf - pf).mean()), 4)
                row["err_" + label] = np.abs(yf - pf)
        if clf:
            row["base_rate"] = round(float(yf.mean()), 4)
        else:
            lastc = "last_" + tgt.split("_")[1]
            if lastc in Y:
                row["mae_same_as_last"] = round(float(np.abs(yf - Y[lastc][m["final"]]).mean()), 4)
            row["mae_cut_vs_control_pct"] = round(100 * (1 - row["mae_model"] / row["mae_control"]), 1)
        row["t_week_model_beats_control"] = round(week_t((row.pop("err_control") - row.pop("err_model")).values, yf.index), 2)
        R["forecast"][tgt] = row
        bt.log_attempt(PLAN, f"E142 {name} forecast {tgt}", "final", dict(n=row["n_final"], mean_bp=None, t_week=row["t_week_model_beats_control"]))
        print(name, tgt, row, flush=True)

    # ---------------- trading
    step = int(round(pd.Timedelta("15min") / (fine.index[1] - fine.index[0])))
    arm, hold = 4 * step, 16 * step
    okidx = X.index[ok & (f.index >= a0) & (f.index < a3)]
    pos = fine.index.searchsorted(okidx + pd.Timedelta("15min"))
    A = atr.reindex(okidx).values
    Hl, Ll = f.h.rolling(16).max().reindex(okidx).values, f.l.rolling(16).min().reindex(okidx).values
    pw, pv = preds["big_4h"]
    watch = (pw.reindex(okidx).values >= np.quantile(pv, 0.75))
    pdir, pdv = preds["dir_4h"]
    conf_thr = np.quantile(np.abs(pdv - 0.5), 0.75)
    pd_ = pdir.reindex(okidx).values
    mdir = np.where(np.abs(pd_ - 0.5) >= conf_thr, np.sign(pd_ - 0.5), 0)
    rng = np.random.default_rng(142)
    rules = {
        "T1 watch breakout": dict(sel=watch, Hlev=Hl, Llev=Ll),
        "T2 every-bar breakout (control)": dict(sel=np.ones(len(okidx), bool), Hlev=Hl, Llev=Ll),
        "T3 watch + direction model": dict(sel=watch, dirs=mdir),
        "T4 watch random side (control)": dict(sel=watch, dirs=rng.choice([-1, 1], len(okidx))),
        "T5 watch fade the break": dict(sel=watch, Hlev=Hl, Llev=Ll, fade=True),
    }
    for rn, r in rules.items():
        s = r.pop("sel")
        kw = {k: (v[s] if isinstance(v, np.ndarray) else v) for k, v in r.items()}
        t, skipped = simulate(fine, pos[s], A[s], arm=arm, hold=hold, **kw)
        R["trades"][rn] = dict(skipped_ambiguous=skipped)
        for cn, cst in cfg["costs"].items():
            R["trades"][rn][cn] = {p: tstats(t, cst, x, y) for p, (x, y) in (("train", (a0, a1)), ("val", (a1, a2)), ("final", (a2, a3)))}
            for p in ("val", "final"):
                st = R["trades"][rn][cn][p]
                bt.log_attempt(PLAN, f"E142 {name} {rn} {cn}", p, dict(n=st.get("n"), mean_bp=st.get("mean_bp"), t_week=st.get("t_week")))
        print(name, rn, {cn: {p: (v.get("n"), v.get("gross_bp"), v.get("mean_bp"), v.get("t_week"), v.get("win")) for p, v in R["trades"][rn][cn].items()} for cn in cfg["costs"]}, flush=True)
    # WATCH facts in plain units (FINAL)
    fm = pd.Series(watch, index=okidx)[lambda s: s.index >= a2]
    mv4 = (f.h[::-1].rolling(16).max()[::-1].shift(-1) - f.l[::-1].rolling(16).min()[::-1].shift(-1)).reindex(fm.index)
    R["watch_final"] = dict(share_of_bars=round(float(fm.mean()), 3), days_with_watch=int(fm[fm].index.normalize().nunique()),
                            days=int(fm.index.normalize().nunique()),
                            median_4h_range_in_watch=round(float(mv4[fm.values].median()), 2),
                            median_4h_range_outside=round(float(mv4[~fm.values].median()), 2))
    print(name, "watch", R["watch_final"], flush=True)
    res[name] = R


def main(xau, paxg):
    res = dict(plan="edges/plans/E142_movement_forecast.md", md5=PLAN)
    btc = bt.load("BTCUSDT", "5m")[["o", "h", "l", "c", "v", "tbv"]].astype(float)
    run("BTC", btc, SETS["BTC"], res)
    run("GOLD", pd.read_parquet(xau)[["o", "h", "l", "c", "v"]].astype(float), SETS["GOLD"], res)
    run("PAXG", pd.read_parquet(paxg)[["o", "h", "l", "c", "v"]].astype(float), SETS["PAXG"], res)
    v = []
    for n in ("BTC", "GOLD", "PAXG"):
        T = res[n]["trades"]
        best = [k for k in T if "control" not in k and (T[k]["base"]["final"].get("mean_bp") or -1) > 0
                and (T[k]["base"]["final"].get("t_week") or 0) >= 2 and (T[k]["base"]["val"].get("mean_bp") or -1) > 0
                and (T[k]["base"]["val"].get("t_week") or 0) >= 1.5]
        v.append(f"{n}: trading {'PASS ' + ', '.join(best) if best else 'FAIL'}")
    res["verdict"] = "; ".join(v)
    json.dump(res, open("edges/results/E142_result.json", "w"), indent=1, default=str)
    print(res["verdict"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
