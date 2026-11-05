# OMEGA v6.5.78 — round 16: the first direction rule to pass all three tests (19 Oct 2026)

Built from v6.5.77 by `patch78.py`. Delivered as `omega-v6_5-47.html`. Plan and results: `research/PLAN16.md`
(addendum A; the frozen text is `PLAN16_frozen_A.md`).

## What research found
Margaret asked to go back through history, find what moves the market, and see whether trading on it makes a difference.

**The footprints with history** are on hourly perpetual bars:
- aggressive buying share;
- volume;
- the premium against spot;
- funding.

**18 rules were tested.** Each was compared with the same setup without the footprint, to see whether the footprint
made the difference. They covered:
- absorption;
- exhaustion after a dip;
- flow divergence;
- a leverage flush completing;
- stop runs reclaimed;
- spot-led and leverage-led breakouts;
- the climax wick.

They ran on 25 coins, then 140, then once on 324 coins nothing had touched.

**One passed all three: the climax reversal.**
- **The setup:** a coin's perpetual falls 3 or more of its own hourly standard deviations on at least 3× normal
  volume, and the hour closes in the top 40% of its range. Buyers took most of the fall back within the hour.
- **The trade:** buy at the next open and hold 12 hours.

| Coins | A year over the market | z | Notes |
| --- | --- | --- | --- |
| 25 | +2.5% | 2.30 | |
| 140 | +7.4% | 2.54 | |
| 324 untouched (final) | +5.3% | 2.35 (bar 2.326) | +4.6% with costs doubled, 440 trades, +1.8% a trade before costs, 58% winners |

**Honest limits:**
- It passed the final bar only just.
- Most of the profit is in the bigger rebounds.
- It trades rarely, so it adds about 5% a year to the whole account.
- Only forward weeks will confirm it.

## What changed in the app
**New: Climax reversal watch.** It sits at the top of the Edge Lab, with a copy on Market Watch.
- **What it watches:** every Binance USDT coin perpetual. Metals and other non-coin contracts are left out.
- **When it checks:** about a minute after each hour closes, while the app is open.
- **When a coin fires:** it shows **BUY (paper)** with the coin, the entry hour and the exit hour, and sends an alert if
  alerts are on.
- **Paper trades:**
  - 5% of the account each, at most 20 at once;
  - closed after 12 hours with costs and funding;
  - forward record from 19 Oct 2026 12:00 UTC, judged week by week against the market;
  - judged after 26 weeks.
- **OMEGA places no orders.**
- **On by default.** Turn it off on the card.

**Research record and built-in knowledge** now include round 16, with 2,226 rules in all and a new lesson.

## Checks
- **s78 (13/13):**
  - the watch takes the same 61 trades as the research engine on the 25 studied coins' busiest 3,000 hours: hour, coin,
    depth of fall and return after funding all match;
  - volume and close-location measures match research exactly;
  - no look-ahead;
  - never more than 20 trades or one coin twice;
  - live entry waits for the next open;
  - the forward record adds up;
  - the card, record and knowledge are in place.
- **Earlier suites:** s49 11/11, s50 5/5, s58 9/9, s60 9/9, s62 7/7, s67 15/15, s69 21/21, s70 21/21, s71 16/16,
  s72 11/11, s73 7/7, s77 27/27.
- 110 script blocks pass `node --check`. Phone guard clean.
- **Chromium at 412 px with Binance mocked:**
  - a planted selling climax (−13.9σ on 9.2× volume, closing at 69% of the hour) fired and showed BUY (paper) with the
    right entry and exit hours;
  - a metals perpetual was left out;
  - the card shows on both pages;
  - no errors, no sideways scroll.
- Not run on a real phone or against the live exchange.
