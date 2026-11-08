# OMEGA v6.5.109 — clean-up: research leaves the app (it now runs in `edges`, the GitHub paper bot/scouts and the Live API)
- **Size:** 4,573,298 → 2,465,880 bytes (−46%). The biggest cut is the 1.06 MB embedded "starting knowledge" seed: 99% research
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
- Build: `python3 patch109.py <v6.5.108> <out>`. Test: `PREV=<v6.5.108> node s109_test.js <build>` (14/14).
