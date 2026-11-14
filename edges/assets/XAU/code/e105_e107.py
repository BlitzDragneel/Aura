"""E105 CME-break gap (plan E105_cme_break_xau.md) and E107 intraday momentum (plan E107_intraday_momentum_xau.md)."""
import sys, numpy as np, pandas as pd
from edges.assets.XAU.code import xlib as X

def cell_ret(C, tz, a, b, wd, nd=False):
    ents, M = C.windows(tz, a, b, weekdays=wd, next_day=nd)
    lr, g = C.wret(M)
    return pd.DataFrame(dict(lr=lr, g=g, first=M[:, 0]), index=ents.tz_convert(tz).normalize().tz_localize(None) if not nd else ents.tz_convert(tz).normalize().tz_localize(None))

def signal_trades(sig, tr_df, mode, per, mult, filt=None):
    j = tr_df.join(sig[["lr", "g"]].rename(columns={"lr": "s", "g": "gs"}), how="inner")
    if filt is not None:
        j = j[filt.reindex(j.index).fillna(False).values]
    side = np.sign(j.s.values) * (1 if mode == "FOLLOW" else -1)
    t = X.trades_from(pd.DatetimeIndex(j.t0), j.lr.values, side, (j.g & j.gs).values, np.zeros(len(j)), mult=mult)
    return X.cut(t, per, "time")

def run(plan, C, specs, nullfn, finalC=None, gcfn=None):
    out = {"plan": plan, "md5": X.MD5[plan], "discovery": {}, "validation": {}, "final": {}}
    dp = X.PER_PAXG["discovery"]
    for k, f in specs.items():
        s = X.summ(f(dp, 1.0), k); out["discovery"][k] = s; X.log(plan, k, "discovery", s)
        print(plan, k, s["n"], s["mean_bp"], s["t_week"], s.get("years"), flush=True)
    best = max(s["t_week"] for s in out["discovery"].values())
    nul = nullfn(dp)
    out["luck"] = dict(real_best_t=best, null_p95=float(np.percentile(nul, 95)))
    print("luck", out["luck"], flush=True)
    elig = sorted([k for k, s in out["discovery"].items() if X.eligible(s)], key=lambda k: -out["discovery"][k]["t_week"])[:2]
    out["eligible_promoted"] = elig
    if elig and best < out["luck"]["null_p95"]:
        out["verdict"] = "FAIL (luck)"; elig = []
    for k in elig:
        s = X.summ(specs[k](X.PER_PAXG["validation"], 1.0), k); out["validation"][k] = s; X.log(plan, k, "validation", s); print("VAL", k, s)
    ok = [k for k in elig if out["validation"][k]["mean_bp"] > 0 and out["validation"][k]["t_week"] >= 1.5]
    if ok:
        ch = max(ok, key=lambda k: out["validation"][k]["t_week"]); out["chosen"] = ch
        s = X.summ(specs[ch](X.PER_PAXG["final"], 1.0), ch); s["stress_mean_bp"] = X.summ(specs[ch](X.PER_PAXG["final"], 2.0))["mean_bp"]
        out["final"]["PAXG"] = s; X.log(plan, ch, "final", s); print("FINAL", s)
        if gcfn:
            g = gcfn(ch); out["final"]["GC1h_2026"] = X.summ(g); out["final"]["GC1h_halves"] = X.halves_pos(g)
    out.setdefault("verdict", "FAIL (nothing eligible/validated)" if not ok else "see final")
    X.dump(plan, out); print(plan, out["verdict"])
    return out

def e105():
    C = X.Cells(X.bars("PAXG_1h")); wd = (0, 1, 2, 3)
    sig = cell_ret(C, X.CT, "17:00", "18:00", wd)
    sd = sig.lr.where(sig.g).rolling(20, min_periods=10).std().shift(1)
    big = sig.lr.abs() > sd
    trs = {}
    for H in (1, 2, 4):
        ents, M = C.windows(X.CT, "18:00", f"{18 + H}:00", weekdays=wd); lr, g = C.wret(M)
        trs[H] = pd.DataFrame(dict(lr=lr, g=g, t0=ents), index=ents.tz_convert(X.CT).normalize().tz_localize(None))
    specs = {}
    for mode in ("FADE", "FOLLOW"):
        for H in (1, 2, 4):
            for fl in ("ALL", "BIG"):
                specs[f"{mode}_H{H}_{fl}"] = (lambda per, mult, mode=mode, H=H, fl=fl, s=sig:
                                              signal_trades(s, trs[H], mode, per, mult, big if fl == "BIG" else None))
    others = {h: cell_ret(C, X.CT, f"{h}:00", f"{h + 1}:00", wd) for h in range(12, 17)}
    def nullfn(per):
        rng = np.random.default_rng(1); res = []
        idx = sig.index
        for i in range(200):
            pick = rng.integers(12, 17, len(idx))
            ns = pd.concat([others[h].reindex(idx)[["lr", "g"]].where(pd.Series(pick == h, index=idx), axis=0) for h in range(12, 17)]).groupby(level=0).first().reindex(idx)
            ns["g"] = ns.g.fillna(False).astype(bool)
            nsd = ns.lr.rolling(20, min_periods=10).std().shift(1); nbig = ns.lr.abs() > nsd
            res.append(max(X.bt.tstat_weekly(signal_trades(ns, trs[H], m, per, 1.0, nbig if fl == "BIG" else None))
                           for m in ("FADE", "FOLLOW") for H in (1, 2, 4) for fl in ("ALL", "BIG")))
        return res
    def gcfn(ch):
        g = X.bars("GC_1h"); mode, H, fl = ch.split("_"); H = int(H[1:])
        lt = g.index.tz_convert(X.CT); rows = []
        for d in sorted(set(lt.normalize())):
            if d.weekday() not in wd: continue
            t16, t18 = d + pd.Timedelta(hours=16), d + pd.Timedelta(hours=18)
            try:
                c16 = g.c.loc[t16.tz_convert("UTC")]; o18 = g.o.loc[t18.tz_convert("UTC")]; cx = g.c.loc[(t18 + pd.Timedelta(hours=H - 1)).tz_convert("UTC")]
            except KeyError:
                continue
            rows.append((t18.tz_convert("UTC"), o18 / c16 - 1, cx / o18 - 1))
        df = pd.DataFrame(rows, columns=["time", "gap", "r"])
        df["sd"] = df.gap.rolling(20, min_periods=10).std().shift(1)
        if fl == "BIG": df = df[df.gap.abs() > df.sd]
        side = np.sign(df.gap) * (1 if mode == "FOLLOW" else -1)
        gross = np.where(side > 0, df.r, np.where(side < 0, 1 / (1 + df.r) - 1, np.nan))
        t = pd.DataFrame(dict(time=df.time, gross=gross)); t["net"] = X.net_of(t.gross, 0); t = t.dropna(); t["sym"] = "XAU"
        return X.cut(t, X.PER_GC1H["final"], "time")
    return run("E105", C, specs, nullfn, gcfn=gcfn)

def e107():
    C = X.Cells(X.bars("PAXG_1h")); wd = (0, 1, 2, 3, 4)
    F = {"F1": cell_ret(C, X.NY, "17:00", "09:00", (6, 0, 1, 2, 3), nd=True), "F2": cell_ret(C, X.NY, "08:00", "10:00", wd)}
    F["F1"].index = F["F1"].index + pd.Timedelta(days=1)          # label F1 by the trading day it ends in
    Ls = {}
    for nm, (a, b) in {"L1": ("12:00", "13:00"), "L2": ("12:00", "14:00"), "L3": ("13:00", "16:00")}.items():
        ents, M = C.windows(X.NY, a, b, weekdays=wd); lr, g = C.wret(M)
        Ls[nm] = pd.DataFrame(dict(lr=lr, g=g, t0=ents), index=ents.tz_convert(X.NY).normalize().tz_localize(None))
    specs = {f"{f}_{l}_{m}": (lambda per, mult, f=f, l=l, m=m: signal_trades(F[f], Ls[l], m, per, mult))
             for f in F for l in Ls for m in ("FOLLOW", "FADE")}
    def nullfn(per):
        rng = np.random.default_rng(2); res = []
        for i in range(200):
            NF = {k: v.set_axis(v.index.values[rng.permutation(len(v))]).sort_index() for k, v in F.items()}
            res.append(max(X.bt.tstat_weekly(signal_trades(NF[f], Ls[l], m, per, 1.0)) for f in F for l in Ls for m in ("FOLLOW", "FADE")))
        return res
    return run("E107", C, specs, nullfn)

if __name__ == "__main__":
    {"e105": e105, "e107": e107}[sys.argv[1]]()
