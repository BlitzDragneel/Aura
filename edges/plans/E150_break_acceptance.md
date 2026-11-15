# E150 After a break: is it accepted or rejected in the next 15 minutes? (the "which side is winning" question)
Event (as the lab's S2, without the wide-bar condition): a 15m bar closes beyond the prior 4-hour high/low by 0.1 ATR14.
Then watch the NEXT 15 minutes on the fine bars (1m; BTC 5m):
 ACCEPTED: price never trades back through the broken level and the last close is at least 0.25 ATR beyond the break
           bar's close -> trade WITH the break at the next open.
 REJECTED: the last close is back inside the level -> trade AGAINST the break (fade) at the next open.
 otherwise no trade. Events within 4 hours of a taken trade are skipped.
Template and scorer exactly as the Signal Lab (stop 1R = max(ATR 1h, 0.2%, 6 spreads), targets every 0.5R to 2.5R,
fifths with the stop to entry after TP1, spread charged, 24h limit).
Controls on the same events: follow every break immediately; fade every break immediately.
Assets and periods as E148/E149: gold, BTC, silver, ETH, SOL. 4 rules x 5 assets = 20 cells, all logged.
Pass (per rule): pooled FINAL average R > 0 with week-clustered t >= 2, positive on FINAL in at least 4 of 5 assets,
pooled VALIDATION > 0, and better than its immediate control. A pass becomes a new lab setup tagged BACKTEST+ (still
paper until its forward record grades it).
