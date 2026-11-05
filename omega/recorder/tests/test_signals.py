"""The recorder's H1/H3 must give exactly the research engine's trades (E22), and must not look ahead when run live."""
import numpy as np
import reference_e22 as R
from synth import market
from omega_recorder import signals as S

H1R = dict(mode="limit", q=10, k=2, W=3); H3R = dict(mode="taker", q=5, b=20)

def build(n_coins=10, n=2400):
    dfs = {f"C{i}": market(i, n) for i in range(n_coins)}
    ref = {k: R.prep(d) for k, d in dfs.items()}
    mine = {k: S.prep(d.index.values, d.c.values, d.hi.values, d.lo.values) for k, d in dfs.items()}
    return dfs, ref, mine

def ref_trades(ref, spec, lo, hi):
    br = R.breadth_of(ref.values()); out = []
    for k, P in ref.items():
        out += [(k, int(h), round(r, 12)) for h, r in R.run(P, R.masks(P, spec, br), spec["mode"], lo, hi, min_age=720, k=spec.get("k"), W=spec.get("W"))]
    return sorted(out)

def my_trades(mine, spec, lo, hi, live=False):
    br = S.breadth_of(mine.values()); out = []
    for k, P in mine.items():
        out += [(k, t["signal_h"], round(t["net"], 12)) for t in S.run(P, S.mask(P, spec, br), spec, lo, hi, live=live) if t["status"] == "closed"]
    return sorted(out)

def test_breadth_identical():
    _, ref, mine = build()
    a, b = R.breadth_of(ref.values()), S.breadth_of(mine.values())
    assert a.keys() == b.keys() and all(abs(a[h] - b[h]) < 1e-12 for h in a)

def test_h1_and_h3_match_research_exactly():
    dfs, ref, mine = build()
    lo, hi = 473_352, 473_352 + 2400
    for spec_r, spec_m in ((H1R, S.H1), (H3R, S.H3)):
        r = ref_trades(ref, spec_r, lo, hi); m = my_trades(mine, spec_m, lo, hi)
        assert len(r) >= 15, f"synthetic data too quiet for {spec_m['name']}: {len(r)} trades"
        assert r == m, f"{spec_m['name']}: research {len(r)} trades vs recorder {len(m)}"
        assert my_trades(mine, spec_m, lo, hi, live=True) == m     # live mode adds open/pending, never changes closed ones

def test_no_lookahead_when_run_hour_by_hour():
    """Trades closed by hour T must be the same whether computed with data up to T or with all data."""
    dfs, _, _ = build(8, 2200)
    full = {k: S.prep(d.index.values, d.c.values, d.hi.values, d.lo.values) for k, d in dfs.items()}
    fs = 473_352 + 900
    for cut in (1500, 1800, 2100):
        part = {k: S.prep(d.index.values[:cut], d.c.values[:cut], d.hi.values[:cut], d.lo.values[:cut]) for k, d in dfs.items()}
        T = 473_352 + cut - 1
        for spec in (S.H1, S.H3):
            bf, bp = S.breadth_of(full.values()), S.breadth_of(part.values())
            closed_full = sorted((k, t["signal_h"], round(t["net"], 12)) for k, P in full.items()
                                 for t in S.run(P, S.mask(P, spec, bf), spec, fs, T + 1) if t["exit_h"] <= T)
            closed_part = sorted((k, t["signal_h"], round(t["net"], 12)) for k, P in part.items()
                                 for t in S.run(P, S.mask(P, spec, bp), spec, fs, T + 1, live=True) if t["status"] == "closed")
            assert closed_full == closed_part, (spec["name"], cut)

def test_live_reports_pending_and_open():
    P = S.prep(np.arange(473_352, 473_352 + 1000), np.r_[np.full(990, 100.0), np.full(10, 70.0)], np.full(1000, 101.0), np.r_[np.full(997, 99.0), np.full(3, 50.0)])
    P["th"][10][:] = -0.1; P["sig"][:] = 0.01
    m = np.zeros(1000, bool); m[995] = True; m[998] = True
    tr = S.run(P, m, S.H1, 0, 10**9, live=True)
    st = {t["signal_h"] - 473_352: t["status"] for t in tr}
    assert st == {995: "open", 998: "open"}
    # a signal on the last candle, with no low below its limit yet, is pending (its 3-hour window is still running)
    P["l"][:] = 99.0; m[:] = False; m[999] = True
    assert [t["status"] for t in S.run(P, m, S.H1, 0, 10**9, live=True)] == ["pending"]
    assert S.run(P, m, S.H1, 0, 10**9) == []                       # research mode drops it, as e22_lib does
