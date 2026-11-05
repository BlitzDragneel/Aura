# E50 — Time-series momentum / trend following on BTC, ETH and a top-10 basket (4h and daily), vol-targeted portfolio
Conventions: `E50_common_bot2.md` (same fingerprint set). Written before the data.

## Hypothesis
Crypto majors trend over weeks: an asset whose own trailing return is positive keeps a positive drift; going flat (or short)
in down-trends cuts the large bear-market drawdowns. Measured as a portfolio against buy-and-hold.

## How this differs from E28 (daily direction picks failed)
E28 picked direction day by day (hold 1/3/7 days) from cross-sectional ranks or market gauges; costs ate it. Here the signal is
each asset's OWN trend over 10–120 days, so the position changes rarely (median holding weeks, turnover ~1–3 round trips a
month), positions are sized by inverse realised volatility (vol targeting), and the result is judged as a portfolio vs holding.

## Assets
A1 BTCUSDT, A2 ETHUSDT, A3 top-10 basket: the 10 most liquid crypto perps (common rules) re-selected on the 1st of each month,
each sleeve run on its own coin and equal-risk averaged (each of 10 sleeves 1/10 of capital).

## Grid (all counted)
- bar: 1d (signal at 00:00 UTC close, trade at that price) | 4h (signal every 4h close).
- signal (lookbacks in days, converted to bars): R10, R20, R40, R60, R120 = sign of trailing log return; COMBO = mean of
  sign(R20), sign(R60), sign(R120) (values −1, −1/3, 1/3, 1); EMA(10/40), EMA(20/100) cross = sign(fast − slow).
- mode: long/flat (negative → 0) | long/short.
- sizing: fixed (|w| = 1 × signal) | vol target: w = signal × min(1, 0.40 / σ_ann), σ from the trailing 30-day hourly
  returns (annualised), recomputed at each bar; trades only when the target weight changes by > 10% of capital (band) to
  limit turnover (fixed sizing trades only on signal change).
= 3 assets × 2 bars × 8 signals × 2 modes × 2 sizings = 192 variants.

## Luck check
Null grid: each asset's signal series circularly shifted by a random offset (≥ 180 days, < length − 180) — keeps the signal's
persistence, long/short share and turnover, breaks timing. 200 null grids; real best weakest-year ≥ 95th pct of null bests.

## Periods / selection / pass
Common rules. Benchmark buy-and-hold of the same asset (A3: equal-weight top-10 basket rebalanced monthly), with the same cost
model. Also reported: excess over buy-and-hold, CAGR, max drawdown per period. FINAL 2025-01 → latest, judged once.
