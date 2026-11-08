"""E84 volatility-managed holding (plan edges/plans/E84_vol_managed.md, md5 3badc45b...)."""
import itertools
import json

import numpy as np
import pandas as pd

from edges.lib import bt

PLAN = "3badc45bb5a4ba764837e1a6512772e2"
PER = {"discovery": ("2020-01-01", "2024-01-01"), "validation": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2100-01-01")}
GRID = list(itertools.product((0.40, 0.60), (10, 30), (1.0, 2.0)))


def daily(sym):
    d = bt.load(sym)
    c = d.c.resample("1D").last().dropna()
    f = bt.funding(sym).resample("1D").sum().reindex(c.index).fillna(0.0)
    return pd.DataFrame(dict(r=np.log(c).diff(), f=f)).dropna()


def book(r, f, tv, hl, cap, shift=0):
    sig = (r.ewm(halflife=hl).std() * np.sqrt(365)).shift(1)
    if shift:
        sig = sig.shift(shift)
    w = (tv / sig).clip(upper=cap).fillna(0.0)
    turn = w.diff().abs().fillna(w)
    ret = w * (np.exp(r) - 1) - 0.001 * turn - w * f
    return ret


def stats(x):
    x = x.dropna()
    if len(x) < 20:
        return dict(sharpe=np.nan)
    eq = (1 + x).cumprod()
    return dict(sharpe=round(float(x.mean() / x.std() * np.sqrt(365)), 2), cagr=round(float(eq.iloc[-1] ** (365 / len(x)) - 1), 3),
                max_dd=round(float((eq / eq.cummax() - 1).min()), 3), days=int(len(x)))


def cut(x, p):
    a, b = PER[p]
    return x[(x.index >= a) & (x.index < b)]


def main():
    A = {s: daily(s) for s in ("BTCUSDT", "ETHUSDT")}
    both = pd.concat([A["BTCUSDT"], A["ETHUSDT"]], axis=1, keys=["b", "e"]).dropna()
    assets = {"BTC": (A["BTCUSDT"].r, A["BTCUSDT"].f), "ETH": (A["ETHUSDT"].r, A["ETHUSDT"].f)}
    res = dict(plan="edges/plans/E84_vol_managed.md", md5=PLAN, discovery={}, chosen={})
    best, best_gain = None, -9
    for name, (r, f) in assets.items():
        bh = stats(cut(np.exp(r) - 1 - f, "discovery"))
        for v in GRID:
            s = stats(cut(book(r, f, *v), "discovery"))
            res["discovery"][f"{name} tv{v[0]} hl{v[1]} cap{v[2]}"] = dict(**s, bh_sharpe=bh["sharpe"])
            bt.log_attempt(PLAN, f"E84 {name} {v}", "discovery", dict(n=s.get("days"), mean_bp=None, t_week=s["sharpe"]))
            gain = s["sharpe"] - bh["sharpe"]
            if gain > best_gain:
                best, best_gain = (name, v), gain
    # luck: shifted sigma
    rng = np.random.default_rng(3)
    null = []
    for _ in range(100):
        sh = int(rng.integers(60, 300))
        g = -9
        for name, (r, f) in assets.items():
            bh = stats(cut(np.exp(r) - 1 - f, "discovery"))["sharpe"]
            for v in GRID:
                g = max(g, stats(cut(book(r, f, *v, shift=sh), "discovery"))["sharpe"] - bh)
        null.append(g)
    res["luck"] = dict(real_best_gain=round(best_gain, 3), null_p95=round(float(np.percentile(null, 95)), 3))
    name, v = best
    r, f = assets[name]
    for p in PER:
        vm, bh = stats(cut(book(r, f, *v), p)), stats(cut(np.exp(r) - 1 - f, p))
        res["chosen"][p] = dict(vol_managed=vm, buy_and_hold=bh)
        if p != "discovery":
            bt.log_attempt(PLAN, f"E84 chosen {name} {v}", p, dict(n=vm["days"], mean_bp=None, t_week=vm["sharpe"]))
    ok = res["luck"]["real_best_gain"] > res["luck"]["null_p95"] and all(
        res["chosen"][p]["vol_managed"]["sharpe"] > res["chosen"][p]["buy_and_hold"]["sharpe"]
        and res["chosen"][p]["vol_managed"]["max_dd"] > 0.75 * res["chosen"][p]["buy_and_hold"]["max_dd"] for p in ("validation", "final"))
    res["verdict"] = ("PASS" if ok else "FAIL") + f": {name} tv{v[0]} hl{v[1]} cap{v[2]}"
    json.dump(res, open("edges/results/E84_result.json", "w"), indent=1, default=str)
    print("luck", res["luck"])
    for p in PER:
        print(p, res["chosen"][p])
    print(res["verdict"])


if __name__ == "__main__":
    main()
