"""E69 — CoinMetrics exchange flows / activity (plan edges/plans/E69_onchain_flows.md)."""
import warnings
import numpy as np
import pandas as pd
from edges.research3.common import perp, DATA
from edges.research3.driver import run_plan

warnings.filterwarnings("ignore")
CM = {}
for a, c in (("btc", "BTCUSDT"), ("eth", "ETHUSDT")):
    d = pd.read_parquet(f"{DATA}/coinmetrics/{a}.parquet")
    d.index = pd.to_datetime(d.ts, unit="ms", utc=True)
    CM[c] = d.sort_index().asfreq("D")[["FlowInExNtv", "FlowOutExNtv", "SplyExNtv", "AdrActCnt"]]
PERPS = {c: perp(c) for c in CM}


def feats(c, shift):
    df = PERPS[c]
    d = CM[c]
    if shift:
        d = pd.DataFrame(np.roll(d.values, shift, axis=0), index=d.index, columns=d.columns)
    nf7 = ((d.FlowInExNtv - d.FlowOutExNtv).rolling(7).sum() / d.SplyExNtv)
    z = (nf7 - nf7.rolling(365, min_periods=180).mean().shift(1)) / nf7.rolling(365, min_periods=180).std().shift(1)
    ds30 = np.log(d.SplyExNtv).diff(30)
    ds_lo = ds30.rolling(365, min_periods=180).quantile(0.1).shift(1)
    a7 = d.AdrActCnt.rolling(7).mean() / d.AdrActCnt.shift(7).rolling(28).mean() - 1
    za = (a7 - a7.rolling(365, min_periods=180).mean().shift(1)) / a7.rolling(365, min_periods=180).std().shift(1)
    X = pd.DataFrame(dict(z=z, sup=(ds30 <= ds_lo).astype(float), za=za))
    X.index = X.index + pd.Timedelta(hours=28)                 # day D usable from D+1 04:00
    X = X.reindex(df.index, method="ffill")
    at4 = df.index.hour == 4
    return df, dict(z=X.z.values, sup=X.sup.values, za=X.za.values, at4=at4)


V = []
for k in (1.5, 2, 2.5):
    for H in (3, 7, 14):
        V.append((f"Out z<=-{k} long H{H}d", lambda F, k=k: (F["at4"] & (F["z"] <= -k), 1), H * 24))
        V.append((f"In z>={k} short H{H}d", lambda F, k=k: (F["at4"] & (F["z"] >= k), -1), H * 24))
for H in (7, 14):
    V.append((f"Supply dS30<=p10 long H{H}d", lambda F: (F["at4"] & (F["sup"] > 0), 1), H * 24))
    V.append((f"Activity za>=2 long H{H}d", lambda F: (F["at4"] & (F["za"] >= 2), 1), H * 24))

if __name__ == "__main__":
    n = len(CM["BTCUSDT"])
    out, R = run_plan("E69", "E69_onchain_flows", list(PERPS), feats, V, n_null=200, shift_range=(60, n - 60))
    print({k: out[k] for k in ("luck", "promoted", "validation", "final", "verdict")})
    for r in sorted(out["discovery"], key=lambda r: -(r["t"] if r["t"] == r["t"] else -9))[:6]:
        print(r["label"], r["n"], r.get("mean_bp"), round(r["t"], 2), r.get("years"))
