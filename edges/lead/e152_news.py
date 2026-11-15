import json, re, sys, warnings
import numpy as np, pandas as pd
from edges.lib import bt
warnings.filterwarnings("ignore")
PLAN = sys.argv[2]
UP = ["Non-Farm Employment Change", "ADP Non-Farm Employment Change", "CPI m/m", "CPI y/y", "Core CPI m/m", "PPI m/m", "Core PPI m/m",
      "Core PCE Price Index m/m", "Average Hourly Earnings m/m", "Retail Sales m/m", "Core Retail Sales m/m", "ISM Manufacturing PMI",
      "ISM Services PMI", "Flash Manufacturing PMI", "Flash Services PMI", "JOLTS Job Openings", "Advance GDP q/q", "Federal Funds Rate"]
DN = ["Unemployment Rate", "Unemployment Claims"]


def num(x):
    if not isinstance(x, str):
        return np.nan
    m = re.match(r"^\s*(-?[\d.]+)\s*([KMBT%]?)", x)
    if not m:
        return np.nan
    v = float(m.group(1)); return v * {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}.get(m.group(2), 1)


d = pd.read_csv("/home/user/data/ff/high_impact_2020_2026.csv")
d = d[(d.Currency == "USD") & d.Event.isin(UP + DN)].copy()
d["t"] = pd.to_datetime(d.DateTime, utc=True)
d["a"], d["f"] = d.Actual.map(num), d.Forecast.map(num)
d = d.dropna(subset=["a", "f"])
d["s"] = np.sign(d.a - d.f) * np.where(d.Event.isin(DN), -1, 1)
ev = d.groupby("t").s.sum().apply(np.sign)
ev = ev[ev != 0]
print("events", len(ev), ev.index.min(), ev.index.max(), flush=True)

pax = pd.read_parquet("/tmp/claude-0/-home-user/375add60-6270-57b4-b1f1-bf3b645fa7c7/scratchpad/e140/dl/PAXG_1m.parquet")[["o", "c"]]
xau = pd.read_parquet(sys.argv[1])[["o", "c"]]
gold = pd.concat([pax, xau[xau.index > pax.index[-1]]])
btc = bt.load("BTCUSDT", "5m")[["o", "c"]]
PER = {"discovery": ("2021-01-01", "2024-01-01"), "val": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2026-03-01")}


def px_at(s, t):
    i = s.index.searchsorted(t)
    return (s.o.iloc[i], s.index[i]) if i < len(s) and s.index[i] - t < pd.Timedelta("6min") else (np.nan, None)


def trades(series, rule, hold):
    rows = []
    for t, sg in ev.items():
        if rule == "fade":
            t0 = t + pd.Timedelta("2min"); dr = -sg
        else:
            p0, _ = px_at(series, t); p5, _ = px_at(series, t + pd.Timedelta("5min"))
            if not (p0 > 0 and p5 > 0) or p5 == p0:
                continue
            t0 = t + pd.Timedelta("5min"); dr = np.sign(p5 - p0)
        a, ta = px_at(series, t0); b, tb = px_at(series, t0 + pd.Timedelta(minutes=hold))
        if a > 0 and b > 0:
            rows.append(dict(time=t, gross=dr * (b - a) / a))
    return pd.DataFrame(rows)


res = dict(plan="edges/plans/E152_news_surprise.md", md5=PLAN, n_events=int(len(ev)), cells={})
for name, series, costs in (("gold", gold, {"base": 0.001, "perp": 0.0002}), ("btc", btc, {"base": 0.0007})):
    for rule in ("fade", "follow5"):
        for hold in (60, 240):
            T = trades(series, rule, hold)
            key = f"{name} {rule} {hold}m"
            res["cells"][key] = {}
            for p, (a, b) in PER.items():
                x = T[(T.time >= pd.Timestamp(a, tz="UTC")) & (T.time < pd.Timestamp(b, tz="UTC"))]
                cell = dict(n=int(len(x)), gross_bp=round(float(x.gross.mean() * 1e4), 1) if len(x) else None, right=round(float((x.gross > 0).mean()), 3) if len(x) else None)
                for cn, c in costs.items():
                    y = x.assign(net=x.gross - 2 * c)
                    cell[f"net_bp_{cn}"] = round(float(y.net.mean() * 1e4), 1) if len(y) else None
                    cell[f"t_{cn}"] = round(bt.tstat_weekly(y), 2) if len(y) > 5 else None
                res["cells"][key][p] = cell
                if p != "discovery":
                    bt.log_attempt(PLAN, f"E152 {key}", p, dict(n=cell["n"], mean_bp=cell["net_bp_base"], t_week=cell["t_base"]))
            print(key, {p: (c["n"], c["gross_bp"], c["net_bp_base"], c["t_base"], c["right"]) for p, c in res["cells"][key].items()}, flush=True)
ok = [k for k, v in res["cells"].items() if (v["final"]["net_bp_base"] or -1) > 0 and (v["final"]["t_base"] or 0) >= 2 and (v["val"]["net_bp_base"] or -1) > 0 and (v["val"]["t_base"] or 0) >= 1.5]
res["verdict"] = ("PASS " + ", ".join(ok)) if ok else "FAIL"
json.dump(res, open("edges/results/E152_result.json", "w"), indent=1, default=str); print(res["verdict"])
