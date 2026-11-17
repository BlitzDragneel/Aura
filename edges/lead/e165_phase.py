"""E165 follow or fade by market phase (plan edges/plans/E165_follow_or_fade_by_phase.md).
Usage: python -m edges.lead.e165_phase replay SYM   (writes the both-sides replay)  |  python -m edges.lead.e165_phase eval"""
import json, sys, warnings
import numpy as np, pandas as pd
from edges.lib import bt
from edges.siglab import lab
from edges.auditor import core
warnings.filterwarnings("ignore")
PLAN = "5216aad5ac094eb2e3d9798e33fb737f"
OUT = "/tmp/claude-0/-home-user/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/e165"
agg = dict(o="first", h="max", l="min", c="last")
SP = "/tmp/claude-0/-home-user/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/e140/dl/"
D = "/home/user/data/metrics/"
P1 = {"disc": ("2026-01-01", "2026-06-01"), "val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-12-01")}
P2 = {"disc": ("2025-06-01", "2026-01-01"), "val": ("2026-01-01", "2026-06-01"), "final": ("2026-06-01", "2026-12-01")}
PB = {"disc": ("2024-01-01", "2025-01-01"), "val": ("2025-01-01", "2025-07-01"), "final": ("2025-07-01", "2026-12-01")}


def data(sym):
    if sym == "XAUUSD":
        return pd.read_parquet(SP + "XAU_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float), "2025-12-20", P1
    if sym == "XAGUSD":
        return pd.read_parquet(D + "XAG_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float), "2026-01-12", P1
    if sym == "BTCUSD":
        return bt.load("BTCUSDT", "5m")[["o", "h", "l", "c"]].astype(float)["2023-12-20":], "2024-01-01", PB


def k1m(s):
    import glob, zipfile
    parts = []
    for f in sorted(glob.glob(f"{D}e145/{s}USDT-1m-*.zip")):
        with zipfile.ZipFile(f) as z:
            k = pd.read_csv(z.open(z.namelist()[0]), header=None)
            if not str(k.iloc[0, 0]).isdigit():
                k = k.iloc[1:]
            parts.append(k.iloc[:, :5].astype(float))
    k = pd.concat(parts); k.columns = ["t", "o", "h", "l", "c"]; k.index = pd.to_datetime(k.t.astype("int64"), unit="ms", utc=True)
    return k[~k.index.duplicated()].sort_index()[["o", "h", "l", "c"]]


def replay_both(sym):
    if sym in ("ETHUSD", "SOLUSD"):
        fine, start, per = k1m(sym[:3]), "2025-06-05", P2
    else:
        fine, start, per = data(sym)
    F = fine.resample("15min").agg(agg).dropna()
    H1 = fine.resample("1h").agg(agg).dropna()
    ft = np.asarray((fine.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms"), dtype="int64")
    FO, FH, FL, FC = fine.o.values, fine.h.values, fine.l.values, fine.c.values
    span = int(25 * 3600_000 / int(ft[1] - ft[0]))
    h1_end = (H1.index + pd.Timedelta("1h")).values
    # phase (past only, hourly)
    c = H1.c
    eff = (c - c.shift(120)).abs() / c.diff().abs().rolling(120).sum()
    sma20d = c.rolling(480).mean()
    wk = np.sign(c - c.shift(168))
    seen, rows = set(), []
    i0 = max(300, F.index.searchsorted(pd.Timestamp(start, tz="UTC")))
    for i in range(i0, len(F) - 100):
        f = F.iloc[i - 299:i + 1]
        end = f.index[-1] + pd.Timedelta("15min")
        k = np.searchsorted(h1_end, end.to_datetime64(), side="right")
        found, ctx = lab.detect(f, H1.iloc[max(0, k - 60):k])
        if not ctx:
            continue
        for setup, d, why in found:
            if (setup, str(end.date())) in seen:
                continue
            seen.add((setup, str(end.date())))
            s = lab.make(sym, setup, d, why, ctx)
            j = np.searchsorted(ft, s["logged_ms"])
            bars = [dict(t=int(ft[q]), o=FO[q], h=FH[q], l=FL[q], c=FC[q]) for q in range(j, min(j + span, len(ft)))]
            ref = s["ref_price"]
            a = core.score(core.Signal(sym, s["side"], s["logged_ms"], stop=s["stop"], targets=s["targets"]), bars, 1, 24)
            fs = "sell" if s["side"] == "buy" else "buy"
            b = core.score(core.Signal(sym, fs, s["logged_ms"], stop=2 * ref - s["stop"], targets=[2 * ref - t for t in s["targets"]]), bars, 1, 24)
            if a.get("status") == "closed" and b.get("status") == "closed":
                h = k - 1
                dr = 1 if s["side"] == "buy" else -1
                rows.append(dict(time=end, sym=sym, setup=setup, side="with" if s["state"]["with_trend"] else "against",
                                 R=a["ladder"]["R"], R_flip=b["ladder"]["R"],
                                 close_ms=max(a["ladder"]["exit_ms"] or 0, b["ladder"]["exit_ms"] or 0),
                                 eff5d=float(eff.iloc[h]) if h >= 0 else np.nan,
                                 vs20d=float(np.sign(c.iloc[h] - sma20d.iloc[h]) * dr) if h >= 0 else np.nan,
                                 vs1w=float(wk.iloc[h] * dr) if h >= 0 else np.nan))
        if i % 5000 == 0:
            print(sym, end, len(rows), flush=True)
    T = pd.DataFrame(rows); T.to_parquet(f"{OUT}/{sym}.parquet"); print(sym, "done", len(T))


PER = {"XAUUSD": P1, "XAGUSD": P1, "BTCUSD": PB, "ETHUSD": P2, "SOLUSD": P2}


def period(T, sym):
    p = pd.Series("pre", index=T.index)
    for name, (a, b) in PER[sym].items():
        p[(T.time >= pd.Timestamp(a, tz="UTC")) & (T.time < pd.Timestamp(b, tz="UTC"))] = name
    return p


def online(T, n=20, skip_neg=False, rng=None):
    """Side chosen from the last n CLOSED signals of the same market x setup (closed before this signal)."""
    out = np.full(len(T), np.nan)
    for (sym, setup), g in T.groupby(["sym", "setup"]):
        g = g.sort_values("time")
        tms = g.time.values.astype("datetime64[ms]").astype("int64")
        cl, R, Rf = g.close_ms.values, g.R.values, g.R_flip.values
        if rng is not None:
            perm = rng.permutation(len(g)); R, Rf = R[perm], Rf[perm]
        for j, idx in enumerate(g.index):
            done = np.where(cl[:j] < tms[j])[0][-n:]
            if len(done) < 10:
                continue
            a, b = R[done].mean(), Rf[done].mean()
            if skip_neg and max(a, b) < 0:
                continue
            out[T.index.get_loc(idx)] = g.R.at[idx] if a >= b else g.R_flip.at[idx]
    return out


def stat(x, t):
    x = pd.Series(x, index=t.index).dropna()
    if len(x) < 8:
        return dict(n=int(len(x)))
    tt = t.loc[x.index]
    return dict(n=int(len(x)), avg_R=round(float(x.mean()), 3), t=round(float(bt.tstat_weekly(pd.DataFrame(dict(time=tt.time, net=x.values)))), 2))


def evaluate():
    T = pd.concat([pd.read_parquet(f"{OUT}/{s}.parquet") for s in PER if __import__("os").path.exists(f"{OUT}/{s}.parquet")], ignore_index=True)
    T["per"] = pd.concat([period(g, s) for s, g in T.groupby("sym")]).reindex(T.index)
    T["eff_t"] = np.nan
    for s, g in T.groupby("sym"):
        q = g[g.per == "disc"].eff5d.quantile([1 / 3, 2 / 3]).values
        T.loc[g.index, "eff_t"] = np.digitize(g.eff5d, q)
    D_ = T[T.per == "disc"]
    rule = {}
    for key, g in D_.groupby(["setup", "side", "eff_t"]):
        fo, fa = g.R.mean(), g.R_flip.mean()
        rule[key] = "follow" if fo > 0.05 and fo >= fa else "fade" if fa > 0.05 and fa > fo else "skip"
    act = T.apply(lambda r: rule.get((r.setup, r.side, r.eff_t), "skip"), axis=1)
    T["R1"] = np.where(act == "follow", T.R, np.where(act == "fade", T.R_flip, np.nan))
    T["R2"] = online(T); T["R3"] = online(T, skip_neg=True); T["R2_shuf"] = online(T, rng=np.random.default_rng(165))
    T["follow"], T["fade"] = T.R, T.R_flip
    res = dict(plan="edges/plans/E165_follow_or_fade_by_phase.md", md5=PLAN, rule={f"{k[0]} {k[1]} eff{int(k[2])}": v for k, v in rule.items()}, pooled={}, by_market={})
    for v in ("follow", "fade", "R1", "R2", "R3", "R2_shuf"):
        res["pooled"][v] = {p: stat(T[v][T.per == p], T[T.per == p]) for p in ("disc", "val", "final")}
        for p in ("val", "final"):
            bt.log_attempt(PLAN, f"E165 pooled {v}", p, dict(n=res["pooled"][v][p].get("n"), mean_bp=res["pooled"][v][p].get("avg_R"), t_week=res["pooled"][v][p].get("t")))
        res["by_market"][v] = {s: stat(g[v][g.per == "final"], g[g.per == "final"]).get("avg_R") for s, g in T.groupby("sym")}
        print(v, res["pooled"][v], res["by_market"][v], flush=True)
    # by phase, descriptive: which phase makes fakeouts (pooled VAL+FINAL)
    V = T[T.per.isin(["val", "final"])]
    res["fakeout_table"] = {f"{k[0]} {k[1]} eff{int(k[2])}": [round(float(g.R.mean()), 3), round(float(g.R_flip.mean()), 3), int(len(g))]
                            for k, g in V.groupby(["setup", "side", "eff_t"]) if len(g) >= 20}
    ok = [v for v in ("R1", "R2", "R3") if (res["pooled"][v]["final"].get("avg_R") or -1) > 0 and (res["pooled"][v]["final"].get("t") or 0) >= 2
          and (res["pooled"][v]["val"].get("avg_R") or -1) > 0 and sum((x or -1) > 0 for x in res["by_market"][v].values()) >= 3]
    res["verdict"] = "PASS " + ", ".join(ok) if ok else "FAIL"
    json.dump(res, open("edges/results/E165_result.json", "w"), indent=1, default=str); print(res["verdict"])


if __name__ == "__main__":
    import os; os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == "replay":
        replay_both(sys.argv[2])
    else:
        evaluate()
