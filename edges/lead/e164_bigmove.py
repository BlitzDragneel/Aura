"""E164 direction call only when a big move is expected (plan edges/plans/E164_direction_when_big_move.md)."""
import json, sys
import numpy as np, pandas as pd
from edges.lib import bt
from edges.lead import e163_mistakes as e163
PLAN = "71570a3e12a385e3ff2cc61275621fd5"


def trades(S, side, hold, cost):
    out, busy = [], None
    ret = S.ret1h if hold == 1 else S.ret4h
    for t, sd in side.items():
        if busy is not None and t < busy or not np.isfinite(ret.get(t, np.nan)):
            continue
        out.append((t, sd * ret[t] - 2 * cost)); busy = t + pd.Timedelta(hours=hold, minutes=15)
    T = pd.DataFrame(out, columns=["time", "net"])
    if len(T) < 5:
        return dict(n=int(len(T)))
    return dict(n=int(len(T)), net_bp=round(float(T.net.mean() * 1e4), 2), t=round(float(bt.tstat_weekly(T)), 2),
                win=round(float((T.net > 0).mean()), 3))


def main(which):
    rng = np.random.default_rng(164); res = {}
    for a in which:
        load, sm, warm, per, cost = e163.CFG[a]
        P = e163.predictions(a, load(), sm, warm, per)
        q80 = float(P[P.index < pd.Timestamp(per["val"][0], tz="UTC")].nb_big4.quantile(0.8))
        R = dict(big_threshold=round(q80, 3))
        for p, (s, e) in per.items():
            S = P[(P.index >= pd.Timestamp(s, tz="UTC")) & (P.index < pd.Timestamp(e, tz="UTC"))]
            big = S.nb_big4 >= q80
            appr = S.E_pright >= 0.55
            side = np.sign(S.D - 0.5)
            sel = S[big & appr]
            r = {}
            for hold in (1, 4):
                r[f"rule_{hold}h"] = trades(S, side[big & appr], hold, cost)
                r[f"coinflip_{hold}h"] = trades(S, pd.Series(rng.choice([-1, 1], len(sel)), index=sel.index), hold, cost)
                r[f"big_only_{hold}h"] = trades(S, side[big], hold, cost)
                for k in (f"rule_{hold}h", f"coinflip_{hold}h", f"big_only_{hold}h"):
                    bt.log_attempt(PLAN, f"E164 {a} {k}", p, dict(n=r[k].get("n"), mean_bp=r[k].get("net_bp"), t_week=r[k].get("t")))
            r["acc_rule"] = round(float((np.sign(sel.D - 0.5) == np.sign(sel.ret1h)).mean()), 3) if len(sel) else None
            r["avg_abs_move_bp_rule_1h"] = round(float(sel.ret1h.abs().mean() * 1e4), 1) if len(sel) else None
            r["avg_abs_move_bp_all_1h"] = round(float(S.ret1h.abs().mean() * 1e4), 1)
            R[p] = r
        res[a] = R
        print(a, json.dumps(R), flush=True)
    ok = [f"{a} {h}" for a, R in res.items() for h in ("rule_1h", "rule_4h")
          if (R["final"][h].get("net_bp") or -1) > 0 and (R["final"][h].get("t") or 0) >= 2 and (R["val"][h].get("net_bp") or -1) > 0]
    res["verdict"] = ("PASS " + ", ".join(ok)) if ok else "FAIL"
    json.dump(res, open("edges/results/E164_result.json", "w"), indent=1); print(res["verdict"])


if __name__ == "__main__":
    main(sys.argv[1:] or ["BTC", "PAXG", "XAU", "XAG"])
