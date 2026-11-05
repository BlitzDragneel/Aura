# OMEGA v6.5.49 — OMEGA proposes its own strategies from what it observes

Builds on v6.5.48 (which fixed the stop used by CREED's "as it could be taken" replay figures). VERIFIED = run against the app in Node (the verification harness) on synthetic markets, and in headless Chromium (21 pages crawled, no page errors, no overflow; the new card renders at phone width).

## New: the Strategy Workshop (an Autopilot research job)
Each round, three steps that never mix:
1. **Observe** the earlier 60% of history (later rounds: everything up to where the last round's test ended). Every closed hourly bar of every studied market is put in fixed bins, written before any result, of 8 measurements: RSI, distance from the 20 EMA, EMA20 − EMA50, place in the 50-bar range, 10-bar change, volatility percentile, relative volume, taker flow. For all 700 pairs of bins, what followed over the next 24 hours is added up, long and short, after costs. No outcome may end after the observation's cut.
2. **Propose** the 10 strongest cells (200+ bars over 30+ weeks, weeks as the sample, at most two per pair of measurements) as rules, frozen with the date.
3. **Test once** on the later data the observation never touched: entered at the bar's close, 2 ATR stop, out after 24 hours, one trade at a time, the Research Lab's costs and cleaning. Passes with 50+ trades over 15+ weeks, positive also with costs doubled, and z at or above the one-sided Bonferroni bar over **every rule ever proposed**. Passed rules that are mostly the same trades as a stronger passed rule are noted as the same evidence and not followed twice.

Survivors are then judged only on trades after the round (every 7 days): 50+ trades over 8+ weeks and z at or above the bar for every rule that reached that stage; after qualifying, the demotion rule applies. A new round needs 90 days of data no earlier round used. Paper only.

VERIFIED on 6 synthetic markets (5-minute bars, 700 days):
- pure random prices: 10 rules proposed (the best of 700 cells always looks good on the data it was picked from), **0 passed** the test;
- with a planted effect (a drift up for a day after a sharp fall): found from observation and passed, long only; 7 of the 9 passing variants were recognised as the same evidence, leaving 3 to follow.

## New: one table of everything the Autopilot researches
On the OMEGA Strategy page: the Research Lab, shortlist backtests, exploration of every bar size, portfolio strategies, the edge search, CREED replays and studies, and the workshop, each with its last run and latest result.

## Not changed
CREED's method; every other job; the v6.5.48 replay fix (its 6 checks pass on this build too).

## Tests
`s49_test.js` (11 checks) and `s48_test.js` (6 checks), both Node with `smoke.js` and `fake_idb.js` from the verification bundle (`HARNESS=<folder>`). Outputs in `s49_output.txt`. The workshop source is `workshop.js`; `patch49.py` applies it to v6.5.48.
