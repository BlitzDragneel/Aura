# PLAN E11 — absorption on BTC and ETH: aggressive buying that does not move price
Written 2026-10-21 before computing anything below. Data: omega_history_creed15_1 (BTC, ETH; Binance spot, 15-minute,
2020 – Oct 2026; sha256 5e9fa47e…), resampled to hours: return = ln(close/previous close); taker-buy share = taker-buy
volume / volume. Never used for this measure.
Cause: if aggressive buyers dominate an hour but price does not rise, passive sellers are absorbing them (and the reverse).
Signal at an hour's close, per coin:
  buy absorption  : taker-buy share in the top 5% of that coin's previous 720 hours AND the hour's return ≤ 0  → short 4 h
  sell absorption : taker-buy share in the bottom 5% of the previous 720 hours AND the hour's return ≥ 0     → long 4 h
Enter at the next open; costs 0.05% a side (BTC/ETH perpetual taker fee; slippage negligible at this size); no overlap
within a coin; BTC and ETH pooled, equal weight per trade.
Pass (one rule, both legs together): weekly t ≥ 2.0 over all weeks, positive overall, and positive both before 2024 and
from 2024. Each leg reported separately (not tested separately). Run once; reported whatever happens.
