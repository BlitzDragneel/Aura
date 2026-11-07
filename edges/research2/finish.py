"""Apply the common selection rules to a finished discovery: luck check, promotion (<=3), validation once, FINAL once.
Usage: python finish.py E50|E52|E53|E54"""
import sys, os, json
sys.path.insert(0, "/home/user/Aura"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from edges.lib import bt
import lib2

PLAN = sys.argv[1]
SCR = lib2.SCR


def rebuilder(plan):
    if plan == "E50":
        import e50_tsmom as m
        cache = {}
        def f(name):
            tf, asset, sn, mode, sz = name.split("_", 4) if not name.split("_")[2].startswith("EMA") else None, None, None, None, None
            parts = name.split("_")
            tf, asset = parts[0], parts[1]
            mode, sz = parts[-2], parts[-1]
            sn = "_".join(parts[2:-2])
            if tf not in cache:
                cache[tf] = m.setup(tf)
            S = cache[tf]
            return m.variant(S, asset, m.signal(S["C"], sn, S["bpd"]), mode, sz)
        def bench(name):
            tf, asset = name.split("_")[:2]
            return m.bench(cache[tf], asset)
        return m.MD5, f, bench
    if plan == "E52":
        import e52_xsec as m
        S = m.setup()
        def f(name):
            p = name.split("_")
            g = (int(p[0][1:]), int(p[1][1:]), p[2], int(p[3][1:]), p[4], p[5])
            return m.run_variant(S, *g)
        return m.MD5, f, lambda n: m.bench(S, n.split("_")[2])
    if plan == "E53":
        import e53_altbtc as m
        S = m.setup()
        def f(name):
            N, me, bk, fr = name.split("_")
            return m.run(S, m.sig(S, int(N[1:]), me), bk, fr)
        return m.MD5, f, lambda n: m.bench(S)
    if plan == "E54":
        import e54_funding as m
        S = m.setup(); pct = {}
        def f(name):
            p = name.split("_")
            if p[0] == "XS":
                return m.run_xs(S, (p[1], p[2], int(p[3][1:]), p[4]))
            if "g" not in pct:
                pct["g"] = m.gauge(S)
            return m.run_ts(S, (float(p[1][1:]), p[2], p[3]), pct["g"])
        def bench(name):   # equal-weight top-100 weekly
            import e52_xsec as m2
            S2 = m2.setup(); return m2.bench(S2, "w")
        return m.MD5, f, bench
    raise SystemExit("unknown plan")


def main():
    d = json.load(open(f"{SCR}/{PLAN.lower()}/disc.json"))
    V = d["variants"]; nb = np.array(d["null_best_weakest_bp"], dtype=float)
    real_best = max(v["weakest_year_bp"] for v in V)
    p95 = float(np.percentile(nb, 95)); pct = float((nb < real_best).mean())
    elig = sorted([v for v in V if (v.get("t_week") or 0) >= 2 and v["weakest_year_bp"] > 0],
                  key=lambda v: -v["weakest_year_bp"])
    luck_ok = real_best >= p95
    md5, f, bench = rebuilder(PLAN)
    out = dict(plan=PLAN, md5=md5, variants=len(V), luck=dict(real_best_weakest_bp=real_best, null_p95_bp=round(p95, 2),
               null_median_bp=round(float(np.median(nb)), 2), real_pct=pct, passed=bool(luck_ok)),
               eligible=[v["label"] for v in elig], promoted=[], validation={}, final=None, info_only=None)
    best_disc = max(V, key=lambda v: v["weakest_year_bp"])
    out["best_discovery"] = best_disc
    chosen = None
    if luck_ok and elig:
        for v in elig[:3]:
            o = f(v["label"]); s = lib2.stats(lib2.period(o, "validation"), v["label"] + "_validation")
            bt.log_attempt(md5, v["label"], "validation", s); out["promoted"].append(v["label"]); out["validation"][v["label"]] = s
        ok = [(s["t_week"], n) for n, s in out["validation"].items() if s["mean_bp"] > 0 and s["t_week"] >= 1.5]
        if ok:
            chosen = max(ok)[1]
    name = chosen or best_disc["label"]
    o = f(name)
    res = {p: lib2.stats(lib2.period(o, p), f"{name}_{p}") for p in ("discovery", "validation", "final")}
    res["all"] = lib2.stats(o[o.index >= "2020-01-01"], f"{name}_all")
    D = lib2.trim(lib2.daily()); Cb = D["c"][["BTCUSDT"]].astype(float)
    btc = lib2.run_book(pd.DataFrame(1.0, index=Cb.index, columns=["BTCUSDT"]), Cb, D["qv"][["BTCUSDT"]].astype(float),
                        lib2.fund_daily()[["BTCUSDT"]])
    res["btc_hold"] = {p: lib2.stats(lib2.period(btc, p), f"btc_hold_{p}") for p in ("discovery", "validation", "final")}
    def path(x):
        x = x[x.index >= "2025-01-01"]; e = 100 * (1 + x.net).cumprod()
        return {str(k.date()): round(float(v), 1) for k, v in e.resample("QE").last().items()}
    res["account_path_100usdt_final"] = dict(rule=path(o), btc_hold=path(btc))
    b = bench(name)
    res["bench"] = {p: lib2.stats(lib2.period(b, p), f"bench_{p}") for p in ("discovery", "validation", "final")}
    if chosen:
        bt.log_attempt(md5, name, "final", res["final"]); out["final"] = dict(variant=name, **res)
        fs = res["final"]
        passed = (fs["mean_bp"] > 0 and fs["t_week"] >= 2.0 and res["all"]["years_pos"] / res["all"]["years_total"] >= 0.6
                  and fs["n"] >= 100 and fs["orders"] >= 100)
        out["verdict"] = "PASS-candidate" if passed else "FAIL"
    else:
        bt.log_attempt(md5, name, "final_INFO_ONLY", res["final"]); out["info_only"] = dict(variant=name, **res)
        out["verdict"] = "FAIL"
    o.to_pickle(f"{SCR}/{PLAN.lower()}/daily_{name}.pkl")
    json.dump(out, open(f"{SCR}/{PLAN.lower()}/finish.json", "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("luck", "eligible", "promoted", "verdict")}, default=str))
    for k, s in out["validation"].items():
        print("VAL", k, s["mean_bp"], s["t_week"], s["cagr"], s["max_dd"])
    r = out["final"] or out["info_only"]
    for p in ("discovery", "validation", "final", "all"):
        s = r[p]; print(r["variant"], p, s["mean_bp"], s["t_week"], s["cagr"], s["max_dd"], s["years"], s["ex_top5pct_bp"], s["orders_per_day"])
    for p, s in r["btc_hold"].items():
        print("btc_hold", p, s["mean_bp"], s["t_week"], s["cagr"], s["max_dd"])
    print(r["account_path_100usdt_final"])
    for p, s in r["bench"].items():
        print("bench", p, s["mean_bp"], s["t_week"], s["cagr"], s["max_dd"])


if __name__ == "__main__":
    main()
