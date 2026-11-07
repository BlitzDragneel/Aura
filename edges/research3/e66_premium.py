"""E66 — perp premium index extremes (plan edges/plans/E66_perp_premium.md)."""
import os, warnings
import numpy as np
import pandas as pd
from edges.research3.common import perp, DATA
from edges.research3.driver import run_plan

warnings.filterwarnings("ignore")
COINS, PREM, PERPS = [], {}, {}
for f in sorted(os.listdir(f"{DATA}/premium_1h")):
    if not f.endswith(".parquet"):
        continue
    c = f[:-8]
    if not os.path.exists(f"{DATA}/1h/{c}.parquet"):
        continue
    d = pd.read_parquet(f"{DATA}/premium_1h/{f}")
    s = pd.Series(d.c.values.astype(float), index=pd.to_datetime(d.ts, unit="ms", utc=True)).sort_index()
    s = s[~s.index.duplicated()]
    PREM[c] = s.asfreq("h")
    PERPS[c] = perp(c)
    COINS.append(c)


def feats(c, shift):
    df = PERPS[c]
    s = PREM[c]
    if shift:
        s = pd.Series(np.roll(s.values, shift % len(s)), index=s.index)
    s = s.copy(); s.index = s.index + pd.Timedelta(hours=1)
    m = s.rolling(720, min_periods=360).mean().shift(1)
    sd = s.rolling(720, min_periods=360).std().shift(1)
    z = ((s - m) / sd).reindex(df.index).values
    return df, dict(z=z, p=s.reindex(df.index).values)


V = []
for k in (3, 4, 5):
    for H in (4, 12, 24):
        V.append((f"Zlong z<=-{k} H{H}", lambda F, k=k: (F["z"] <= -k, 1), H))
        V.append((f"Zshort z>={k} H{H}", lambda F, k=k: (F["z"] >= k, -1), H))
for p in (0.003, 0.006):
    for H in (4, 12, 24):
        V.append((f"Raw p<=-{p} long H{H}", lambda F, p=p: (F["p"] <= -p, 1), H))

if __name__ == "__main__":
    print(len(COINS), "coins")
    out, R = run_plan("E66", "E66_perp_premium", COINS, feats, V, n_null=100, shift_range=(60 * 24, 20000))
    print({k: out[k] for k in ("luck", "promoted", "validation", "final", "verdict")})
    for r in sorted(out["discovery"], key=lambda r: -(r["t"] if r["t"] == r["t"] else -9))[:8]:
        print(r["label"], r["n"], r.get("mean_bp"), round(r["t"], 2), r.get("per_day"), r.get("years"))
