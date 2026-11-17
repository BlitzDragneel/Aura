import json, sys, warnings
import numpy as np, pandas as pd
from edges.lib import bt
warnings.filterwarnings("ignore")
PLAN = sys.argv[1]
src = open("edges/lead/e157_liquidity.py").read().split("sets = [")[0].replace("PLAN = sys.argv[2]", "PLAN = 'x'")
ns = {}; exec(src, ns)
fine = bt.load("BTCUSDT", "5m")[["o", "h", "l", "c", "v"]].astype(float)["2023-01-01":]
X = ns["prep"](fine, pd.read_parquet("/home/user/data/depth/BTCUSDT_5m.parquet"))
f = ns["bars15"](fine)
H, L, C, T5 = fine.h.values, fine.l.values, fine.c.values, fine.index
MK, TK = 0.0002, 0.0007
rng = np.random.default_rng(158)


def run(z, hold, randomize=False):
    out, busy = [], pd.Timestamp("2000-01-01", tz="UTC")
    zz = X[z]
    for t, v in zz.items():
        if not np.isfinite(v) or abs(v) < 2 or t < busy:
            continue
        d = 1 if v > 0 else -1
        if randomize:
            d = int(rng.choice([-1, 1]))
        lim = f.c.get(t)
        i0 = T5.searchsorted(t + pd.Timedelta("15min"))
        if lim is None or i0 + 3 + hold * 12 + 3 >= len(C):
            continue
        w = slice(i0, i0 + 3)
        filled = (L[w] < lim).any() if d == 1 else (H[w] > lim).any()
        if not filled:
            continue
        j = i0 + int(np.argmax(L[w] < lim) if d == 1 else np.argmax(H[w] > lim)) + 1
        k = j + hold * 12
        ex_lim = C[k - 1]
        w2 = slice(k, k + 3)
        ex_fill = (H[w2] > ex_lim).any() if d == 1 else (L[w2] < ex_lim).any()
        if ex_fill:
            ex, ec = ex_lim, MK
        else:
            ex, ec = C[min(k + 2, len(C) - 1)], TK
        out.append(dict(time=t, net=d * (ex - lim) / lim - MK - ec, gross=d * (ex - lim) / lim, maker_exit=ex_fill))
        busy = T5[min(k + 3, len(T5) - 1)]
    return pd.DataFrame(out)


PER = {"train": ("2023-01-01", "2024-01-01"), "val": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2026-11-04")}
res, ok = dict(plan="edges/plans/E158_book_maker.md", md5=PLAN, cells={}), []
for z in ("z1", "z5"):
    for hold in (1, 4):
        key = f"{z} FOLLOW {hold}h"; res["cells"][key] = {}
        for nm, rnd in (("rule", False), ("random", True)):
            Tr = run(z, hold, rnd)
            for p, (a, b) in PER.items():
                x = Tr[(Tr.time >= pd.Timestamp(a, tz="UTC")) & (Tr.time < pd.Timestamp(b, tz="UTC"))]
                cell = dict(n=int(len(x)), gross_bp=round(float(x.gross.mean() * 1e4), 1), net_bp=round(float(x.net.mean() * 1e4), 1),
                            t=round(bt.tstat_weekly(x), 2), maker_exit=round(float(x.maker_exit.mean()), 2))
                res["cells"][key][f"{nm} {p}"] = cell
                if nm == "rule" and p != "train":
                    bt.log_attempt(PLAN, f"E158 {key}", p, dict(n=cell["n"], mean_bp=cell["net_bp"], t_week=cell["t"]))
        c = res["cells"][key]
        print(key, {k: (v["n"], v["gross_bp"], v["net_bp"], v["t"]) for k, v in c.items()}, flush=True)
        if c["rule final"]["net_bp"] > 0 and c["rule final"]["t"] >= 2 and c["rule val"]["net_bp"] > 0 and c["rule val"]["t"] >= 1.5 and c["rule final"]["net_bp"] > c["random final"]["net_bp"]:
            ok.append(key)
res["verdict"] = ("PASS " + ", ".join(ok)) if ok else "FAIL"
json.dump(res, open("edges/results/E158_result.json", "w"), indent=1, default=str); print(res["verdict"])
