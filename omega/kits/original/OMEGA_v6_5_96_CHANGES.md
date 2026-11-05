# OMEGA v6.5.96 — Data check, baseline and fill stress (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.96 · build 2026-10-25 01:30 UTC. Made with `python3 patch96.py <v6.5.95 build> <new build>` (uses `truth.js`).

## Why
The pasted competitor audit (QuantConnect, TrendSpider, TradingView, Trade Ideas, Backtrader) was weighed against OMEGA. The sites
could not be browsed from this environment, so it was reviewed from the audit and known product capabilities.

**Already in place:**
- hypotheses written down first, an untouched holdout, every variant counted;
- the pass mark corrected for the number of tests, with results counted by week;
- cross-market comparison.

**Not taken:**
- one unified simulation engine: a large refactor with no direct path to an edge;
- AI ranking of signals: nothing to rank until something passes.

**Taken, as useful for finding an edge or keeping data honest:**
- a baseline to beat;
- fill uncertainty;
- data checks.

## New
- **Data check (top of the Analysis page; module `OMEGA_TRUTH`):**
  - every Autopilot job: fresh, overdue (more than twice its schedule plus 10 min), failing, never run, or off;
  - for every market read, whether the newest finished candle is current (older than 2 h = the feed stopped) and whether the futures mark price is within 0.5% of the spot index (built by Binance from several spot exchanges);
  - problems listed plainly, with a notification at most once every 6 hours.
- **"Is the bot worth it?" (Risk Guard page):**
  - the Growth Bot's change against holding BTC over the same period (from the first time BTC is read while the bot exists) and against cash;
  - **fill stress:** the bot's result again with +0.05% and +0.15% extra cost a side on every trade, labelled robust, sensitive, fragile or losing.
- **The Growth Bot now keeps each closed trade's size** (`nt`), which the fill stress needs. Its rules and results are unchanged; older trades without a size are skipped, not guessed.
- **Autopilot job `truth`,** every 30 min.

## Verification
- **s96 (6 checks):**
  - job statuses;
  - stale candles and a 1.2% index gap flagged, healthy markets passing;
  - the baseline comparison;
  - fill-stress categories, with older trades skipped;
  - the bot keeps size and its result is unchanged;
  - a browser run: both cards, the Autopilot job; no NaN, no overflow, no page errors.
- **All 30 suites pass** (s49…s96). s93, s89 and s87 need a 130-second timeout.
- **Other checks:** 115 script blocks pass the syntax check; no duplicate ids; phone guard clean; 28-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.** Live Binance data cannot be reached from the build environment, so the data check is what finds live-data problems on her device.
