"""E121 handoff intraday families on silver hourly (plan edges/plans/E121_xag_handoff_intraday.md)."""
import warnings

import numpy as np
import pandas as pd

from edges.lib import bt
from edges.research_xag import xlib as X

warnings.filterwarnings("ignore")
PLAN = "214c2b880d15b17c06444333b94e60ef"
FOMC = ["2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18", "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
        "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-10", "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
        "2026-07-29", "2026-09-16", "2026-10-28"]  # federalreserve.gov fomccalendars.htm, fetched 14 Nov 2026


def prior_ext(A, N):
    hh = pd.Series(A.h).rolling(N).max().shift(1).values
    ll = pd.Series(A.l).rolling(N).min().shift(1).values
    return hh, ll


def fam_breakout(A, N):
    hh, ll = prior_ext(A, N)
    s = []
    flat = A.d.flat.values
    for i in range(N + 14, A.n):
        if flat[i]:
            continue
        if A.c[i] > hh[i]:
            s.append((i, 1))
        elif A.c[i] < ll[i]:
            s.append((i, -1))
    return s


def fam_compression(A, confirm):
    hh, ll = prior_ext(A, 16)
    ratio = pd.Series((hh - ll) / A.atr)
    pr = ratio.rolling(500).rank(pct=True).values
    flat = A.d.flat.values
    s = []
    for i in range(520, A.n - 1):
        if flat[i] or not (pr[i] < 0.2):
            continue
        side = 1 if A.c[i] > hh[i] else (-1 if A.c[i] < ll[i] else 0)
        if side == 0:
            continue
        if not confirm:
            s.append((i, side))
        else:
            j = i + 1
            if (side > 0 and A.c[j] > hh[i]) or (side < 0 and A.c[j] < ll[i]):
                s.append((j, side))
    return s


def fam_retest(A):
    hh, ll = prior_ext(A, 16)
    flat = A.d.flat.values
    s = []
    for b in range(30, A.n - 5):
        if flat[b]:
            continue
        for side, lev in ((1, hh[b]), (-1, ll[b])):
            if not ((side > 0 and A.c[b] > lev) or (side < 0 and A.c[b] < lev)):
                continue
            for k in range(1, 5):
                j = b + k
                a = A.atr[b]
                if side > 0 and A.l[j] <= lev + 0.25 * a and A.c[j] > lev:
                    s.append((j, 1)); break
                if side < 0 and A.h[j] >= lev - 0.25 * a and A.c[j] < lev:
                    s.append((j, -1)); break
    return sorted(set(s))


def fam_failed_auction(A):
    hh, ll = prior_ext(A, 16)
    s = []
    for i in range(30, A.n):
        a = A.atr[i]
        rg = A.h[i] - A.l[i]
        if not np.isfinite(a) or rg < 1.5 * a or rg <= 0:
            continue
        loc = (A.c[i] - A.l[i]) / rg
        if A.h[i] >= hh[i] + 0.1 * a and A.c[i] < hh[i] and loc <= 0.4:
            s.append((i, -1))
        elif A.l[i] <= ll[i] - 0.1 * a and A.c[i] > ll[i] and loc >= 0.6:
            s.append((i, 1))
    return s


def features(A):
    d = A.d
    lc = np.log(d.c)
    F = pd.DataFrame(index=d.index)
    for k in (1, 2, 4, 8, 16, 32):
        F[f"r{k}"] = lc.diff(k)
    F["atrp"] = d.atr / d.c
    hh, ll = d.h.rolling(16).max(), d.l.rolling(16).min()
    F["pos16"] = (d.c - ll) / (hh - ll)
    F["hour"] = d.index.hour
    F["dow"] = d.index.dayofweek
    F["dh32"] = (d.h.rolling(32).max() - d.c) / d.atr
    F["dl32"] = (d.c - d.l.rolling(32).min()) / d.atr
    fwd = lc.shift(-4) - lc
    bnd = np.maximum(0.0012, 0.5 * d.atr / d.c)
    y3 = pd.Series(np.where(fwd > bnd, 2, np.where(fwd < -bnd, 0, 1)), index=d.index).where(fwd.notna())
    big = (fwd.abs() > np.maximum(0.004, 2 * d.atr / d.c)).astype(float).where(fwd.notna())
    return F, y3, big


def models(A):
    import lightgbm as lgb
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss
    F, y3, big = features(A)
    per = {p: (F.index >= a) & (F.index < b) for p, (a, b) in X.HPER.items()}
    ok = F.notna().all(axis=1) & y3.notna()
    tr = per["discovery"] & ok & (F.index < pd.Timestamp(X.HPER["discovery"][1], tz="UTC") - pd.Timedelta(hours=8))
    prm = dict(n_estimators=200, learning_rate=0.05, num_leaves=15, min_child_samples=50, verbose=-1, random_state=0)
    m3 = lgb.LGBMClassifier(objective="multiclass", **prm).fit(F[tr], y3[tr].astype(int))
    allok = F.notna().all(axis=1)
    P = pd.DataFrame(m3.predict_proba(F[allok]), index=F.index[allok], columns=["dn", "flat", "up"])
    mx = P[["dn", "up"]].max(axis=1)
    thr = float(mx[per["validation"][allok.values]].quantile(0.75))
    sigs = []
    idx = {t: i for i, t in enumerate(A.t)}
    for t, row in P.iterrows():
        if max(row.dn, row.up) > thr and max(row.dn, row.up) > row.flat:
            sigs.append((idx[t], 1 if row.up > row.dn else -1))
    # movement-timing watch
    mb = lgb.LGBMClassifier(objective="binary", **prm).fit(F[tr], big[tr].astype(int))
    pb = pd.Series(mb.predict_proba(F[allok])[:, 1], index=F.index[allok])
    C = pd.get_dummies(F["hour"].astype(int), prefix="h").astype(float)
    C["atrp"] = F["atrp"] * 100
    ctrl = LogisticRegression(max_iter=2000).fit(C[tr], big[tr].astype(int))
    pc = pd.Series(ctrl.predict_proba(C[allok])[:, 1], index=F.index[allok])
    wthr = float(pb[per["validation"][allok.values]].quantile(0.75))
    watch = {}
    for p in ("discovery", "validation", "final"):
        m = per[p][allok.values] & big[allok].notna().values
        yy = big[allok][m]
        w = pb[m] > wthr
        watch[p] = dict(n=int(m.sum()), big_rate=round(float(yy.mean()), 3), big_rate_in_watch=round(float(yy[w].mean()), 3),
                        watch_share=round(float(w.mean()), 3), logloss_model=round(float(log_loss(yy, pb[m])), 4),
                        logloss_volclock=round(float(log_loss(yy, pc[m])), 4))
    return sigs, thr, watch


def fomc(A, mode):
    ny = A.t.tz_convert("America/New_York")
    s = []
    for dstr in FOMC:
        d = pd.Timestamp(dstr)
        i0 = np.where((ny.date == d.date()) & (ny.hour == 14))[0]
        i1 = np.where((ny.date == d.date()) & (ny.hour == 16))[0]  # 17:00 NY = CME break: last bar before it
        if len(i0) == 0 or len(i1) == 0:
            continue
        react = A.c[i1[0]] - A.o[i0[0]]
        if react == 0:
            continue
        side = int(np.sign(react)) * (1 if mode == "FOLLOW" else -1)
        s.append((i1[0], side))  # entry next bar open (18:00 NY): lag 1
    return s


def main():
    A = X.H(X.hourly("SI"))
    fams = {"breakout_N16": (fam_breakout(A, 16), 2), "breakout_N32": (fam_breakout(A, 32), 2),
            "compression": (fam_compression(A, False), 2), "compression_confirm": (fam_compression(A, True), 2),
            "accepted_retest": (fam_retest(A), 2), "failed_auction": (fam_failed_auction(A), 2)}
    msig, thr, watch = models(A)
    fams["learned_price_only"] = (msig, 2)
    fams["fomc_FOLLOW"] = (fomc(A, "FOLLOW"), 1)
    fams["fomc_FADE"] = (fomc(A, "FADE"), 1)
    res = dict(plan="edges/plans/E121_xag_handoff_intraday.md", md5=PLAN, tf="1h (no 15m data)", families={},
               notes=["FOMC reaction window = 14:00 NY bar open -> 16:00 NY bar close (17:00 NY is the CME break, no bar); "
                      "entry at the reopen bar (18:00 NY). Forced by data, decided before seeing FOMC results.",
                      "learned_price_only discovery = training sample (in-sample), not used for selection; validation is its first OOS test.",
                      "FINAL numbers for non-promoted families are information only."],
               model_threshold=thr, movement_watch=watch)
    trades = {}
    for name, (sigs, lag) in fams.items():
        tr = X.run_signals(A, sigs, lag)
        trs = X.run_signals(A, sigs, lag, stress=2.0)
        trades[name] = tr
        row = {}
        for p, sub in X.hsplit(tr).items():
            row[p] = X.hsum(sub, name)
            row[p]["stress_mean_bp"] = round(X.hsplit(trs)[p].net.mean() * 1e4, 2) if len(X.hsplit(trs)[p]) else None
            bt.log_attempt(PLAN, f"E121 {name}", p, row[p])
        res["families"][name] = row
        print(name, {p: (row[p].get("n"), row[p].get("mean_bp"), row[p].get("t_week")) for p in row}, flush=True)
    # selection on discovery (>= 20 trades)
    # the learned model's discovery period is its TRAINING sample (in-sample): excluded from selection;
    # its first out-of-sample test is validation.
    cand = {k: v["discovery"] for k, v in res["families"].items() if v["discovery"].get("n", 0) >= 20
            and k != "learned_price_only"}
    best = max(cand, key=lambda k: cand[k]["t_week"] if cand[k]["t_week"] == cand[k]["t_week"] else -9)
    d = cand[best]
    disc = X.hsplit(trades[best])["discovery"]
    rc = X.random_control(A, disc, 2.0, 6.0, 4, n=200)
    # grid best-t null (families 1-4, 7 have shiftable signals)
    rng = np.random.default_rng(7)
    shiftable = {k: v for k, v in fams.items() if k != "learned_price_only"}
    null = []
    lo = int(np.searchsorted(A.t, pd.Timestamp(X.HPER["discovery"][0], tz="UTC")))
    hi = int(np.searchsorted(A.t, pd.Timestamp(X.HPER["discovery"][1], tz="UTC")))
    for _ in range(100):
        off = int(rng.integers(50, hi - lo - 50))
        bestt = -9
        for k, (sigs, lag) in shiftable.items():
            ss = [((i - lo + off) % (hi - lo) + lo, sd) for i, sd in sigs if lo <= i < hi]
            ss.sort()
            tr = X.run_signals(A, ss, lag)
            if len(tr) >= 20:
                t = bt.tstat_weekly(tr)
                if t == t:
                    bestt = max(bestt, t)
        null.append(bestt)
    res["selection"] = dict(best=best, discovery=d, random_entry_p95_bp=round(float(np.nanpercentile(rc, 95)) * 1e4, 2),
                            shifted_grid_best_t_p95=round(float(np.percentile(null, 95)), 2))
    promoted = d["t_week"] >= 2 and d["mean_bp"] > res["selection"]["random_entry_p95_bp"] and \
        d["t_week"] >= res["selection"]["shifted_grid_best_t_p95"]
    v = res["families"][best]["validation"]
    f = res["families"][best]["final"]
    vpass = promoted and v.get("n", 0) > 0 and v["mean_bp"] > 0 and v["t_week"] >= 1.5
    res["verdict"] = ("judged FINAL" if vpass else "FAIL before FINAL") + f" | best={best} promoted={promoted} " \
        f"val=({v.get('n')},{v.get('mean_bp')},{v.get('t_week')}) final(info unless judged)=({f.get('n')},{f.get('mean_bp')},{f.get('t_week')})"
    if vpass:
        ok = f["mean_bp"] > 0 and f["t_week"] >= 2 and (f["n"] >= 100 or (f["n"] >= 50 and f["t_week"] >= 3))
        res["verdict"] = ("PASS " if ok else "FAIL ") + res["verdict"]
    print(res["selection"], res["verdict"], watch, flush=True)
    X.save("E121", res)


if __name__ == "__main__":
    main()
