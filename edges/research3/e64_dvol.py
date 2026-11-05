"""E64 — Deribit DVOL spikes / VRP (plan edges/plans/E64_dvol.md). Discovery 2021-03-24 → 2023-12-31."""
import warnings
import numpy as np
import pandas as pd
from edges.research3.common import perp, DATA, circ_shift
from edges.research3.driver import run_plan

warnings.filterwarnings("ignore")
DV = {}
for c in ("BTC", "ETH"):
    d = pd.read_parquet(f"{DATA}/deribit_dvol/{c}.parquet")
    s = pd.Series(d.c.values.astype(float), index=pd.to_datetime(d.ts, unit="ms", utc=True)).sort_index()
    DV[c + "USDT"] = s[~s.index.duplicated()].asfreq("h").ffill()
PERPS = {c: perp(c) for c in DV}


def rq(x, q, w=24 * 365):
    return pd.Series(x).rolling(w, min_periods=w // 2).quantile(q).shift(1).values


def feats(c, shift):
    df = PERPS[c]
    s = circ_shift(DV[c], shift) if shift else DV[c]
    k = s.copy()
    k.index = k.index + pd.Timedelta(hours=1)                  # hour bar ts closes at ts+1h → usable at that open
    k = k.reindex(df.index)
    v = k.values
    lr = np.log(df.o / df.o.shift(1))                           # returns known at entry (open-to-open)
    rv = lr.rolling(720, min_periods=500).std().values * np.sqrt(8760) * 100
    vrp = v - rv
    z = ((k - k.rolling(720, min_periods=500).mean().shift(1)) / k.rolling(720, min_periods=500).std().shift(1)).values
    ch = np.log(k / k.shift(24)).values
    return df, dict(v=v, ch=ch, z=z, vrp=vrp, lo10=rq(vrp, 0.1), hi90=rq(vrp, 0.9))


V = []
for kk in (0.15, 0.25, 0.35):
    for H in (12, 24, 72):
        V.append((f"A spike>={kk} H{H}", lambda F, kk=kk: (F["ch"] >= kk, 1), H))
for z0 in (2, 3):
    for H in (24, 72):
        V.append((f"B z>={z0} H{H}", lambda F, z0=z0: (F["z"] >= z0, 1), H))
for H in (24, 72):
    V.append((f"C vrp<=p10 long H{H}", lambda F: (F["vrp"] <= F["lo10"], 1), H))
    V.append((f"C vrp>=p90 short H{H}", lambda F: (F["vrp"] >= F["hi90"], -1), H))

if __name__ == "__main__":
    n = len(DV["BTCUSDT"])
    out, R = run_plan("E64", "E64_dvol", list(PERPS), feats, V, n_null=200, disc_start="2021-03-24",
                      shift_range=(60 * 24, n - 60 * 24))
    print({k: out[k] for k in ("luck", "promoted", "validation", "final", "verdict")})
    for r in sorted(out["discovery"], key=lambda r: -(r["t"] if r["t"] == r["t"] else -9))[:8]:
        print(r["label"], r["n"], r.get("mean_bp"), round(r["t"], 2), r.get("years"))
