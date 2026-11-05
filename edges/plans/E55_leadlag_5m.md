# E55 — BTC → alt lead-lag at 5m / 15m on the 30-coin 5m set
Conventions: `E50_common_bot2.md` (DISCOVERY here = 2022-01-01 .. 2023-12-31, the 5m data start). Written before the data.

## Hypothesis: when BTC makes a sharp move in one bar, alts that have not yet followed (small residual vs their beta) catch up
over the next minutes. E20 found no lead at the daily scale; this tests intraday. Costs (≥ 0.14% round trip for majors) are
the obstacle; gross numbers are reported so the size of the effect is visible.
## Rule
Bars 5m | 15m (15m resampled from 5m). BTC bar log return r_b; σ_b = std of r_b over the prior 288 5m-bars-equivalent (1 day)
of that bar size. Trigger: |r_b| > k σ_b, k ∈ {2, 3, 4}. For each of the 29 alts: β = rolling 1-day OLS beta of alt on BTC
bar returns (prior bars only); residual e = r_alt − β r_b. Filter ∈ {all alts, lagging alts only: e·sign(r_b) < −0.5 β|r_b|
(alt moved < half its expected move)}. Enter each alt in BTC's direction at the next bar open, exit after h bars at that bar's
close, h ∈ {1, 3, 6, 12}. Taker both sides + slippage by qv24; no funding (holds < 8h unless h·bar crosses settlement:
charged when crossed).
## Grid: 2 bars × 3 k × 2 filters × 4 h = 48 variants (both directions together).
## Luck: same alts, same counts, random trigger bars (200 runs), same exit rule.
## Selection/pass: common rules (trade units; ranking by weakest discovery year 2022/2023).
