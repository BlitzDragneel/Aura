import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from edges.siglab import lab


def sig(setup, with_trend, R):
    return dict(symbol="XAUUSD", setup=setup, status="closed", R_ladder=R, state=dict(with_trend=with_trend))


def test_adapt_mutes_and_unmutes():
    S = dict(signals=[dict(sig("S5", True, -0.3) if i % 3 else sig("S5", True, 0.1), logged_ms=i * 3_600_000) for i in range(40)])
    m = lab.adapt(S)
    assert S["adapt"]["S5 with"]["state"] == "muted" and m and "MUTED" in m[0]
    s = lab.make("XAUUSD", "S5", 1, "x", dict(price=4000, R=10, bar_close_ms=0, state=dict(trend="up", vol="normal", shape="normal", session="London")))
    assert lab.prior(s)[0] == "muted" and "No trade plan" in lab.text(s, "PAPER", lab.stats([]))
    S["signals"] = [dict(sig("S5", True, 0.5) if i % 4 else sig("S5", True, -0.5), logged_ms=i * 3_600_000) for i in range(60)]
    m = lab.adapt(S)
    assert S["adapt"]["S5 with"]["state"] == "earned" and "EARNED" in m[0]
    assert "EARNED LIVE" in lab.text(s, "PAPER", lab.stats([]))
    assert len(S["adapt_log"]) == 2
