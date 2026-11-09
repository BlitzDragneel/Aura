# OMEGA v6.5.116 — one Autopilot that runs the app by itself
- **One scheduler: the job runner (OMEGA_OPERATOR).** OMEGA_AUTOPILOT keeps paper trading, revalidation and the risk
  governor, but its own 60 s timer no longer starts when the runner exists; the runner's job **paper** calls it every minute.
  Also moved into the runner (own timers removed): the Brain's daily reflection, the Forex board's 20 s and the bots feed's
  2 min page timers.
- **Audit.** Before (active): intel, scanner, positioning, live, journal, reason, desk, analysis, bots, health, panic, climax,
  mread, dplan, rguard, cockpit, truth, + the Autopilot core's own timer and the reflection timer; dead code filtered since
  v6.5.109: deep, creed, patterns, topup, lab, edge, context, entry, forecast, reflect, council.
  After (25): the 17 kept + **forecast** (Brain prediction scorecard, range forecasts) and **reflect** (Brain "what it has
  learned"), back because the Brain page reads them + **paper** + new **fxboard, botsfeed, scouts, academy, connections**.
  Retired: deep, creed, patterns, topup, lab, edge, context, entry, council (and older research ids); their runner state
  entries are dropped; stored history, replays and lab results stay in storage untouched.
- **New jobs:** fxboard (1 min while the board is open, else 15), botsfeed (2 min while Bots/Home is open, else 15), scouts
  (/scouts?speed=fast, 15 min), academy (catalog, daily), connections (30 min: /health, token present and accepted, Binance
  reachable or OKX in use, Twelve Data key or Live API fallback). Without a token the Live API jobs wait (not errors).
- **Runs itself:** on at first launch (flag omega_selfrun116, plus the existing "When the app opens" autostart; Pause in the
  card also switches that off, so a pause survives reloads); back on after any reload or crash; missed runs catch up one job
  per lane, most overdue first; errors back off 5 min → 6 h; heavy jobs (forecast, reflect, journal) only with a visible tab
  and charging or unknown battery.
- **"OMEGA is running itself" card** on Home and the Autopilot page: on/pause, jobs on, last and next run, problems with a
  one-tap fix (Autopilot off, no/refused token → Settings, server asleep → check again, Binance down → "switched to OKX",
  failing jobs → retry, heavy jobs waiting on battery), the first-run **setup check** (server, token, theme, install,
  Autopilot) completed by itself where it can, the honest note (a browser app runs only while open; 24/7 = laptop Station and
  cloud bots, About link) and **Keep screen on** (Wake Lock, where supported).
- Suites updated with reasons: s109 (forecast/reflect run again from v6.5.116), s112 (the bots-feed refresh is now the
  "botsfeed" job, not a page timer). New s116 (16/16). Build `python3 patch116.py <v6.5.115> <out>`.
