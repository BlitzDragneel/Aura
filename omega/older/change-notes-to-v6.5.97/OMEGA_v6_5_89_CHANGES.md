# OMEGA v6.5.89 — Market Read, Brain and Autopilot upgrades (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.89 · build 2026-10-21 13:54 UTC. Made with `python3 patch89.py <v6.5.88 build> <new build>`. It uses
`mread.js` and `goldh89.js`, and edits the built-in knowledge, the Mind's lessons and the research record.

## New: Market Read (menu above Market Profiles; module `OMEGA_MREAD`)
The app's own read of 11 markets: BTC, ETH, SOL, BNB, XRP, gold, DOGE, LINK, LTC, ADA, AVAX. Binance USD-M public data, keyless: hourly klines, order book (500 levels), premium index and funding, open-interest history and the accounts' long/short ratio.

**Where liquidity lies:**
- **Stops gather at:** last week's and yesterday's highs and lows, today's so far, the 24- and 72-hour extremes, equal highs and lows (hourly swing points within 0.15% or a quarter of an hourly range), and round numbers.
- **Weighting and merging:** each level is weighted; levels within a quarter range of each other merge.
- **Measured:** distance in % and in hourly ranges.

**Resting orders:** bids and asks within 0.5%, 1% and 2%; the book imbalance; and the biggest walls within 2% (at least 3× the median price bucket).

**Who is crowded:** funding, open-interest change over 24 hours, and the long/short ratio. Longs count as crowded at funding ≥ 0.02% per period, or long/short ≥ 2 with open interest up 3%+; shorts the reverse.

**On the page:**
- **The read:** where price sits, the nearest pools above and below, the closer side, the book and positioning, and a closing statement of what the research supports (E12, breakouts and fakeouts, the climax rule). It describes and does not predict.
- **A liquidity ladder:** red levels above, green below, the price line, and book walls as bars.

**Level memory:**
- The nearest two pools on each side are remembered every hour.
- After 24 hours, each is scored by whether price reached it, by kind of level and by distance band.
- The page shows the app's own hit rates since it started reading (localStorage `omega_mread_mem_v1`, 45 days kept).

**Market Watch recording:** each finished UTC day's BTC minute coverage is computed from the recorder's own store; days with 80%+ are counted toward plan E13.

## Autopilot (Operator jobs)
- **`mread`** (Watching lane, hourly): reads BTC and ETH, remembers their levels and scores the old ones.
- **`mwdays`** (Watching lane, every 30 min): counts full recorded days. After a new one, it notifies you to export 3 days and send them.
- **Gold download:** a paid-plan answer (silver) is final; it is marked "not available on the free Twelve Data plan", gold completes, and there are no more requests. The `goldh` job then reports Complete.

## Brain
- **Built-in knowledge:**
  - 13 entries added for plans E1–E13, so `KN.earlier` now holds 39 studies;
  - 6 new lessons, 20 in total (picking the best fails on new data; count by week; small-account minimums; management cannot create an edge; stop-outs are mostly noise; liquidations follow price).
- **The Mind's lessons:** three added (judge on unseen weeks, a stop-out is usually noise, liquidity sits at obvious levels).
- **Research record:** rounds 26 (E8–E10), 27 (E11–E12) and 28 (Market Watch, E13, Market Read); the heading now reads rounds 1–28.

## Verification
- **s89 (11 checks):**
  - yesterday's high and low found exactly;
  - the planted equal highs found;
  - round numbers present;
  - the planted bid wall and a buyer-heavy book;
  - crowded longs, a complete read, the research statement, no NaN;
  - level memory scores a reached level;
  - a full Market Watch day is counted;
  - the Brain holds E1–E13, the new lessons, and rounds 26–28;
  - silver's paid-plan answer is final with no further requests;
  - a browser run: the read and ladder (8 levels, 1 wall), no NaN, no overflow, no page errors;
  - the Autopilot runs `mread` and `mwdays`.
- **All 23 suites pass** (s49…s89).
- **Debug finding fixed during the build:** re-saving the knowledge had escaped special characters; it now keeps the original UTF-8 style (s82 caught it).
- **Other checks:** 110 script blocks pass the syntax check; no duplicate ids; phone guard clean; 27-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.**
