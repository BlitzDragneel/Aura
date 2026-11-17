# E162 Candle memory ("what usually comes next"): nearest-neighbour forecaster on 15-minute candles
Owner: the bot must learn what comes after each kind of candle behaviour. Method: describe each closed 15m candle by
~20 numbers (last 4 candles' body, upper wick, lower wick and range in ATR units; returns over 1h/4h/24h in ATR units;
position in the 24h range; distance to the 20/50-bar averages; volatility percentile; session; weekday-or-weekend),
standardise, find the k = 200 most similar candles in MEMORY (past only), and read what followed them:
P(next candle up), P(next hour up), P(next 4h up), median next-hour move, P(4h move > 2 ATR).
Memory = everything before the predicted candle (expanding; refreshed monthly in the test, every 15 min live).
Data: BTC 2022 -> 2026-11 (5m -> 15m), gold perp and silver perp 2026 (1m -> 15m), PAXG 2021-2025 for a longer gold test.
Periods: BTC VALIDATION 2024, FINAL 2025->; PAXG VALIDATION 2024, FINAL 2025; gold/silver perp VALIDATION Jun-Aug,
FINAL Sep-Nov 2026 (memory from Jan).
Measures: AUC of each probability vs what happened; accuracy of the most confident 10% of calls; a trade test:
when P(next hour up) >= 0.6 (or <= 0.4) enter at the next open, exit 1h later, costs BTC 0.07%/side, gold 0.02%,
silver 0.04%. Controls: base rate (always the majority side) and a memory built from shuffled outcomes.
Pass (for the live bot to send DIRECTION calls): FINAL AUC >= 0.53 for next-hour direction on 2+ markets, confident
accuracy >= 55%, and the trade test FINAL > 0 with t >= 2 and VALIDATION > 0. Otherwise the memory runs live as
information (scored forward), and its forward record decides later.
