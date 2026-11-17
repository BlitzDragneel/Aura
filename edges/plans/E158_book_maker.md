# E158 BTC order-book pressure with limit (maker) orders — follow-up of E157
E157: BTC book imbalance (z of (bid-ask)/(bid+ask) within 1% / 5%) predicts the next 1-4h slightly in all periods;
following it made +2..+9 bp gross per trade, killed by 0.07%/side taker costs. Here, cheaper execution:
Signal at a 15m close when z1 (or z5) >= +2 (long) / <= -2 (short), FOLLOW only (the MAGNET side lost everywhere).
ENTRY: limit at the signal bar's close; filled only if price trades THROUGH it (5m low < limit for a buy) within the
next 15 minutes, else no trade (adverse selection is part of the test). EXIT after H = 1h or 4h from the fill: limit at
that bar's close, filled if traded through within 15 minutes, else at market (taker 0.05% + 0.02% slippage).
Costs: maker 0.02% per filled limit. Periods: TRAIN 2023, VALIDATION 2024, FINAL 2025-01 -> 2026-11-03.
Variants: 2 features x 2 holds = 4. Control: same fills, random direction (seed 158).
Pass: FINAL mean > 0 with week-clustered t >= 2, VALIDATION > 0 with t >= 1.5, above the control.
