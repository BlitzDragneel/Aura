"""E52 cross-sectional momentum / reversal, weekly & 4-weekly (plan edges/plans/E52_xsec_weekly.md)."""
import sys, os, json, hashlib
sys.path.insert(0, "/home/user/Aura"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from edges.lib import bt
import lib2

MD5 = hashlib.md5(open(os.path.join(bt.ROOT, "plans/E52_xsec_weekly.md"), "rb").read()).hexdigest()
OUT = f"{lib2.SCR}/e52"; os.makedirs(OUT, exist_ok=True)


def setup():
    D = lib2.trim(lib2.daily()); F = lib2.fund_daily()
    ex = lib2.excluded()
    C, QV = D["c"].astype(float), D["qv"].astype(float)
    C = C[[c for c in C.columns if c not in ex]]; QV = QV[C.columns]
    idx = C.index
    sundays = idx[(idx.dayofweek == 6) & (idx >= "2020-03-01")]
    top = lib2.top_n(QV, C, 100, sundays, exclude=ex)
    cols = sorted(set(sum(top.values(), [])))
    B = lib2.Book(C, QV, F, cols)
    U = np.zeros((len(idx), len(cols)), bool)
    pos = {d: i for i, d in enumerate(idx)}
    for d, l in top.items():
        U[pos[d], [B.ci[s] for s in l]] = True
    Cc = C[cols].values
    return dict(B=B, U=U, Cc=Cc, idx=idx, sundays=sundays, pos=pos, cols=cols)


def formation(S, L, skip):
    Cc = S["Cc"]; T = len(Cc)
    a = np.full_like(Cc, np.nan); b = 7 * skip; e = 7 * (skip + L)
    a[e:] = Cc[e - b:T - b] / Cc[:T - e] - 1 if b > 0 else Cc[e:] / Cc[:T - e] - 1
    return a


def pick_targets(score, elig, rows, k, book):
    """score: [T,N] (higher = long side). Returns target matrix filled on rows."""
    T, N = score.shape
    tg = np.zeros((T, N))
    for t in rows:
        m = elig[t] & np.isfinite(score[t])
        ids = np.where(m)[0]
        if len(ids) < 2 * k:
            continue
        o = ids[np.argsort(score[t, ids])]
        lo, hi = o[:k], o[-k:]
        if book == "mn":
            tg[t, hi] = 0.5 / k; tg[t, lo] = -0.5 / k
        else:
            tg[t, hi] = 1.0 / k
    return tg


def reb_rows(S, freq):
    rows = np.array([S["pos"][d] for d in S["sundays"]])
    return rows if freq == "w" else rows[::4]


GRID = [(L, sk, fr, k, dr, bk) for L in (1, 2, 4, 12) for sk in (0, 1) for fr in ("w", "m") for k in (10, 20)
        for dr in ("mom", "rev") for bk in ("mn", "lo")]


def run_variant(S, L, sk, fr, k, dr, bk, score_override=None):
    rows = reb_rows(S, fr)
    f = formation(S, L, sk)
    sc = f if dr == "mom" else -f
    if score_override is not None:
        sc = np.where(np.isfinite(sc), score_override, np.nan)
    tg = pick_targets(sc, S["U"], rows, k, bk)
    mask = np.zeros(len(S["idx"]), bool); mask[rows] = True
    return S["B"].run(tg, mask)


def bench(S, fr="w"):
    rows = reb_rows(S, fr)
    tg = np.zeros((len(S["idx"]), len(S["cols"])))
    for t in rows:
        ids = np.where(S["U"][t])[0]; tg[t, ids] = 1.0 / len(ids)
    mask = np.zeros(len(S["idx"]), bool); mask[rows] = True
    return S["B"].run(tg, mask)


def main():
    S = setup()
    res = dict(plan="E52_xsec_weekly", md5=MD5, variants=[], bench={})
    b = bench(S)
    for p in ("discovery", "validation", "final"):
        res["bench"][p] = lib2.stats(lib2.period(b, p), f"ew_top100_{p}")
    NNULL = int(os.environ.get("NNULL", 200))
    ck = f"{OUT}/ckpt.pkl"
    if os.path.exists(ck):
        res, null_best, done = pd.read_pickle(ck)
    else:
        null_best = np.full(NNULL, -np.inf); done = set()
    for gi, g in enumerate(GRID):
        name = "L{}_s{}_{}_k{}_{}_{}".format(*g)
        if name in done:
            continue
        rng = np.random.default_rng(52000 + gi)
        o = run_variant(S, *g)
        dsc = lib2.period(o, "discovery")
        st = lib2.stats(dsc, name); st["weakest_year_bp"] = round(lib2.weakest_year(dsc) * 1e4, 2)
        bt.log_attempt(MD5, name, "discovery", st)
        res["variants"].append(st)
        print(name, st["mean_bp"], st["t_week"], st["weakest_year_bp"], st["cagr"], st["max_dd"], st["years"], flush=True)
        for j in range(NNULL):
            on = run_variant(S, *g, score_override=rng.random(S["Cc"].shape))
            null_best[j] = max(null_best[j], lib2.weakest_year(lib2.period(on, "discovery")))
        done.add(name)
        pd.to_pickle((res, null_best, done), ck)
    res["null_best_weakest_bp"] = [round(x * 1e4, 3) for x in null_best]
    json.dump(res, open(f"{OUT}/disc.json", "w"), indent=1, default=str)
    print("LUCK p95", np.percentile(null_best, 95) * 1e4)


if __name__ == "__main__":
    main()
