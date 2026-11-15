"""Bar-by-bar replay of the live Signal Lab detectors on history (used by E148/E149)."""
import numpy as np, pandas as pd
from edges.lib import bt
from edges.siglab import lab
from edges.auditor import core

agg = dict(o="first", h="max", l="min", c="last")


def replay(sym, fine, start):
    F = fine.resample("15min").agg(agg).dropna()
    H1 = fine.resample("1h").agg(agg).dropna()
    ft = np.asarray((fine.index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta("1ms"), dtype="int64")
    FO, FH, FL, FC = fine.o.values, fine.h.values, fine.l.values, fine.c.values
    span = int(25 * 3600_000 / int(ft[1] - ft[0]))
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
        for setup, d, why in found:
            if (setup, str(end.date())) in seen:
                continue
            seen.add((setup, str(end.date())))
            s = lab.make(sym, setup, d, why, ctx)
            j = np.searchsorted(ft, s["logged_ms"])
            bars = [dict(t=int(ft[q]), o=FO[q], h=FH[q], l=FL[q], c=FC[q]) for q in range(j, min(j + span, len(ft)))]
            r = core.score(core.Signal(sym, s["side"], s["logged_ms"], stop=s["stop"], targets=s["targets"]), bars, 1, 24)
            if r.get("status") == "closed":
                rows.append(dict(time=end, setup=setup, side="with" if s["state"]["with_trend"] else "against", vol=s["state"]["vol"],
                                 shape=s["state"]["shape"], session=s["state"]["session"], R=r["ladder"]["R"], R1=r["tp1"]["R"]))
    return pd.DataFrame(rows)


def st(x):
    if len(x) < 8:
        return dict(n=int(len(x)))
    return dict(n=int(len(x)), avg_R=round(float(x.R.mean()), 3), t=round(bt.tstat_weekly(x.assign(net=x.R)), 2), win=round(float((x.R > 0).mean()), 3))
