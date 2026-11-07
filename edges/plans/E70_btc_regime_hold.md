# E70 — New-data regime switch: hold BTC vs cash (owner request: slow rules welcome)
Conventions: `E63_common_bot3.md` (publication lags, costs, funding, periods, luck check). Written before running.
## Rule: at each rebalance (daily 04:00 UTC, or weekly Monday 04:00 UTC) be 1× long the BTCUSDT perp if the regime is ON,
else flat (cash, 0 return). Each switch pays taker + slippage on the traded side (bt.TAKER + bt.slippage(qv24)); funding is
charged on every 00/08/16 stamp while long. Unit = daily return (00:00→00:00 UTC marked to perp open), all days incl. cash.
## Regimes (known at rebalance; lags per conventions) — 6 × 2 rebalance = 12 variants
R1 stablecoin total supply 30-d growth > 0 · R2 stablecoin 30-d growth > its trailing-365-d median · R3 Fear & Greed 7-d
mean ≤ 50 (contrarian: hold when not greedy) · R4 BTC DVOL ≤ its trailing-365-d median (calm; discovery from 2021-03-24)
· R5 BTC exchange netflow (CoinMetrics In−Out) 30-d sum < 0 · R6 R1 AND R5.
## Judgement vs buy-and-hold (same perp, funding charged)
- Selection: discovery Sharpe (daily, ann.) of the strategy; luck check = regime series circularly shifted (200), best
  discovery Sharpe ≥ 95th pct. Promote ≤ 3 that also beat B&H Sharpe in discovery.
- Edge test (protocol t): daily BTC return on ON-days minus OFF-days, week-clustered t (ON-day mean − OFF-day mean,
  tested as the mean of [r·(+1 if ON) , r·(−1 if OFF)] scaled — implemented as a two-sample Welch t on weekly-aggregated
  means). VALIDATION: strategy Sharpe > B&H Sharpe and edge t ≥ 1.5. FINAL: edge t ≥ 2.0, strategy CAGR > 0 and Calmar
  (CAGR / maxDD) > B&H Calmar; ≥ 60% of calendar years with strategy return ≥ B&H return OR lower drawdown.
- Report CAGR, max DD, time in market, switches/year for strategy and B&H in every period. Leverage table not applicable
  beyond 1× (a 1×-3× sizing table is reported for information).
