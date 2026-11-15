import glob, json, sys, warnings, zipfile
import pandas as pd
from edges.lib import bt
from edges.siglab.replay import replay, st
warnings.filterwarnings("ignore")
PLAN = sys.argv[1]
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


P1 = {"train": ("2026-01-01", "2026-06-01"), "val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-12-01")}
P2 = {"train": ("2025-06-01", "2026-01-01"), "val": ("2026-01-01", "2026-06-01"), "final": ("2026-06-01", "2026-12-01")}
res = dict(plan="edges/plans/E149_siglab_replay_more.md", md5=PLAN, assets={}, muted={}, backtest_plus={}, trades={})
allT = {}
for sym, fine, start, per in (("XAGUSD", pd.read_parquet(D + "XAG_perp_1m.parquet")[["o", "h", "l", "c"]].astype(float), "2026-01-12", P1),
                              ("ETHUSD", k1m("ETH"), "2025-06-05", P2), ("SOLUSD", k1m("SOL"), "2025-06-05", P2)):
    T = replay(sym, fine, start)
    T["final"] = (T.time >= pd.Timestamp(per["final"][0], tz="UTC"))
    allT[sym] = T
    A, mut, plus = {}, [], []
    for setup in sorted(T.setup.unique()):
        for side in ("with", "against"):
            x = T[(T.setup == setup) & (T.side == side)]
            cell = {p: st(x[(x.time >= pd.Timestamp(a, tz="UTC")) & (x.time < pd.Timestamp(b, tz="UTC"))]) for p, (a, b) in per.items()}
            A[f"{setup} {side}"] = cell
            v, f_ = cell["val"], cell["final"]
            for p in ("val", "final"):
                bt.log_attempt(PLAN, f"E149 {sym} {setup} {side}", p, dict(n=cell[p].get("n"), mean_bp=cell[p].get("avg_R"), t_week=cell[p].get("t")))
            if (v.get("avg_R") or 0) < 0 and (f_.get("avg_R") or 0) < 0 and min(v.get("t") or 0, f_.get("t") or 0) <= -1.5:
                mut.append(f"{setup} {side}")
            if (v.get("avg_R") or -1) > 0 and (f_.get("avg_R") or -1) > 0 and (f_.get("t") or 0) >= 2:
                plus.append(f"{setup} {side}")
            print(sym, setup, side, {p: (c.get("n"), c.get("avg_R"), c.get("t")) for p, c in cell.items()}, flush=True)
    res["assets"][sym], res["muted"][sym], res["backtest_plus"][sym] = A, mut, plus
    print(sym, "MUTED", mut, "PLUS", plus, flush=True)
    T.to_parquet(f"/tmp/e149_{sym}.parquet")
json.dump(res, open("edges/results/E149_result.json", "w"), indent=1, default=str)
