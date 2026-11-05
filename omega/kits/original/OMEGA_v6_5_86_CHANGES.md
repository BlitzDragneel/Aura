# OMEGA v6.5.86 — Market Profiles: both directions (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.86 · build 2026-10-20 23:26 UTC. Made with `python3 patch86.py <v6.5.85 build> <new build>`. It uses
`mprof86.js`, generated from `mprof86_src.js` plus the E5 data and texts from `mprof.js` and `plans/E7_anatomy.json`.

## Changed: every Market Profile has a "Both directions" section (plan E7, md5 `4601481e4f61bb8cafe56ecffff9d128`)
- **Rising against falling:**
  - share of hours and days, average hour, the 1-in-100 hour;
  - the biggest hour and biggest 24 hours, with dates;
  - swings of 10%+ (coins) or 3%+ (gold): how many, typical size and length, the biggest and longest;
  - movement in the 24 hours after a big hour up against after a big hour down;
  - the share of big hours that come in US hours.
- **What the data says, per market:** whether its sharp hours are mostly spikes up (DOGE) or drops (LTC, LINK, gold), and whether falls are quicker than rallies.
- **Long side against short side** of plan E5's two-sided rules, 2024–2026, after costs.
- **Four short-only rules**, chosen on 2020–2023 and judged once on 2024–2026: blow-off short, failed-breakout short, downtrend US-hours short, breakdown in a downtrend. **None passed on any market.** The blow-off short fires too rarely on a single market to judge.
- **Short-side guidance:** where shorting is possible (on MT5 gold, overnight swap applies), squeeze risk from each market's biggest up moves, and the plain conclusion that neither direction gave an edge on its own.
- **Start-here text:** now says "buying or shorting".
- **Research record:** round 24; the heading now reads rounds 1–24.

## Verification
- **s86 (5 checks):** version and record; every figure equal to `fixtures/E7_anatomy.json`; all six sections render (20+ table rows, verdicts, guidance, no NaN); per-market wording follows the data; the page includes the section.
- **All 20 suites pass** (s49…s86). s85's version and heading checks were widened.
- **Other checks:** 107 script blocks pass the syntax check; no duplicate ids; phone guard clean; 26-page crawl offline and with a fake exchange shows 0 errors.
- **Not run on a real phone.**
