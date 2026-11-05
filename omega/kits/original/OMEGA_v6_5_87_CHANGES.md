# OMEGA v6.5.87 — the Autopilot runs everything (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.87 · build 2026-10-20 23:48 UTC. Made with `python3 patch87.py <v6.5.86 build> <new build>` (uses `autocov.js`).

## What was wrong
- The Autopilot's scheduler (the Operator) ran 20 built-in jobs, plus 7 that the research modules register themselves (harvest, round 12, carry, BTC trend, Edge Lab, workshop, wide data).
- **The five newest parts never registered,** so they ran on their own timers while the app was open, invisible to the Autopilot:
  - climax watch (v6.5.78);
  - Market Watch (v6.5.77);
  - Breakout Desk (v6.5.83);
  - gold and silver download (v6.5.84);
  - Market Profiles' forward record (v6.5.85).
- **The gold download** only ran when the button was pressed.

## Change
New module `OMEGA_AUTOCOV` registers five Operator jobs, the same way the older modules do:

| Job | Lane | Runs | What it does |
|---|---|---|---|
| Climax watch | Watching | every 15 min (once per new hour) | calls the climax watch's own check; waits 3 min after the hour for the bar to settle |
| Breakout Desk records | Watching | every 15 min (once per new hour) | steps both paper accounts (failed setups, record only) |
| Market Profiles | Watching | hourly | live prices, and the plan E6 session record |
| Market Watch recorder | Watching | every 10 min | starts the recorder if it is not running |
| Gold and silver download | Downloads & research | every 6 h until done | continues the plan E4 download through the shared Twelve Data queue; a daily limit waits 3 h; when complete it says to press Save file |

- **One switch:** "Brain automation" now runs all 35 jobs.
- **Visible:** the Autopilot page's job table shows each new job's last result, next run and its own on/off switch.
- **Fallback:** the parts' own timers stay, for when the Autopilot is off.
- **Research record:** round 25 (a check, not a study); the heading now reads rounds 1–25.

## Verification
- **s87 (5 checks):**
  - the five jobs are registered (35 jobs in total) with valid fields;
  - the Operator runs the Market Profiles job (6 of 6 live prices, result recorded);
  - the gold and desk jobs leave readable results;
  - the Autopilot page's table lists all five;
  - no page errors.
- **All 21 suites pass** (s49…s87).
- **Other checks:** 108 script blocks pass the syntax check; no duplicate ids; phone guard clean; 26-page crawl offline and with a fake exchange shows 0 errors.
- **Not run on a real phone.**
