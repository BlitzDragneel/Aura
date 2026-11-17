# E163 Candle memory that learns from its mistakes
Owner: every time the prediction is wrong, the bot must look at why and upgrade itself.
Same markets, data, periods, costs and trade test as E162 (BTC VAL 2024 / FINAL 2025->; PAXG VAL 2024 / FINAL 2025;
gold and silver perps VAL Jun-Aug / FINAL Sep-Nov 2026). Walk-forward, refreshed monthly, past-only memory.
Variants (all predict P(next hour up)):
- A  E162 memory: k=200 nearest candles on the 26 E162 numbers (the baseline).
- B  richer description: + 1h candle and 4h candle (body/wicks/range of the last 4 and 16 bars), distance to the previous
     day's high and low and to today's open, same-colour streak, weekday (39 numbers). k=200.
- C  gradient boosting (LightGBM, 300 trees, lr 0.03, 31 leaves, min 300 per leaf) on B's numbers, retrained monthly on
     all the past. Boosting is literally learning from the previous trees' errors.
- D  average of B and C.
- E  MISTAKE MODEL on top of D: a second model is trained only on D's own earlier out-of-sample predictions (months
     before the one predicted) to learn WHEN D is wrong: inputs = the situation (B's numbers) + D's vote margin + how
     unfamiliar the situation is (mean distance to the 200 neighbours) + agreement with next-candle / 4h votes.
     Target = D was right. E only makes a call when the mistake model says P(right) >= 0.55; otherwise "no call".
Warm-up predictions start one period before VAL (BTC/PAXG 2023, perps from March 2026) so E has past mistakes to learn from.
Measures per period: next-hour AUC, accuracy of the confident 10% (E: of its calls), share of candles called, trade
test (P>=0.6 / <=0.4 for A-D; E's calls), costs as E162.
Choice: the live model is chosen on VALIDATION AUC (E judged on call accuracy x coverage vs D) - FINAL is reported once.
Improvement claim: the chosen model's FINAL AUC beats A on 3 of 4 markets.
Trade pass (unchanged): FINAL net > 0 with t >= 2 and VALIDATION net > 0, on any market.
Also reported (descriptive, the "why it was wrong" table): D's accuracy by condition on VAL+FINAL - unfamiliar
situation (top 20% distance), close vote (|p-0.5|<0.05), session (Asia/London/NY/late), volatility tercile,
with/against the 24h move, weekend.
