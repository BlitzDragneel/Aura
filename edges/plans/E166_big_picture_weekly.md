# E166 The big picture: does the week/month regime and money flow predict next week?
Owner: "learn why the market moves overall for the week/month; since the hack everything has been going down because
money converted removes it from the market". Testable form: when money leaves crypto (stablecoin supply shrinking)
and the month trend is down, next week is down more often; the same for gold with the dollar and real yields.
Data (daily, free): total stablecoin supply (DefiLlama, 2018->), Fear & Greed (alternative.me, 2018->), BTC daily
(Binance), gold (PAXG 2020-> / GC=F Yahoo 2010->), DXY (DX-Y.NYB) and US 10-year yield (^TNX) from Yahoo.
Weekly decision every Monday 00:00 UTC, hold one week. Features (past only): 4-week and 12-week return, price vs
20-week average, 4-week change in stablecoin supply, Fear & Greed level and 4-week change, 4-week change in DXY and 10y.
Periods: BTC discovery 2019-2022, validation 2023, final 2024-01..2026-11; gold same.
Models: (a) single rules fixed in advance: momentum (sign of 12-week return), money flow (sign of 4-week stablecoin
change), both agree; gold: momentum, dollar (opposite sign of DXY 4-week change), both agree.
(b) logistic regression on all features, fit on discovery only.
Costs: BTC 0.14%, gold 0.04% per round trip per week. Controls: always long, random sign.
Pass: FINAL > 0 with t >= 2 (weekly returns, Newey-West not needed for non-overlapping weeks), VALIDATION > 0, and better
than always-long on FINAL. A pass becomes the bot's weekly "overall play" bias; otherwise the weekly map is reported
as description only.
