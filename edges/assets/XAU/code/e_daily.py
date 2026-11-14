"""Daily gold plans E108-E112 (swing + hold), GC=F settlement closes. Plans in edges/plans/E108..E112_*.md."""
import sys, numpy as np, pandas as pd
from edges.assets.XAU.code import xlib as X

C = X.daily_close("GC_1d")
C = C[C.index >= "2000-08-30"]
R = C.pct_change()
DAYS = pd.Series(C.index, index=C.index).diff().dt.days.shift(-1).fillna(1)      # calendar nights until the next settle
IRX = X.daily_close("IRX_1d").reindex(C.index, method="ffill") / 100
CASH = (IRX * DAYS / 360).shift(1).reindex(C.index).fillna(0)                      # T-bill accrual earned over day t (set at t-1)
DXY = X.daily_close("DXY_1d").reindex(C.index, method="ffill")
TNX = X.daily_close("TNX_1d").reindex(C.index, method="ffill")
PD = X.PER_D
YRS = 252


def book(w, cost=0.0005, fin=False, cash=False, mult=1.0, lag=0):
    """w: exposure decided at settle t (index t). Earns r_{t+1}. Returns daily net series indexed by the day the return is earned."""
    w = w.reindex(C.index).fillna(0.0).shift(lag)
    turn = w.diff().abs().fillna(w.abs())
    nxt = R.shift(-1)
    pnl = w * nxt - mult * cost * turn
    if fin:
        pnl -= mult * X.FIN * w.abs() * DAYS
    if cash:
        pnl += (1 - w.clip(0, 1)) * CASH.shift(-1)
    return pnl.shift(1).dropna()


def cut(s, p):
    a, b = PD[p]
    return s[(s.index >= a) & (s.index < b)]


def st(x):
    x = x.dropna()
    if len(x) < 30 or x.std() == 0:
        return dict(n=len(x))
    eq = (1 + x).cumprod()
    yrs = x.groupby(x.index.year).sum()
    return dict(n=int(len(x)), mean_bp=round(x.mean() * 1e4, 3), t_nw=round(X.nw_t(x), 2), sharpe=round(float(x.mean() / x.std() * np.sqrt(YRS)), 2),
                cagr=round(float(eq.iloc[-1] ** (YRS / len(x)) - 1), 4), max_dd=round(float((eq / eq.cummax() - 1).min()), 3),
                years_pos=int((yrs > 0).sum()), years_total=int(len(yrs)), total=round(float(eq.iloc[-1] - 1), 3))


def elig(s):
    return s.get("t_nw", -9) >= 2 and s["mean_bp"] > 0 and s["years_pos"] >= np.ceil(0.6 * s["years_total"])


def evol(hl=20):
    return np.sqrt((R ** 2).ewm(halflife=hl, min_periods=20).mean() * YRS)


def shift_series(s, k):
    v = s.values
    return pd.Series(np.roll(v, k), index=s.index)


def select_validate_final(plan, W, out, fin=True, cash=False, null_fn=None):
    """Generic discovery -> luck -> validation -> FINAL for a dict of exposure series W."""
    for k, w in W.items():
        s = st(cut(book(w, fin=fin, cash=cash), "discovery")); out["discovery"][k] = s; X.log(plan, k, "discovery", s)
        print(plan, k, s, flush=True)
    best = max(s.get("t_nw", -9) for s in out["discovery"].values())
    if null_fn is not None:
        nb = null_fn()
        out["luck"] = dict(real_best_t=best, null_p95=round(float(np.percentile(nb, 95)), 2), null_p99=round(float(np.percentile(nb, 99)), 2))
        print("luck", out["luck"], flush=True)
    el = sorted([k for k, s in out["discovery"].items() if elig(s)], key=lambda k: -out["discovery"][k]["t_nw"])[:2]
    out["eligible_promoted"] = el
    if el and null_fn is not None and best < out["luck"]["null_p95"]:
        out["verdict"] = "FAIL (luck check)"; return out, None
    for k in el:
        s = st(cut(book(W[k], fin=fin, cash=cash), "validation")); out["validation"][k] = s; X.log(plan, k, "validation", s); print("VAL", k, s)
    ok = [k for k in el if out["validation"][k]["mean_bp"] > 0 and out["validation"][k]["t_nw"] >= 1.5]
    if not ok:
        out["verdict"] = "FAIL (nothing eligible)" if not el else "FAIL (validation)"; return out, None
    ch = max(ok, key=lambda k: out["validation"][k]["t_nw"]); out["chosen"] = ch
    f = st(cut(book(W[ch], fin=fin, cash=cash), "final")); f["stress"] = st(cut(book(W[ch], fin=fin, cash=cash, mult=2), "final"))
    f["lag1"] = st(cut(book(W[ch], fin=fin, cash=cash, lag=1), "final"))
    out["final"][ch] = f; X.log(plan, ch, "final", f); print("FINAL", ch, f)
    return out, ch


# ------------------------------------------------------------------ E108 TSMOM
def e108():
    P = "E108"; out = {"plan": P, "md5": X.MD5[P], "discovery": {}, "validation": {}, "final": {}}
    scale = (0.10 / evol()).clip(upper=1.0)
    sig = {L: np.sign(C / C.shift(L) - 1) for L in (5, 10, 20, 60, 120, 250)}
    W = {}
    for L, s in sig.items():
        W[f"L{L}_LS"] = s * scale
        W[f"L{L}_LF"] = s.clip(lower=0) * scale
    rng = np.random.default_rng(8)

    def null():
        dmask = (C.index >= PD["discovery"][0]) & (C.index < PD["discovery"][1])
        nxt = R.shift(-1); res = []
        for i in range(500):
            k = int(rng.integers(250, len(C) - 250)); b = -9
            for L, s in sig.items():
                ss = shift_series(s, k)
                for mode in ("LS", "LF"):
                    w = (ss if mode == "LS" else ss.clip(lower=0)) * scale
                    x = book(w, fin=True); x = x[(x.index >= PD["discovery"][0]) & (x.index < PD["discovery"][1])]
                    b = max(b, X.nw_t(x))
            res.append(b)
        return res
    out, ch = select_validate_final(P, W, out, fin=True, null_fn=null)
    out["reference"] = {p: {"BH_vol10_longonly": st(cut(book(scale, fin=True), p)), "BH_cfd": st(cut(book(pd.Series(1.0, index=C.index), fin=True), p)),
                            "BH_unfunded": st(cut(book(pd.Series(1.0, index=C.index)), p))} for p in PD}
    if ch:
        # FINAL control: its own shifted nulls (mean), real must exceed 95th pct
        L = int(ch.split("_")[0][1:]); mode = ch.split("_")[1]; m = []
        for i in range(500):
            ss = shift_series(sig[L], int(rng.integers(250, len(C) - 250)))
            w = (ss if mode == "LS" else ss.clip(lower=0)) * scale
            m.append(cut(book(w, fin=True), "final").mean())
        out["final"][ch]["shift_control_p95_bp"] = round(float(np.percentile(m, 95)) * 1e4, 3)
    X.dump(P, out); print(out.get("verdict", "see final"))


# ------------------------------------------------------------------ E109 shocks
def e109():
    P = "E109"; out = {"plan": P, "md5": X.MD5[P], "discovery": {}, "validation": {}, "final": {}}
    sd = R.rolling(20).std().shift(1)

    def events(k, side):
        return (R > k * sd) if side == "UP" else (R < -k * sd)

    def expo(ev, mode, H, side):
        """Exposure series: from settle t of the event, hold H days; overlapping events skipped."""
        d = 1 if side == "UP" else -1
        d = d if mode == "FOLLOW" else -d
        w = np.zeros(len(C)); e = np.where(ev.fillna(False).values)[0]; busy = -1
        for i in e:
            if i <= busy:
                continue
            w[i:i + H] = d; busy = i + H - 1
        return pd.Series(w, index=C.index)
    W = {}
    for k in (2, 3):
        for side in ("UP", "DOWN"):
            ev = events(k, side)
            for mode in ("FOLLOW", "FADE"):
                for H in (1, 3, 5, 10):
                    W[f"K{k}_{side}_{mode}_H{H}"] = expo(ev, mode, H, side)
    for k in W:
        pass
    rng = np.random.default_rng(9)

    def null():
        res = []
        dd = np.arange(len(C))
        for i in range(200):
            b = -9
            for k in (2, 3):
                for side in ("UP", "DOWN"):
                    n_ev = int(events(k, side).sum())
                    pe = pd.Series(False, index=C.index); pe.iloc[rng.choice(dd[25:-12], n_ev, replace=False)] = True
                    for mode in ("FOLLOW", "FADE"):
                        for H in (1, 3, 5, 10):
                            x = cut(book(expo(pe, mode, H, side), fin=True), "discovery")
                            if (x != 0).sum() > 10:
                                b = max(b, X.nw_t(x[x != 0]))
            res.append(b)
        return res
    # per-variant stats on ACTIVE days only (flat days carry no information) -> st() on days with exposure
    for kname, w in W.items():
        x = cut(book(w, fin=True), "discovery"); xa = x[w.reindex(x.index).shift(1).fillna(0) != 0]
        s = st(xa); s["events"] = int((w.diff().abs() > 0).sum() // 2); out["discovery"][kname] = s; X.log(P, kname, "discovery", s)
        print(P, kname, s, flush=True)
    best = max(s.get("t_nw", -9) for s in out["discovery"].values())
    nb = null(); out["luck"] = dict(real_best_t=best, null_p95=round(float(np.percentile(nb, 95)), 2))
    print("luck", out["luck"])
    el = sorted([k for k, s in out["discovery"].items() if elig(s)], key=lambda k: -out["discovery"][k]["t_nw"])[:2]
    out["eligible_promoted"] = el
    if el and best < out["luck"]["null_p95"]:
        out["verdict"] = "FAIL (luck check)"; el = []
    ok = []
    for kname in el:
        w = W[kname]; x = cut(book(w, fin=True), "validation"); s = st(x[w.reindex(x.index).shift(1).fillna(0) != 0])
        out["validation"][kname] = s; X.log(P, kname, "validation", s); print("VAL", kname, s)
        if s.get("mean_bp", -1) > 0 and s.get("t_nw", 0) >= 1.5:
            ok.append(kname)
    if ok:
        ch = max(ok, key=lambda k: out["validation"][k]["t_nw"]); w = W[ch]; out["chosen"] = ch
        x = cut(book(w, fin=True), "final"); f = st(x[w.reindex(x.index).shift(1).fillna(0) != 0])
        xs = cut(book(w, fin=True, mult=2), "final"); f["stress"] = st(xs[w.reindex(xs.index).shift(1).fillna(0) != 0])
        out["final"][ch] = f; X.log(P, ch, "final", f); print("FINAL", f)
    out.setdefault("verdict", "FAIL (nothing eligible)" if not el else ("FAIL (validation)" if not ok else "see final"))
    X.dump(P, out); print(out["verdict"])


# ------------------------------------------------------------------ E110 USD / rates
def e110():
    P = "E110"; out = {"plan": P, "md5": X.MD5[P], "discovery": {}, "validation": {}, "final": {}}
    W, raw = {}, {}
    for N in (50, 100, 200):
        s = np.sign(DXY.rolling(N).mean() - DXY).shift(1)          # +1 when the dollar is below its mean; extra 1-day lag
        raw[f"D_MA{N}"] = s
        W[f"D_MA{N}_LF"] = s.clip(lower=0); W[f"D_MA{N}_LS"] = s
    for N in (20, 60):
        s = -np.sign(TNX - TNX.shift(N)).shift(1)
        raw[f"R_CHG{N}"] = s
        W[f"R_CHG{N}_LF"] = s.clip(lower=0); W[f"R_CHG{N}_LS"] = s
    rng = np.random.default_rng(10)

    def null():
        res = []
        for i in range(500):
            k = int(rng.integers(250, len(C) - 250)); b = -9
            for nm, s in raw.items():
                ss = shift_series(s.fillna(0), k)
                for w in (ss.clip(lower=0), ss):
                    b = max(b, X.nw_t(cut(book(w, fin=True), "discovery")))
            res.append(b)
        return res
    out, ch = select_validate_final(P, W, out, fin=True, null_fn=null)
    out["reference"] = {p: st(cut(book(pd.Series(1.0, index=C.index), fin=True), p)) for p in PD}
    X.dump(P, out); print(out.get("verdict", "see final"))


# ------------------------------------------------------------------ E111 hold controllers
def part(lbs):
    return sum((C / C.shift(k) - 1 > 0).astype(float) for k in lbs) / len(lbs)


def vscale(tv):
    lr = np.log(C).diff()
    v = np.maximum(lr.rolling(20).std(), lr.rolling(60).std()) * np.sqrt(YRS)
    return (tv / v).clip(upper=1.0)


def monthly_hold(sig_month_end):
    """Signal evaluated at month-end closes, held for the next month."""
    me = C.groupby([C.index.year, C.index.month]).tail(1).index
    s = pd.Series(np.nan, index=C.index); s.loc[me] = sig_month_end.reindex(me).values
    return s.ffill()


def thresh(w, th=0.10):
    w = w.fillna(0).values; o = np.zeros_like(w); cur = 0.0
    for i, x in enumerate(w):
        if abs(x - cur) >= th or (x == 0 and cur != 0):
            cur = x
        o[i] = cur
    return pd.Series(o, index=C.index)


def e111():
    P = "E111"; out = {"plan": P, "md5": X.MD5[P], "periods": {}}
    sma200 = (C > C.rolling(200).mean()).astype(float)
    m10 = C.groupby([C.index.year, C.index.month]).transform("last")
    me_close = C.groupby([C.index.year, C.index.month]).tail(1)
    faber = (me_close > me_close.rolling(10).mean()).astype(float)
    mom121 = ((me_close.shift(1) / me_close.shift(12) - 1) > 0).astype(float)
    cash12 = (IRX.rolling(252).mean())
    dual = ((C / C.shift(252) - 1) > cash12).astype(float)
    sig = {"V1": (sma200, None), "V2": (monthly_hold(faber), None), "V3": (monthly_hold(mom121), None),
           "V4": (part((60, 120, 250)), 0.10), "V5": (part((20, 60, 120)), 0.15), "V6": (part((60, 120, 250)), 0.15),
           "V7": (sma200, 0.15), "V8": (dual, None), "E85": (part((20, 60, 120)), 0.10)}
    W = {k: thresh(s * (vscale(tv) if tv else 1.0)) for k, (s, tv) in sig.items()}
    BH = pd.Series(1.0, index=C.index)
    VO = {None: BH, 0.10: thresh(vscale(0.10)), 0.15: thresh(vscale(0.15))}
    rng = np.random.default_rng(11)
    for p in PD:
        rows = {"buy_hold": st(cut(book(BH, cash=True), p)), "buy_hold_CFD": st(cut(book(BH, fin=True), p)),
                "vol_only_10": st(cut(book(VO[0.10], cash=True), p)), "vol_only_15": st(cut(book(VO[0.15], cash=True), p))}
        for k, w in W.items():
            rows[k] = st(cut(book(w, cash=True), p)); rows[k]["avg_exposure"] = round(float(cut(w, p).mean()), 2)
            rows[k]["stress"] = st(cut(book(w, cash=True, mult=2), p)).get("sharpe")
            X.log(P, k, p, rows[k])
        out["periods"][p] = rows
        print(p, {k: (v.get("sharpe"), v.get("cagr"), v.get("max_dd")) for k, v in rows.items()}, flush=True)
    # luck: discovery Sharpe gain over matched vol-only vs shifted trend signal (300)
    luck = {}
    for k, (s, tv) in sig.items():
        if k == "E85":
            continue
        base = out["periods"]["discovery"]["vol_only_" + ("10" if tv == 0.10 else "15") if tv else "buy_hold"]["sharpe"]
        real = out["periods"]["discovery"][k]["sharpe"] - base
        g = []
        for i in range(300):
            ss = shift_series(s.fillna(0), int(rng.integers(250, len(C) - 250)))
            w = thresh(ss * (vscale(tv) if tv else 1.0))
            g.append(st(cut(book(w, cash=True), "discovery"))["sharpe"] - base)
        luck[k] = dict(real_gain=round(real, 3), null_p95=round(float(np.percentile(g, 95)), 3))
        print("luck", k, luck[k], flush=True)
    out["luck"] = luck
    ver = {}
    for k, (s, tv) in sig.items():
        vo = "vol_only_" + ("10" if tv == 0.10 else "15") if tv else "buy_hold"
        ok = all(out["periods"][p][k]["sharpe"] > out["periods"][p]["buy_hold"]["sharpe"] and out["periods"][p][k]["sharpe"] > out["periods"][p][vo]["sharpe"]
                 and out["periods"][p][k]["max_dd"] > 0.75 * out["periods"][p]["buy_hold"]["max_dd"] for p in ("validation", "final"))
        lk = luck.get(k, {}).get("real_gain", -9) >= luck.get(k, {}).get("null_p95", 9)
        ver[k] = ("PASS" if ok and lk else "FAIL") + f" (val+final criteria {'met' if ok else 'not met'}; luck {'ok' if lk else 'fails'})"
    out["verdicts"] = ver; print(ver)
    X.dump(P, out)


# ------------------------------------------------------------------ E112 seasonality
def e112():
    P = "E112"; out = {"plan": P, "md5": X.MD5[P], "describe": {}, "rules": {}}
    d = cut(R, "discovery").dropna()
    mon = d.groupby(d.index.month).agg(["mean", "count"]); out["describe"]["month_mean_bp_discovery"] = {int(m): round(v * 1e4, 2) for m, v in mon["mean"].items()}
    dow = d.groupby(d.index.weekday).mean(); out["describe"]["weekday_mean_bp_discovery"] = {int(k): round(v * 1e4, 2) for k, v in dow.items()}
    for p in ("validation", "final"):
        x = cut(R, p)
        out["describe"][f"month_mean_bp_{p}"] = {int(m): round(v * 1e4, 2) for m, v in x.groupby(x.index.month).mean().items()}
    best6 = list(mon["mean"].sort_values().index[-6:]); best3 = list(mon["mean"].sort_values().index[-3:])
    out["best6"], out["best3"] = [int(m) for m in best6], [int(m) for m in best3]
    # "on" flags refer to the day the return is EARNED (t+1); exposure at t = flag of next trading day
    nxt_idx = pd.Series(C.index, index=C.index).shift(-1)
    nm = nxt_idx.dt.month; nwd = nxt_idx.dt.weekday
    pos = pd.Series(np.arange(len(C)), index=C.index)
    g = C.groupby([C.index.year, C.index.month])
    k_from_start = g.cumcount(); k_from_end = g.cumcount(ascending=False)
    tom_day = (k_from_start < 3) | (k_from_end < 2)
    tom_next = tom_day.shift(-1).fillna(False)
    bestwd = int(dow.idxmax())
    flags = {"S1_best6": nm.isin(best6), "S2_best3": nm.isin(best3), "S3_AugFeb": nm.isin([8, 9, 10, 11, 12, 1, 2]),
             "S4_TOM": tom_next.astype(bool), f"S5_weekday{bestwd}": (nwd == bestwd)}
    rng = np.random.default_rng(12)
    for k, f in flags.items():
        w = f.astype(float)
        res = {}
        for p in PD:
            on = cut(R, p)[cut(f.shift(1).fillna(False).astype(bool), p)]   # earned on "on" days
            off = cut(R, p)[~cut(f.shift(1).fillna(False).astype(bool), p)]
            diff = pd.concat([on, -off * (len(on) / max(1, len(off)))]).sort_index()
            res[p] = dict(rule=st(cut(book(w, cash=True), p)), buy_hold=st(cut(book(pd.Series(1.0, index=C.index), cash=True), p)).get("sharpe"),
                          on_mean_bp=round(on.mean() * 1e4, 2), off_mean_bp=round(off.mean() * 1e4, 2),
                          on_minus_off_t=round(float((on.mean() - off.mean()) / np.sqrt(on.var() / len(on) + off.var() / len(off))), 2))
            X.log(P, k, p, dict(n=res[p]["rule"].get("n"), mean_bp=res[p]["on_mean_bp"], t_week=res[p]["on_minus_off_t"]))
        out["rules"][k] = res
        print(k, {p: (r["rule"].get("sharpe"), r["buy_hold"], r["on_mean_bp"], r["off_mean_bp"], r["on_minus_off_t"]) for p, r in res.items()}, flush=True)
    # luck for S1/S2: permute month labels within each year (500), recompute discovery on-off t of the best-k months
    yrs = d.index.year; mons = d.index.month
    nb6, nb3 = [], []
    for i in range(500):
        perm = {y: dict(zip(range(1, 13), rng.permutation(np.arange(1, 13)))) for y in np.unique(yrs)}
        pm = np.array([perm[y][m] for y, m in zip(yrs, mons)])
        mm = pd.Series(d.values).groupby(pm).mean().sort_values()
        for kk, store in ((6, nb6), (3, nb3)):
            sel = np.isin(pm, mm.index[-kk:]); on, off = d.values[sel], d.values[~sel]
            store.append((on.mean() - off.mean()) / np.sqrt(on.var() / len(on) + off.var() / len(off)))
    out["luck"] = dict(S1_real=out["rules"]["S1_best6"]["discovery"]["on_minus_off_t"], S1_null_p95=round(float(np.percentile(nb6, 95)), 2),
                       S2_real=out["rules"]["S2_best3"]["discovery"]["on_minus_off_t"], S2_null_p95=round(float(np.percentile(nb3, 95)), 2))
    print("luck", out["luck"])
    v = {}
    for k, res in out["rules"].items():
        ok = all(res[p]["rule"].get("sharpe", -9) > res[p]["buy_hold"] for p in ("validation", "final")) and res["final"]["on_minus_off_t"] >= 2 \
            and res["validation"]["on_minus_off_t"] >= 1.5
        v[k] = "PASS" if ok else "FAIL"
    out["verdicts"] = v; print(v)
    X.dump(P, out)




# ------------------------------------------------------------------ E113 vol-managed holding (contaminated, grade C max)
def e113():
    P = "E113"; out = {"plan": P, "md5": X.MD5[P], "periods": {}}
    BH = pd.Series(1.0, index=C.index)
    lr = np.log(C).diff()
    vmax = np.maximum(lr.rolling(20).std(), lr.rolling(60).std()) * np.sqrt(YRS)

    def rule(v, tv=0.10):
        return thresh((tv / v).clip(upper=1.0))

    def exs(x):                                     # excess over cash
        return x - CASH.reindex(x.index).fillna(0)

    def sh(x):
        x = x.dropna(); return float(x.mean() / x.std() * np.sqrt(YRS))
    W = {"VT10": rule(vmax), "VT15": rule(vmax, 0.15)}
    for p in PD:
        rows = {"buy_hold": st(cut(book(BH, cash=True), p))}
        rows["buy_hold"]["excess_sharpe"] = round(sh(exs(cut(book(BH, cash=True), p))), 2)
        rows["buy_hold_CFD"] = st(cut(book(BH, fin=True), p))
        for k, w in W.items():
            x = cut(book(w, cash=True), p); rows[k] = st(x); rows[k]["excess_sharpe"] = round(sh(exs(x)), 2)
            rows[k]["avg_exposure"] = round(float(cut(w, p).mean()), 2)
            rows[k]["lag1_excess_sharpe"] = round(sh(exs(cut(book(w, cash=True, lag=1), p))), 2)
            rows[k]["stress_excess_sharpe"] = round(sh(exs(cut(book(w, cash=True, mult=2), p))), 2)
            rows[k]["CFD_financed"] = st(cut(book(w, fin=True), p))
            X.log(P, k, p, dict(n=rows[k]["n"], mean_bp=rows[k]["mean_bp"], t_week=rows[k]["excess_sharpe"]))
        out["periods"][p] = rows
        print(p, {k: (v.get("excess_sharpe"), v.get("sharpe"), v.get("cagr"), v.get("max_dd")) for k, v in rows.items()}, flush=True)
    rng = np.random.default_rng(13)
    real = out["periods"]["discovery"]["VT10"]["excess_sharpe"] - out["periods"]["discovery"]["buy_hold"]["excess_sharpe"]
    g = []
    for i in range(500):
        vs = shift_series(vmax.bfill(), int(rng.integers(250, len(C) - 250)))
        g.append(sh(exs(cut(book(rule(vs), cash=True), "discovery"))) - out["periods"]["discovery"]["buy_hold"]["excess_sharpe"])
    out["luck"] = dict(real_gain=round(real, 3), null_p95=round(float(np.percentile(g, 95)), 3))
    # whole-sample block bootstrap of the excess-Sharpe difference
    a = exs(book(W["VT10"], cash=True)).dropna(); b = exs(book(BH, cash=True)).reindex(a.index).dropna(); a = a.reindex(b.index)
    av, bv = a.values, b.values; n = len(av); d0 = sh(a) - sh(b); bs = []
    for i in range(2000):
        st_ = rng.integers(0, n - 20, n // 20 + 1); ix = (st_[:, None] + np.arange(20)[None, :]).ravel()[:n]
        xa, xb = av[ix], bv[ix]
        bs.append(xa.mean() / xa.std() - xb.mean() / xb.std())
    bs = np.array(bs) * np.sqrt(YRS)
    out["bootstrap"] = dict(diff=round(d0, 3), p_one_sided=round(float((bs - bs.mean() + d0 <= 0).mean()), 4), ci90=[round(float(np.percentile(bs, 5)), 3), round(float(np.percentile(bs, 95)), 3)])
    crit = all(out["periods"][p]["VT10"]["excess_sharpe"] > out["periods"][p]["buy_hold"]["excess_sharpe"] and
               out["periods"][p]["VT10"]["max_dd"] > 0.75 * out["periods"][p]["buy_hold"]["max_dd"] for p in ("validation", "final"))
    out["verdict"] = (f"criteria {'met' if crit else 'not met'}; luck {'ok' if real >= out['luck']['null_p95'] else 'fails'}; "
                      "contaminated (seen as E85/E111 control) -> grade C at most, never PASS")
    print(out["luck"], out["bootstrap"], out["verdict"])
    X.dump(P, out)




# ------------------------------------------------------------------ E115 rotation gold / silver / cash
def e115():
    P = "E115"; out = {"plan": P, "md5": X.MD5[P], "periods": {}}
    S = X.daily_close("SI_1d").reindex(C.index, method="ffill")
    RS = S.pct_change()
    me = C.groupby([C.index.year, C.index.month]).tail(1).index
    cashacc = (1 + CASH).cumprod()

    def choice(L):
        g = C.loc[me] / C.loc[me].shift(L) - 1; s = S.loc[me] / S.loc[me].shift(L) - 1
        c = cashacc.loc[me] / cashacc.loc[me].shift(L) - 1
        ch = pd.Series(np.where((g >= s) & (g > c), 1, np.where((s > g) & (s > c), 2, 0)), index=me).where(g.notna() & s.notna())
        return ch

    def run(ch, mult=1.0):
        d = pd.Series(np.nan, index=C.index); d.loc[ch.index] = ch.values; d = d.ffill().fillna(0)
        wg, ws = (d == 1).astype(float), (d == 2).astype(float)
        turn = wg.diff().abs().fillna(wg) + ws.diff().abs().fillna(ws)
        pnl = wg * R.shift(-1) + ws * RS.shift(-1) + (1 - wg - ws) * CASH.shift(-1) - mult * 0.0005 * turn
        return pnl.shift(1).dropna()

    def fifty():
        pnl = 0.5 * R.shift(-1) + 0.5 * RS.shift(-1)
        return pnl.shift(1).dropna() - 0.0005 * 0.0          # monthly rebalancing cost negligible, ignored (favours the control)
    CH = {f"L{L}": choice(L) for L in (3, 6, 12)}
    BH = book(pd.Series(1.0, index=C.index), cash=True)
    for p in PD:
        rows = {"gold_BH": st(cut(BH, p)), "silver_BH": st(cut(RS.dropna(), p)), "gold_silver_5050": st(cut(fifty(), p))}
        for k, ch in CH.items():
            rows[k] = st(cut(run(ch), p)); rows[k]["stress_sharpe"] = st(cut(run(ch, 2.0), p)).get("sharpe")
            cc = ch[(ch.index >= PD[p][0]) & (ch.index < PD[p][1])]
            rows[k]["months_gold_silver_cash"] = [int((cc == 1).sum()), int((cc == 2).sum()), int((cc == 0).sum())]
            X.log(P, k, p, dict(n=rows[k]["n"], mean_bp=rows[k]["mean_bp"], t_week=rows[k]["sharpe"]))
        out["periods"][p] = rows
        print(p, {k: (v.get("sharpe"), v.get("cagr"), v.get("max_dd")) for k, v in rows.items()}, flush=True)
    rng = np.random.default_rng(15); luck = {}
    for k, ch in CH.items():
        real = out["periods"]["discovery"][k]["sharpe"] - out["periods"]["discovery"]["gold_BH"]["sharpe"]; g = []
        v = ch.dropna()
        for i in range(300):
            sh_ = pd.Series(np.roll(v.values, int(rng.integers(12, len(v) - 12))), index=v.index)
            g.append(st(cut(run(sh_), "discovery"))["sharpe"] - out["periods"]["discovery"]["gold_BH"]["sharpe"])
        luck[k] = dict(real_gain=round(real, 3), null_p95=round(float(np.percentile(g, 95)), 3))
    out["luck"] = luck
    ver = {}
    for k in CH:
        ok = all(out["periods"][p][k]["sharpe"] > out["periods"][p]["gold_BH"]["sharpe"] and out["periods"][p][k]["sharpe"] > out["periods"][p]["gold_silver_5050"]["sharpe"]
                 and out["periods"][p][k]["max_dd"] > 0.75 * out["periods"][p]["gold_BH"]["max_dd"] for p in ("validation", "final"))
        ver[k] = ("PASS" if ok and luck[k]["real_gain"] >= luck[k]["null_p95"] else "FAIL") + f" (criteria {'met' if ok else 'not met'}; luck {luck[k]})"
    out["verdicts"] = ver; print(ver)
    X.dump(P, out)


if __name__ == "__main__":
    {"e108": e108, "e109": e109, "e110": e110, "e111": e111, "e112": e112, "e113": e113, "e115": e115}[sys.argv[1]]()
