"""E97 BTC+gold inverse-vol allocation on untouched 2014-2019 (plans/E97_btc_gold_alloc_2014.md)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from libbtc import *  # noqa
from e94_holding import monthly
MD5 = "9792bb1a50e76d17b48f8620035aa7b8"


def main():
    cm = pd.read_parquet(f"{bt.DATA}/coinmetrics/btc_price_long.parquet").PriceUSD
    cm.index = cm.index.tz_convert("UTC").normalize() if cm.index.tz is not None else cm.index.tz_localize("UTC").normalize()
    # data check vs Binance perp 2020 closes (outside the test period)
    d = bars("1d")
    j = pd.concat([cm, d.c], axis=1, keys=["cm", "bn"]).loc["2020-02-01":"2020-12-31"].dropna()
    check = dict(corr_ret_same_day=float(j.cm.pct_change().corr(j.bn.pct_change())),
                 corr_ret_shift=float(j.cm.pct_change().corr(j.bn.pct_change().shift(1))),
                 med_abs_diff_pct=float((j.cm / j.bn - 1).abs().median()))
    gc = pd.read_parquet(f"{bt.DATA}/metals/GC_1d.parquet").c
    gc.index = pd.DatetimeIndex(gc.index).tz_convert("UTC").normalize()
    idx = pd.date_range("2012-06-01", "2019-12-31", freq="D", tz="UTC")
    btc = cm.reindex(idx).ffill(limit=3); gold = gc[~gc.index.duplicated()].reindex(idx).ffill()
    rB = btc.pct_change().fillna(0); rG = gold.pct_change().fillna(0)
    lB = np.log(btc).diff(); lG = np.log(gold).diff()
    v20 = lB.rolling(20, min_periods=15).std() * np.sqrt(365)
    v60 = lB.rolling(60, min_periods=40).std() * np.sqrt(365); vg60 = lG.rolling(60, min_periods=40).std() * np.sqrt(365)
    above = (btc > btc.rolling(200, min_periods=200).mean()).astype(float)
    part = sum((btc / btc.shift(n) - 1 > 0).astype(float) for n in (20, 60, 120)) / 3
    ib = monthly(((1 / v60) / (1 / v60 + 1 / vg60)).ffill().fillna(0.5))
    one = pd.Series(1.0, index=idx); zero = 0 * one
    W = {"BTC buy&hold": (one, zero), "H6 inv-vol BTC/gold": (ib, 1 - ib),
         "H7 H6 + SMA200 (info)": (ib * above, 1 - ib * above),
         "H2 E85 controller (info)": (part * np.minimum(1, 0.10 / np.maximum(v20, v60)).fillna(0), zero),
         "50/50 (info)": (0.5 * one, 0.5 * one), "gold buy&hold (info)": (zero, one)}
    def run(b, g):
        b = b.shift(1).fillna(0); g = g.shift(1).fillna(0)
        return b * rB + g * rG - 0.001 * (b.diff().abs().fillna(0) + g.diff().abs().fillna(0))
    R = {k: run(*w) for k, w in W.items()}
    out = dict(plan="E97", md5=MD5, data_check_2020=check, stats={})
    for k, r in R.items():
        s = {}
        for nm, (a, b) in {"2014-2019": ("2014-01-01", "2020-01-01"), "2014-2016": ("2014-01-01", "2017-01-01"),
                           "2017-2019": ("2017-01-01", "2020-01-01")}.items():
            x = r[(r.index >= a) & (r.index < b)]
            s[nm] = curve_stats(x); s[nm]["total_return"] = round(float((1 + x).prod() - 1), 4)
        x = r[(r.index >= "2014-01-01") & (r.index < "2020-01-01")]
        s["years"] = {int(y): round(float((1 + v).prod() - 1), 4) for y, v in x.groupby(x.index.year)}
        out["stats"][k] = s
    h6, bh = out["stats"]["H6 inv-vol BTC/gold"], out["stats"]["BTC buy&hold"]
    bt.log_attempt(MD5, "H6 inv-vol BTC/gold", "final", h6["2014-2019"])
    chk = dict(sharpe=h6["2014-2019"]["sharpe"] > bh["2014-2019"]["sharpe"],
               dd=h6["2014-2019"]["maxdd"] >= 0.75 * bh["2014-2019"]["maxdd"],
               ret=h6["2014-2019"]["total_return"] > 0,
               years=sum(v > 0 for v in h6["years"].values()) >= 4)
    out["checks"] = chk; out["verdict"] = "PASS" if all(chk.values()) else "FAIL"
    json.dump(out, open(f"{ROOT}/edges/results/E97_result.json", "w"), indent=1, default=str)
    print(check)
    for k, s in out["stats"].items():
        print(f"{k:26s}", " | ".join(f"{p} Sh {s[p]['sharpe']:5.2f} CAGR {s[p]['cagr']*100:6.1f}% DD {s[p]['maxdd']*100:5.1f}%" for p in ("2014-2019", "2014-2016", "2017-2019")), s["years"])
    print(chk, out["verdict"])


if __name__ == "__main__":
    main()
