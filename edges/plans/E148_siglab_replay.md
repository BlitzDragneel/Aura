# E148 Replay of the Signal Lab's seven setups on history (to mute the ones that lose)
The live Signal Lab (edges/siglab/lab.py, code as committed in 2802eb9) is replayed bar by bar, unchanged: same
detectors, same template (stop 1R = max(ATR 1h, 0.2%), targets every 0.5R to 2.5R), same scorer (1-minute path for gold,
5-minute for BTC, stop first, spread charged, 24h limit), one signal per setup per UTC day.
Data: gold perp 2025-12-11 -> 2026-11-13 (TRAIN -> May, VALIDATION Jun-Aug, FINAL Sep-Nov); BTC perp 5m 2024-01 ->
2026-11-03 (TRAIN 2024, VALIDATION 2025-H1, FINAL 2025-07 -> 2026-11).
Reported per setup and per setup x (with/against the 15m trend): n, average R ("fifths, stop to entry after TP1"),
week-clustered t, win rate, for each period.
Use (fixed now): a setup x trend-side cell is MUTED in the live lab (logged, never sent) if its average R is negative
in BOTH validation and final with t <= -1.5 in at least one of them, on that asset. A cell is given a head start
(label "BACKTEST+" shown next to PAPER) only if average R > 0 in validation AND final with t >= 2 in final; it still
needs its own forward record to become PROMISING/CONFIDENT. Everything else stays PAPER. 28 cells per asset counted.
