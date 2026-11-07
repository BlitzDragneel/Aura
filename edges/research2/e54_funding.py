"""E54 funding as a contrarian price signal, weekly horizons (plan edges/plans/E54_funding_contrarian.md)."""
import sys, os, json, hashlib
sys.path.insert(0, "/home/user/Aura"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from edges.lib import bt
import lib2

MD5 = hashlib.md5(open(os.path.join(bt.ROOT, "plans/E54_funding_contrarian.md"), "rb").read()).hexdigest()
OUT = f"{lib2.SCR}/e54"; os.makedirs(OUT, exist_ok=True)


def setup():
    D = lib2.trim(lib2.daily()); FD = lib2.fund_daily(); ex = lib2.excluded()
    C, QV = D["c"].astype(float), D["qv"].astype(float)
    C = C[[c for c in C.columns if c not in ex]]; QV = QV[C.columns]
    idx = C.index
    sundays = idx[(idx.dayofweek == 6) & (idx >= "2020-03-01")]
    top = lib2.top_n(QV, C, 100, sundays, exclude=ex)
    top10 = {d: l[:10] for d, l in top.items()}
    cols = sorted(set(sum(top.values(), [])))
    B = lib2.Book(C, QV, FD, cols)
    U = np.zeros((len(idx), len(cols)), bool); pos = {d: i for i, d in enumerate(idx)}
    for d, l in top.items():
        U[pos[d], [B.ci[s] for s in l]] = True
    F8 = lib2.fund_bars(cols, "8h").reindex(columns=cols)
    F8 = F8[F8.index >= "2019-12-01"]
    f7 = F8.rolling(21, min_periods=15).mean(); m90 = F8.rolling(270, min_periods=150).mean()
    s90 = F8.rolling(270, min_periods=150).std()
    Z = (f7 - m90) / s90.replace(0, np.nan)
    # value known at end of day d = last 8h bin starting 16:00 of day d
    end = lambda X: X[X.index.hour == 16].set_axis(X[X.index.hour == 16].index.floor("1D")).reindex(idx)
    FDc = FD.reindex(index=idx, columns=cols)
    sigs = dict(F7=FDc.rolling(7, min_periods=5).mean().values, F30=FDc.rolling(30, min_periods=20).mean().values,
                Z=end(Z).values)
    return dict(B=B, U=U, idx=idx, sundays=sundays, pos=pos, cols=cols, sigs=sigs, top10=top10)


def rows_for(S, fr):
    r = np.array([S["pos"][d] for d in S["sundays"]])
    return r if fr == "w" else r[::4]


def xs_targets(S, sc, rows, k, book):
    T, N = sc.shape; tg = np.zeros((T, N))
    for t in rows:
        ids = np.where(S["U"][t] & np.isfinite(sc[t]))[0]
        if len(ids) < 2 * k:
            continue
        o = ids[np.argsort(sc[t, ids])]
        lo, hi = o[:k], o[-k:]
        if book == "mn":
            tg[t, hi] = -0.5 / k; tg[t, lo] = 0.5 / k    # short crowded (high funding), long low funding
        else:
            tg[t, lo] = 1.0 / k
    return tg


def gauge(S):
    """market median Z of the top-100 at each day, and its percentile within the prior 365 days."""
    U = S["U"]; rm = U.any(1)
    Um = pd.DataFrame(np.where(rm[:, None], U.astype(float), np.nan), index=S["idx"]).ffill().fillna(0).values > 0
    med = pd.Series(np.nanmedian(np.where(Um, S["sigs"]["Z"], np.nan), axis=1), index=S["idx"])
    pct = med.rolling(366, min_periods=200).apply(lambda a: (a[:-1] < a[-1]).mean() if np.isfinite(a[-1]) else np.nan,
                                                  raw=True)
    return pct.values


def ts_targets(S, pct, rows, q, act):
    T, N = len(S["idx"]), len(S["cols"]); tg = np.zeros((T, N))
    for t in rows:
        p = pct[t]
        if not np.isfinite(p):
            continue
        d = S["idx"][t]; ids = [S["B"].ci[s] for s in S["top10"].get(d, [])]
        if not ids:
            continue
        if p >= 1 - q and act in ("short", "both"):
            tg[t, ids] = -0.1
        elif p <= q and act in ("long", "both"):
            tg[t, ids] = 0.1
    return tg


XS = [(sg, fr, k, bk) for sg in ("F7", "F30", "Z") for fr in ("w", "m") for k in (10, 20) for bk in ("mn", "lo")]
TS = [(q, act, fr) for q in (0.2, 0.33) for act in ("short", "long", "both") for fr in ("w", "m")]


def run_xs(S, g, perm_rng=None):
    sgn, fr, k, bk = g; rows = rows_for(S, fr)
    sc = S["sigs"][sgn]
    if perm_rng is not None:
        sc = np.where(np.isfinite(sc), perm_rng.random(sc.shape), np.nan)
    m = np.zeros(len(S["idx"]), bool); m[rows] = True
    return S["B"].run(xs_targets(S, sc, rows, k, bk), m)


def run_ts(S, g, pct):
    q, act, fr = g; rows = rows_for(S, fr)
    m = np.zeros(len(S["idx"]), bool); m[rows] = True
    return S["B"].run(ts_targets(S, pct, rows, q, act), m)


def record(res, name, o):
    dsc = lib2.period(o, "discovery")
    st = lib2.stats(dsc, name); st["weakest_year_bp"] = round(lib2.weakest_year(dsc) * 1e4, 2)
    st["price_only_bp"] = round((dsc.gross + dsc.cost).mean() * 1e4, 2)
    bt.log_attempt(MD5, name, "discovery", st); res["variants"].append(st)
    print(name, st["mean_bp"], st["price_only_bp"], st["t_week"], st["weakest_year_bp"], st["max_dd"], st["years"], flush=True)
    return lib2.weakest_year(dsc)


def main():
    S = setup()
    res = dict(plan="E54_funding_contrarian", md5=MD5, variants=[])
    rng = np.random.default_rng(54); NNULL = int(os.environ.get("NNULL", 200))
    null_best = np.full(NNULL, -np.inf)
    for g in XS:
        record(res, "XS_{}_{}_k{}_{}".format(*g), run_xs(S, g))
        for j in range(NNULL):
            null_best[j] = max(null_best[j], lib2.weakest_year(lib2.period(run_xs(S, g, rng), "discovery")))
    pct = gauge(S); T = len(pct)
    offs = rng.integers(180, T - 180, size=NNULL)
    for g in TS:
        record(res, "TS_q{}_{}_{}".format(*g), run_ts(S, g, pct))
        for j in range(NNULL):
            null_best[j] = max(null_best[j], lib2.weakest_year(lib2.period(run_ts(S, g, np.roll(pct, offs[j])), "discovery")))
    res["null_best_weakest_bp"] = [round(x * 1e4, 3) for x in null_best]
    json.dump(res, open(f"{OUT}/disc.json", "w"), indent=1, default=str)
    print("LUCK p95", np.percentile(null_best, 95) * 1e4)


if __name__ == "__main__":
    main()
