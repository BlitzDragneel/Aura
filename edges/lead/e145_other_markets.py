"""E145 OI-confirmed move on other markets (plan md5 2b55cb6a...)."""
import glob, json, warnings, zipfile
import numpy as np, pandas as pd
from edges.lib import bt
from edges.lead.e144_oi_replication import trades

warnings.filterwarnings("ignore")
PLAN = "2b55cb6a6c91b54a8775215725cb534f"
D = "/home/user/data/metrics/e145/"
G = {"COMMODITY": ["XPT", "XPD", "COPPER", "NATGAS", "CL"], "INDEX": ["QQQ", "SPY"], "CRYPTO": ["ETH", "SOL"]}


def load(s):
    mp, kp = [], []
    for f in sorted(glob.glob(f"{D}{s}USDT-metrics-*.zip")):
        with zipfile.ZipFile(f) as z:
            mp.append(pd.read_csv(z.open(z.namelist()[0])))
    m = pd.concat(mp); m.index = pd.to_datetime(m.create_time, utc=True).dt.floor("5min")
    m = m[~m.index.duplicated()].sort_index().drop(columns=["create_time", "symbol"]).apply(pd.to_numeric, errors="coerce")
    m.columns = ["oi", "oiv", "top_acct", "top_pos", "crowd", "taker"]
    for f in sorted(glob.glob(f"{D}{s}USDT-1m-*.zip")):
        with zipfile.ZipFile(f) as z:
            k = pd.read_csv(z.open(z.namelist()[0]), header=None)
            if not str(k.iloc[0, 0]).isdigit():
                k = k.iloc[1:]
            kp.append(k.iloc[:, :6].astype(float))
    k = pd.concat(kp); k.columns = ["t", "o", "h", "l", "c", "v"]; k.index = pd.to_datetime(k.t.astype("int64"), unit="ms", utc=True)
    return k[~k.index.duplicated()].sort_index()[["o", "h", "l", "c", "v"]], m


def st(t, cost):
    if len(t) < 5:
        return dict(n=int(len(t)))
    x = t.assign(net=t.gross - 2 * cost)
    return dict(n=int(len(x)), mean_bp=round(float(x.net.mean() * 1e4), 2), t_week=round(bt.tstat_weekly(x), 2), win=round(float((x.net > 0).mean()), 3))


res = dict(plan="edges/plans/E145_oi_move_other_markets.md", md5=PLAN, markets={}, pooled={})
pool = {}
for g, syms in G.items():
    cost = 0.0007 if g == "CRYPTO" else 0.0004
    for s in syms:
        fine, met = load(s)
        res["markets"][s] = dict(group=g, start=str(fine.index[0].date()))
        for hl, hb, sk, tk in (("4h", 16, 1.5, 3.0), ("24h", 96, 3.0, None)):
            t, tc = trades(fine, met, 2.0, 2.0, hb, sk, tk, seed=145)
            mid = fine.index[0] + (fine.index[-1] - fine.index[0]) / 2
            r = dict(all=st(t, cost), first_half=st(t[t.time < mid], cost), second_half=st(t[t.time >= mid], cost), control=st(tc, cost))
            res["markets"][s][hl] = r
            bt.log_attempt(PLAN, f"E145 {s} P4 {hl}", "all", dict(n=r["all"].get("n"), mean_bp=r["all"].get("mean_bp"), t_week=r["all"].get("t_week")))
            pool.setdefault((g, hl), []).append(t.assign(net=t.gross - 2 * cost, sym=s))
            pool.setdefault((g, hl, "c"), []).append(tc.assign(net=tc.gross - 2 * cost))
            print(s, hl, {k: (v.get("n"), v.get("mean_bp"), v.get("t_week"), v.get("win")) for k, v in r.items()}, flush=True)
for g in G:
    for hl in ("4h", "24h"):
        x, c = pd.concat(pool[(g, hl)]).sort_values("time"), pd.concat(pool[(g, hl, "c")])
        res["pooled"][f"{g} {hl}"] = dict(n=int(len(x)), mean_bp=round(float(x.net.mean() * 1e4), 2), t_week=round(bt.tstat_weekly(x), 2),
                                           win=round(float((x.net > 0).mean()), 3), markets_positive=int((x.groupby("sym").net.mean() > 0).sum()),
                                           control_bp=round(float(c.net.mean() * 1e4), 2))
        print("POOLED", g, hl, res["pooled"][f"{g} {hl}"])
ok = [hl for hl in ("4h", "24h") if (p := res["pooled"][f"COMMODITY {hl}"])["mean_bp"] > 0 and p["t_week"] >= 2 and p["markets_positive"] >= 4 and p["mean_bp"] > p["control_bp"]]
res["verdict"] = ("PASS on real-asset perps: " + ", ".join(ok)) if ok else "FAIL (not replicated on other real-asset perps)"
json.dump(res, open("edges/results/E145_result.json", "w"), indent=1, default=str)
print(res["verdict"])
