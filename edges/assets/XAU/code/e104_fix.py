"""E104 London gold auctions 10:30 / 15:00 London (plan edges/plans/E104_london_fix_xau.md)."""
import numpy as np, pandas as pd
from edges.assets.XAU.code import xlib as X
P = "E104"
RULES = ["PRE_L", "PRE_S", "POST_L", "POST_S", "FADE60", "FADE120", "FOLLOW60", "FOLLOW120"]

def hm(m): return f"{m // 60:02d}:{m % 60:02d}"

def anchor_trades(C, A, per, mult=1.0):
    """A = minutes after midnight London. Returns {rule: trades}."""
    k = int(pd.Timedelta("1h") / C.freq)                       # cells per hour
    ents, M120 = C.windows(X.LDN, hm(A), hm(A + 120))
    M60 = M120[:, :k]
    pre = M120[:, :1] - np.arange(k, 0, -1)[None, :]
    lr_pre, g_pre = C.wret(pre)
    out = {}
    for r in RULES:
        if r.startswith("PRE"):
            ent = ents - pd.Timedelta("1h"); lr, g = lr_pre, g_pre; side = 1 if r.endswith("L") else -1
        else:
            M = M60 if r.endswith("60") or r.startswith("POST") else M120
            lr, g = C.wret(M); ent = ents; g = g & g_pre
            side = (1 if r.endswith("L") else -1) if r.startswith("POST") else (-np.sign(lr_pre) if r.startswith("FADE") else np.sign(lr_pre))
        tr = X.trades_from(ent, lr, side, g, np.zeros(len(ent)), mult=mult)
        out[r] = X.cut(tr, per, "time")
    return out

def main():
    C = X.Cells(X.bars("PAXG_15m"), "15min")
    out = {"plan": P, "md5": X.MD5[P], "discovery": {}, "validation": {}, "final": {}}
    dper = X.PER_PAXG["discovery"]; real = {}
    for nm, A in (("AM", 630), ("PM", 900)):
        for r, tr in anchor_trades(C, A, dper).items():
            s = X.summ(tr, f"{nm}_{r}"); out["discovery"][f"{nm}_{r}"] = s; X.log(P, f"{nm}_{r}", "discovery", s)
            print(nm, r, s["n"], s["mean_bp"], s["t_week"], s["years"], flush=True)
    best = max(s["t_week"] for s in out["discovery"].values())
    anchors = [a for a in range(420, 1021, 15) if min(abs(a - 630), abs(a - 900)) >= 60]
    nb = []
    for a in anchors:
        nb.append(max(X.bt.tstat_weekly(t) for t in anchor_trades(C, a, dper).values()))
    pairs = [max(x, y) for i, x in enumerate(nb) for y in nb[i + 1:]]
    out["luck"] = dict(real_best_t=best, null_anchor_pairs_p95=float(np.percentile(pairs, 95)), n_anchors=len(anchors),
                       anchor_best_t={hm(a): round(v, 2) for a, v in zip(anchors, nb)})
    print("luck", out["luck"]["real_best_t"], out["luck"]["null_anchor_pairs_p95"], flush=True)
    elig = sorted([k for k, s in out["discovery"].items() if X.eligible(s)], key=lambda k: -out["discovery"][k]["t_week"])[:2]
    out["eligible_promoted"] = elig
    if elig and best < out["luck"]["null_anchor_pairs_p95"]:
        out["verdict"] = "FAIL (luck)"; elig = []
    for k in elig:
        A = 630 if k.startswith("AM") else 900
        s = X.summ(anchor_trades(C, A, X.PER_PAXG["validation"])[k[3:]], k); out["validation"][k] = s; X.log(P, k, "validation", s)
        print("VAL", k, s["n"], s["mean_bp"], s["t_week"])
    ok = [k for k in elig if out["validation"][k]["mean_bp"] > 0 and out["validation"][k]["t_week"] >= 1.5]
    if ok:
        ch = max(ok, key=lambda k: out["validation"][k]["t_week"]); A = 630 if ch.startswith("AM") else 900
        s = X.summ(anchor_trades(C, A, X.PER_PAXG["final"])[ch[3:]], ch)
        s["stress_mean_bp"] = X.summ(anchor_trades(C, A, X.PER_PAXG["final"], 2.0)[ch[3:]])["mean_bp"]
        out["final"]["PAXG"] = s; out["chosen"] = ch; X.log(P, ch, "final", s); print("FINAL", s)
    out.setdefault("verdict", "FAIL (nothing eligible/validated)" if not ok else "see final")
    X.dump(P, out); print(out["verdict"])

if __name__ == "__main__":
    main()
