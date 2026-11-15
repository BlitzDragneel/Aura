"""E144 replication of the gold OI-confirmed move (plan md5 b8460baf...)."""
import json, sys, warnings
import numpy as np, pandas as pd
from edges.lib import bt
from edges.lead.e142_movement import bars15, features, simulate
from edges.lead.e143_positioning import positioning, tstats

warnings.filterwarnings("ignore")
PLAN = "b8460bafd1a3d5f96e51d6391f48dd87"
M = "/home/user/data/metrics/"
A1, A2, A3 = [pd.Timestamp(x, tz="UTC") for x in ("2026-06-01", "2026-09-01", "2026-11-14")]


def trades(fine, met, zk, mk, hold_bars, sk, tk, seed=None):
    f = bars15(fine)
    X, atr = features(f)
    P = positioning(met, f.index)
    ok = X.notna().all(axis=1)
    idx = X.index[ok]
    pos = fine.index.searchsorted(idx + pd.Timedelta("15min"))
    A = atr.reindex(idx).values
    r4 = (f.c / f.c.shift(16) - 1).reindex(idx).values
    a14 = (atr / f.c).reindex(idx).values
    d = np.nan_to_num(np.where((P.z_doi4.reindex(idx).values >= zk) & (np.abs(r4) >= mk * a14), np.sign(r4), 0)).astype(int)
    s = d != 0
    t, _ = simulate(fine, pos[s], A[s], dirs=d[s], arm=60, hold=hold_bars * 15, stop_k=sk, tgt_k=tk)
    if seed is None:
        return t
    rng = np.random.default_rng(seed)
    im = pd.Series(idx.strftime("%Y-%m"))
    mon = pd.Series(t.time.dt.strftime("%Y-%m")).value_counts()
    pick = np.sort(np.concatenate([rng.choice(np.flatnonzero((im == m).values), size=min(c * 5, int((im == m).sum())), replace=False) for m, c in mon.items()]))
    tc, _ = simulate(fine, pos[pick], A[pick], dirs=rng.choice([-1, 1], len(pick)), arm=60, hold=hold_bars * 15, stop_k=sk, tgt_k=tk)
    return t, tc


def main(xau):
    gold = pd.read_parquet(xau)[["o", "h", "l", "c", "v"]].astype(float)
    gm = pd.read_parquet(M + "XAUUSDT_metrics_5m.parquet")
    silver = pd.read_parquet(M + "XAG_perp_1m.parquet")
    sm = pd.read_parquet(M + "XAGUSDT_metrics_5m.parquet")
    res = dict(plan="edges/plans/E144_oi_move_replication.md", md5=PLAN, silver={}, gold_grid={}, pooled={})
    per = (("train", (pd.Timestamp("2026-01-01", tz="UTC"), A1)), ("val", (A1, A2)), ("final", (A2, A3)))
    keep = {}
    for hl, hb, sk, tk in (("4h", 16, 1.5, 3.0), ("24h", 96, 3.0, None)):
        t, tc = trades(silver, sm, 2.0, 2.0, hb, sk, tk, seed=144)
        keep[("XAG", hl)] = t
        res["silver"][hl] = {cn: {**{p: tstats(t, c, a, b) for p, (a, b) in per}, "control_final": tstats(tc, c, A2, A3)} for cn, c in (("base", 0.0004), ("tight", 0.0001))}
        for p in ("val", "final"):
            st = res["silver"][hl]["base"][p]
            bt.log_attempt(PLAN, f"E144 XAG P4 {hl}", p, dict(n=st.get("n"), mean_bp=st.get("mean_bp"), t_week=st.get("t_week")))
        print("SILVER", hl, res["silver"][hl], flush=True)
    for zk in (1.5, 2.0, 2.5):
        for mk in (1.5, 2.0, 3.0):
            t = trades(gold, gm, zk, mk, 16, 1.5, 3.0)
            if (zk, mk) == (2.0, 2.0):
                keep[("XAU", "4h")] = t
            r = {p: tstats(t, 0.0002, a, b) for p, (a, b) in per[1:]}
            res["gold_grid"][f"z{zk} m{mk}"] = r
            for p in r:
                bt.log_attempt(PLAN, f"E144 XAU P4 z{zk} m{mk}", p, dict(n=r[p].get("n"), mean_bp=r[p].get("mean_bp"), t_week=r[p].get("t_week")))
            print("GOLD grid", zk, mk, {p: (v.get("n"), v.get("mean_bp"), v.get("t_week")) for p, v in r.items()}, flush=True)
    g, s = keep[("XAU", "4h")].copy(), keep[("XAG", "4h")].copy()
    g["net"], s["net"] = g.gross - 0.0004, s.gross - 0.0008
    pool = pd.concat([g, s]).sort_values("time")
    for p, (a, b) in per[1:]:
        x = pool[(pool.time >= a) & (pool.time < b)]
        res["pooled"][p] = dict(n=int(len(x)), mean_bp=round(float(x.net.mean() * 1e4), 2), t_week=round(bt.tstat_weekly(x), 2), win=round(float((x.net > 0).mean()), 3))
    print("POOLED", res["pooled"])
    G = res["gold_grid"]
    plateau = sum((v["final"].get("mean_bp") or -1) > 0 for v in G.values()) >= 7 and sum((v["val"].get("mean_bp") or -1) > 0 for v in G.values()) >= 6
    sf = res["silver"]["4h"]["base"]["final"].get("mean_bp") or -1
    ok = sf > 0 and res["pooled"]["final"]["t_week"] >= 2 and res["pooled"]["val"]["mean_bp"] > 0 and plateau
    res["plateau"] = bool(plateau)
    res["verdict"] = "PROMOTE to grade B (paper)" if ok else ("DROP (silver final negative)" if sf < 0 else "stays grade C")
    json.dump(res, open("edges/results/E144_result.json", "w"), indent=1, default=str)
    print(res["verdict"], "plateau", plateau)


if __name__ == "__main__":
    main(sys.argv[1])
