# PLAN E28 — the daily-trading search (written 2026-10-26 before any daily panel or result exists)
GOAL: a rule that gives trades on most days (≥ 1 position on ≥ 80% of days), net positive after costs and funding, that a
100 USDT account can run (positions ≥ 5 USDT), and that survives data it was not chosen on.

DATA: Binance's archive, every USDT perpetual incl. delisted (E26 data, 2020-11 → 2026-10-18; volume-0 candles missing; a coin
whose data ends during a hold exits at its last close with a 5% penalty against the position) + the archive's funding rates.
Daily bars 00:00–24:00 UTC. Universe each day: coins with all 24 hours of the previous day, listed 60+ days, ranked in the top
100 by 30-day median dollar volume (liquid enough for real fills). Ends 2026-09-30 (funding files end there).

THREE STAGES, NEVER MIXED:
- DISCOVERY 2021-01-01 → 2023-12-31: everything may be tried here, as often as needed. Every variant is counted.
- VALIDATION 2024-01-01 → 2024-12-31: only variants promoted from discovery, each counted. A variant passes if its validation
  net mean is > 0 with weekly t ≥ 2.0, and its sign agrees with discovery.
- FINAL 2025-01-01 → 2026-09-30: at most 10 finalists, run ONCE, written down by name before running. Bar: weekly t ≥ Bonferroni
  for the number of finalists (one-sided α 0.05/m), net mean > 0, positive in 2025 and 2026, max drawdown of the 100 USDT version
  < 35%. Caveat stated now: 2024–2026 was used by E22–E25 (panic-bounce rules only); the FINAL period has not been used for any
  daily rule.
LUCK CHECK in discovery: for every round, the same search is run on shuffled signals (feature values permuted across coins each
day), giving the best result luck alone produces for that many tries. A variant is only promoted if it beats the luck-best.

COSTS: 0.10% per side (taker 0.05% + 0.05% slippage) on every unit of turnover; funding paid by longs and received by shorts at the
archive's rates; positions held across a delisting take the 5% penalty.
EVERY ROUND REPORTS: tries counted (running total), the luck-best, what passed and why the rest failed — costs (gross > 0 but net
≤ 0), one period only, one leg only, a few days carrying it, delisted coins carrying it, too few trading days — and the idea it
gives for the next round. Rounds may add new ideas at any time; only discovery data is used to invent them.
Paper only: no orders, ever.
