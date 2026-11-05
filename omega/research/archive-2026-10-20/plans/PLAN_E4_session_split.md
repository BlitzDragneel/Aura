# PLAN E4 — does the metals session split hold on data nobody has seen?
Written 2026-10-20, after plan E3 on gold (Jul 2020 – Oct 2026) and before any of the data below exists.
Found on gold (descriptive, E3): holding only outside US hours made +103% (log, before costs) while holding only during
US hours (bars opening 13:00–20:00 UTC) made −21%. Gold cannot confirm this any more. Two untouched sets can:
  S1: XAG/USD hourly (silver), all of it, from the same OMEGA download (Twelve Data, UTC);
  S2: XAU/USD hourly BEFORE 2020-07-15 06:00 UTC, if the continued download reaches it (at least 2 years needed).
Each set is run ONCE, with the file's sha256 recorded first.
Bar return = ln(close / previous bar's close); "US hours" = bars opening 13:00–20:00 UTC; "outside" = all other bars.
Test A (the split): each calendar week, (sum of outside returns) − (sum of US-hours returns); t = mean/(sd/√weeks).
  Confirmed on a set if t ≥ 1.65 (one-sided 5%) AND the difference is positive in at least half the calendar years.
Test B (tradeable on a low-cost account): long outside US hours, flat during them, one round trip a day,
  0.005% a side (MT5 raw-spread level; financing/swap not included and reported as a limit); 0.02% also reported.
  Passes on a set if the weekly P&L has t ≥ 1.65 and is positive at 0.005% a side.
Reported whatever the result; nothing changes after seeing data. A confirmed split is a forward hypothesis for live
paper tracking, not a trading rule, until it also survives new weeks.
