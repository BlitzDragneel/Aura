# OMEGA v6.5.80 — round 15: the Bybit test (19 Oct 2026)

Built from v6.5.79 by `patch80.py`. Delivered as `omega-v6_5-47.html`. Plan and results: `research/PLAN15.md`
(addenda A–C and results).

## The test
**The Bybit download worked against the live API.** Your phone fetched three files:
- 166 seen coins, all with Bybit funding;
- 115 of 125 untouched coins;
- 181 of 199 new listings.

BTC has 7,197 settlements from March 2020, the same 00/08/16 UTC schedule as Binance, and a median of 0.0100%.

| Rule | 140 coins (validation, bar 2.39) | 324 untouched coins (final, run once) |
| --- | --- | --- |
| Harvest on Bybit only | −3.8% a year against Binance (fail) | — |
| Half on each venue | −1.9% (fail) | — |
| Each coin on the venue paying more | **+5.3% a year, t 7.39, 7 of 7 years (pass)** | **+0.7%, t 1.25 against a bar of 2.13: FAIL** |

**Why it failed.** On the 140 coins, Bybit paid more on 39% of days. On the untouched coins it paid more on only 12%.
The harvest stays on Binance, ranked on 30 days.

The final bar counts that this file was also used by round 16. Even the original bar (1.96) was not met.

## Described (not tested): where funding was paid in 2025–26
On the 324 untouched coins, the plain Binance harvest made:

| Coin group | 2025 | 2026 |
| --- | --- | --- |
| All 324 | +12% | +27% |
| 125 older coins | +5% | −2% |
| 199 coins listed since April 2025 | +6% | +27% |

- Worst week: −8%.
- Many of the new coins may have no Binance spot market to hold, which the harvest needs. That is unchecked, so this
  is a question for the next round, not a rule.

## App changes
- The harvest card states the Bybit result and where funding was paid.
- The research record completes round 15.
- The knowledge now holds 2,239 rules and studies.

## Checks
- s80 4/4.
- All earlier suites: s49 11/11, s50 5/5, s58 9/9, s60 9/9, s62 7/7, s67 15/15, s69 21/21, s70 21/21, s71 16/16,
  s72 11/11, s73 7/7, s77 27/27, s78 13/13, s79 9/9.
- 111 script blocks pass `node --check`. Phone guard clean.
- Chromium shows the card with no errors.
