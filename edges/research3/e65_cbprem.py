"""E65 — Coinbase premium vs Binance spot (plan edges/plans/E65_coinbase_premium.md)."""
import warnings
import numpy as np
import pandas as pd
from edges.research3.common import perp, DATA, circ_shift
from edges.research3.driver import run_plan

warnings.filterwarnings("ignore")


def _s(path, col="c"):
    d = pd.read_parquet(path)
    s = pd.Series(d[col].values.astype(float), index=pd.to_datetime(d.ts, unit="ms", utc=True)).sort_index()
    s = s[~s.index.duplicated()]
    if "v" in d:
        v = pd.Series(d.v.values, index=pd.to_datetime(d.ts, unit="ms", utc=True)).sort_index()
        s[v[~v.index.duplicated()].reindex(s.index) <= 0] = np.nan
    return s


PREM = {}
for a, p in (("BTCUSDT", "BTC-USD"), ("ETHUSDT", "ETH-USD")):
    cb, bn = _s(f"{DATA}/coinbase_1h/{p}.parquet"), _s(f"{DATA}/spot_1h/{a}.parquet")
    idx = pd.date_range(pd.Timestamp("2020-01-01", tz="UTC"), max(cb.index.max(), bn.index.max()), freq="h")
    PREM[a] = np.log(cb.reindex(idx) / bn.reindex(idx))
PERPS = {c: perp(c) for c in PREM}


def feats(c, shift):
    df = PERPS[c]
    s = circ_shift(PREM[c], shift) if shift else PREM[c]
    s = s.copy(); s.index = s.index + pd.Timedelta(hours=1)
    out = {}
    for W in (168, 720):
        m = s.rolling(W, min_periods=W // 2).mean().shift(1)
        sd = s.rolling(W, min_periods=W // 2).std().shift(1)
        out[W] = ((s - m) / sd).reindex(df.index).values
    return df, out


V = []
for W in (168, 720):
    for k in (2, 3):
        for H in (4, 12, 24):
            for mode, sg in (("follow", 1), ("fade", -1)):
                V.append((f"{mode} W{W} k{k} H{H}", lambda F, W=W, k=k, sg=sg: (
                    np.abs(np.nan_to_num(F[W])) >= k, sg * np.sign(np.nan_to_num(F[W])).astype(int)), H))

if __name__ == "__main__":
    n = len(PREM["BTCUSDT"])
    out, R = run_plan("E65", "E65_coinbase_premium", list(PERPS), feats, V, n_null=200,
                      shift_range=(60 * 24, n - 60 * 24))
    print({k: out[k] for k in ("luck", "promoted", "validation", "final", "verdict")})
    for r in sorted(out["discovery"], key=lambda r: -(r["t"] if r["t"] == r["t"] else -9))[:8]:
        print(r["label"], r["n"], r.get("mean_bp"), round(r["t"], 2), r.get("per_day"), r.get("years"))
