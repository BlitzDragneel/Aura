# PLAN E25 — addendum B (written 2026-10-25, after downloading and checking coverage; NO returns, signals or trades computed)
What was looked at before writing this: per coin, first/last candle, holes, zero-volume flat candles, and the last traded price.
FINDING: the archive keeps publishing flat candles (high = low, volume 0) at the last price after a perpetual stops trading
(e.g. WAVESUSDT last traded 2024-06-11, flat candles to 2026-10-18; LINA, OMG, STMX, REEF, AMB, ALPACA alike). Addendum A's
"data ends" definition would call these coins alive, and their flat hours (24-hour return 0 against a bottom-10% line of 0)
would count as panics in H3's breadth.
RULES, replacing addendum A point 3 where they differ:
1. Every candle with volume 0 is treated as MISSING (NaN), for every coin, at every hour (also the rare halt on a live coin).
2. A coin's last traded hour = its last candle with volume > 0. DELISTED = last traded hour before 2026-10-11 00:00 UTC.
3. Holds that run past a delisted coin's last traded hour exit at that hour's close − 5% (addendum A point 4b). Gaps inside a
   hold follow addendum A point 4c (missing = volume-0 or absent candles).
4. Breadth (H3) counts a coin at an hour only if it has a real (volume > 0) candle then and 24 hours before.
5. Reported in addition (not pass/fail): the count of delisted coins and of trades on them; the result without stablecoin pairs
   and without non-crypto perpetuals (stock, index and metal contracts), listed by name before the run.
6. Everything else in PLAN E25 and addendum A stands, including: no run until the data check against the final4 files.
