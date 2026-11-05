# PLAN E21 — the deep scan: which rules have a consistent direction before costs, either way (written before running)
Written 2026-10-25. Question from the owner: can the inverse of what failed work? A rule's inverse is the same trade taken the
other way, so the scan measures every rule's GROSS (before costs) result; a consistent loser's inverse is a consistent winner.
RULE LIBRARY (73 rules, hourly, entry at the signal hour's close, exit H hours later, no overlap within a coin):
 F1 momentum: past L-hour return in the top 10% (long) / bottom 10% (short) of the coin's previous 720 hours; L 1,4,24,72; H 1,4,24.
 F2 breakout: close above the prior N-hour high (long) / below the low (short); N 24,72,168; H 4,24.
 F3 sweep: high above the prior N-hour high but close back below it (short) / mirror (long); N 24,72; H 4,24.
 F4 RSI(14): below 30 long / above 70 short; H 4,24.     F5 close crosses above (long) / below (short) its N-hour average; N 50,200; H 24.
 F6 volume over 3× its 168-hour median with an up hour (long) / down hour (short); H 4,24.
 F7 an hour of 3σ or more (σ of the prior 168 hours) up (long) / down (short); H 4,24.
 F8 long through each session from its start: Asia 00 (8 h), London 08 (5 h), US 13 (8 h), Late 21 (3 h).
 F9 quiet market (24 h range under half its 720-hour median): top 10% of the 72-hour range short / bottom 10% long; H 24.
 F10 long each weekday from 00:00 UTC for 24 h (7 rules).
DISCOVERY on the 25 majors (creed15_1–5), 2020-03 → 2023-12 and 2024-01 → 2026-10-18; trades pooled by week (equal weight).
 A candidate = the rule, or its inverse, whose gross weekly t has the same sign with |t| ≥ 2.0 in BOTH periods and whose gross
 mean per trade is at least 0.25% in BOTH (round-trip costs are 0.20%).
TEST, run ONCE: the candidates on the Binance USD-M perpetuals of the final4 files that are NOT among the 25 majors,
 2024-01-01 → 2026-10-18, coins listed 30+ days, after 0.20% round-trip costs. Pass: net weekly t ≥ the one-sided Bonferroni bar
 for the number of candidates (α 0.05/m), net mean > 0, and positive in 2024, 2025 and 2026. Reported whatever happens.
