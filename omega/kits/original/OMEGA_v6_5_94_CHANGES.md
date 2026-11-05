# OMEGA v6.5.94 — Events ahead and the Monthly review (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.94 · build 2026-10-22 10:33 UTC. Made with `python3 patch94.py <v6.5.93 build> <new build>` (uses `review.js`, `rguard94.js`).
These files were written in an earlier, interrupted attempt in this session. They were reviewed line by line and tested
before release.

## New
- **Events ahead,** under Market now on the Analysis page and Market Read:
  - the next US inflation (CPI) and Fed (FOMC) releases, in UTC and Tobago time;
  - taken from the Market Clock's official calendar (BLS schedule and Federal Reserve calendar, built in v6.5.79; 2027 Fed dates marked tentative there). No date is typed from memory.
  - From 2 hours before to 1 hour after a release, a red warning says not to open new trades.
- **The same warning in the Risk Guard's pre-trade check.** It is advice only: the Growth Bot's rules stay exactly as plan E17 fixed them.
- **Monthly review** at the bottom of the Risk Guard page. Per calendar month, from the records only:
  - the Growth Bot: trades, result and month-end equity;
  - the Daily Plan: trades and R;
  - your logged trades: result, rule breaks and what they cost.

## Verification
- **s94 (4 checks):**
  - events from the calendar, with the window running 2 h before to 1 h after (CPI 10 Nov, Fed 28 Oct);
  - the monthly review's figures;
  - the pre-trade check warns inside the window and not outside it, while the bot's rules ignore events;
  - a browser run: Events ahead on Analysis, the Monthly review on Risk Guard; no NaN, no overflow, no page errors.
- **All 28 suites pass** (s49…s94). s93, s89 and s87 need more than 45 seconds; run them with a 130-second timeout.
- **Other checks:** 114 script blocks pass the syntax check; no duplicate ids; phone guard clean; 28-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.**
