# PLAN E12 — stop-outs near entry: ordinary noise, or are stops at obvious levels hunted?
Written 2026-10-21 before computing anything below. Data: BTC and ETH hourly from omega_history_creed15_1, 2020 – Oct 2026.
Entries: every 4th hourly close, both a long and a short (not a strategy; a sample of ordinary entries). ATR = Wilder 14.
Two stop placements for each entry:
  OBVIOUS  : just beyond the prior 24-hour low (long) / high (short), by 0.1 ATR; used only when 0.5–3 ATR from entry.
  FIXED    : 1.5 ATR from entry, wherever that falls.
Measured within 48 hours of entry: (a) the stop is hit; (b) after the stop is hit, price reaches entry + 1 × stop distance in
the trade's direction within the next 24 hours ("stopped out, then it went my way").
Null: the same entries and rules on each coin's hourly moves shuffled into random order (no stops to hunt, no levels with
meaning), 20 shuffles.
Question 1 (is it noise?): the real rate of (b) among stopped trades vs the shuffled rate, for each placement.
Question 2 (are obvious stops hunted?): hunt effect = (real − shuffled rate of b) for OBVIOUS minus the same for FIXED.
  Evidence of hunting if the hunt effect > 0 and a bootstrap 95% interval (by week) excludes 0.
Reported whatever happens; nothing changed after seeing data.
