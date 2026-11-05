"""E53 ALT/BTC ratio trend (plan edges/plans/E53_altbtc_ratio.md)."""
import sys, os, json, hashlib
sys.path.insert(0, "/home/user/Aura"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from edges.lib import bt
import lib2

MD5 = hashlib.md5(open(os.path.join(bt.ROOT, "plans/E53_altbtc_ratio.md"), "rb").read()).hexdigest()
OUT = f"{lib2.SCR}/e53"; os.makedirs(OUT, exist_ok=True)


def setup():
    D = lib2.trim(lib2.daily()); F = lib2.fund_daily(); ex = lib2.excluded() | {"BTCUSDT"}
    C, QV = D["c"].astype(float), D["qv"].astype(float)
    idx = C.index
    sundays = idx[(idx.dayofweek == 6) & (idx >= "2020-03-01")]
    top = lib2.top_n(QV, C, 100, sundays, exclude=ex)
    alts = sorted(set(sum(top.values(), [])))
    cols = alts + ["BTCUSDT"]
    B = lib2.Book(C, QV, F, cols)
    U = np.zeros((len(idx), len(cols)), bool); pos = {d: i for i, d in enumerate(idx)}
    for d, l in top.items():
        U[pos[d], [B.ci[s] for s in l]] = True
    R = C[alts].div(C["BTCUSDT"], axis=0)
    return dict(B=B, U=U, R=R, idx=idx, sundays=sundays, pos=pos, cols=cols, nalt=len(alts))


def sig(S, N, method):
    R = S["R"]
    if method == "MA":
        s = R > R.rolling(N, min_periods=N).mean()
        valid = R.rolling(N, min_periods=N).mean().notna() & R.notna()
    else:
        s = np.log(R) - np.log(R.shift(N)) > 0
        valid = R.shift(N).notna() & R.notna()
    return np.where(valid.values, np.where(s.values, 1.0, -1.0), 0.0)   # +1 up, -1 down, 0 unknown


def targets(S, sg, book, rows):
    T = len(S["idx"]); na = S["nalt"]
    tg = np.zeros((T, na + 1))
    for t in rows:
        el = S["U"][t, :na]
        up = np.where(el & (sg[t] > 0))[0]; dn = np.where(el & (sg[t] < 0))[0]
        if book == "H":
            if len(up):
                tg[t, up] = 0.5 / len(up); tg[t, na] = -0.5
        elif book == "LS":
            if len(up) and len(dn):
                tg[t, up] = 0.25 / len(up); tg[t, dn] = -0.25 / len(dn)
                tg[t, na] = 0.0   # BTC hedges net out
            elif len(up):
                tg[t, up] = 0.5 / len(up); tg[t, na] = -0.5
            elif len(dn):
                tg[t, dn] = -0.5 / len(dn); tg[t, na] = 0.5
        else:  # U
            if len(up):
                tg[t, up] = 1.0 / len(up)
    return tg


def rows_for(S, fr):
    r = np.array([S["pos"][d] for d in S["sundays"]])
    return r if fr == "w" else r[::4]


def run(S, sg, book, fr):
    rows = rows_for(S, fr); m = np.zeros(len(S["idx"]), bool); m[rows] = True
    return S["B"].run(targets(S, sg, book, rows), m)


GRID = [(N, me, bk, fr) for N in (10, 20, 40, 60, 90) for me in ("MA", "RET") for bk in ("H", "LS", "U") for fr in ("w", "m")]


def bench(S):
    rows = rows_for(S, "w"); na = S["nalt"]
    tg = np.zeros((len(S["idx"]), na + 1))
    for t in rows:
        ids = np.where(S["U"][t, :na])[0]; tg[t, ids] = 1 / len(ids)
    m = np.zeros(len(S["idx"]), bool); m[rows] = True
    return S["B"].run(tg, m)


def main():
    S = setup()
    res = dict(plan="E53_altbtc_ratio", md5=MD5, variants=[], bench={})
    b = bench(S)
    for p in ("discovery", "validation", "final"):
        res["bench"][p] = lib2.stats(lib2.period(b, p), f"ew_top100_alts_{p}")
    rng = np.random.default_rng(53); NNULL = int(os.environ.get("NNULL", 200))
    null_best = np.full(NNULL, -np.inf)
    T = len(S["idx"])
    sigs = {}
    for g in GRID:
        N, me, bk, fr = g
        if (N, me) not in sigs:
            sigs[(N, me)] = sig(S, N, me)
        sg = sigs[(N, me)]
        name = f"N{N}_{me}_{bk}_{fr}"
        o = run(S, sg, bk, fr); dsc = lib2.period(o, "discovery")
        st = lib2.stats(dsc, name); st["weakest_year_bp"] = round(lib2.weakest_year(dsc) * 1e4, 2)
        bt.log_attempt(MD5, name, "discovery", st); res["variants"].append(st)
        print(name, st["mean_bp"], st["t_week"], st["weakest_year_bp"], st["cagr"], st["max_dd"], st["years"], flush=True)
        for j in range(NNULL):
            offs = rng.integers(180, T - 180, size=sg.shape[1])
            ns = np.empty_like(sg)
            for c in range(sg.shape[1]):
                ns[:, c] = np.roll(sg[:, c], offs[c])
            null_best[j] = max(null_best[j], lib2.weakest_year(lib2.period(run(S, ns, bk, fr), "discovery")))
    res["null_best_weakest_bp"] = [round(x * 1e4, 3) for x in null_best]
    json.dump(res, open(f"{OUT}/disc.json", "w"), indent=1, default=str)
    print("LUCK p95", np.percentile(null_best, 95) * 1e4)


if __name__ == "__main__":
    main()
