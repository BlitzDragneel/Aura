"""E101 re-run of the external handoff's gold families (plan edges/plans/E101_handoff_rerun_xau.md)."""
import sys, numpy as np, pandas as pd, lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from edges.assets.XAU.code import xlib as X
P = "E101"
PANELS = {
    "A_perp15m": dict(file="XAUUSDT_perp_15m", H=16, LB=16, split=[("train", "2025-12-11", "2026-07-01"), ("select", "2026-07-01", "2026-09-01"),
                      ("eval", "2026-09-01", "2026-11-01"), ("check", "2026-11-01", "2026-11-14")], funding=True),
    "B_paxg15m": dict(file="PAXG_15m", H=16, LB=16, split=[("train", "2020-08-28", "2024-01-01"), ("select", "2024-01-01", "2025-01-01"),
                      ("eval", "2025-01-01", "2026-11-01")], funding=False),
    "C_gc1h": dict(file="GC_1h", H=4, LB=16, split=[("train", "2024-06-24", "2025-07-01"), ("select", "2025-07-01", "2026-01-01"),
                   ("eval", "2026-01-01", "2026-11-14")], funding=False),
}


def features(df, H):
    c, h, l = df.c, df.h, df.l
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    lr = np.log(c).diff()
    F = pd.DataFrame(index=df.index)
    for k in (1, 2, 4, 8, 16, 32, 96):
        F[f"r{k}"] = np.log(c / c.shift(k))
    F["atrp"] = atr / c
    F["rv16"], F["rv96"] = lr.rolling(16).std(), lr.rolling(96).std()
    for k in (16, 96):
        hh, ll = h.rolling(k).max(), l.rolling(k).min()
        F[f"pos{k}"] = (c - ll) / (hh - ll)
    F["dist96"] = (c - c.rolling(96).mean()) / atr
    hr = df.index.hour + df.index.minute / 60
    F["hs"], F["hc"] = np.sin(2 * np.pi * hr / 24), np.cos(2 * np.pi * hr / 24)
    F["wd"] = df.index.weekday
    fwd = c.shift(-H) / c - 1
    b = np.maximum(0.0012, 0.5 * atr / c)
    y3 = pd.Series(np.where(fwd > b, 2, np.where(fwd < -b, 0, 1)), index=df.index).where(fwd.notna())
    big = (fwd.abs() > np.maximum(0.0040, 2 * atr / c)).astype(float).where(fwd.notna())
    return F, atr, y3, big


def engine(df, atr, sig, H, cps, fund=None):
    """sig: array of side per bar (signal at close of bar t). Entry at open of t+2. Returns trades DataFrame."""
    o, h, l, c, a = df.o.values, df.h.values, df.l.values, df.c.values, atr.values
    idx = df.index; n = len(df); rows = []; t = 0
    while t < n - 3:
        s = sig[t]
        if s == 0 or not np.isfinite(a[t]):
            t += 1; continue
        e = t + 2; pe = o[e]; st = pe - s * 2 * a[t]; tg = pe + s * 6 * a[t]; xp = None; mae = 0.0
        last = min(e + H - 1, n - 1)
        for k in range(e, last + 1):
            if s > 0:
                if o[k] <= st: xp = o[k]; mae = min(mae, o[k] / pe - 1); break
                mae = min(mae, l[k] / pe - 1)
                if l[k] <= st: xp = st; break
                if h[k] >= tg: xp = tg; break
            else:
                if o[k] >= st: xp = o[k]; mae = min(mae, pe / o[k] - 1); break
                mae = min(mae, pe / h[k] - 1)
                if h[k] >= st: xp = st; break
                if l[k] <= tg: xp = tg; break
        if xp is None:
            xp, k = c[last], last
        gross = s * (xp / pe - 1)
        fcost = 0.0
        if fund is not None:
            fr = fund[(fund.index > idx[e]) & (fund.index <= idx[k] + (idx[1] - idx[0]))]
            fcost = float(s * fr.sum())
        stopd = 2 * a[t] / pe
        rows.append((idx[e], idx[k], s, gross, fcost, mae, stopd, idx[t]))
        t = k + 1
    T = pd.DataFrame(rows, columns=["time", "exit_time", "side", "gross", "fund", "mae", "stopd", "sigtime"])
    T["net"] = T.gross - 2 * cps - T.fund
    T["sym"] = "XAU"
    return T


def account_pct(T, cps):
    """Handoff account view: 10,000, risk 25 incl. costs per trade, notional <= 1x, non-compounding."""
    if len(T) == 0:
        return 0.0
    notional = np.minimum(25.0 / (T.stopd + 2 * cps), 10000.0)
    return round(float((notional * (T.gross - 2 * cps - T.fund)).sum() / 10000 * 100), 3)


def families(df, atr, LB):
    c, h, l = df.c, df.h, df.l
    ph, pl = h.shift(1).rolling(LB).max(), l.shift(1).rolling(LB).min()
    up, dn = c > ph, c < pl
    brk = np.where(up, 1, np.where(dn, -1, 0))
    rng = (h.rolling(LB).max() - l.rolling(LB).min()) / atr
    comp = rng <= rng.rolling(960, min_periods=200).quantile(0.2)
    recent = comp.astype(float).rolling(8, min_periods=1).max().shift(1).fillna(0) > 0
    compb = np.where(recent, brk, 0)
    conf = np.zeros(len(df), dtype=int)
    cb = pd.Series(compb, index=df.index)
    lvl_u, lvl_d = ph.shift(1), pl.shift(1)
    conf[1:] = np.where((cb.shift(1).values[1:] == 1) & (c.values[1:] > lvl_u.values[1:]), 1,
                        np.where((cb.shift(1).values[1:] == -1) & (c.values[1:] < lvl_d.values[1:]), -1, 0))
    # accepted retest
    ret = np.zeros(len(df), dtype=int); cv, hv, lv = c.values, h.values, l.values
    phv, plv = ph.values, pl.values
    for i in np.where(brk != 0)[0]:
        L = phv[i] if brk[i] > 0 else plv[i]
        for j in range(i + 1, min(i + 9, len(df))):
            if brk[i] > 0 and lv[j] <= L and cv[j] > L:
                ret[j] = 1; break
            if brk[i] < 0 and hv[j] >= L and cv[j] < L:
                ret[j] = -1; break
    # failed auction
    a = atr.values; rngb = hv - lv; loc = (cv - lv) / np.where(rngb > 0, rngb, np.nan)
    fa_s = (hv >= phv + 0.1 * a) & (cv < phv) & (rngb >= 1.5 * a) & (loc <= 0.4)
    fa_l = (lv <= plv - 0.1 * a) & (cv > plv) & (rngb >= 1.5 * a) & (loc >= 0.6)
    fa = np.where(fa_l, 1, np.where(fa_s, -1, 0))
    return {"price_breakout": brk, "compression": compb, "compression_confirm": conf, "accepted_retest": ret, "failed_auction": fa}


def run_panel(name, cfg):
    df = X.bars(cfg["file"])[["o", "h", "l", "c"]].dropna()
    H, LB = cfg["H"], cfg["LB"]
    F, atr, y3, big = features(df, H)
    fund = None
    if cfg["funding"]:
        fund = pd.read_parquet(f"{X.D}/XAUUSDT_funding.parquet").rate
    per = {k: (pd.Timestamp(a, tz="UTC"), pd.Timestamp(b, tz="UTC")) for k, a, b in cfg["split"]}
    m = {k: (df.index >= a) & (df.index < b) for k, (a, b) in per.items()}
    out = {"panel": name, "bars": len(df), "periods": {k: [str(a), str(b)] for k, (a, b) in per.items()}}
    ok = F.notna().all(1)
    # ---- 1. learned price-only direction model
    trm = m["train"] & ok & y3.notna()
    trm &= df.index < per["train"][1] - pd.Timedelta(hours=H)
    mdl = lgb.LGBMClassifier(objective="multiclass", num_leaves=15, n_estimators=200, learning_rate=0.03, min_child_samples=200,
                             random_state=0, n_jobs=2, verbose=-1)
    mdl.fit(F[trm], y3[trm].astype(int))
    pr = pd.DataFrame(mdl.predict_proba(F.fillna(0)), index=df.index, columns=[0, 1, 2])
    pr[~ok] = np.nan

    def model_sig(q, mask):
        s = np.where((pr[2] >= q) & (pr[2] >= pr[0]), 1, np.where((pr[0] >= q) & (pr[0] > pr[2]), -1, 0))
        return np.where(mask, s, 0)

    res = {}
    sel = {}
    for q in (0.40, 0.45, 0.50, 0.55, 0.60):
        T = engine(df, atr, model_sig(q, m["select"]), H, 0.0006, fund)
        sel[q] = (len(T), float(T.net.sum()) if len(T) else -9)
        X.log(P, f"{name} price_model q{q}", "select", dict(n=len(T), mean_bp=round(T.net.mean() * 1e4, 2) if len(T) else None))
    cand = [q for q in sel if sel[q][0] >= 10] or list(sel)
    q = max(cand, key=lambda k: sel[k][1])
    out["price_model_q_select"] = {str(k): [v[0], round(v[1] * 1e4, 1)] for k, v in sel.items()}
    out["price_model_q"] = q
    sigs = {"price_model": lambda mask: model_sig(q, mask)}
    for k, s in families(df, atr, LB).items():
        sigs[k] = (lambda mask, s=s: np.where(mask, s, 0))
    for per_name in [p for p in per if p != "train"]:
        for fam, fn in sigs.items():
            T = engine(df, atr, fn(m[per_name]), H, 0.0006, fund)
            r = dict(n=len(T), acct_pct_6bp=account_pct(T, 0.0006), acct_pct_12bp=account_pct(T, 0.0012),
                     gross_bp=round(T.gross.mean() * 1e4, 2) if len(T) else None,
                     breakeven_bp_side=round(T.gross.mean() * 1e4 / 2, 2) if len(T) else None)
            if len(T) >= 3:
                Tc = T.copy(); Tc["net"] = Tc.gross - 2 * X.SPREAD - Tc.fund
                r["cfd_mean_bp"] = round(Tc.net.mean() * 1e4, 2); r["cfd_t_week"] = round(X.bt.tstat_weekly(Tc), 2)
                r["handoff_cost_t_week"] = round(X.bt.tstat_weekly(T), 2)
            res.setdefault(per_name, {})[fam] = r
            X.log(P, f"{name} {fam}", per_name, dict(n=r["n"], mean_bp=r.get("cfd_mean_bp"), t_week=r.get("cfd_t_week")))
    out["families"] = res
    # ---- 2. movement-timing watch vs volatility/clock control
    bm = m["train"] & ok & big.notna() & (df.index < per["train"][1] - pd.Timedelta(hours=H))
    wm = lgb.LGBMClassifier(objective="binary", num_leaves=15, n_estimators=200, learning_rate=0.03, min_child_samples=200,
                            random_state=0, n_jobs=2, verbose=-1).fit(F[bm], big[bm].astype(int))
    pw = pd.Series(wm.predict_proba(F.fillna(0))[:, 1], index=df.index)
    G = pd.DataFrame(dict(atrp=F.atrp, rv16=F.rv16, rv96=F.rv96), index=df.index)
    G = pd.concat([G, pd.get_dummies(df.index.hour, prefix="h").set_index(df.index).astype(float),
                   pd.get_dummies(df.index.weekday, prefix="d").set_index(df.index).astype(float)], axis=1)
    mu, sd = G[bm].mean(), G[bm].std().replace(0, 1)
    Gz = ((G - mu) / sd).fillna(0)
    ctl = LogisticRegression(max_iter=2000).fit(Gz[bm], big[bm].astype(int))
    pc = pd.Series(ctl.predict_proba(Gz)[:, 1], index=df.index)
    thr = float(np.nanpercentile(pw[m["select"] & ok], 75))
    thr_c = float(np.nanpercentile(pc[m["select"] & ok], 75))
    wt = {}
    for per_name in [p for p in per if p != "train"]:
        mm = m[per_name] & ok & big.notna()
        yy = big[mm].astype(int)
        if yy.nunique() < 2:
            continue
        wt[per_name] = dict(base_rate=round(float(yy.mean()), 3), watch_rate=round(float(yy[pw[mm] >= thr].mean()), 3),
                            control_watch_rate=round(float(yy[pc[mm] >= thr_c].mean()), 3),
                            logloss_model=round(log_loss(yy, pw[mm].clip(1e-6, 1 - 1e-6)), 4),
                            logloss_control=round(log_loss(yy, pc[mm].clip(1e-6, 1 - 1e-6)), 4), n=int(mm.sum()))
    out["movement_watch"] = wt
    # ---- 7. NY 08-12 opportunities: model vs constant short on the same signal bars; constant short/long each 08:00 NY
    lt = df.index.tz_convert(X.NY)
    ny = (lt.hour >= 8) & (lt.hour < 12)
    ny8 = (lt.hour == 8) & (lt.minute == 0)
    nyres = {}
    for per_name in [p for p in per if p not in ("train",)]:
        ms = model_sig(q, m[per_name] & ny)
        T1 = engine(df, atr, ms, H, 0.0006, fund)
        T2 = engine(df, atr, np.where(ms != 0, -1, 0), H, 0.0006, fund)
        T3 = engine(df, atr, np.where(m[per_name] & ny8, -1, 0), H, 0.0006, fund)
        T4 = engine(df, atr, np.where(m[per_name] & ny8, 1, 0), H, 0.0006, fund)
        nyres[per_name] = {"model_in_ny0812": [len(T1), account_pct(T1, 0.0006)], "const_short_same_bars": [len(T2), account_pct(T2, 0.0006)],
                           "const_short_every_0800": [len(T3), account_pct(T3, 0.0006)], "const_long_every_0800": [len(T4), account_pct(T4, 0.0006)]}
    out["ny0812"] = nyres
    # ---- 8. weekends flat share
    lab = y3.dropna()
    wkend = lab.index.weekday >= 5
    if wkend.any():
        out["flat_share"] = dict(weekend=round(float((lab[wkend] == 1).mean()), 3), weekday=round(float((lab[~wkend] == 1).mean()), 3),
                                 weekend_share_of_windows=round(float(wkend.mean()), 3))
    return out


def main(which):
    res = {"plan": P, "md5": X.MD5[P], "panels": {}}
    for name, cfg in PANELS.items():
        if which != "all" and not name.startswith(which):
            continue
        r = run_panel(name, cfg)
        res["panels"][name] = r
        print(name, "q", r["price_model_q"], flush=True)
        for pn, fams in r["families"].items():
            for f, v in fams.items():
                print(f"  {pn:7s} {f:20s} {v}", flush=True)
        print("  watch", r["movement_watch"]); print("  ny", r["ny0812"]); print("  flat", r.get("flat_share"), flush=True)
        X.dump(f"E101_{name}", res["panels"][name])
    if which == "all":
        X.dump(P, res)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
