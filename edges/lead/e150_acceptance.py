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


def run(sym, fine):
    F = fine.resample("15min").agg(agg).dropna()
    H1 = fine.resample("1h").agg(agg).dropna()
    a15 = lab.atr(F).values
    r1h = lab.atr(H1).reindex(F.index, method="ffill").shift(4).values     # last fully closed hourly ATR
    hh = F.h.rolling(16).max().shift(1).values
    ll = F.l.rolling(16).min().shift(1).values
    C = F.c.values
    ft = np.asarray((fine.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms"), dtype="int64")
    FO, FH, FL, FC = fine.o.values, fine.h.values, fine.l.values, fine.c.values
    step = int(ft[1] - ft[0]); span = int(25 * 3600_000 / step)
    f15 = np.asarray((F.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms"), dtype="int64")
    rows, busy = [], {k: 0 for k in ("accepted", "rejected", "follow_now", "fade_now")}

    def trade(rule, t_ms, d, px, R):
        if t_ms < busy[rule]:
            return
        s = lab.make(sym, "S2", d, rule, dict(price=px, R=R, bar_close_ms=int(t_ms), state={}))
        j = np.searchsorted(ft, t_ms)
        bars = [dict(t=int(ft[q]), o=FO[q], h=FH[q], l=FL[q], c=FC[q]) for q in range(j, min(j + span, len(ft)))]
        r = core.score(core.Signal(sym, s["side"], int(t_ms), stop=s["stop"], targets=s["targets"]), bars, 1, 24)
        if r.get("status") == "closed":
            rows.append(dict(time=pd.Timestamp(t_ms, unit="ms", tz="UTC"), rule=rule, R=r["ladder"]["R"]))
            busy[rule] = t_ms + 4 * 3600_000

    for i in range(120, len(F) - 100):
        A, R = a15[i], r1h[i]
        if not (A > 0 and R > 0):
            continue
        d = 1 if C[i] > hh[i] + 0.1 * A else (-1 if C[i] < ll[i] - 0.1 * A else 0)
        if not d:
            continue
        lvl = hh[i] if d == 1 else ll[i]
        t0 = f15[i] + 900_000                       # break bar closes
        trade("follow_now", t0, d, C[i], R)
        trade("fade_now", t0, -d, C[i], R)
        j0, j1 = np.searchsorted(ft, t0), np.searchsorted(ft, t0 + 900_000)
        if j1 - j0 < 2:
            continue
        last = FC[j1 - 1]
        held = (FL[j0:j1].min() > lvl) if d == 1 else (FH[j0:j1].max() < lvl)
        if held and d * (last - C[i]) >= 0.25 * A:
            trade("accepted", t0 + 900_000, d, last, R)
        elif d * (last - lvl) < 0:
            trade("rejected", t0 + 900_000, -d, last, R)
    return pd.DataFrame(rows)


P_G = {"val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-12-01")}
P_B = {"val": ("2025-01-01", "2025-07-01"), "final": ("2025-07-01", "2026-12-01")}
P_C = {"val": ("2026-01-01", "2026-06-01"), "final": ("2026-06-01", "2026-12-01")}
sets = [("XAUUSD", pd.read_parquet(sys.argv[1])[["o", "h", "l", "c"]].astype(float), P_G),
        ("BTCUSD", bt.load("BTCUSDT", "5m")[["o", "h", "l", "c"]].astype(float)["2024-01-01":], P_B),
        ("XAGUSD", pd.read_parquet(D + "XAG_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float), P_G),
        ("ETHUSD", k1m("ETH"), P_C), ("SOLUSD", k1m("SOL"), P_C)]
res = dict(plan="edges/plans/E150_break_acceptance.md", md5=PLAN, assets={}, pooled={})
pool = []
for sym, fine, per in sets:
    T = run(sym, fine)
    res["assets"][sym] = {}
    for rule in ("accepted", "rejected", "follow_now", "fade_now"):
        x = T[T.rule == rule]
        cell = {}
        for p, (a, b) in per.items():
            s = x[(x.time >= pd.Timestamp(a, tz="UTC")) & (x.time < pd.Timestamp(b, tz="UTC"))]
            cell[p] = dict(n=int(len(s)), avg_R=round(float(s.R.mean()), 3) if len(s) else None, t=round(bt.tstat_weekly(s.assign(net=s.R)), 2) if len(s) > 5 else None,
                           win=round(float((s.R > 0).mean()), 3) if len(s) else None)
            pool.append(s.assign(sym=sym, period=p))
            bt.log_attempt(PLAN, f"E150 {sym} {rule}", p, dict(n=cell[p]["n"], mean_bp=cell[p]["avg_R"], t_week=cell[p]["t"]))
        res["assets"][sym][rule] = cell
        print(sym, rule, {p: (c["n"], c["avg_R"], c["t"], c["win"]) for p, c in cell.items()}, flush=True)
Pn = pd.concat(pool)
passed = []
for rule in ("accepted", "rejected", "follow_now", "fade_now"):
    res["pooled"][rule] = {}
    for p in ("val", "final"):
        s = Pn[(Pn.rule == rule) & (Pn.period == p)].sort_values("time")
        res["pooled"][rule][p] = dict(n=int(len(s)), avg_R=round(float(s.R.mean()), 3), t=round(bt.tstat_weekly(s.assign(net=s.R)), 2),
                                      assets_positive=int((s.groupby("sym").R.mean() > 0).sum()))
    print("POOLED", rule, res["pooled"][rule], flush=True)
for rule, ctrl in (("accepted", "follow_now"), ("rejected", "fade_now")):
    f_, v = res["pooled"][rule]["final"], res["pooled"][rule]["val"]
    if f_["avg_R"] > 0 and f_["t"] >= 2 and f_["assets_positive"] >= 4 and v["avg_R"] > 0 and f_["avg_R"] > res["pooled"][ctrl]["final"]["avg_R"]:
        passed.append(rule)
res["verdict"] = ("PASS: " + ", ".join(passed)) if passed else "FAIL"
json.dump(res, open("edges/results/E150_result.json", "w"), indent=1, default=str)
print(res["verdict"])
