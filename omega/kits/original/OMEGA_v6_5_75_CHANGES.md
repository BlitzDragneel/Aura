# OMEGA v6.5.75: round 15's data download

Built from v6.5.74 by patch75.py. Delivered as omega-v6_5-47.html. Plan: research/PLAN15.md.

## New: "Round 15: Bybit funding" (OMEGA Strategy page, under the research downloads)
- **What it fetches.** Funding history of Bybit's USDT perpetual, same symbol, from Jan 2020, for every research coin,
  in 3 files:
  - the 166 coins used before;
  - the 125 untouched coins;
  - the 199 new listings.
- **Time and content.** About an hour in all. Each file can be downloaded again on its own. Funding rates only, from
  Bybit's public API.
- **Why.** The funding harvest is OMEGA's one repeatedly confirmed edge, but Binance funding has thinned. Round 15
  tests three things written down in advance:
  - the harvest on Bybit;
  - the harvest on whichever venue pays more, coin by coin;
  - half on each venue.
  Each is judged against the Binance harvest on the same coins and weeks, with the final test on the 324 untouched
  coins.

## Checks
- **Real Chromium with Bybit mocked:**
  - paging works (BTC: 7,270 settlements, oldest to newest, in 37 requests);
  - coins without a Bybit perpetual are listed as missing, not failed;
  - the file decodes in the research loader;
  - no page errors.
- **All suites:** s73 7/7, s72 11/11, s71 16/16, s70 21/21, s69 21/21, s67 15/15, s62 7/7, s60 9/9, s58 9/9,
  s50 5/5, s49 11/11.
- All 108 scripts pass a syntax check. Phone guard clean.
- **Not verified:** a real phone, or Bybit's live API. The workspace can't reach Bybit, so the request format follows
  Bybit's documented behaviour; please tell me if the file comes back empty.
