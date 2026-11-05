# OMEGA v6.5.73: the model across coins joins the shadow book

Built from v6.5.72 by patch73.py. Delivered as omega-v6_5-47.html. Everything in v6.5.71 and v6.5.72 is included.

## New: round 14's model across coins, frozen, judged on new weeks (Edge Lab)
- **What it is.** Gradient boosting on 28 daily features: returns over 1–180 days, volatility, skew, distance from the
  year's high and low, volume, taker buying, funding, coin age, and beta to the market. Each Sunday the features are
  ranked across coins, and the strategy goes long the top fifth and short the bottom fifth.
- **Why it is only in the shadow book.**
  - Walk-forward on 165 coins: z 2.42, which passed its validation.
  - On 125 untouched coins: +37.8% a year over the market (z 2.89). That is below the strict bar of 3.29, because that
    file has been used for 101 finalists.
  - So it is not an edge. It is judged only on weeks after 18 Oct 2026, on all 291 coins, like the harvest and the two
    round-12 blends. It becomes an EDGE only if its forward weeks clear the bar.
- **Frozen.** Trained once in research on every week known by 11 Oct 2026; the app never retrains it. Its 124 trees are
  built into the app (72 KB).

## Checks
- **s73 (7/7):**
  - its predictions match the research code exactly on the app's own daily data: 1,500 coin-Sundays, 25 coins, the
    last 60 Sundays;
  - no look-ahead: changing prices, volume and funding after a day leaves every earlier prediction identical;
  - it holds nothing before it was frozen, then holds long the top fifth and short the bottom fifth, half the account
    each side;
  - costs on each weekly rebalance, and funding;
  - it sits in the shadow book as a research entry from 18 Oct 2026.
- **Real Chromium with Binance mocked:** the Edge Lab filled 291 coins and ran with the model in the book (SHADOW, no
  errors). The model scores 291 coins in 0.7 s on a desktop.
- **Every earlier suite:** s72 10/10, s71 16/16, s70 21/21, s69 21/21, s67 15/15, s62 7/7, s60 9/9, s58 9/9,
  s50 5/5, s49 11/11.
- All 107 scripts pass a syntax check. Phone guard clean.
- Not run on a real phone.
