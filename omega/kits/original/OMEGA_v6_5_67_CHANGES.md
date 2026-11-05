# OMEGA v6.5.67: results of rounds 10 and 11

Built from v6.5.66 by patch67.py. Delivered as omega-v6_5-47.html (same file name, so stored data carries over).

## The results

### Round 10: the perpetuals' own data (PLAN10)
The tests were fixed before the data was read. The five fresh files were fingerprinted on arrival.

- **The basis barely matters on the 25 coins.** The 10-coin harvest made +11.9% a year with the perpetual's own price,
  against +12.0% counting funding only. The basis's worst week was −0.19%.
- **B1–B3 (premium extremes, leverage-led moves, futures vs spot buyers):** out at design.
- **B4 (10-coin harvest, opening a pair only when the perpetual is rich): PASS on 140 untouched coins.**
  - +11.9% a year, z 4.28 against a bar of 1.65, +10.0% with costs doubled, worst fall −5.3%.
  - SXP has no perpetual data, so the test ran on 140 coins, not 141.
  - This is the funding harvest passing a third untouched test, now with the basis counted. The filter itself adds
    nothing reliable, so the app keeps the plain harvest.
- **C1 fade the crowd (BTC/ETH long/short ratio):** +7.5% a year on 2025 to Oct 2026, but z 1.03 against a bar of 2.13.
  Fail; a lead only.
- **C2:** fail. **C3:** out at design.

### Round 11: forex (PLAN11)
All four rules failed:

| Rule | Return a year | z |
|---|---|---|
| Carry | +2.1% | 1.41 |
| Trend, 3 months | −1.0% | — |
| Trend blend | −0.8% | — |
| Carry and trend together | +0.7% | — |

Missing forex data was not the reason for the lack of success.

### Checks added after the result (explain it, do not change the verdict)
- **Funding has thinned.** Funding collected on the 140 coins by year:

  | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (to Oct) |
  |---|---|---|---|---|---|---|
  | +20% | +51% | +1% | +7% | +14% | +2% | −0.2% |

  On the 25 coins, the 10-coin harvest made +2.8% in 2025 and +0.9% in 2026 to date.
- **The 2026 loss came from delistings.** Binance delisted the ATA and SYS perpetuals on 19–20 May 2026 while the test
  held them, and the test kept the spot coins unhedged to Sunday as they fell about 70%. Closing a pair on the day its
  market stops gives +12.5% a year, with a worst fall of −2.0%.

## What changed in the app
- **Harvest card**
  - The title now says the harvest passed untouched tests "three times".
  - A new paragraph covers the third test and the filter result.
  - The basis caveat now gives the measured cost.
  - "Read it the right way" gives the thin 2025–26 years on the 25 coins.
  - A new delisting caveat says to close a pair at once if its perpetual is delisted.
- **New flag on the harvest card.** When a coin the rule holds stops receiving funding (16+ hours behind the other
  coins), a red box says so and tells you to check Binance's announcements and close that pair, both legs. It works for
  both the 5-coin and 10-coin versions. The frozen rule itself is unchanged.
- **Positioning Desk:** new Round 10 and Round 11 cards, laid out as stacked rows that read at phone width.
- **Research record:** rounds 10 and 11 added. Its title now says the harvest passed untouched tests "three times".
- **Brain observation** for the harvest updated with the third test, the thin recent years and the delisting rule.
- **Reports:** the research report carries round10, round11, the measured basis and the current stopped-funding list.

## Not changed
- CREED, the three desk markets, the Brain's method, the Autopilot and the trading rules.
- The 5- and 10-coin harvests are identical to the Python test code (153 weeks).
- Everything stays paper only.

## Checks
- **New tests (s67, 15/15):**
  - every figure in the app is read back against partB_fresh.json, diagB4_delist.json, partC.json and round11.json;
  - the rules are unchanged;
  - the stopped-funding flag fires on a stopped coin and stays quiet when all coins pay.
- **Regression tests:** s62 7/7, s60 9/9, s58 9/9, s50 5/5, s49 11/11. s62's headline-wording check now accepts
  "three times", on purpose.
- **Browser test:**
  - the harvest card and desk render at phone width with no sideways scroll and no page errors;
  - v6.5.66's one-file download test passes again on this build.
- **Guards:** phone-number guard clean; no API key in the file.
