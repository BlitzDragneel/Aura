"""Stage 2 for every E37-E46 plan: discovery table + luck check -> promotion -> validation -> final (mechanical, as planned).
usage: python evaluate.py E37 [nmin]"""
import sys, glob, pickle, hashlib
import numpy as np, pandas as pd
from lib1 import *  # noqa
from searchkit import best_t

PLAN_FILES = {os.path.basename(p)[:3]: p for p in glob.glob(os.path.join(ROOT, "edges/plans/E*.md"))}


def plan_md5(plan):
    return hashlib.md5(open(PLAN_FILES[plan], "rb").read()).hexdigest()


def sub(tr, p):
    return tr[period_mask(tr.time, p)] if len(tr) else tr


def clean(s):
    return {k: v for k, v in s.items()}


def evaluate(plan, P, nmin=100, extra=None):
    md5 = plan_md5(plan)
    names, real = P["names"], P["real"]
    disc = []
    for i, nm in enumerate(names):
        s = bt.summarize(sub(real[i], "discovery"), nm) if len(real[i]) else dict(label=nm, n=0)
        if s["n"]:
            bt.log_attempt(md5, nm, "discovery", s)
        disc.append(s)
    ok = [(i, s) for i, s in enumerate(disc) if s["n"] >= nmin and s["mean_bp"] > 0 and s["t_week"] == s["t_week"]]
    ok.sort(key=lambda x: -x[1]["t_week"])
    n_l, mu_l, t_l = P["luck"]
    luck = best_t(n_l, mu_l, t_l, nmin)
    luck = luck[np.isfinite(luck)] if np.isfinite(luck).any() else np.array([-np.inf])
    best = ok[0][1]["t_week"] if ok else None
    luck_rep = dict(repeats=int(len(P["luck"][0])), luck_best_t_p50=float(np.percentile(luck, 50)),
                    luck_best_t_p95=float(np.percentile(luck, 95)), luck_best_t_max=float(luck.max()),
                    real_best_t=best, real_pct=(float((luck < best).mean() * 100) if best is not None else None))
    out = dict(plan=plan, plan_md5=md5, variants=len(names), discovery=disc, luck=luck_rep)
    out["discovery_winner"] = ok[0][1]["label"] if ok else None
    promoted = [(i, s) for i, s in ok if s["t_week"] >= 2.0][:2]
    out["promoted"] = [names[i] for i, _ in promoted]
    out["validation"] = {}
    for i, _ in promoted:
        s = bt.summarize(sub(real[i], "validation"), names[i]); bt.log_attempt(md5, names[i], "validation", s)
        out["validation"][names[i]] = s
    passv = [(i, out["validation"][names[i]]) for i, _ in promoted]
    passv = [(i, s) for i, s in passv if s["n"] and s["mean_bp"] > 0 and s["t_week"] >= 1.5]
    chosen = None
    if passv:
        chosen = max(passv, key=lambda x: x[1]["t_week"])[0]; out["final_status"] = "judged"
    elif promoted:
        chosen = promoted[0][0]; out["final_status"] = "information only (validation failed)"
    else:
        out["final_status"] = "not run (nothing promoted)"
    if chosen is not None:
        f = sub(real[chosen], "final")
        s = bt.summarize(f, names[chosen]) if len(f) else dict(label=names[chosen], n=0)
        bt.log_attempt(md5, names[chosen], "final", s)
        out["chosen"] = names[chosen]; out["final"] = s
        alls = bt.summarize(real[chosen], names[chosen])
        out["all_periods"] = alls
        # verdict
        pv = out["validation"][names[chosen]]
        c1 = s["n"] > 0 and s["mean_bp"] > 0 and s["t_week"] >= 2.0 and pv["mean_bp"] > 0 and pv["t_week"] >= 1.5
        c2 = luck_rep["real_pct"] is not None and luck_rep["real_pct"] >= 95
        c3 = alls["years_pos"] >= 0.6 * alls["years_total"]
        c5 = s["n"] >= 100 or (s["n"] >= 50 and s["t_week"] >= 3)
        out["checks"] = dict(final_and_validation=bool(c1), luck=bool(c2), years=bool(c3), enough_trades=bool(c5))
        out["verdict"] = "PASS" if (c1 and c2 and c3 and c5 and out["final_status"] == "judged") else "FAIL"
        if out["verdict"] == "PASS":
            fz = f.copy(); allz = real[chosen].copy()
            out["leverage_final"] = bt.leverage_table(fz); out["leverage_all"] = bt.leverage_table(allz)
            okL = [r["leverage"] for r in out["leverage_all"] if r["liquidations"] == 0 and r["max_dd"] > -0.35]
            okF = [r["leverage"] for r in out["leverage_final"] if r["liquidations"] == 0 and r["max_dd"] > -0.35]
            out["max_leverage"] = min(max(okL, default=0), max(okF, default=0))
    else:
        out["verdict"] = "FAIL"
    if extra:
        out.update(extra)
    jdump(out, os.path.join(ROOT, f"edges/results/{plan}_result.json"))
    return out


def show(out):
    print(out["plan"], out["plan_md5"], "variants", out["variants"])
    for s in sorted(out["discovery"], key=lambda s: -(s.get("t_week") or -99) if s.get("n") else 99)[:8]:
        if s.get("n"):
            print("  D", s["label"], s["n"], s["mean_bp"], "t", s["t_week"], "ex5", s["ex_top5pct_bp"], "/d", s["per_day"])
    print("  luck", out["luck"])
    print("  promoted", out["promoted"])
    for k, v in out["validation"].items():
        print("  V", k, v.get("n"), v.get("mean_bp"), "t", v.get("t_week"))
    if "final" in out:
        f = out["final"]; print("  F", out["chosen"], out["final_status"], f.get("n"), f.get("mean_bp"), "t", f.get("t_week"),
                                 "ex5", f.get("ex_top5pct_bp"), "/d", f.get("per_day"), "years", out["all_periods"]["years"])
        print("  checks", out.get("checks"))
    print("  VERDICT", out["verdict"], out.get("max_leverage"))
    if "leverage_all" in out:
        for r in out["leverage_all"]:
            print("   L", r)


if __name__ == "__main__":
    plan = sys.argv[1]
    P = pickle.load(open(f"{SCR}/{plan}_stage1.pkl", "rb"))
    show(evaluate(plan, P, int(sys.argv[2]) if len(sys.argv) > 2 else 100))
