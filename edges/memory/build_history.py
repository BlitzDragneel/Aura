"""Replay (walk-forward, past-only memory, monthly refresh) of the E163 model over the seed candles, so the mistake
model starts with a record of the model's own out-of-sample rights and wrongs. Writes seed/<SYM>_history.parquet.
Usage: python -m edges.memory.build_history BTCUSD [months]"""
import sys
import numpy as np, pandas as pd
from edges.memory.features import RICH, describe_rich, outcomes
from edges.memory.model import META, predict
SEED = "edges/memory/seed"


def main(sym, months=14):
    f = pd.read_parquet(f"{SEED}/{sym}_15m.parquet").astype(float)
    X, Y = describe_rich(f), outcomes(f)
    ok = X.notna().all(axis=1) & Y.up1h.notna(); X, Y = X[ok], Y[ok]
    end = X.index[-1].to_period("M").to_timestamp().tz_localize("UTC") + pd.offsets.MonthBegin(1)
    ms = pd.date_range(end - pd.DateOffset(months=months), end, freq="MS")
    out = []
    for i, m in enumerate(ms[:-1]):
        mem = X.index < m - pd.Timedelta("5h"); q = (X.index >= m) & (X.index < ms[i + 1])
        if mem.sum() < 5000 or not q.any():
            continue
        P = predict(X[mem], Y[mem], X[q])
        P["right"] = ((P.p_up1h > 0.5) == (Y.up1h[q] > 0.5)).astype(float).values
        out.append(P[RICH + META + ["p_up1h", "right"]].astype("float32")); print(sym, m.date(), int(q.sum()), flush=True)
    H = pd.concat(out); H.to_parquet(f"{SEED}/{sym}_history.parquet", compression="zstd")
    print(sym, len(H), "acc", round(float(H.right.mean()), 3))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 14)
