# PLAN E2 — one-shot test of the 5-unit method and the new method on gold hourly
Written 2026-10-20, before any gold hourly data was downloaded (none exists in the research files; round 11 used daily gold).

Data: XAU/USD hourly candles (UTC) from Twelve Data, downloaded by OMEGA v6.5.84 (file omega-history-gold1h-*.json.gz),
as far back as Twelve Data serves. XAG/USD in the same file is reported separately and is not part of the pass.
Decoded with edge/load.py (the same format as the other history files). Before running: sha256 of the file recorded,
the file's own checks read (hours, dates, corrected and dropped candles, gaps over 72 hours).

Entry (frozen; no volume filter, because Twelve Data gives no volume for metals): at the close of an hourly bar that opened
13:00–20:00 UTC, the close is above the highest high of the 72 bars before it (long) or below their lowest low (short).
ATR = Wilder ATR(14) on hourly bars. One position at a time; a new signal is taken only when flat.

Methods (each judged on its own):
- M1, the owner's 5-unit method: 5 × 0.2 units at the next open; stop 2 ATR; at +1R close 60% and move the stop to entry;
  add 0.2 at each further +1R (up to 3; stop to the last add − 1R); trail 3 ATR from the best price; out after 168 hours.
- M2, the new method: a limit 0.5 ATR back from the signal close, valid 6 hours (otherwise skipped); stop 3 ATR; no adds;
  close half at +1R; trail 3 ATR from the best price; out after 168 hours.
Engine: edge/engine3.py (sim_all, account), as used for plan E1. Gaps (weekends) fill at the open when they jump a stop.

Costs: 0.05% a side on every fill (the main result); 0.10% a side reported as well. No funding (spot gold).
Account: 100 USDT, a true 1% risk every trade (no minimum-order rounding).

Pass, for each method: the account ends above 100 over the whole history AND beats at least 97.5% of 200 accounts with the
same signals and coin-flip direction (95% split over the two methods) AND at least half of the calendar years end positive.
Reported whatever the result. No rule, cost or period is changed after the data is seen; anything changed is a new plan
that needs new data.
