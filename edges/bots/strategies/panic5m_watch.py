"""WATCH (grade C, paper only): E37 panic bounce, limit entry on 5-minute bars — variant judged in FINAL: L288 k4 W3 H288.

The coin's 24-hour (288 x 5m) log return is in its own bottom 10% (thresholds from the 8640 bars = 30 days before,
refreshed every 288 bars) -> limit buy at close * exp(-4 sigma) (sigma = std of the 168 5m returns before, >= 120 valid);
fills only if one of the next 3 bars trades below it; exit at the close 288 bars (24 h) after the fill bar.
30 coins (the research's 5m universe). Research (edges/results/E37_result.json): discovery 2022-23 +72.6 bp t 2.56,
validation 2024 +93.8 t 1.83, FINAL 2025-26 +31.8 bp t 1.05 (n 3,345, 5/day), without the best 5% -32.7 -> FAIL,
kept on the watch list to build a forward record. Not tradable.
"""
from edges.bots.strategies._panic_tf import PanicTF


class Panic5mWatch(PanicTF):
    id = "panic5m_watch"
    tf = "5m"
    L, K, W, H = 288, 4.0, 3, 288
    LOOK, STEP = 8640, 288


STRATEGY = Panic5mWatch()
