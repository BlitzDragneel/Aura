# E157 Does order-book liquidity control movement? (Binance bookDepth archives, new data)
Data: cumulative bid/ask notional within +-0.2/1/2/5% of price, 5-minute rows (edges/data/fetch_depth.py).
BTC perp: TRAIN 2023, VALIDATION 2024, FINAL 2025-01 -> 2026-11-03 (price 5m file). Gold perp: TRAIN 2025-12 -> 2026-05,
VALIDATION Jun-Aug, FINAL Sep -> 13 Nov 2026. Features known at the close of each 15-minute bar (last 5m depth row).
Q1 SIZE: depth within +-1% vs its trailing 7-day median (ratio). Next-4h high-low range in the thinnest fifth vs the
   thickest fifth vs the middle, FINAL period. Plus AUC of "thinness" alone for the E142 big-move label.
Q2 DIRECTION (book imbalance): imb_k = (bid_k - ask_k) / (bid_k + ask_k), k = 0.2%, 1%, 5%; z-score vs trailing 7 days.
   Rank correlation (IC) with the next 1h and 4h return. Rules (one position at a time, entry next bar open, exit after
   H hours, H = 1 and 4): FOLLOW: z(imb_1) >= +2 long, <= -2 short; MAGNET: the opposite (price drawn toward the thicker
   side). Same for imb_5. Costs BTC 0.07%/side, gold 0.02%/side.
Q3 FLOW OF LIQUIDITY: 1-hour change in imb_1 (orders being pulled/stacked), z >= 2 / <= -2, FOLLOW and MAGNET, H = 1, 4.
Variants counted: 2 assets x (2 depths x 2 rules x 2 holds + 2 rules x 2 holds) = 24 rules + ICs.
Pass (rule): FINAL mean > 0 after costs, week-clustered t >= 2, VALIDATION > 0 with t >= 1.5. Q1 is descriptive.
