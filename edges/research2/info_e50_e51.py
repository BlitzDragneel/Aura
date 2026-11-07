import sys, os, json
sys.path.insert(0, "/home/user/Aura"); sys.path.insert(0, "/home/user/Aura/edges/research2")
import numpy as np, pandas as pd
from edges.lib import bt
import lib2, e50_tsmom as e50, e51_breakout as e51
SCR = lib2.SCR
out = {}
d = json.load(open(f"{SCR}/e50/disc.json"))
el = [v["label"] for v in d["variants"] if (v.get("t_week") or 0) >= 2 and v["weakest_year_bp"] > 0]
out["e50_eligible"] = el
st4 = pd.read_pickle(f"{SCR}/e50/store_4h.pkl"); st1 = pd.read_pickle(f"{SCR}/e50/store_1d.pkl")
best = "4h_BTC_R60_ls_fx"
o = st4[best]
res = {}
for p in ("discovery", "validation", "final"):
    s = lib2.stats(lib2.period(o, p), f"{best}_{p}"); res[p] = s
    if p != "discovery":
        bt.log_attempt(e50.MD5, best, p + "_INFO_ONLY", s)
out["e50_best"] = res
out["e50_bench"] = {k: v for k, v in d["bench"].items() if k.startswith("4h_BTC") or k.startswith("1d_")}
# also the 2025-26 picture of each asset's best variant (descriptive, data already used? no: FINAL; info only, not logged as pass)
# E51
D = e51.load()
N, ex, dr = 100, 3.0, "both"
t = e51.trades(D, e51.signals(D, N, dr), N, ex, True)
r51 = {}
for p, tt in bt.split(t).items():
    s = bt.summarize(tt, f"E51_N100_x3_both_{p}"); r51[p] = s
    if p != "discovery":
        bt.log_attempt(e51.MD5, "N100_x3.0_both", p + "_INFO_ONLY", s)
out["e51_best"] = r51
json.dump(out, open(f"{SCR}/info_e50_e51.json", "w"), indent=1, default=str)
for k in ("e50_best", "e51_best"):
    for p, s in out[k].items():
        print(k, p, {x: s.get(x) for x in ("n", "mean_bp", "t_week", "cagr", "max_dd", "years", "ex_top5pct_bp", "years_pos")})
for k, v in out["e50_bench"].items():
    print(k, v.get("mean_bp"), v.get("t_week"), v.get("cagr"), v.get("max_dd"))
print(el)
