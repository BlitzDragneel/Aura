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
    spec = core.instrument(sym)[1]
    F = fine.resample("15min").agg(agg).dropna()
    H1 = fine.resample("1h").agg(agg).dropna()
    e50, e200 = H1.c.ewm(span=50).mean(), H1.c.ewm(span=200).mean()
    tr1 = pd.Series(np.sign(e50 - e200).values, index=H1.index + pd.Timedelta("1h")).reindex(F.index + pd.Timedelta("15min"), method="ffill").values
    O, H, L, C = F.o.values, F.h.values, F.l.values, F.c.values
    A = lab.atr(F).values
    rng = H - L
    hh16 = pd.Series(H).rolling(16).max().shift(1).values; ll16 = pd.Series(L).rolling(16).min().shift(1).values
    f15 = np.asarray((F.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms"), dtype="int64")
    ft = np.asarray((fine.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms"), dtype="int64")
    FO, FH, FL, FC = fine.o.values, fine.h.values, fine.l.values, fine.c.values
    span = int(25 * 3600_000 / int(ft[1] - ft[0]))
    busy, rows = {}, []

    def take(rule, i, d, entry, stop, limit):
        """entry None = market at the next bar's open; else limit valid 16 bars."""
        t0 = f15[i] + 900_000
        if t0 < busy.get(rule, 0):
            return
        px = C[i]
        if entry is None:
            entry = O[i + 1] if i + 1 < len(O) else px
        R = abs(entry - stop)
        R = max(R, 0.002 * entry, 6 * (spec["spread"] if spec.get("spread") is not None else entry * spec["spread_frac"]))
        stop = entry - d * R
        tg = [entry + d * R * 0.5 * q for q in range(1, 6)]
        j = np.searchsorted(ft, t0)
        bars = [dict(t=int(ft[q]), o=FO[q], h=FH[q], l=FL[q], c=FC[q]) for q in range(j, min(j + span + 2000, len(ft)))]
        sg = core.Signal(sym, "buy" if d == 1 else "sell", int(t0), entry=(entry if limit else None), stop=stop, targets=tg)
        r = core.score(sg, bars, 4 if limit else 1, 24)
        if r.get("status") == "closed":
            rows.append(dict(time=pd.Timestamp(t0, unit="ms", tz="UTC"), rule=rule, R=r["ladder"]["R"]))
            busy[rule] = r["ladder"]["exit_ms"]
        elif r.get("status") == "not filled":
            busy[rule] = t0 + 4 * 3600_000

    for i in range(300, len(F) - 120):
        a = A[i]
        if not a > 0:
            continue
        tr = tr1[i]
        # F: FVG completed at bar i
        if L[i] > H[i - 2] and rng[i - 1] >= 1.5 * a:
            take("F", i, 1, (L[i] + H[i - 2]) / 2, H[i - 2] - 0.25 * a, True)
            if tr > 0: take("F-T", i, 1, (L[i] + H[i - 2]) / 2, H[i - 2] - 0.25 * a, True)
        if H[i] < L[i - 2] and rng[i - 1] >= 1.5 * a:
            take("F", i, -1, (H[i] + L[i - 2]) / 2, L[i - 2] + 0.25 * a, True)
            if tr < 0: take("F-T", i, -1, (H[i] + L[i - 2]) / 2, L[i - 2] + 0.25 * a, True)
        # O: displacement bar breaking structure
        body = abs(C[i] - O[i])
        if rng[i] >= 2 * a and body >= 0.6 * rng[i]:
            d = 1 if (C[i] > O[i] and C[i] > hh16[i]) else (-1 if (C[i] < O[i] and C[i] < ll16[i]) else 0)
            if d:
                k = i - 1
                while k > i - 8 and np.sign(C[k] - O[k]) != -d:
                    k -= 1
                if np.sign(C[k] - O[k]) == -d:
                    stop = (L[k] - 0.25 * a) if d == 1 else (H[k] + 0.25 * a)
                    take("O", i, d, O[k], stop, True)
                    if tr == d: take("O-T", i, d, O[k], stop, True)
        # L: sweep and reclaim
        if L[i] < ll16[i] - 0.1 * a and C[i] > ll16[i]:
            take("L", i, 1, None, L[i] - 0.25 * a, False)
            if tr > 0: take("L-T", i, 1, None, L[i] - 0.25 * a, False)
        if H[i] > hh16[i] + 0.1 * a and C[i] < hh16[i]:
            take("L", i, -1, None, H[i] + 0.25 * a, False)
            if tr < 0: take("L-T", i, -1, None, H[i] + 0.25 * a, False)
    return pd.DataFrame(rows)


P_G = {"val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-12-01")}
P_B = {"val": ("2025-01-01", "2025-07-01"), "final": ("2025-07-01", "2026-12-01")}
P_C = {"val": ("2026-01-01", "2026-06-01"), "final": ("2026-06-01", "2026-12-01")}
sets = [("XAUUSD", pd.read_parquet(sys.argv[1])[["o", "h", "l", "c"]].astype(float), P_G),
        ("BTCUSD", bt.load("BTCUSDT", "5m")[["o", "h", "l", "c"]].astype(float)["2024-01-01":], P_B),
        ("XAGUSD", pd.read_parquet(D + "XAG_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float), P_G),
        ("ETHUSD", k1m("ETH"), P_C), ("SOLUSD", k1m("SOL"), P_C)]
RULES = ["F", "F-T", "O", "O-T", "L", "L-T"]
res, pool = dict(plan="edges/plans/E153_smc.md", md5=PLAN, assets={}, pooled={}), []
for sym, fine, per in sets:
    T = run(sym, fine)
    res["assets"][sym] = {}
    for rule in RULES:
        x0 = T[T.rule == rule] if len(T) else T
        cell = {}
        for p, (a, b) in per.items():
            x = x0[(x0.time >= pd.Timestamp(a, tz="UTC")) & (x0.time < pd.Timestamp(b, tz="UTC"))]
            cell[p] = dict(n=int(len(x)), avg_R=round(float(x.R.mean()), 3) if len(x) else None, t=round(bt.tstat_weekly(x.assign(net=x.R)), 2) if len(x) > 5 else None, win=round(float((x.R > 0).mean()), 3) if len(x) else None)
            pool.append(x.assign(sym=sym, period=p))
            bt.log_attempt(PLAN, f"E153 {sym} {rule}", p, dict(n=cell[p]["n"], mean_bp=cell[p]["avg_R"], t_week=cell[p]["t"]))
        res["assets"][sym][rule] = cell
        print(sym, rule, {p: (c["n"], c["avg_R"], c["t"], c["win"]) for p, c in cell.items()}, flush=True)
Pn = pd.concat(pool)
ok = []
for rule in RULES:
    res["pooled"][rule] = {}
    for p in ("val", "final"):
        x = Pn[(Pn.rule == rule) & (Pn.period == p)].sort_values("time")
        res["pooled"][rule][p] = dict(n=int(len(x)), avg_R=round(float(x.R.mean()), 3), t=round(bt.tstat_weekly(x.assign(net=x.R)), 2), assets_positive=int((x.groupby("sym").R.mean() > 0).sum()))
    f, v = res["pooled"][rule]["final"], res["pooled"][rule]["val"]
    if f["avg_R"] > 0 and f["t"] >= 2 and f["assets_positive"] >= 4 and v["avg_R"] > 0:
        ok.append(rule)
    print("POOLED", rule, res["pooled"][rule], flush=True)
res["verdict"] = ("PASS " + ", ".join(ok)) if ok else "FAIL"
json.dump(res, open("edges/results/E153_result.json", "w"), indent=1, default=str); print(res["verdict"])
