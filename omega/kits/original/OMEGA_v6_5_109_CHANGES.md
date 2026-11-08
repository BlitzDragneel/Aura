# OMEGA v6.5.109 — clean-up: research leaves the app (it now runs in `edges`, the GitHub paper bot/scouts and the Live API)
- **Size:** 4,573,298 → 2,464,799 bytes (−46%). The biggest cut is the 1.06 MB embedded "starting knowledge" seed: 99% research
  stores (Lab results, entry/pattern/range tables) plus 789 backtest journal rows. Her device applied it long ago; backups cover
  a new device. No localStorage is deleted — stores of removed pages are simply no longer read.
- **Pages removed** (markup, menu, palette, page hooks, links): Research Lab, Edge Lab, Market Watch, Market Profiles, Breakout
  Desk, OMEGA Strategy, Strategy Scanner, Strategy Backtest, CREED Backtest (Simulation), How OMEGA thinks, Scoreboard.
- **Modules removed:** seed, Sim Labs 2&3 (orphaned), Scoreboard, Edge Finder, OMEGA Strategy + cross-section, auto backtest,
  exploration, market board, portfolio lab, workshop, all research exports, outside research record, carry weekly, funding
  harvest, round 12, BTC trend, wide data store, edge library, Edge Lab, "why signals are rare", Breakout Desk, gold hourly
  download, Market Profiles, model across coins, Market Watch recorder; CSS niCss/btCss.
- **Autopilot jobs removed:** deep, topup, creed (replay), patterns, lab, edge, context, entry, forecast, reflect, council, and
  backtests, explore, portfolio, workshop, harvest, r12, btctrend, wide, edgelab, bdesk, mprof, mwatch, mwdays, goldh, autoexp.
  Kept: intel, scanner, positioning, live, journal, reason, desk, analysis, bots, health, panic, climax, mread, dplan, rguard
  (Growth Bot), cockpit, truth.
- **Kept as code only** (kept pages or CREED's bots call them): Research Lab engine + its signals module, Mind (broker costs),
  entry/context studies (CREED bot add-ons), history store, simulation engine v2.2 (switchTab/decimalsFor used everywhere).
- **Navigation:** menu regrouped (Home · Charts & markets · Signals · Bots & risk · Trading desk · Learn · System); phone bar
  Home / Charts / Signals / CREED / Bots / (Academy from v6.5.110) / More; the app always opens on Home; a link to a removed page
  lands on Home.
- **Signals:** climax (A), panic bounce (B), Daily Plan (C, now shown here with its grade explained) and an Evidence note
  (what passed, what failed, link to https://omega-board.onrender.com). The Research Lab's own signal lists left the page.
- **Futures:** the research backtest card (Lab/CREED-backtest buttons) left; calculator settings, leverage warning and paper
  account stay. Self-test: the Sim Labs checks went with the module (carry-monitor check kept).
- CREED's engine and its whole module are byte-identical (s102 and s109 with PREV = v6.5.108).
- Also re-homed: the climax and panic cards (their Edge Lab/Watch hosts kept the panic card from rendering) now wire to the
  Signals page alone; the Market Clock (sessions, CPI/FOMC/expiry calendar) moved from Market Watch to Market Intelligence;
  Market Read's "Market Watch recording" and Risk Guard's "Research exports" sections removed.
- Build: `python3 patch109.py <v6.5.108> <out>`. Test: `PREV=<v6.5.108> node s109_test.js <build>` (16/16).

## Suites (node 22, Playwright; HARNESS=kits/original/tools, PREV=v6.5.108)
- v6.5.108: 38 of 49 files pass in full (s100–s108, s49, s50, s58, s60, s62, s70*, s71, s73, s78, s80–s99); failing: s48, s55, s56,
  s59, s67, s69, s72, s77, s79 (known: missing research files / superseded; see audits/bugs/BUG_REPORT.md).
  *s70 now uses `process.env.HARNESS + '/fake_idb.js'` (B7 fix). tools/crawl.js takes `PAGES=a,b,c` for the kept pages.
- v6.5.110: pass — s102, s107, s108, s109, s110, s58, s78, s89, s91–s99 (21 files).
- **Updated** for the removal (kept features still tested): s58 (navigator list; the report field left with OMEGA Strategy),
  s78 (climax parity runs without the edge library; the watch now lives on Signals), s89 (Market Read; gold download, research
  knowledge and Market Watch days skipped from v6.5.109), s92 (Risk Guard without research exports/autoexp), s98 (panic card on
  Signals only), s102 (engine + reality check; research card skipped when absent).
- **Retired by design** (they test removed research): s100, s103, s104, s105, s106 (research card, harvest/round-12 cards,
  harvest job), s49 (workshop), s50 (history export), s60 (BTC trend), s62 (harvest), s70 (Edge Lab), s71 (CREED replay
  history card, needs OMEGA_EXPLORE), s73 (edge library), s77 and s101 (Market Watch), s80, s81 (harvest card/research record),
  s82 (audit trims of research cards), s83, s84 (Breakout Desk), s85, s86 (Market Profiles), s87, s90 (Autopilot coverage
  jobs for research parts), s88 (research files). Still failing as before: s48, s55, s56, s59, s67, s69, s72, s79.
- Crawl of the 18 kept pages (incl. Academy), offline and with mocked feeds: 0 page errors, 0 console errors.
