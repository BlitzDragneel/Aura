# E54 — Funding as a CONTRARIAN price signal on weekly horizons (not a harvest)
Conventions: `E50_common_bot2.md`. Written before the data.

## Hypothesis: crowded long positioning (high funding, especially funding high relative to the coin's own normal) precedes
weaker PRICE performance over the next 1–4 weeks; crowded shorts precede squeezes.
## What is NOT new (honest): E28 round 1/2 already had funding level (fund−) ranks held 1–14 days; that is included here only
as the reference level variant and counted. New: (a) funding normalised by the coin's own 90-day history (z-score), (b)
weekly/4-weekly single executable book, (c) PRICE-ONLY component reported separately from funding received, and (d) a
time-series market variant: aggregate (median top-100) funding z-score → short/long the top-10 basket for a week.
## Universe: top 100 crypto perps by liquidity (common rules); funding from `/home/user/data/funding`.
## Signals at rebalance (Monday 00 UTC): F7 = mean funding last 7 days; F30 = last 30 days; Z = (F7 − mean90)/sd90 of the
coin's 8h funding over the prior 90 days.
## Grid
- XS: signal ∈ {F7, F30, Z}; rebalance weekly | 4-weekly; k 10 | 20; book market-neutral (short highest, long lowest) |
  short-tilt free long-only (long the k LOWEST-signal coins) → 3 × 2 × 2 × 2 = 24.
- TS: market median Z of the top-100 ∈ top/bottom 20% or 33% of its own trailing 365-day history → short basket (crowded)
  / long basket (fearful) / both, hold 1 week or 4 weeks → 2 × 3 × 2 = 12.
= 36 variants. Luck: XS — permute signals across coins per rebalance; TS — circular shift of the gauge (≥ 180 d). 200 runs.
## Selection/pass: common rules; results reported with and without funding P&L.
