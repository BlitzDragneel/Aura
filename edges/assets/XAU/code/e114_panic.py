"""E114 hourly panic bounce / spike fade on gold (plan edges/plans/E114_panic_bounce_xau.md)."""
import numpy as np, pandas as pd
from edges.assets.XAU.code import xlib as X
P = "E114"

def closed(ts_ny):
    wd, h = ts_ny.weekday(), ts_ny.hour
    return (wd == 4 and h >= 17) or wd == 5 or (wd == 6 and h < 18)

class Sim:
    def __init__(self, df):
        self.df = df
        self.o, self.h, self.l, self.c = (df[k].values for k in "ohlc")
        lr = np.log(df.c).diff()
        self.r = lr.values
        self.sig = lr.rolling(720, min_periods=500).std().shift(1).values
        self.idx = df.index; self.ny = df.index.tz_convert(X.NY)
        self.cl = np.array([closed(t) for t in self.ny])
        self.contig = np.r_[False, np.asarray(np.diff(df.index) == pd.Timedelta(hours=1))]

    def triggers(self, side, k):
        z = self.r / self.sig
        m = (z <= -k) if side == "DOWN" else (z >= k)
        return np.where(m & ~self.cl & self.contig)[0]

    def run(self, trig, side, entry, H, mult=1.0):
        d = 1 if side == "DOWN" else -1; n = len(self.c); rows = []; busy = -1
        for t in trig:
            if t <= busy or t + H + 4 >= n or not np.isfinite(self.sig[t]): continue
            if entry == "MKT":
                e = t + 1; pe = self.o[e]
            else:
                lim = self.c[t] * np.exp(-d * 2 * self.sig[t]); e = None
                for j in range(t + 1, t + 4):
                    if (d > 0 and self.l[j] < lim) or (d < 0 and self.h[j] > lim):
                        e = j; pe = lim; break
                if e is None: continue
            x = e + H - 1 if entry == "MKT" else e + H
            if x >= n: continue
            # skip if the hold touches the CFD weekend closure or the bars are not contiguous hours
            if self.cl[e:x + 1].any() or (self.idx[x] - self.idx[e]) != pd.Timedelta(hours=x - e): continue
            px = self.c[x]
            gross = d * (px / pe - 1) if d > 0 else pe / px - 1
            lo = self.l[e:x + 1].min(); hi = self.h[e:x + 1].max()
            mae = lo / pe - 1 if d > 0 else pe / hi - 1
            nts = X.nights(self.idx[e], self.idx[x] + pd.Timedelta(hours=1))
            rows.append((self.idx[e], self.idx[x] + pd.Timedelta(hours=1), gross, mae, nts))
            busy = x
        T = pd.DataFrame(rows, columns=["time", "exit_time", "gross", "mae", "nts"])
        T["net"] = X.net_of(T.gross, T.nts, mult); T["sym"] = "XAU"
        return T

VARS = [(s, k, e, H) for s in ("DOWN", "UP") for k in (3, 4) for e in ("MKT", "LIM") for H in (6, 12, 24)]
def name(v): return f"{v[0]}_k{v[1]}_{v[2]}_H{v[3]}"

def main():
    S = Sim(X.bars("PAXG_1h")); per = X.PER_PAXG
    out = {"plan": P, "md5": X.MD5[P], "discovery": {}, "validation": {}, "final": {}}
    full = {v: S.run(S.triggers(v[0], v[1]), v[0], v[2], v[3]) for v in VARS}
    for v, T in full.items():
        s = X.summ(X.cut(T, per["discovery"], "time"), name(v)); s["gross_bp"] = round(X.cut(T, per["discovery"], "time").gross.mean() * 1e4, 2)
        out["discovery"][name(v)] = s; X.log(P, name(v), "discovery", s)
        print(name(v), s["n"], s["gross_bp"], s.get("mean_bp"), s.get("t_week"), s.get("years"), flush=True)
    best = max(s.get("t_week", -9) for s in out["discovery"].values() if s["n"] >= 20)
    rng = np.random.default_rng(14)
    dmask = np.where((S.idx >= pd.Timestamp(per["discovery"][0], tz="UTC")) & (S.idx < pd.Timestamp(per["discovery"][1], tz="UTC")) & ~S.cl & S.contig)[0]
    nb = []
    for i in range(200):
        b = -9
        for v in VARS:
            nt = (S.triggers(v[0], v[1]) < dmask[-1]).sum()
            tr = np.sort(rng.choice(dmask, max(nt, 1), replace=False))
            T = S.run(tr, v[0], v[2], v[3])
            if len(T) >= 20: b = max(b, X.bt.tstat_weekly(T))
        nb.append(b)
    out["luck"] = dict(real_best_t=best, null_p95=round(float(np.percentile(nb, 95)), 2))
    print("luck", out["luck"], flush=True)
    el = sorted([k for k, s in out["discovery"].items() if X.eligible(s)], key=lambda k: -out["discovery"][k]["t_week"])[:2]
    out["eligible_promoted"] = el
    if el and best < out["luck"]["null_p95"]:
        out["verdict"] = "FAIL (luck)"; el = []
    byname = {name(v): v for v in VARS}
    for k in el:
        s = X.summ(X.cut(full[byname[k]], per["validation"], "time"), k); out["validation"][k] = s; X.log(P, k, "validation", s); print("VAL", k, s)
    ok = [k for k in el if out["validation"][k]["mean_bp"] > 0 and out["validation"][k]["t_week"] >= 1.5]
    if ok:
        ch = max(ok, key=lambda k: out["validation"][k]["t_week"]); v = byname[ch]; out["chosen"] = ch
        T = X.cut(full[v], per["final"], "time"); s = X.summ(T, ch)
        s["stress_mean_bp"] = round(X.cut(S.run(S.triggers(v[0], v[1]), v[0], v[2], v[3], 2.0), per["final"], "time").net.mean() * 1e4, 2)
        out["final"]["PAXG"] = s; X.log(P, ch, "final", s); print("FINAL", s)
        G = Sim(X.bars("GC_1h")); g = X.cut(G.run(G.triggers(v[0], v[1]), v[0], v[2], v[3]), X.PER_GC1H["final"], "time")
        out["final"]["GC1h_2026"] = X.summ(g, ch)
    out.setdefault("verdict", "FAIL (nothing eligible)" if not el else ("FAIL (validation)" if not ok else "see final"))
    X.dump(P, out); print(out["verdict"])

if __name__ == "__main__":
    main()
