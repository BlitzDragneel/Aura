"""E85 trend/volatility long-or-cash controller (plan edges/plans/E85_trend_vol_controller.md, md5 fb92a37b...)."""
import json
import sys

import numpy as np
import pandas as pd

from edges.lib import bt

PLAN = "fb92a37b1326916b61ebb400be2a92d9"
PER = {"BTC": {"discovery": ("2020-01-01", "2024-01-01"), "validation": ("2024-01-01", "2025-01-01"), "final": ("2025-01-01", "2100-01-01")},
       "GOLD": {"discovery": ("2001-01-01", "2018-01-01"), "validation": ("2018-01-01", "2022-01-01"), "final": ("2022-01-01", "2100-01-01")}}


def btc():
    d = bt.load("BTCUSDT")
    c = d.c.resample("1D").last().dropna()
    f = bt.funding("BTCUSDT").resample("1D").sum().reindex(c.index).fillna(0.0)
    return c, f, 365, 0.0010


def gold(path):
    r = json.load(open(path))["chart"]["result"][0]
    c = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s", utc=True).normalize()).dropna()
    c = c[~c.index.duplicated(keep="last")]
    return c, pd.Series(0.0, index=c.index), 252, 0.0005


def books(c, f, ann, cost):
    lr = np.log(c).diff()
    part = sum((c / c.shift(k) - 1 > 0).astype(float) for k in (20, 60, 120)) / 3
    v20, v60 = lr.rolling(20).std() * np.sqrt(ann), lr.rolling(60).std() * np.sqrt(ann)
    scale = (0.10 / np.maximum(v20, v60)).clip(upper=1.0)
    nxt = np.exp(lr.shift(-1)) - 1          # return over the next day
    fn = f.shift(-1).fillna(0.0)
    out = {}
    for name, w in (("controller", part * scale), ("vol_only", scale), ("trend_only", part), ("buy_hold", pd.Series(1.0, index=c.index))):
        w = w.fillna(0.0)
        for k, mult in (("base", 1), ("stress", 2)):
            turn = w.diff().abs().fillna(w)
            out[(name, k)] = (w * nxt - w * fn - mult * cost * turn).dropna()
    return out


def stats(x, ann):
    x = x.dropna()
    eq = (1 + x).cumprod()
    return dict(sharpe=round(float(x.mean() / x.std() * np.sqrt(ann)), 2) if x.std() > 0 else None,
                cagr=round(float(eq.iloc[-1] ** (ann / len(x)) - 1), 3), max_dd=round(float((eq / eq.cummax() - 1).min()), 3),
                total=round(float(eq.iloc[-1] - 1), 3), days=int(len(x)))


def main(gold_path):
    res = dict(plan="edges/plans/E85_trend_vol_controller.md", md5=PLAN, assets={})
    verdicts = []
    for asset, (c, f, ann, cost) in (("BTC", btc()), ("GOLD", gold(gold_path))):
        B = books(c, f, ann, cost)
        A = {}
        for p, (a, b) in PER[asset].items():
            A[p] = {f"{n}/{k}": stats(s[(s.index >= a) & (s.index < b)], ann) for (n, k), s in B.items()}
            bt.log_attempt(PLAN, f"E85 {asset} controller", p, dict(n=A[p]["controller/base"]["days"], mean_bp=None, t_week=A[p]["controller/base"]["sharpe"]))
        ok = all(A[p]["controller/base"]["sharpe"] > A[p]["buy_hold/base"]["sharpe"]
                 and A[p]["controller/base"]["sharpe"] > A[p]["vol_only/base"]["sharpe"]
                 and A[p]["controller/base"]["max_dd"] > 0.75 * A[p]["buy_hold/base"]["max_dd"] for p in ("validation", "final"))
        verdicts.append(f"{asset} {'PASS' if ok else 'FAIL'}")
        res["assets"][asset] = A
        for p in PER[asset]:
            row = {k: (v["sharpe"], v["cagr"], v["max_dd"]) for k, v in A[p].items() if k.endswith("/base")}
            print(asset, p, row, "| controller stress", (A[p]["controller/stress"]["sharpe"], A[p]["controller/stress"]["cagr"]), flush=True)
    res["verdict"] = "; ".join(verdicts)
    json.dump(res, open("edges/results/E85_result.json", "w"), indent=1)
    print(res["verdict"])


if __name__ == "__main__":
    main(sys.argv[1])
