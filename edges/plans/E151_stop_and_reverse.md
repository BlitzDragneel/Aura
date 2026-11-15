# E151 Stop-and-reverse: when a Signal Lab trade is stopped out, trade the other way
Owner's idea (15 Nov BTC: a pullback BUY stopped out and the real move was down). On the E148/E149 replays (same code,
same markets and periods), every lab signal whose ladder outcome is SL is followed by a REVERSE trade: opposite side,
entry at the stop price at the minute it was hit (plus spread), same R, targets every 0.5R to 2.5R, same scorer, 24h max.
Reported per market and pooled, VALIDATION and FINAL, average R and week-clustered t; control = a trade in a random
direction at the same moments (seed 151).
Pass: pooled FINAL > 0 with t >= 2, positive on FINAL in at least 4 of 5 markets, pooled VALIDATION > 0, above control.
A pass becomes a live "REVERSAL" alert sent after every stop-out (paper, BACKTEST+).
