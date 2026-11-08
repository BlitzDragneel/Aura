"""E83 overnight drift (plan edges/plans/E83_overnight_drift.md, md5 40fdf85f...)."""
import json

import numpy as np
import pandas as pd

from edges.lib import bt

PLAN = "40fdf85fa54320c4d8233a8e3d88941a"
SYMS = ("SPY", "QQQ", "IWM", "DIA")
SPREAD, ETF_COST, FIN = 0.00015, 0.0002, 0.065 / 360
PER = {"discovery": ("2000-01-01", "2016-01-01"), "validation": ("2016-01-01", "2021-01-01"), "final": ("2021-01-01", "2100-01-01")}


def load(s):
    d = json.load(open(f"/home/user/data/stocks/{s}.json"))["chart"]["result"][0]
    q = d["indicators"]["quote"][0]
    df = pd.DataFrame(dict(o=q["open"], c=q["close"]), index=pd.to_datetime(d["timestamp"], unit="s").normalize())
    df = df.dropna()
    div = pd.Series({pd.to_datetime(v["date"], unit="s").normalize(): v["amount"] for v in d.get("events", {}).get("dividends", {}).values()})
    df["div"] = div.reindex(df.index).fillna(0.0)
    pc = df.c.shift(1)
    df["on"] = (df.o + df["div"]) / pc - 1
    df["intra"] = df.c / df.o - 1
    df["nights"] = (df.index.to_series().diff().dt.days).fillna(1)
    df["prev_down"] = (df.c.shift(1) < df.o.shift(1))
    df["mon"] = df.index.dayofweek == 0          # the night before a Monday open = weekend
    return df.dropna(subset=["on"])


def nw_t(x, lags=5):
    x = np.asarray(x, float); x = x[np.isfinite(x)]; n = len(x)
    if n < 30:
        return np.nan
    e = x - x.mean(); v = e @ e / n
    for L in range(1, lags + 1):
        v += 2 * (1 - L / (lags + 1)) * (e[L:] @ e[:-L]) / n
    return x.mean() / np.sqrt(v / n)


def stats(r, idx):
    s = pd.Series(r, index=idx).dropna()
    eq = (1 + s).cumprod()
    yr = s.groupby(s.index.year).sum()
    return dict(n=int(len(s)), mean_bp=round(s.mean() * 1e4, 2), t=round(float(nw_t(s)), 2),
                ann_pct=round(((eq.iloc[-1]) ** (252 / len(s)) - 1) * 100, 1) if len(s) else None,
                max_dd=round(float((eq / eq.cummax() - 1).min()), 3), years_pos=f"{int((yr > 0).sum())}/{len(yr)}")


def variant(df, rule, cost):
    m = pd.Series(True, index=df.index)
    if rule == "weekday":
        m &= ~df.mon
    elif rule == "after_down":
        m &= df.prev_down
    gross = df.on.where(m)
    if cost == "cfd":
        net = gross - SPREAD - FIN * df.nights
    else:
        net = gross - ETF_COST
    return net


def main():
    res = dict(plan="edges/plans/E83_overnight_drift.md", md5=PLAN, discovery={}, benchmarks={})
    D = {s: load(s) for s in SYMS}
    for s, df in D.items():
        for rule in ("all", "weekday", "after_down"):
            for p, (a, b) in PER.items():
                sub = df[(df.index >= a) & (df.index < b)]
                st = stats(variant(sub, rule, "cfd"), sub.index)
                res["discovery" if p == "discovery" else p].setdefault(f"{s}/{rule}", st) if p == "discovery" else None
                if p == "discovery":
                    bt.log_attempt(PLAN, f"E83 {s} {rule} cfd", p, dict(n=st["n"], mean_bp=st["mean_bp"], t_week=st["t"]))
    best = max(res["discovery"], key=lambda k: res["discovery"][k]["t"])
    s, rule = best.split("/")
    df = D[s]
    out = {}
    for p, (a, b) in PER.items():
        sub = df[(df.index >= a) & (df.index < b)]
        out[p] = dict(cfd=stats(variant(sub, rule, "cfd"), sub.index), etf=stats(variant(sub, rule, "etf"), sub.index),
                      gross=stats(variant(sub, rule, "none").where(lambda x: x.notna()) + ETF_COST, sub.index),
                      intraday_same_days=stats(sub.intra - SPREAD, sub.index),
                      buy_and_hold=stats(sub.c.pct_change(), sub.index))
        if p != "discovery":
            bt.log_attempt(PLAN, f"E83 chosen {best}", p, dict(n=out[p]["cfd"]["n"], mean_bp=out[p]["cfd"]["mean_bp"], t_week=out[p]["cfd"]["t"]))
    res["chosen"] = best
    res["chosen_periods"] = out
    v, f = out["validation"]["cfd"], out["final"]["cfd"]
    passed = v["mean_bp"] > 0 and v["t"] >= 1.5 and f["mean_bp"] > 0 and f["t"] >= 2
    res["verdict"] = ("PASS" if passed else "FAIL") + f": {best} CFD final {f['mean_bp']} bp/night t {f['t']}, validation {v['mean_bp']} t {v['t']}"
    json.dump(res, open("edges/results/E83_result.json", "w"), indent=1, default=str)
    print("discovery top:", sorted(((k, x["mean_bp"], x["t"]) for k, x in res["discovery"].items()), key=lambda z: -z[2])[:5])
    for p in PER:
        print(p, {k: (x["mean_bp"], x["t"], x["ann_pct"], x["max_dd"], x["years_pos"]) for k, x in out[p].items()})
    print(res["verdict"])


if __name__ == "__main__":
    main()
