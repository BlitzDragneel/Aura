# OMEGA v6.5.71: honest CREED numbers, round 14 so far, two research downloads

Built from v6.5.70 by patch71.py. Delivered as omega-v6_5-47.html. Plan: research/PLAN14.md (addenda A and B).

## CREED: the honest record comes first
- **Replay version 10.** Every market is replayed again (one every 20 minutes while the app is open). Each replay now
  measures, on their own, the setups **shown on time**: set up and shown on the same 15-minute close, so the quoted
  entry is a price you could really take. For those setups it also measures:
  - breakeven off;
  - three take-profit tiers;
  - the share that reach +1R before the stop.
- **Your 13 Oct replays, split this way (25 markets, 6,989 setups):**

  | Setups | Count | Average a trade |
  | --- | --- | --- |
  | Shown on time | 2,497 | +0.015R before costs, −0.085R after |
  | Shown later, priced at the earlier close | 4,492 | +0.70R |

  The +0.47R headline is almost all that hindsight.
- **Exits:**
  - three tiers: +0.001R;
  - breakeven off: +0.057R;
  - 49% reach +1R first, which is a coin toss.
- **Where it shows:**
  - The CREED history card (Autopilot page) opens with the on-time record, and labels the old total "as taught
    (counts hindsight)".
  - The list of trades OMEGA sees quotes on-time figures for CREED setups.
  - The scoreboard's CREED line counts on-time setups only.
- **CREED Backtest: a new Entry setting.**
  - "When CREED shows the setup" (the default) enters a late setup at the close of the candle it appears on. It skips
    the setup if price is already past the stop or target.
  - "As taught" keeps the old entry.
  - The status line and the journal notes say which one ran.
  - CREED's own method (gates, levels, desk markets) is unchanged.

## Round 14 so far (research, PLAN14)
- **One candidate edge.** Buy a coin after a capitulation hour: a fall of 5+ of its own hourly standard deviations
  while its perpetual trades at an unusual discount (premium at or below its 5th percentile over 30 days). Hold 12 hours.
  - On 140 coins it never saw: +19.4% a year over the market, z 3.04 (bar 2.90), +17.0% with costs doubled, 6 of 7
    years positive.
  - Typical trade +1.6% before costs, 60% winners.
  - The 4, 24 and 48-hour holds were also positive.
  - It is not an edge until it passes the final test on untouched coins, which needs the new download.
- **Walk-forward model across coins** (30 daily features, gradient boosting, weekly long/short): on 125 untouched coins
  +37.8% a year over the market, z 2.89. That is below the strict bar of 3.29, because that file has now been used for
  101 finalists. It will be judged on new weeks.
- **Failed:**
  - the market's capitulation;
  - premium extremes;
  - hourly reversal across coins (lost heavily to costs);
  - shorting young listings;
  - shorting 5-sigma up-hours (pumps kept going).
- The research record and the Edge Lab's built-in knowledge now include round 14 and the CREED finding.

## Two downloads (OMEGA Strategy page, under the research downloads)
- **Round 14 final test:** 5 files.
  - Hourly perpetual candles, premium index and funding for the 125 untouched coins with a perpetual (4 files).
  - Perpetuals listed since 1 Apr 2025 whose coin was never used (1 file; non-coins and metals excluded).
  - About 90 minutes.
- **CREED research data:** 15-minute candles for the 25 studied coins, Jan 2020 to now, in 5 files (about 25
  minutes). CREED's replays never saw 2020–2023, so those years are a clean test for a better trigger.
- Each file can be downloaded again on its own, and there is a save-again link for each. Prices only; no keys.

## Checks
- **s71 (16/16):**
  - the replay splits every setup into on time or late, and its totals are the sums of its own trades;
  - the verdict and the card use them;
  - the backtest setting is in place;
  - the new-listing rule picks exactly the plan's coins (multiplier contracts, stablecoins, metals, equities, dated
    contracts and used coins all handled);
  - the 15-minute file decodes exactly in the research loader.
- **Earlier suites:** s70 21/21, s69 21/21, s67 15/15, s62 7/7, s60 9/9, s58 9/9, s50 5/5, s49 11/11.
- **Real Chromium with Binance mocked:**
  - both downloads save, and they decode with the research loader (hourly with premium and funding; 15-minute with
    quarter-hour times);
  - the backtest runs in both modes: "as taught" 8 trades; "when shown" 2 trades, with 6 late setups skipped because
    price was already past their stop or target;
  - no page errors, no sideways scroll at phone width.
- All 105 scripts pass a syntax check. Phone guard clean.
- Not run on a real phone.
