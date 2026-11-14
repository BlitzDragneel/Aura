# E125 — Silver multi-day momentum/reversal with vol targeting, and post-shock drift (common methods E120)

Daily SI closes, CFD costs (0.04%/side + financing per night on |notional|), positions decided at close t.
A. Momentum / reversal (16 variants): signal s = sign(log return over L days), L ∈ {5, 10, 20, 60}; MOM trades s,
   REV trades −s; LS (long and short) or LONG-only (cash instead of short). Rebalanced daily; notional =
   min(2, 20% / vol20) (vol20 = annualised 20-day realized vol, known at t). 4 × 2 × 2 = 16.
B. Post-shock drift (12 variants): shock day |r_t| > k·σ60 (σ60 = std of the prior 60 daily returns), k ∈ {2, 3}.
   FOLLOW (trade the shock's direction) or FADE; enter at close t, hold H ∈ {1, 5, 10} days; notional 1; overlapping
   shocks extend nothing (a new shock while in a trade is ignored).
Evaluation as E124 (daily book, NW t, trades = runs/entries). Selection: highest discovery t (B: ≥ 30 trades).
Luck: whole grid on circularly shifted signals (200 shifts) and random-entry control with the same holds and sides.
Counted variants: 28.
