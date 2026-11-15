"""E151 stop-and-reverse (plan edges/plans/E151_stop_and_reverse.md)."""
import glob, json, sys, warnings, zipfile
import numpy as np, pandas as pd
from edges.lib import bt
from edges.siglab import lab
from edges.siglab.replay import agg
from edges.auditor import core
warnings.filterwarnings("ignore")
PLAN = sys.argv[2]
D = "/home/user/data/metrics/"


def k1m(s):
    parts = []
    for f in sorted(glob.glob(f"{D}e145/{s}USDT-1m-*.zip")):
        with zipfile.ZipFile(f) as z:
            k = pd.read_csv(z.open(z.namelist()[0]), header=None)
            if not str(k.iloc[0, 0]).isdigit():
                k = k.iloc[1:]
            parts.append(k.iloc[:, :5].astype(float))
    k = pd.concat(parts); k.columns = ["t", "o", "h", "l", "c"]; k.index = pd.to_datetime(k.t.astype("int64"), unit="ms", utc=True)
    return k[~k.index.duplicated()].sort_index()[["o", "h", "l", "c"]]


def run(sym, fine, start, rng):
    F = fine.resample("15min").agg(agg).dropna(); H1 = fine.resample("1h").agg(agg).dropna()
    ft = np.asarray((fine.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms"), dtype="int64")
    FO, FH, FL, FC = fine.o.values, fine.h.values, fine.l.values, fine.c.values
    span = int(25 * 3600_000 / int(ft[1] - ft[0])); h1_end = (H1.index + pd.Timedelta("1h")).values
    bars_at = lambda j: [dict(t=int(ft[q]), o=FO[q], h=FH[q], l=FL[q], c=FC[q]) for q in range(j, min(j + span, len(ft)))]
    seen, rows = set(), []
    for i in range(max(300, F.index.searchsorted(pd.Timestamp(start, tz="UTC"))), len(F) - 100):
        f = F.iloc[i - 299:i + 1]; end = f.index[-1] + pd.Timedelta("15min")
        k = np.searchsorted(h1_end, end.to_datetime64(), side="right")
        found, ctx = lab.detect(f, H1.iloc[max(0, k - 60):k])
        if not ctx:
            continue
        for setup, d, why in found:
            if (setup, str(end.date())) in seen:
                continue
            seen.add((setup, str(end.date())))
            s = lab.make(sym, setup, d, why, ctx)
            r = core.score(core.Signal(sym, s["side"], s["logged_ms"], stop=s["stop"], targets=s["targets"]), bars_at(np.searchsorted(ft, s["logged_ms"])), 1, 24)
            if r.get("status") != "closed" or r["ladder"]["outcome"] != "SL":
                continue
            t_ms, R, px = r["ladder"]["exit_ms"] + 60_000, s["R"], s["stop"]
            for kind, dd in (("reverse", -d), ("random", int(rng.choice([-1, 1])))):
                tg = [px + dd * R * 0.5 * q for q in range(1, 6)]
                rv = core.score(core.Signal(sym, "buy" if dd == 1 else "sell", int(t_ms), entry=None, stop=px - dd * R, targets=tg), bars_at(np.searchsorted(ft, t_ms)), 1, 24)
                if rv.get("status") == "closed":
                    rows.append(dict(time=pd.Timestamp(t_ms, unit="ms", tz="UTC"), kind=kind, setup=setup, R=rv["ladder"]["R"]))
    return pd.DataFrame(rows)


P_G = {"val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-12-01")}
P_B = {"val": ("2025-01-01", "2025-07-01"), "final": ("2025-07-01", "2026-12-01")}
P_C = {"val": ("2026-01-01", "2026-06-01"), "final": ("2026-06-01", "2026-12-01")}
rng = np.random.default_rng(151)
sets = [("XAUUSD", pd.read_parquet(sys.argv[1])[["o", "h", "l", "c"]].astype(float), "2025-12-15", P_G),
        ("BTCUSD", bt.load("BTCUSDT", "5m")[["o", "h", "l", "c"]].astype(float)["2023-12-20":], "2024-01-01", P_B),
        ("XAGUSD", pd.read_parquet(D + "XAG_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float), "2026-01-12", P_G),
        ("ETHUSD", k1m("ETH"), "2025-06-05", P_C), ("SOLUSD", k1m("SOL"), "2025-06-05", P_C)]
res, pool = dict(plan="edges/plans/E151_stop_and_reverse.md", md5=PLAN, assets={}, pooled={}), []
for sym, fine, start, per in sets:
    T = run(sym, fine, start, rng)
    res["assets"][sym] = {}
    for kind in ("reverse", "random"):
        res["assets"][sym][kind] = {}
        for p, (a, b) in per.items():
            x = T[(T.kind == kind) & (T.time >= pd.Timestamp(a, tz="UTC")) & (T.time < pd.Timestamp(b, tz="UTC"))]
            res["assets"][sym][kind][p] = dict(n=int(len(x)), avg_R=round(float(x.R.mean()), 3) if len(x) else None, t=round(bt.tstat_weekly(x.assign(net=x.R)), 2) if len(x) > 5 else None, win=round(float((x.R > 0).mean()), 3) if len(x) else None)
            pool.append(x.assign(sym=sym, period=p))
            if kind == "reverse":
                bt.log_attempt(PLAN, f"E151 {sym} reverse", p, dict(n=len(x), mean_bp=res["assets"][sym][kind][p]["avg_R"], t_week=res["assets"][sym][kind][p]["t"]))
        print(sym, kind, res["assets"][sym][kind], flush=True)
Pn = pd.concat(pool)
for kind in ("reverse", "random"):
    res["pooled"][kind] = {}
    for p in ("val", "final"):
        x = Pn[(Pn.kind == kind) & (Pn.period == p)].sort_values("time")
        res["pooled"][kind][p] = dict(n=int(len(x)), avg_R=round(float(x.R.mean()), 3), t=round(bt.tstat_weekly(x.assign(net=x.R)), 2), assets_positive=int((x.groupby("sym").R.mean() > 0).sum()))
    print("POOLED", kind, res["pooled"][kind], flush=True)
f, v, c = res["pooled"]["reverse"]["final"], res["pooled"]["reverse"]["val"], res["pooled"]["random"]["final"]
res["verdict"] = "PASS" if f["avg_R"] > 0 and f["t"] >= 2 and f["assets_positive"] >= 4 and v["avg_R"] > 0 and f["avg_R"] > c["avg_R"] else "FAIL"
json.dump(res, open("edges/results/E151_result.json", "w"), indent=1, default=str); print(res["verdict"])
