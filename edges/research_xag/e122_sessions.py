"""E122 silver day trades: CME-break gap, silver fix window, opening-range breakouts (plan E122_xag_day_sessions.md)."""
import numpy as np
import pandas as pd

from edges.lib import bt
from edges.research_xag import xlib as X

PLAN = "3528118b066cedf5bc736fdd897d630e"


def grid_eval(A, V, PLANMD5, tag, min_n=30, nshift=100, seed=11):
    """V: {name: dict(sigs, lag, stop_atr, tgt_atr, hold, venue)}. Returns results dict incl. selection & luck."""
    res, trades = {}, {}
    for name, v in V.items():
        tr = X.run_signals(A, v["sigs"], v["lag"], v["stop_atr"], v["tgt_atr"], v["hold"], venue=v.get("venue", "cfd"))
        trs = X.run_signals(A, v["sigs"], v["lag"], v["stop_atr"], v["tgt_atr"], v["hold"], venue=v.get("venue", "cfd"), stress=2)
        trades[name] = tr
        row = {}
        sp, sps = X.hsplit(tr), X.hsplit(trs)
        for p in X.HPER:
            row[p] = X.hsum(sp[p], name)
            row[p]["stress_mean_bp"] = round(sps[p].net.mean() * 1e4, 2) if len(sps[p]) else None
        bt.log_attempt(PLANMD5, f"{tag} {name}", "discovery", row["discovery"])
        res[name] = row
    cand = {k: v["discovery"] for k, v in res.items() if v["discovery"].get("n", 0) >= min_n}
    out = dict(variants=res)
    if not cand:
        out["verdict"] = "FAIL: no variant with enough discovery trades"
        return out, trades
    best = max(cand, key=lambda k: cand[k]["t_week"] if cand[k]["t_week"] == cand[k]["t_week"] else -9)
    d = cand[best]
    v = V[best]
    disc = X.hsplit(trades[best])["discovery"]
    rc = X.random_control(A, disc, v["stop_atr"], v["tgt_atr"], v["hold"], n=200, venue=v.get("venue", "cfd"))
    lo = int(np.searchsorted(A.t, pd.Timestamp(X.HPER["discovery"][0], tz="UTC")))
    hi = int(np.searchsorted(A.t, pd.Timestamp(X.HPER["discovery"][1], tz="UTC")))
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(nshift):
        off = int(rng.integers(50, hi - lo - 50))
        bestt = -9
        for k, vv in V.items():
            ss = sorted(((s[0] - lo + off) % (hi - lo) + lo,) + tuple(s[1:]) for s in vv["sigs"] if lo <= s[0] < hi)
            tr = X.run_signals(A, ss, vv["lag"], vv["stop_atr"], vv["tgt_atr"], vv["hold"], venue=vv.get("venue", "cfd"))
            if len(tr) >= min_n:
                t = bt.tstat_weekly(tr)
                if t == t:
                    bestt = max(bestt, t)
        null.append(bestt)
    p95r = float(np.nanpercentile(rc, 95)) * 1e4
    p95t = float(np.percentile(null, 95))
    promoted = d["t_week"] >= 2 and d["mean_bp"] > p95r and d["t_week"] >= p95t
    out["selection"] = dict(best=best, discovery=d, random_entry_p95_bp=round(p95r, 2), shifted_grid_best_t_p95=round(p95t, 2),
                            promoted=bool(promoted))
    val, fin = res[best]["validation"], res[best]["final"]
    if promoted:
        bt.log_attempt(PLANMD5, f"{tag} {best}", "validation", val)
    vpass = promoted and val.get("n", 0) > 0 and val["mean_bp"] > 0 and val["t_week"] >= 1.5
    if vpass:
        bt.log_attempt(PLANMD5, f"{tag} {best}", "final", fin)
        ok = fin.get("n", 0) > 0 and fin["mean_bp"] > 0 and fin["t_week"] >= 2 and \
            (fin["n"] >= 100 or (fin["n"] >= 50 and fin["t_week"] >= 3))
        out["verdict"] = f"{'PASS' if ok else 'FAIL'} (FINAL judged) best={best}"
    else:
        out["verdict"] = f"FAIL before FINAL: best={best} promoted={promoted} val=({val.get('n')},{val.get('mean_bp')},{val.get('t_week')})" \
                         f" final_info=({fin.get('n')},{fin.get('mean_bp')},{fin.get('t_week')})"
    return out, trades


def build(A, d):
    ny = A.t.tz_convert("America/New_York")
    ldn = A.t.tz_convert("Europe/London")
    V = {}
    # A. break gap
    hole = np.r_[False, (np.diff(A.t.values).astype("timedelta64[m]").astype(int) >= 120)]
    reopen = np.where(hole & (ny.hour == 18))[0]
    for k in (0.5, 1.0):
        for mode in ("FOLLOW", "FADE"):
            sigs = []
            for i in reopen:
                a = A.atr[i - 1]
                g = (A.o[i] - A.c[i - 1]) / a if a > 0 else np.nan
                if np.isfinite(g) and abs(g) > k:
                    sigs.append((i - 1, int(np.sign(g)) * (1 if mode == "FOLLOW" else -1)))
            for h in (1, 2, 4):
                V[f"gap_k{k}_{mode}_h{h}"] = dict(sigs=sigs, lag=1, stop_atr=2.0, tgt_atr=None, hold=h)
    # B. silver fix 12:00 London
    day = ldn.date
    idx = pd.DataFrame({"i": np.arange(A.n), "d": day, "hr": ldn.hour})
    i07 = idx[idx.hr == 7].set_index("d").i
    i11 = idx[idx.hr == 11].set_index("d").i
    i12 = idx[idx.hr == 12].set_index("d").i
    for mode in ("FOLLOW", "FADE"):
        sigs = []
        for dd, j in i11.items():
            if dd not in i07.index or dd not in i12.index or i12[dd] != j + 1:
                continue
            a = A.atr[j]
            pm = (A.c[j] - A.c[i07[dd]]) / a
            if np.isfinite(pm) and abs(pm) > 1:
                sigs.append((j, int(np.sign(pm)) * (1 if mode == "FOLLOW" else -1)))
        for h in (2, 4):
            V[f"fix_{mode}_h{h}"] = dict(sigs=sigs, lag=1, stop_atr=None, tgt_atr=None, hold=h)
    # C. opening range breakout
    hr_ret = pd.Series(np.log(A.c), index=A.t).diff()
    dvol = hr_ret.groupby(A.t.normalize()).std()
    med = dvol.rolling(250, min_periods=60).median()
    hivol_day = (dvol > med).shift(1)  # prior day's vol above its median -> known today
    hv = hivol_day.reindex(A.t.normalize()).values
    for sess, tz in (("LDN", ldn), ("NY", ny)):
        orb = np.where(tz.hour == 8)[0]
        for trig in (0.0, 0.25):
            for gate in ("none", "hivol"):
                sigs = []
                for i in orb:
                    if gate == "hivol" and hv[i] is not True:
                        continue
                    hi_, lo_ = A.h[i], A.l[i]
                    for j in range(i + 1, min(i + 5, A.n)):
                        if (A.t[j] - A.t[i]) > pd.Timedelta(hours=4):
                            break
                        a = A.atr[j]
                        if A.c[j] > hi_ + trig * a:
                            sigs.append((j, 1, min(A.c[j] - lo_, 2 * a))); break
                        if A.c[j] < lo_ - trig * a:
                            sigs.append((j, -1, min(hi_ - A.c[j], 2 * a))); break
                V[f"orb_{sess}_trig{trig}_{gate}"] = dict(sigs=sigs, lag=1, stop_atr=2.0, tgt_atr=None, hold=4)
    return V


def cost_room():
    out = {}
    for sym, rt in (("SI", 2 * X.SPREAD["SI"]), ("GC", 2 * X.SPREAD["GC"])):
        d = X.hourly(sym)
        lc = np.log(d.c)
        out[sym] = {f"{h}h_mean_abs_bp": round(float((lc.shift(-h) - lc).abs().mean() * 1e4), 1) for h in (1, 2, 4)}
        out[sym]["roundtrip_cost_bp"] = rt * 1e4
        out[sym]["cost_share_of_4h_move"] = round(rt * 1e4 / out[sym]["4h_mean_abs_bp"], 3)
    return out


def main():
    A = X.H(X.hourly("SI"))
    V = build(A, None)
    out, trades = grid_eval(A, V, PLAN, "E122")
    out["cost_room"] = cost_room()
    out["plan"], out["md5"] = "edges/plans/E122_xag_day_sessions.md", PLAN
    out["notes"] = ["opening-range vol gate: prior-day realized vol of hourly returns vs its rolling 250-day median "
                    "(min 60 days, the hourly file starts Jun 2024)", "fix-window variants have no stop/target (time exit), as planned"]
    for k, v in out["variants"].items():
        print(k, [(p, v[p].get("n"), v[p].get("mean_bp"), v[p].get("t_week")) for p in ("discovery",)])
    print(out.get("selection"), out["verdict"], out["cost_room"])
    X.save("E122", out)


if __name__ == "__main__":
    main()
