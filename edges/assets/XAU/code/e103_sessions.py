"""E103 gold session clock effects (plan edges/plans/E103_sessions_xau.md)."""
import numpy as np, pandas as pd
from edges.assets.XAU.code import xlib as X
P = "E103"
W = {"ASIA": (X.TK, "09:00", "15:00", False), "LONDON": (X.LDN, "08:00", "12:00", False), "NYAM": (X.NY, "08:00", "12:00", False),
     "NYPM": (X.NY, "12:00", "17:00", False), "OUTUS": (X.NY, "17:00", "08:00", True), "OPEN_TK": (X.TK, "09:00", "10:00", False),
     "OPEN_LDN": (X.LDN, "08:00", "09:00", False), "OPEN_NY": (X.NY, "09:00", "10:00", False)}

def build(C):
    out = {}
    for k, (tz, a, b, nd) in W.items():
        wd = (0, 1, 2, 3) if k == "OUTUS" else (0, 1, 2, 3, 4)
        ents, M = C.windows(tz, a, b, weekdays=wd, next_day=nd)
        nts = np.array([X.nights(e, e + pd.Timedelta(hours=int((M[i] >= 0).sum()))) for i, e in enumerate(ents)])
        out[k] = (ents, M, nts)
    return out

def grid(C, B, rot=None, per=None, mult=1.0):
    res = {}
    for k, (ents, M, nts) in B.items():
        lr, good = C.wret(M, rot)
        for side, nm in ((1, "L"), (-1, "S")):
            tr = X.trades_from(ents, lr, side, good, nts, mult=mult)
            if per: tr = X.cut(tr, per, "time")
            res[f"{k}_{nm}"] = tr
    return res

def main():
    pax = X.bars("PAXG_1h"); C = X.Cells(pax); B = build(C)
    out = {"plan": P, "md5": X.MD5[P], "discovery": {}, "luck": {}, "validation": {}, "final": {}}
    D = grid(C, B, per=X.PER_PAXG["discovery"])
    for k, tr in D.items():
        s = X.summ(tr, k); out["discovery"][k] = s; X.log(P, k, "discovery", s)
        print(k, s["n"], s["mean_bp"], s["t_week"], s["years"], flush=True)
    best = max(v["t_week"] for v in out["discovery"].values())
    rng = np.random.default_rng(0); null = []
    for i in range(200):
        rot = rng.integers(0, 24, C.ndays)
        G = grid(C, B, rot=rot, per=X.PER_PAXG["discovery"])
        null.append(max(X.bt.tstat_weekly(t) for t in G.values()))
    out["luck"] = dict(real_best_t=best, null_p95=float(np.percentile(null, 95)), null_p99=float(np.percentile(null, 99)))
    print("luck", out["luck"], flush=True)
    elig = sorted([k for k, s in out["discovery"].items() if X.eligible(s)], key=lambda k: -out["discovery"][k]["t_week"])[:2]
    out["eligible_promoted"] = elig
    if best < out["luck"]["null_p95"]:
        out["verdict"] = "FAIL (luck check: best discovery t below the rotation null's 95th pct)"; elig = []
    V = grid(C, B, per=X.PER_PAXG["validation"])
    for k in elig:
        s = X.summ(V[k], k); out["validation"][k] = s; X.log(P, k, "validation", s); print("VAL", k, s["n"], s["mean_bp"], s["t_week"])
    ok = [k for k in elig if out["validation"][k]["mean_bp"] > 0 and out["validation"][k]["t_week"] >= 1.5]
    if ok:
        ch = max(ok, key=lambda k: out["validation"][k]["t_week"]); out["chosen"] = ch
        F = grid(C, B, per=X.PER_PAXG["final"]); Fs = grid(C, B, per=X.PER_PAXG["final"], mult=2.0)
        s = X.summ(F[ch], ch); s["stress"] = X.summ(Fs[ch], ch)["mean_bp"]; out["final"]["PAXG"] = s; X.log(P, ch, "final", s)
        G = X.Cells(X.bars("GC_1h")); GB = build(G); gf = grid(G, GB, per=X.PER_GC1H["final"])[ch]
        out["final"]["GC1h_2026"] = X.summ(gf, ch); out["final"]["GC1h_halves"] = X.halves_pos(gf)
        print("FINAL", out["final"])
        out.setdefault("verdict", "see final")
    else:
        out.setdefault("verdict", "FAIL (nothing eligible/validated)")
    # description only: all windows, every period, PAXG and GC (no selection made from it)
    out["describe"] = {}
    G = X.Cells(X.bars("GC_1h")); GB = build(G)
    for nm, per in (("PAXG_val", X.PER_PAXG["validation"]), ("PAXG_final", X.PER_PAXG["final"])):
        out["describe"][nm] = {k: [X.summ(t)["mean_bp"], X.summ(t)["t_week"]] for k, t in grid(C, B, per=per).items() if k.endswith("_L")}
    for nm, per in X.PER_GC1H.items():
        out["describe"]["GC_" + nm] = {k: [X.summ(t)["mean_bp"], X.summ(t)["t_week"]] for k, t in grid(G, GB, per=per).items() if k.endswith("_L")}
    X.dump(P, out); print(out["verdict"])

if __name__ == "__main__":
    main()
