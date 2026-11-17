"""E166 big picture: week/month regime and money flow -> next week (plan edges/plans/E166_big_picture_weekly.md)."""
import json
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from edges.lib import bt
PLAN = "ea697f90ad4b3f33c8243fe2bd99843f"
PER = {"disc": ("2019-01-01", "2023-01-01"), "val": ("2023-01-01", "2024-01-01"), "final": ("2024-01-01", "2026-12-01")}


def weekly():
    D = pd.read_parquet("/home/user/data/macro/daily.parquet").ffill()
    W = D.resample("W-SUN").last()          # values known at the end of Sunday; trade the next week
    return W


def feats(W, a):
    p = W[a]
    F = pd.DataFrame(index=W.index)
    F["r4"], F["r12"] = p.pct_change(4), p.pct_change(12)
    F["vs20w"] = p / p.rolling(20).mean() - 1
    F["stable4"] = W.STABLE.pct_change(4)
    F["fg"], F["fg4"] = W.FG, W.FG.diff(4)
    F["dxy4"], F["tnx4"] = W.DXY.pct_change(4), W.TNX.diff(4)
    F["nxt"] = p.shift(-1) / p - 1
    return F


def st(r, idx):
    r = pd.Series(r, index=idx).dropna()
    if len(r) < 10:
        return dict(n=int(len(r)))
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))
    return dict(n=int(len(r)), avg_pct=round(float(r.mean() * 100), 3), t=round(float(t), 2), win=round(float((r > 0).mean()), 3),
                total_pct=round(float(r.sum() * 100), 1))


def main():
    W = weekly(); res = dict(plan="edges/plans/E166_big_picture_weekly.md", md5=PLAN, assets={})
    rng = np.random.default_rng(166)
    for a, cost in (("BTC", 0.0014), ("GOLD", 0.0004)):
        F = feats(W, a).dropna(subset=["r12", "vs20w", "dxy4", "nxt"])
        F = F[F.index >= "2018-06-01"]
        sig = {"always long": pd.Series(1.0, index=F.index), "momentum 12w": np.sign(F.r12), "random": pd.Series(rng.choice([-1.0, 1.0], len(F)), index=F.index)}
        if a == "BTC":
            sig["money flow (stablecoins 4w)"] = np.sign(F.stable4)
            sig["momentum + money flow agree"] = np.where(np.sign(F.r12) == np.sign(F.stable4), np.sign(F.r12), 0.0)
        else:
            sig["dollar (opposite DXY 4w)"] = -np.sign(F.dxy4)
            sig["momentum + dollar agree"] = np.where(np.sign(F.r12) == -np.sign(F.dxy4), np.sign(F.r12), 0.0)
        cols = ["r4", "r12", "vs20w", "dxy4", "tnx4"] + (["stable4", "fg", "fg4"] if a == "BTC" else [])
        Fx = F.dropna(subset=cols)
        disc = (Fx.index >= PER["disc"][0]) & (Fx.index < PER["disc"][1])
        mu, sd = Fx[disc][cols].mean(), Fx[disc][cols].std()
        lr = LogisticRegression(C=0.5).fit(((Fx[disc][cols] - mu) / sd).values, (Fx[disc].nxt > 0).values)
        pr = pd.Series(lr.predict_proba(((Fx[cols] - mu) / sd).values)[:, 1], index=Fx.index)
        sig["logistic (all features)"] = np.sign(pr - 0.5).reindex(F.index)
        A = {}
        for name, s in sig.items():
            s = pd.Series(s, index=F.index)
            r = s * F.nxt - (s != 0) * cost
            A[name] = {p: st(r[(F.index >= x) & (F.index < y)], F.index[(F.index >= x) & (F.index < y)]) for p, (x, y) in PER.items()}
            for p in ("val", "final"):
                bt.log_attempt(PLAN, f"E166 {a} {name}", p, dict(n=A[name][p].get("n"), mean_bp=(A[name][p].get("avg_pct") or 0) * 100, t_week=A[name][p].get("t")))
            print(a, name, {p: (v.get("n"), v.get("avg_pct"), v.get("t"), v.get("total_pct")) for p, v in A[name].items()}, flush=True)
        A["_logistic_coefs"] = dict(zip(cols, np.round(lr.coef_[0], 3)))
        A["_now"] = dict(week_end=str(F.index[-1].date()), **{k: round(float(v), 4) for k, v in feats(W, a).iloc[-1][cols].items() if pd.notna(v)},
                         logistic_p_up=round(float(pr.iloc[-1]), 3))
        res["assets"][a] = A
    ok = []
    for a, A in res["assets"].items():
        for n, v in A.items():
            if n.startswith("_") or n in ("always long", "random"):
                continue
            f, va = v["final"], v["val"]
            if (f.get("avg_pct") or -1) > 0 and (f.get("t") or 0) >= 2 and (va.get("avg_pct") or -1) > 0 and f["total_pct"] > A["always long"]["final"]["total_pct"]:
                ok.append(f"{a} {n}")
    res["verdict"] = "PASS " + ", ".join(ok) if ok else "FAIL"
    json.dump(res, open("edges/results/E166_result.json", "w"), indent=1, default=str); print(res["verdict"]); print(res["assets"]["BTC"]["_now"], res["assets"]["GOLD"]["_now"])


if __name__ == "__main__":
    main()
