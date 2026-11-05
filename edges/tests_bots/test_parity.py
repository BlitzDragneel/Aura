"""PARITY: edges/bots panic_h1 (and panic_h3) reproduce the research engine's trades on the same parquet data.

The research engine is omega/research/e25kit/reference_e22.py (verbatim e22_lib). It is fed the same coins on the same
dense hourly grid (first parquet row -> last), min_age 720 as in the E25 run. Our backtester runs with gap_policy="skip"
(the reference drops a trade whose exit candle is missing) and its trades are compared one by one: same signal hour,
same fill, same exit, same gross return (the reference's return + its fixed 0.12% / 0.20% cost)."""
import importlib.util, os
import numpy as np
import pandas as pd
import pytest
from edges.lib import bt
from edges.bots import backtest as B

REF = os.path.join(os.path.dirname(__file__), "..", "..", "omega", "research", "e25kit", "reference_e22.py")
WANT = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "AAVEUSDT", "1000PEPEUSDT", "ACHUSDT", "1INCHUSDT", "AGLDUSDT",
        "1000SHIBUSDT", "ALGOUSDT", "ALICEUSDT", "ANKRUSDT", "APEUSDT", "ARUSDT", "ATOMUSDT", "AVAXUSDT", "AXSUSDT"]
COINS = [s for s in WANT if os.path.exists(f"{bt.DATA}/1h/{s}.parquet")][:10]
pytestmark = pytest.mark.skipif(len(COINS) < 5, reason="fewer than 5 coins downloaded yet")


def ref_module():
    spec = importlib.util.spec_from_file_location("reference_e22", REF)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ref_prep(R, sym):
    d = bt.load(sym)
    d = d[~d.index.duplicated(keep="last")].sort_index()
    h = (d.ts.values // 3_600_000).astype(np.int64)
    ok = d.v.values > 0
    idx = np.arange(h[0], h[-1] + 1)
    df = pd.DataFrame(index=idx, columns=["c", "hi", "lo", "v"], dtype=float)
    df.loc[h[ok], ["c", "hi", "lo", "v"]] = np.c_[d.c.values[ok], d.h.values[ok], d.l.values[ok], d.v.values[ok]]
    return R.prep(df)


@pytest.fixture(scope="module")
def ref():
    R = ref_module()
    return R, {s: ref_prep(R, s) for s in COINS}


def ours(strategy, coins):
    tr, _ = B.run(strategy, syms=coins, start=None, gap_policy="skip", funding=False, verbose=False)
    f = tr[tr.status == "filled"]
    return f


def test_h1_parity(ref):
    R, Ps = ref
    lo, hi = -10**9, 10**9
    want = []
    for s, P in Ps.items():
        for h, r in R.run(P, R.masks(P, dict(q=10)), "limit", lo, hi, min_age=720, k=2, W=3):
            want.append((s, int(h), round(r + 0.0012, 9)))
    f = ours("panic_h1", COINS)
    got = [(r.sym, int(r.signal_time.timestamp() // 3600), round(r.gross, 9)) for r in f.itertuples()]
    assert len(want) > 20, "too few reference trades to compare"
    assert sorted(got) == sorted(want)


def test_h3_parity(ref):
    R, Ps = ref
    br = R.breadth_of(Ps.values())
    want = []
    for s, P in Ps.items():
        m = R.masks(P, dict(q=5, b=20), br)
        for h, r in R.run(P, m, "taker", -10**9, 10**9, min_age=720):
            want.append((s, int(h)))
    f = ours("panic_h3", COINS)
    got = [(r.sym, int(r.signal_time.timestamp() // 3600)) for r in f.itertuples()]
    # H3 enters at the next bar's open (what a market order after the close gets); the reference books the close.
    assert sorted(got) == sorted(want)
