# OMEGA v6.5.85 — Market Profiles (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.85 · build 2026-10-20 23:13 UTC. Made with `python3 patch85.py <v6.5.84 build> <new build>`. It uses
`mprof.js`, generated from `mprof_src.js` plus `plans/E5_dossiers.json` and the market texts, and `goldh85.js`.

## New: Market Profiles (menu under Breakout Desk; module `OMEGA_MPROF`)
Gold and five coins (DOGE, LINK, LTC, ADA, AVAX), studied one by one in plan E5 (md5 `1e94469c0572d0b0b531573a422763ae`).

**Each profile has:**
- **Right now:** live price, the 24-hour change and range against a typical day, the current session, and how this hour usually moves.
- **When it moves:** a 24-hour clock in UTC and Tobago time. Bar height shows typical movement; colour shows the average drift. There is a "now" marker and a session table (drift a year, years up, typical hour).
- **How it behaves:**
  - after big hours and 24-hour breakouts, in both periods;
  - trend or snap-back (variance ratio);
  - for coins: correlation and beta to the crypto market, how much calmer weekends are, and daily volume;
  - fees as a share of a typical hour.
- **What moves it:** general knowledge up to mid-2026, labelled as not being live news.
- **How to trade it:**
  - honest rules of engagement;
  - a calculator (account, risk %) that sizes a position from a 2-hourly-range stop, using the live range when loaded;
  - a warning when Binance's 5 USDT minimum would force more risk;
  - for gold, the size of MT5's 1 oz minimum against the account.
- **What has been tested on it:** the plan E5 rule table (t on 2020–23 and on 2024–26, the chosen rule, FAILED), plus earlier tests.
- **Forward record (plan E6, md5 `893c625104a6fe7aa37138bcb02ae778`):**
  - from 21 Oct 2026, each whole UTC day's sum of hourly log returns outside US hours, and during them (bars opening 13:00–20:00);
  - read from Binance perpetual hourly closes (XAUUSDT for gold);
  - kept in localStorage `omega_mprof_e6_v1`; complete while the app is opened at least once a month;
  - judged once after 26 weeks.

**Live data:** 6 keyless requests (`/fapi/v1/klines`, 1h, limit 1000) when the page opens, if the last read is over 30 minutes old, and hourly while the app is visible.

## Changed
- **Gold card (Breakout Desk):**
  - shows the plan E2 and E3 results;
  - now serves plan E4 (md5 `0f11ee8e135340aa745c831482f4b5c0`): Download continues gold back from where the first file stopped, then fetches silver.
- **Research record:** rounds 21 (E2), 22 (E3) and 23 (E5/E6) added; the heading now reads rounds 1–23.

## Verification
- **s85 (11 checks):**
  - the page wiring;
  - every figure equal to `fixtures/E5_dossiers.json`;
  - all six profiles render with 24 clock bars, FAILED tables and no NaN;
  - the sizing arithmetic and the minimum-order warning;
  - the E6 record on synthetic hours: whole days from 21 Oct only, and the outside and US sums exact;
  - nothing judged before 26 weeks;
  - the gold card on E4;
  - a browser run: 6 live requests, the clock, switching markets, no NaN, no overflow, no page errors.
- **All 19 suites pass** (s49…s85). s82 and s84 had version and heading checks widened.
- **Other checks:** 107 script blocks pass the syntax check; no duplicate ids; phone guard clean; 26-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.**
