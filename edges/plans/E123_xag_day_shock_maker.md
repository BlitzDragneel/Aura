# E123 — Silver day trades: hourly shocks with volatility gates, and maker-only panic-bounce limits (common methods E120)

Hourly SI. σ = std of the prior 168 hourly log returns (excluding the current bar).
A. Hourly shock follow/fade (24 variants, CFD costs). Signal: bar return r_t with |r_t| > z·σ, z ∈ {2, 3}.
   FOLLOW or FADE, entry at the next bar's open, hold h ∈ {1, 4} bars, stop 2 ATR. Vol gate g ∈ {all, high, low}:
   20-day daily realized vol above / below its trailing 250-day median (known at the signal time).
   2 × 2 × 2 × 3 = 24.
B. Panic bounce adapted, maker-only (4 variants, perp maker costs: maker entry 0.02% only if a later bar trades THROUGH
   the limit; exit at market close of the hold bar, taker 0.05% + 0.02%). Limit buy at C_t·exp(−k·σ), k ∈ {2, 3},
   valid 3 bars; hold H ∈ {4, 12} bars after the fill (≤ 24 h = still a day trade). Also the mirror short limit
   (sell at C·exp(+kσ)) reported as information only (not counted for selection; counted as attempts).
Selection: highest discovery t with ≥ 30 discovery trades. Luck: random entry (same count, hour, side mix, exits);
for B, random-time limit orders at the same k (200 draws). Counted variants: 28 (+4 info mirror).
