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
    H4 = fine.resample("4h").agg(agg).dropna(); D1 = fine.resample("1D").agg(agg).dropna()
    t4 = pd.Series(np.sign(H4.c.ewm(span=20).mean() - H4.c.ewm(span=50).mean()).values, index=H4.index + pd.Timedelta("4h"))
    td = pd.Series(np.sign(D1.c - D1.c.rolling(20).mean()).values, index=D1.index + pd.Timedelta("1D"))
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
        a4 = t4[t4.index <= end]; ad = td[td.index <= end]
        if not len(a4) or not len(ad):
            continue
        g4, gd = a4.iloc[-1], ad.iloc[-1]
        for setup, d, why in found:
            if (setup, str(end.date())) in seen:
                continue
            seen.add((setup, str(end.date())))
            s = lab.make(sym, setup, d, why, ctx)
            j = np.searchsorted(ft, s["logged_ms"])
            bars = [dict(t=int(ft[q]), o=FO[q], h=FH[q], l=FL[q], c=FC[q]) for q in range(j, min(j + span, len(ft)))]
            r = core.score(core.Signal(sym, s["side"], s["logged_ms"], stop=s["stop"], targets=s["targets"]), bars, 1, 24)
            if r.get("status") == "closed":
                grp = "AGREE" if (g4 == d and gd == d) else ("CONFLICT" if (g4 == -d and gd == -d) else "MIXED")
                rows.append(dict(time=end, setup=setup, group=grp, R=r["ladder"]["R"]))
    return pd.DataFrame(rows)


P_G = {"val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-12-01")}
P_B = {"val": ("2025-01-01", "2025-07-01"), "final": ("2025-07-01", "2026-12-01")}
P_C = {"val": ("2026-01-01", "2026-06-01"), "final": ("2026-06-01", "2026-12-01")}
sets = [("XAUUSD", pd.read_parquet(sys.argv[1])[["o", "h", "l", "c"]].astype(float), "2025-12-15", P_G),
        ("BTCUSD", bt.load("BTCUSDT", "5m")[["o", "h", "l", "c"]].astype(float)["2023-11-01":], "2024-01-01", P_B),
        ("XAGUSD", pd.read_parquet(D + "XAG_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float), "2026-02-12", P_G),
        ("ETHUSD", k1m("ETH"), "2025-07-05", P_C), ("SOLUSD", k1m("SOL"), "2025-07-05", P_C)]
res, pool = dict(plan="edges/plans/E154_htf_filter.md", md5=PLAN, assets={}, pooled={}), []
for sym, fine, start, per in sets:
    T = run(sym, fine, start)
    res["assets"][sym] = {}
    for g in ("AGREE", "MIXED", "CONFLICT"):
        cell = {}
        for p, (a, b) in per.items():
            x = T[(T.group == g) & (T.time >= pd.Timestamp(a, tz="UTC")) & (T.time < pd.Timestamp(b, tz="UTC"))]
            cell[p] = dict(n=int(len(x)), avg_R=round(float(x.R.mean()), 3) if len(x) else None, t=round(bt.tstat_weekly(x.assign(net=x.R)), 2) if len(x) > 5 else None)
            pool.append(x.assign(sym=sym, period=p))
            bt.log_attempt(PLAN, f"E154 {sym} {g}", p, dict(n=cell[p]["n"], mean_bp=cell[p]["avg_R"], t_week=cell[p]["t"]))
        res["assets"][sym][g] = cell
        print(sym, g, {p: (c["n"], c["avg_R"], c["t"]) for p, c in cell.items()}, flush=True)
Pn = pd.concat(pool)
for g in ("AGREE", "MIXED", "CONFLICT"):
    res["pooled"][g] = {}
    for p in ("val", "final"):
        x = Pn[(Pn.group == g) & (Pn.period == p)].sort_values("time")
        res["pooled"][g][p] = dict(n=int(len(x)), avg_R=round(float(x.R.mean()), 3), t=round(bt.tstat_weekly(x.assign(net=x.R)), 2), assets_positive=int((x.groupby("sym").R.mean() > 0).sum()))
    print("POOLED", g, res["pooled"][g], flush=True)
A, C = res["pooled"]["AGREE"], res["pooled"]["CONFLICT"]
v = "PASS" if A["final"]["avg_R"] > 0 and A["final"]["t"] >= 2 and A["final"]["assets_positive"] >= 4 and A["val"]["avg_R"] > 0 else "FAIL"
res["mute_conflict"] = bool(C["final"]["avg_R"] < 0 and C["val"]["avg_R"] < 0 and C["final"]["t"] <= -2 and C["val"]["t"] <= -2)
res["verdict"] = v + ("; CONFLICT muted" if res["mute_conflict"] else "")
json.dump(res, open("edges/results/E154_result.json", "w"), indent=1, default=str); print(res["verdict"])
