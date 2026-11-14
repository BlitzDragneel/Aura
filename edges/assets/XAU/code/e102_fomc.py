"""E102 FOMC statement follow/fade on PAXG 15m (plan edges/plans/E102_fomc_xau.md). CPI/NFP/PPI skipped: BLS 403."""
import json, numpy as np, pandas as pd
from edges.assets.XAU.code import xlib as X
P = "E102"
UNSCHED = {"20200303", "20200315", "20200323", "20200331", "20200827"}

def trades(C, dates, W, mode, per, mult=1.0):
    k = int(pd.Timedelta("1h") / C.freq); w = W // 15
    ents, M = C.windows(X.NY, "14:00", "20:00", weekdays=range(7), dates=dates)
    lr_r, g_r = C.wret(M[:, :w]); Mh = M[:, w:w + 4 * k]; lr, g = C.wret(Mh)
    side = np.sign(lr_r) * (1 if mode == "FOLLOW" else -1)
    t = X.trades_from(ents + pd.Timedelta(minutes=W), lr, side, g & g_r, np.zeros(len(ents)), mult=mult)
    t["gross_bp_reaction"] = 0
    return X.cut(t, per, "time")

def main():
    C = X.Cells(X.bars("PAXG_15m"), "15min")
    ds = [d for d in json.load(open(f"{X.D}/fomc_statement_dates.json")) if d not in UNSCHED]
    dates = pd.DatetimeIndex(pd.to_datetime(ds))
    out = {"plan": P, "md5": X.MD5[P], "events": len(ds), "skipped": "CPI/NFP/PPI: bls.gov answers HTTP 403 from this machine",
           "periods": {}}
    specs = [(W, m) for W in (30, 60) for m in ("FOLLOW", "FADE")]
    wd = pd.date_range("2020-09-01", "2026-10-30", freq="B"); wd = wd[~wd.isin(dates)]
    rng = np.random.default_rng(4)
    for pn, per in X.PER_PAXG.items():
        for W, m in specs:
            t = trades(C, dates, W, m, per); s = X.summ(t, f"W{W}_{m}"); s["gross_bp"] = round(t.gross.mean() * 1e4, 2) if len(t) else None
            if pn == "discovery":
                null = [trades(C, pd.DatetimeIndex(rng.choice(wd, len(t), replace=False)), W, m, per).net.mean() for _ in range(200)]
                s["null_p95_bp"] = round(float(np.nanpercentile(null, 95)) * 1e4, 2)
            out["periods"].setdefault(pn, {})[f"W{W}_{m}"] = s; X.log(P, f"W{W}_{m}", pn, s)
            print(pn, W, m, s["n"], s.get("gross_bp"), s.get("mean_bp"), s.get("t_week"), s.get("null_p95_bp"), flush=True)
    d = out["periods"]["discovery"]
    elig = [k for k, s in d.items() if s["n"] >= 20 and s["t_week"] >= 2 and s["mean_bp"] > s["null_p95_bp"]]
    out["verdict"] = "FAIL (no discovery variant with t >= 2 beating the random-day null)" if not elig else f"eligible {elig}"
    X.dump(P, out); print(out["verdict"])

if __name__ == "__main__":
    main()
