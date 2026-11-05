# PLAN E23 — "Two Seats": pick the right one or two panics, not all of them (written before running)
Written 2026-10-25, on the owner's direction: at most two trades at a time, the right ones, the account split between them.
SIGNALS (from E22 H1, which passed): a coin's 24-hour return in its bottom 10% of the previous 720 hours; a buy limit at
C·exp(−2σ) (σ = hourly standard deviation of the prior 168 hours), filled only if a candle in the next 3 hours trades below it;
exit 24 hours after the fill at market. Costs 0.12% round trip plus 0.03% funding. Coins listed 30+ days. No stops.
SELECTION, fixed in advance (directions from earlier evidence, no fitted weights): when several coins signal in the same hour
and seats are free, rank them by the sum of three ranks within that hour — deeper 24-hour fall (E22: deeper bounced more),
higher volume surge (last 24 hours' volume ÷ its 720-hour median; E22: volume-surge panics bounced far more), higher liquidity
(last 24 hours' traded value; avoids thin, dying coins). Ties by depth.
ACCOUNT: 100 USDT; at most 2 seats; a seat is busy from the signal until 3 hours later if unfilled, or until the exit if filled;
each new position uses f of current equity: f = 25% (primary) and f = 50% (reported).
TEST, run ONCE on the perpetuals of the final4 files, 2024-01-01 → 2026-10-18: the same account picking at random among the
same hour's signals, 500 times. PASS (f = 25%): the ranked account ends above at least 95% of the random accounts, above 100,
and gains in each of 2024, 2025 and 2026. Reported: drawdowns, trades, f = 50%, and the 25 majors (discovery set) as a check.
