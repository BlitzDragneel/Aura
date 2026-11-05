# PLAN E19 — the path simulator, version 2, tested once on 20 coins it has never seen (written before running)
Written 2026-10-25 after E18 failed (md5 1d0b2050…): it expected slightly more movement than happened (50% range held 54.2%,
touch odds ~3 points high) because simulated volatility never calmed down and its shock library came from a wilder era.
Data: the 20 majors of omega_history_creed15_2–5 (ADA, DOGE, AVAX, LINK, LTC, TRX, DOT, BCH, NEAR, ATOM, UNI, APT, ARB, OP,
SUI, FIL, ICP, ETC, XLM, INJ), hourly, never used for any simulator. Test: daily origins 00:00 UTC, 2024-01-01 → 2026-10-17.
Two changes, decided now, nothing else changed from E18:
1. Volatility calms down: simulated variance v ← ω + 0.06·r² + 0.93·v (persistence 0.99, half-life about 3 days), with
   ω = 0.01 × the median EWMA variance of the 8,760 hours before the origin (the coin's own normal level, causal).
2. A current shock library and hour pattern: rebuilt at the start of each calendar quarter from the 17,520 hours (2 years)
   before it (at least 4,000 usable hours), and used for that quarter's origins. Direction neutral as before.
5,000 paths per origin (sampling error about ±0.7 points). Same pass marks as E18: (a) coverage within 2 points pooled and 4
per coin at 50/90/99%; (b) every event family ECE ≤ 0.02 and Brier better than the baseline (constant frequency from
2020–2023); (c) beyond the 99% range 0.4–2.0%. Run once; reported whatever happens.
