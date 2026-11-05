# E53 — ALT/BTC ratio trend (E20's suggested next hypothesis)
Conventions: `E50_common_bot2.md`. Written before the data.

## Hypothesis (from E20): the 2024–26 alt bleed happened while BTC itself trended up; an alt's strength AGAINST BTC (its
ALT/BTC ratio trend) should separate alts that keep rising from those that bleed. Time-series rule on each alt's own ratio,
not a rank (unlike E52).

## Universe: top 100 crypto perps by liquidity excluding BTC (common rules). Ratio R = close_alt / close_BTC (daily, 00 UTC).
## Signal: up-trend if (MA) R > its N-day simple average, or (RET) ln R_t − ln R_{t−N} > 0. N ∈ {10, 20, 40, 60, 90}.
## Books (rebalance weekly Monday 00 UTC | 4-weekly):
- H (hedged long): each up-trend alt long and BTC short equal notional (pure ratio bet); gross 1, split equally.
- LS: long ratio up-trend alts hedged by short BTC, short ratio down-trend alts hedged by long BTC (BTC legs net).
- U (unhedged long-only): long the up-trend alts, equal weight, flat when none qualify. Benchmark: equal-weight top-100 alts.
= 5 N × 2 methods × 3 books × 2 rebalances = 60 variants.
## Luck: each alt's signal series circularly shifted by a random offset ≥ 180 days (per alt independently), 200 runs.
## Selection/pass: common rules.
