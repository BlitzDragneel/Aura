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


def run(sym, fine, start):
    F = fine.resample("15min").agg(agg).dropna(); H1 = fine.resample("1h").agg(agg).dropna()
    ft = np.asarray((fine.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms"), dtype="int64")
    FO, FH, FL, FC = fine.o.values, fine.h.values, fine.l.values, fine.c.values
    span = int(25 * 3600_000 / int(ft[1] - ft[0])); h1_end = (H1.index + pd.Timedelta("1h")).values
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
            j = np.searchsorted(ft, ctx["bar_close_ms"])
            bars = [dict(t=int(ft[q]), o=FO[q], h=FH[q], l=FL[q], c=FC[q]) for q in range(j, min(j + span, len(ft)))]
            row = dict(time=end, setup=setup)
            for mode in (False, True):
                lab.ADAPTIVE_TP = mode
                s = lab.make(sym, setup, d, why, ctx)
                r = core.score(core.Signal(sym, s["side"], s["logged_ms"], stop=s["stop"], targets=s["targets"]), bars, 1, 24)
                if r.get("status") != "closed":
                    break
                row["R_ad" if mode else "R_fix"] = r["ladder"]["R"]
                row["tp1_ad" if mode else "tp1_fix"] = r["ladder"]["outcome"].startswith("TP")
            else:
                rows.append(row)
    return pd.DataFrame(rows)


P_G = {"val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-12-01")}
P_B = {"val": ("2025-01-01", "2025-07-01"), "final": ("2025-07-01", "2026-12-01")}
P_C = {"val": ("2026-01-01", "2026-06-01"), "final": ("2026-06-01", "2026-12-01")}
sets = [("XAUUSD", pd.read_parquet(sys.argv[1])[["o", "h", "l", "c"]].astype(float), "2026-06-01", P_G),
        ("BTCUSD", bt.load("BTCUSDT", "5m")[["o", "h", "l", "c"]].astype(float)["2024-12-01":], "2025-01-01", P_B),
        ("ETHUSD", k1m("ETH"), "2026-01-01", P_C)]
res, pool = dict(plan="edges/plans/E155_adaptive_targets.md", md5=PLAN, assets={}, pooled={}), []
for sym, fine, start, per in sets:
    T = run(sym, fine, start)
    res["assets"][sym] = {}
    for p, (a, b) in per.items():
        x = T[(T.time >= pd.Timestamp(a, tz="UTC")) & (T.time < pd.Timestamp(b, tz="UTC"))]
        res["assets"][sym][p] = dict(n=int(len(x)), fixed=round(float(x.R_fix.mean()), 3), adaptive=round(float(x.R_ad.mean()), 3),
                                     tp1_fixed=round(float(x.tp1_fix.mean()), 3), tp1_adaptive=round(float(x.tp1_ad.mean()), 3),
                                     t_adaptive=round(bt.tstat_weekly(x.assign(net=x.R_ad)), 2))
        pool.append(x.assign(sym=sym, period=p))
        bt.log_attempt(PLAN, f"E155 {sym} adaptive", p, dict(n=len(x), mean_bp=res["assets"][sym][p]["adaptive"], t_week=res["assets"][sym][p]["t_adaptive"]))
    print(sym, res["assets"][sym], flush=True)
Pn = pd.concat(pool)
for p in ("val", "final"):
    x = Pn[Pn.period == p].sort_values("time")
    res["pooled"][p] = dict(n=int(len(x)), fixed=round(float(x.R_fix.mean()), 3), adaptive=round(float(x.R_ad.mean()), 3),
                            tp1_fixed=round(float(x.tp1_fix.mean()), 3), tp1_adaptive=round(float(x.tp1_ad.mean()), 3),
                            t_adaptive=round(bt.tstat_weekly(x.assign(net=x.R_ad)), 2))
print("POOLED", res["pooled"])
res["adopt"] = bool(res["pooled"]["final"]["adaptive"] >= res["pooled"]["final"]["fixed"] - 0.02)
json.dump(res, open("edges/results/E155_result.json", "w"), indent=1, default=str); print("ADOPT" if res["adopt"] else "KEEP FIXED")
