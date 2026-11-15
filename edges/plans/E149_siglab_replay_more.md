# E149 Signal Lab replay on silver, Ethereum and Solana (same rule as E148, to mute losing cells)
Exactly as E148 (unchanged live code, same scorer, same muting / BACKTEST+ rule), on:
silver perp 1m 2026-01-07 -> 2026-11-13 (TRAIN -> May, VALIDATION Jun-Aug, FINAL Sep-Nov);
ETH and SOL perps 1m 2025-06-01 -> 2026-11-13 (TRAIN 2025-06 -> 2025-12, VALIDATION 2026-01 -> 2026-05, FINAL 2026-06 ->).
Also reported: for each setup x trend side, the number of assets (gold, BTC, silver, ETH, SOL) where FINAL is positive,
to see whether any cell is consistently good or bad across markets. A cell negative on FINAL in at least 4 of the 5
assets is muted on every market the lab watches; a cell positive on FINAL in at least 4 of 5 with pooled t >= 2 gets
BACKTEST+ everywhere.
