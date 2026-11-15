"""E148 replay of the Signal Lab setups (plan edges/plans/E148_siglab_replay.md)."""
import json, sys, warnings
import numpy as np, pandas as pd
from edges.lib import bt
from edges.siglab import lab
from edges.auditor import core

warnings.filterwarnings("ignore")
PLAN = sys.argv[2]
agg = dict(o="first", h="max", l="min", c="last")


def replay(sym, fine, start):
    F = fine.resample("15min").agg(agg).dropna()
    H1 = fine.resample("1h").agg(agg).dropna()
    ft = np.asarray((fine.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms"), dtype="int64")
    FO, FH, FL, FC = fine.o.values, fine.h.values, fine.l.values, fine.c.values
    step_ms = int(ft[1] - ft[0])
    span = int(25 * 3600_000 / step_ms)
    h1_end = (H1.index + pd.Timedelta("1h")).values
    seen, rows = set(), []
    i0 = max(300, F.index.searchsorted(pd.Timestamp(start, tz="UTC")))
    for i in range(i0, len(F) - 100):
        f = F.iloc[i - 299:i + 1]
        end = f.index[-1] + pd.Timedelta("15min")
        k = np.searchsorted(h1_end, end.to_datetime64(), side="right")
        found, ctx = lab.detect(f, H1.iloc[max(0, k - 60):k])
        if not ctx:
            continue
        day = str(end.date())
        for setup, d, why in found:
            if (setup, day) in seen:
                continue
            seen.add((setup, day))
            s = lab.make(sym, setup, d, why, ctx)
            j = np.searchsorted(ft, s["logged_ms"])
            bars = [dict(t=int(ft[q]), o=FO[q], h=FH[q], l=FL[q], c=FC[q]) for q in range(j, min(j + span, len(ft)))]
            r = core.score(core.Signal(sym, s["side"], s["logged_ms"], stop=s["stop"], targets=s["targets"]), bars, 1, 24)
            if r.get("status") == "closed":
                rows.append(dict(time=end, setup=setup, side="with" if s["state"]["with_trend"] else "against", vol=s["state"]["vol"], R=r["ladder"]["R"], R1=r["tp1"]["R"]))
    return pd.DataFrame(rows)


def st(x):
    if len(x) < 8:
        return dict(n=int(len(x)))
    return dict(n=int(len(x)), avg_R=round(float(x.R.mean()), 3), t=round(bt.tstat_weekly(x.assign(net=x.R)), 2), win=round(float((x.R > 0).mean()), 3))


res = dict(plan="edges/plans/E148_siglab_replay.md", md5=PLAN, assets={}, muted={}, backtest_plus={})
gold = pd.read_parquet(sys.argv[1])[["o", "h", "l", "c"]].astype(float)
btc = bt.load("BTCUSDT", "5m")[["o", "h", "l", "c"]].astype(float)["2023-12-20":]
for sym, fine, start, per in (("XAUUSD", gold, "2025-12-15", {"train": ("2025-12-01", "2026-06-01"), "val": ("2026-06-01", "2026-09-01"), "final": ("2026-09-01", "2026-12-01")}),
                              ("BTCUSD", btc, "2024-01-01", {"train": ("2024-01-01", "2025-01-01"), "val": ("2025-01-01", "2025-07-01"), "final": ("2025-07-01", "2026-12-01")})):
    T = replay(sym, fine, start)
    A, mut, plus = {}, [], []
    for setup in sorted(T.setup.unique()):
        for side in ("all", "with", "against"):
            x = T[T.setup == setup] if side == "all" else T[(T.setup == setup) & (T.side == side)]
            cell = {p: st(x[(x.time >= pd.Timestamp(a, tz="UTC")) & (x.time < pd.Timestamp(b, tz="UTC"))]) for p, (a, b) in per.items()}
            A[f"{setup} {side}"] = cell
            v, f_ = cell["val"], cell["final"]
            if side != "all":
                for p in ("val", "final"):
                    bt.log_attempt(PLAN, f"E148 {sym} {setup} {side}", p, dict(n=cell[p].get("n"), mean_bp=cell[p].get("avg_R"), t_week=cell[p].get("t")))
                if (v.get("avg_R") or 0) < 0 and (f_.get("avg_R") or 0) < 0 and min(v.get("t") or 0, f_.get("t") or 0) <= -1.5:
                    mut.append(f"{setup} {side}")
                if (v.get("avg_R") or -1) > 0 and (f_.get("avg_R") or -1) > 0 and (f_.get("t") or 0) >= 2:
                    plus.append(f"{setup} {side}")
            print(sym, setup, side, {p: (c.get("n"), c.get("avg_R"), c.get("t"), c.get("win")) for p, c in cell.items()}, flush=True)
    res["assets"][sym], res["muted"][sym], res["backtest_plus"][sym] = A, mut, plus
    print(sym, "MUTED", mut, "PLUS", plus, flush=True)
json.dump(res, open("edges/results/E148_result.json", "w"), indent=1, default=str)
