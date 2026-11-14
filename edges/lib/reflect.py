"""Learn from losses without fooling ourselves.

reflect(trades, features) looks ONLY at DISCOVERY trades and asks: where did the losses cluster? For each feature it
splits trades into buckets (terciles for numbers) and reports mean R per bucket. The best bucket becomes a candidate
filter, which must then pass VALIDATION and FINAL like any new rule. Every bucket looked at is counted as a variant,
so the luck check knows how many places we searched.
"""
import numpy as np
import pandas as pd


def buckets(x: pd.Series):
    if x.dtype.kind in "biu" and x.nunique() <= 24:
        return x.astype(str)
    q = x.rank(pct=True)
    return pd.cut(q, [0, 1 / 3, 2 / 3, 1.0], labels=["low", "mid", "high"], include_lowest=True).astype(str)


def reflect(trades: pd.DataFrame, features: list[str], r_col: str = "R", min_n: int = 30):
    rows = []
    for f in features:
        b = buckets(trades[f])
        g = trades.groupby(b)[r_col].agg(["mean", "count", lambda s: (s > 0).mean()])
        for k, r in g.iterrows():
            if r["count"] >= min_n:
                se = trades[r_col][b == k].std() / np.sqrt(r["count"])
                rows.append(dict(feature=f, bucket=k, n=int(r["count"]), mean_R=round(float(r["mean"]), 3),
                                 win=round(float(r.iloc[2]), 3), t=round(float(r["mean"] / se), 2) if se > 0 else None))
    out = pd.DataFrame(rows).sort_values("mean_R", ascending=False)
    return out, len(rows)


def plain(table: pd.DataFrame, top: int = 3) -> str:
    best = table.head(top)
    worst = table.tail(top)
    s = ["Losses cluster in: " + "; ".join(f"{r.feature}={r.bucket} ({r.mean_R:+.2f}R, n={r.n})" for r in worst.itertuples()),
         "Wins cluster in: " + "; ".join(f"{r.feature}={r.bucket} ({r.mean_R:+.2f}R, n={r.n})" for r in best.itertuples())]
    return "\n".join(s)
