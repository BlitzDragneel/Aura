# E140 Gold pyramiding: add to a winner, cut fast if it turns (owner's request, 14 Nov 2026)
Owner's description of a signal trader's method: start small, add more positions only while price keeps moving the
right way, exit everything quickly if it turns. Question: does adding on strength turn gold intraday trades into a
positive expectancy, or does it only make wins and losses bigger?

## Data (fixed before looking)
- XAUUSDT perpetual 1-minute (Binance, Dec 2025 -> 13 Nov 2026). DISCOVERY 2025-12-01 -> 2026-05-31,
  VALIDATION 2026-06-01 -> 2026-08-31, FINAL 2026-09-01 -> 2026-11-13 (judged once).
- PAXGUSDT spot 1-minute (Binance, gold-backed token, a proxy), longer check: DISCOVERY 2021-2023, VALIDATION 2024,
  FINAL 2025-01-01 -> 2025-11-30.

## Entries (two families, fixed)
- M (momentum, like the trader's): on a closed 5-minute bar, buy if the close breaks the prior 60-minute high, sell if it
  breaks the prior 60-minute low; at most one trade open; next bar's open is the fill.
- R (control): same number of trades, random times inside the same months and random direction (seed 140).

## Management (fixed)
S = ATR(14) of 5-minute bars at entry. All units share one trailing stop = best price since entry minus S (buy), plus S
(sell). Max hold 4 hours, then close at market. Checked on 1-minute bars, stop first.
- SINGLE: 1 unit, never adds.
- PYR(k, N): starts with 1 unit; each time price moves k*S beyond the last add's price, add 1 unit at that price (up to
  N adds). Variants k in {0.5, 1.0} x N in {3, 6}.
5 variants x 2 entry families = 10 counted variants (+ the same on PAXG = 20).

## Costs
Gold CFD spread 0.20 USD per unit round trip (stress 0.40). PAXG proxy: 0.10% per unit round trip. Funding ignored
(holds <= 4 h; stated).

## Measures
Per trade P&L in R = USD per base unit / S. Also P&L per unit of PEAK risk (P&L / (max units x S)). Week-clustered t.
Pass: PYR beats SINGLE and beats the random-entry PYR; FINAL mean > 0 with t >= 2; VALIDATION > 0 with t >= 1.5.
Also: an account path at the trader's sizing ($560 balance, 0.1 lot = 10 oz per unit), to show the chance of a
wipe-out.
