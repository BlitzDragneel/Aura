# E84 — Volatility-managed holding (lead, 8 Nov 2026)
Exposure_t = min(cap, target_vol / sigma_t), sigma_t = EWMA(halflife H days) of daily log returns, annualised; daily
rebalance at 00:00 UTC; costs 0.10% of turnover; funding on perps charged (spot variant: none). Assets: BTC, ETH, and an
equal-weight BTC+ETH book. Variants: target_vol {40%, 60%}, H {10, 30}, cap {1 (no leverage), 2} = 8 per asset, 24 total.
Judge vs buy-and-hold of the same asset on Sharpe and max drawdown (not per-trade t):
DISCOVERY 2020–23 picks the best Sharpe; luck: the same search with sigma shifted by a random 60–300 days (100 runs), the
real best Sharpe gain must beat the 95th pct; VALIDATION 2024 and FINAL 2025–26: Sharpe above buy-and-hold AND max drawdown
at least 25% smaller in both. This is a way to hold, not a day-trading rule.
