# E154 Higher-timeframe filter for the Signal Lab (from the 15 Nov BTC loss: a pullback BUY inside a 4h/daily downtrend)
Replay of the unchanged lab detectors on the five markets (as E148/E149). Each signal is tagged with the 4h trend
(EMA20 vs EMA50 of 4h closes, last closed 4h bar) and the daily trend (close vs 20-day average of daily closes, last
closed day). Groups: AGREE (signal direction = 4h trend = daily trend), CONFLICT (against both), MIXED.
Pass: AGREE pooled FINAL average R > 0 with t >= 2, positive on >= 4 of 5 markets, VALIDATION > 0, and above MIXED and
CONFLICT. If AGREE is better than the rest but not positive, the filter is still used to mute CONFLICT signals only if
CONFLICT pooled FINAL and VALIDATION are both negative with t <= -2 (counted; 3 groups x 5 markets).
