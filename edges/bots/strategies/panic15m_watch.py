"""WATCH (grade C, paper only): E38 panic bounce, limit entry on 15-minute bars — variant judged in FINAL: L96 k2 W12 H96.

15m bars are built from 5m candles exactly as the research (a 15m bar exists only if all three 5m bars do; core.resample).
The coin's 24-hour (96 x 15m) log return is in its own bottom 10% (thresholds from the 2880 bars = 30 days before,
refreshed every 96 bars) -> limit buy at close * exp(-2 sigma) (168 15m returns); fills only if one of the next 12 bars
trades below it; exit at the close 96 bars (24 h) after the fill bar. 30 coins.
Research (edges/results/E38_result.json): discovery winner was W3 (+76.3 bp t 2.53); W12 had the better validation
(+85.5 t 1.70) and was the variant judged: FINAL 2025-26 +2.8 bp t 0.10 (n 4,095) -> FAIL. Watch list only.
"""
from edges.bots.strategies._panic_tf import PanicTF


class Panic15mWatch(PanicTF):
    id = "panic15m_watch"
    tf = "15m"
    source_tf = "5m"
    L, K, W, H = 96, 2.0, 12, 96
    LOOK, STEP = 2880, 96


STRATEGY = Panic15mWatch()
