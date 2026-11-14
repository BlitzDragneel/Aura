"""Leverage / stress table for the E97-passed H6 inverse-vol BTC/gold allocation (daily rebalanced L x weights)."""
import json, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from libbtc import *  # noqa
from e93_btc_gold import paxg_daily
from e94_holding import monthly
from e92_mom_rev import daily_funding


def table(rB, rG, advB, wB, wG, fd, cost=0.001):
    rows = []
    b0 = wB.shift(1).fillna(0); g0 = wG.shift(1).fillna(0)
    for L in (1, 2, 3, 5, 10, 20, 40):
        b, g = L * b0, L * g0
        r = b * rB + g * rG - cost * (b.diff().abs().fillna(0) + g.diff().abs().fillna(0)) - b * fd
        worst_intraday = (b * advB + g * np.minimum(rG, 0))  # BTC leg at its daily low, gold leg at its close
        liq_line = -(1.0 - 0.005)  # account-level: losing the whole equity (cross margin, 1 account)
        liq_days = int((worst_intraday <= liq_line).sum())
        s = curve_stats(r)
        rows.append(dict(leverage=L, sharpe=s["sharpe"], cagr=s["cagr"], maxdd=s["maxdd"], worst_day=round(float(r.min()), 4),
                         worst_intraday=round(float(worst_intraday.min()), 4), liquidation_days=liq_days))
    return rows


def main():
    d = bars("1d")
    pg = paxg_daily().reindex(d.index).ffill(limit=3)
    m = (d.index >= "2020-09-01") & (d.index < "2026-11-01")
    d = d[m]; pg = pg[m]
    fd = daily_funding(d)
    rB = d.c.pct_change().fillna(0); rG = pg.pct_change().fillna(0)
    advB = (d.l / d.c.shift(1) - 1).fillna(0)
    lB = np.log(d.c).diff(); lG = np.log(pg).diff()
    v60 = lB.rolling(60, min_periods=40).std() * np.sqrt(365); vg60 = lG.rolling(60, min_periods=40).std() * np.sqrt(365)
    ib = monthly(((1 / v60) / (1 / v60 + 1 / vg60)).ffill().fillna(0.5))
    out = dict(period="2020-09 -> 2026-10 (perp era; gold leg PAXG)", rows=table(rB, rG, advB, ib, 1 - ib, fd),
               bh_rows=table(rB, rG, advB, pd.Series(1.0, index=d.index), pd.Series(0.0, index=d.index), fd),
               note="Account-level (one cross-margined account holding both legs at L x the weights). liquidation_days = days "
                    "where the BTC leg at its daily low plus the gold leg at its close would lose >= 99.5% of equity.")
    r1 = out["rows"]
    ok = [r["leverage"] for r in r1 if r["liquidation_days"] == 0 and r["maxdd"] > -0.35]
    out["max_leverage_no_liq_dd_lt_35"] = max(ok) if ok else 0
    json.dump(out, open(f"{ROOT}/edges/results/E97_leverage.json", "w"), indent=1)
    for r in r1: print(r)
    print("B&H:", out["bh_rows"][:3])
    print("max lev", out["max_leverage_no_liq_dd_lt_35"])


if __name__ == "__main__":
    main()
