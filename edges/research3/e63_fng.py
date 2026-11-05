"""E63 — Fear & Greed extremes (plan edges/plans/E63_fear_greed.md)."""
import numpy as np
import pandas as pd
from edges.research3.common import perp, DATA, circ_shift
from edges.research3.driver import run_plan

FNG = pd.read_parquet(f"{DATA}/fear_greed/fng.parquet")
FNG = pd.Series(FNG.value.values.astype(float), index=pd.to_datetime(FNG.ts, unit="ms", utc=True)).sort_index()
FNG = FNG[~FNG.index.duplicated()].asfreq("D")
PERPS = {c: perp(c) for c in ("BTCUSDT", "ETHUSDT")}


def feats(c, shift):
    df = PERPS[c]
    s = circ_shift(FNG, shift) if shift else FNG
    known = s.copy()
    known.index = known.index + pd.Timedelta(hours=2)          # value stamped D is usable from D 02:00
    v = known.reindex(df.index, method="ffill").values
    d3 = (known - known.shift(3)).reindex(df.index, method="ffill").values
    at2 = (df.index.hour == 2)
    return df, dict(v=v, d3=d3, at2=at2)


V = []
for X in (10, 15, 20, 25):
    for H in (3, 7, 14):
        V.append((f"L fng<={X} H{H}d", lambda F, X=X: (F["at2"] & (F["v"] <= X), 1), H * 24))
for Y in (75, 80, 85, 90):
    for H in (3, 7, 14):
        V.append((f"S fng>={Y} H{H}d", lambda F, Y=Y: (F["at2"] & (F["v"] >= Y), -1), H * 24))
for H in (3, 7, 14):
    V.append((f"D drop20/3d H{H}d", lambda F: (F["at2"] & (F["d3"] <= -20), 1), H * 24))

if __name__ == "__main__":
    n = len(FNG)
    out, R = run_plan("E63", "E63_fear_greed", list(PERPS), feats, V, n_null=200, shift_range=(60, n - 60))
    print({k: out[k] for k in ("luck", "promoted", "validation", "final", "verdict")})
    for r in sorted(out["discovery"], key=lambda r: -(r["t"] if r["t"] == r["t"] else -9))[:8]:
        print(r["label"], r["n"], r["mean_bp"], round(r["t"], 2), r["years"])
