# E52 — Cross-sectional momentum and reversal, weekly / 4-weekly rebalance, top-100 by liquidity, survivorship-free
Conventions: `E50_common_bot2.md`. Written before the data.

## Hypothesis
Over 1–12 weeks, coins that out-performed keep out-performing (momentum) or give it back (reversal). E28 tested daily ranks
held 1–14 days in overlapping cohorts; here it is ONE executable portfolio rebuilt on a fixed weekly (Monday 00:00 UTC) or
4-weekly calendar, with skip-week options and liquidity-scaled costs on actual turnover.

## Universe: top 100 crypto perps by trailing 30-day quote volume at each rebalance (common rules), delisted coins included.

## Grid
- formation return: 1w, 2w, 4w, 12w; skip: 0 or 1 week (formation ends 1 week before rebalance).
- rebalance: weekly | 4-weekly.
- k: 10 | 20 coins per side, equal weight.
- direction: momentum (long winners) | reversal (long losers).
- book: market-neutral (long k at +0.5/k, short k at −0.5/k) | long-only (k coins at 1/k).
= 4 × 2 × 2 × 2 × 2 × 2 = 128 variants.
Costs on turnover at each rebalance; funding on every holding; delisting rule.

## Luck check: the same grid with each rebalance's formation returns randomly permuted across the eligible coins (200 runs).
## Benchmark: equal-weight top-100 long, same rebalance and costs. Selection/pass: common rules.
