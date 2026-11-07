# OMEGA Prime — Claude's own version (delivered as `omega-prime.html`, next to the original `omega-v6_5-47.html`)

Built 25 Oct 2026 from the original build v6.5.96, which is delivered unchanged. Single file, no dependencies, 140 KB. Paper only:
it places no orders and holds no keys or passwords.

## The idea
An instrument that answers three questions every time it is opened: **what is the market doing, is there a trade worth taking,
and how much may be risked?** It also keeps an honest record of whether its own advice works. Everything else was left out.

## What is in it
- **Today (the first screen):** one verdict in a dark ink block, in this order:
  1. the risk rules say stop;
  2. hold off around a Fed or CPI release;
  3. a Grade A climax signal;
  4. a Grade B panic-bounce order or trade (H1/H3);
  5. the best Grade C Daily Plan setup;
  6. stand aside.

  Underneath: the risk status, the market-state dial (depressed, correcting, normal, quiet, booming), the five biggest coins with their side, and the events ahead.
- **Chart:** the cockpit (candles with US hours, volume split by aggressive side, liquidity levels on the price axis, the order-book column, the plan as a position box), then Market Read's liquidity ladder and level memory.
- **Signals:**
  - the climax watch (Grade A): round 16's frozen rule on the 40 most-traded Binance USDT perpetuals, forward record in this app;
  - the panic-bounce watch (Grade B: passed a fair test, not yet confirmed): E22 H1 (a buy limit 2σ under a bottom-10%
    24-hour fall, 3 hours to fill, sold a day after the fill) and H3 (the deepest 5% of falls while 20%+ of the watched coins
    panic), on the 40 most-traded coins, with a gauge of the share of coins in panic and its own forward record;
  - the Daily Plan (Grade C, unproven, followed on paper).
- **Risk:** the Risk Guard rules, the pre-trade check and journal, the Growth Bot (100 USDT, paper), "Is the bot worth it?" (against holding BTC, and under worse fills), and the monthly review.
- **Evidence:** what is known (passed, failed, being measured), the data check, the Autopilot table with an on/off switch per job, keep-screen-on, notifications, and backup/restore.
- **The Autopilot:** one scheduler. It runs climax, panic, mread, dplan, cockpit, rguard and truth while the app is open, and refuses the original build's research-only jobs.

## What was left out, and why (all still in the original build)
- **Research machinery** (Research Lab, Edge Lab, sweeps, Market Watch recording, metals/forex downloads): for research, not for deciding a trade.
- **Failed strategies** (Breakout Desk setups, CREED's rules, the old OMEGA Signals): they failed fair tests.
- **Duplicate pages and static profiles:** the facts that matter are in Evidence and on the chart.

## Design
- Graph-paper background with ink-dark type, serif headings and monospace figures.
- A bottom tab bar on phones; top tabs and two columns on computers.
- The verdict is always the first thing on screen.

## Data kept apart
Both files share one browser storage when opened from the phone's files, so every Prime record is stored under the prefix
`prime:`. The two apps never read or overwrite each other's records.

## Built from tested parts
- **Taken from v6.5.96, with storage switched to `prime:`:** Market Read, Daily Plan, Risk Guard and Growth Bot, Cockpit, Data check, Events and Monthly review. The Market Watch section of Market Read and the research-export section of the Risk Guard were removed.
- **New:** the lighter climax watch, Today, Evidence, Settings, the Autopilot and the design.
- **Accuracy fix found while building:** the data check skipped a market that could not be read and still reported "all live". In Prime a failed read is counted as a problem. The same flaw exists in v6.5.96, which was kept unchanged as asked; it is a one-line fix there if wanted.

## Verification (`s_prime_test.js`, 10 checks)
- **The climax rule:** fires on a 3σ flush with 3× volume closing in the top 40%; not on a weak close, low volume, or a coin under 30 days old.
- **A climax trade:** buys the next open and closes 12 hours later after costs (+1.8% in the check).
- **In the app:**
  - the Autopilot's own scan finds a planted climax among 40 coins (stablecoins skipped);
  - Today raises it as Grade A, with the dial, coins and events;
  - every page renders, with no research-only sections.
- **The Autopilot:** carries Prime's jobs and refuses the research ones.
- **Data check:** counts a failed read as a problem.
- **Storage:** every key starts with `prime:`.
- **Layout:** no overflow and no page errors on a phone (412 px) or a computer (1280 px).
- **Other checks:** 11 script blocks pass the syntax check; no storage access outside the `prime:` wrapper.
- **Not run on a real phone.**

## Build
`python3 build_prime.py <original build>` → `omega-prime.html`, from `prime_shell.html`, `prime_pre.js`, `prime_post.js` and the six
modules in the original build. Test: `node s_prime_test.js`.

## Update 25 Oct 2026 (evening): Grade B panic bounce
- **New module `prime_panic.js`;** `prime_post.js` and `prime_shell.html` changed for the verdict, ledger, Signals page and style.
  `patch_prime_panic.py` turns the earlier Prime into this one (checked byte for byte); `build_prime.py` rebuilds from the
  original build (last run on v6.5.96; not rerun on v6.5.97).
- **Same trades as the research engine:** on 12 synthetic coins with gaps, the app's H1 and H3 give exactly e22_lib's 125 and 69
  trades (`parity/make_parity.py` → `parity/parity.json`). Thresholds are set at 00:00 UTC from the previous 720 hours.
- **A volume-0 candle counts as missing** (trading halts; Binance's archive also writes flat ones after a delisting).
- **Differences from the test, stated in the app:** breadth counts the 40 watched coins, not every perpetual; the 30-day age rule
  uses the listing date when Binance gives one.
- **Checks (`s_prime_panic_test.js`, 16):** parity (H1, H3), numpy percentiles, volume-0 candles, pending → missed, fill → sale
  24 hours later, H3's sale, signals waiting their turn, young coins; in the app: the scan finds a planted market-wide panic only
  on the coins that fell, Today raises Grade B (labelled unconfirmed, small seats), Signals shows the watch and gauge, Evidence
  lists H1/H3 and E25, the Autopilot runs `panic`, storage stays under `prime:`, no overflow or errors on phone or computer.
  `s_prime_test.js` still passes 10/10. **Not run on a real phone, and not against the real Binance.**

## Update: trade tickets on Today (prime_tickets.js)
- **"Your orders"**, directly under the verdict: for every live signal of a rule that passed a fair test (climax reversal,
  panic bounce H1/H3) an order slip: Binance USDT-M futures, 1× isolated, side, type, exact price, size in USDT (default 5,
  Binance's minimum; adjustable), when to cancel an unfilled limit, when to sell. Exits that are due come first as SELL NOW.
- Each ticket carries the rule's measured odds and tail risk. CREED and the Daily Plan never get tickets (no edge after costs).
- "I placed it" / "Skip" per ticket; a reminder notification when a placed ticket's exit is due; a scoreboard of every
  ticket (paper) and of the ones placed. Stored under prime:prime_tickets_v1. Prime places no orders itself.
- `patch_prime_panic.py` now also adds the tickets. Checks: `s_prime_tickets_test.js` (14) on phone and computer;
  `s_prime_panic_test.js` 17/17 and `s_prime_test.js` 10/10 still pass. Not run on a real phone.

## Update 5 Nov 2026: UX layer (prime_ux.js, patch_prime_ux.py) — display only
- **Build chain (reproducible):** `omega-prime-base-25oct.html` (the 25 Oct Prime, md5 85d94f81…, recovered byte for byte from the
  tickets build) → `python3 patch_prime_panic.py omega-prime-base-25oct.html tk.html` (md5 2d6f2dae…, the tickets build, checked) →
  `python3 patch_prime_ux.py tk.html omega-prime.html [edges/approved.json]`. The UX patch asserts that the climax, panic-bounce,
  ticket and Autopilot script blocks stay byte-identical: no rule, threshold, ticket or number changed.
- **Today:** "Your orders" sits directly under the verdict (the dial and the five coins moved below). When the hourly scans could not
  reach the market the verdict says **"No market data — Cannot check today"** instead of "Stand aside" (offline it used to claim the
  rules were checked, with a "data live" chip, although the data check had read nothing); "Checking the market…" before the first scan;
  "data live" only when a feed was really read; a chip with when the signals were last checked; a note over the orders when there is no data.
  A Grade C plan is drawn as a paper card with dashed border and "Not an order" (tickets come only from tested rules); tested signals keep the dark ink block.
- **Signals:** "The rule book" at the top: every rule by grade (A, B, C), one line each with its live state, tap to jump to its card.
  Rules the research adds to `edges/approved.json` are embedded at build time (`window.PRIME_EDGES`) and appear under their grade in a
  collapsed "N more from the research list" line, and in Evidence; no new pages. To refresh only the list:
  `python3 patch_prime_ux.py omega-prime.html omega-prime.html ../../../../edges/approved.json`.
- **Evidence:** the ledger grouped as passed / being measured / failed, with counts and jump buttons.
- **Back button:** each page has its own address (#today, #signals…), so Android's back returns to the previous page instead of leaving the app.
- **Readability:** gold text #a8701a → #8f5e12 (4.1 → 5.5:1, WCAG AA), dial labels 3.6 → 5.6:1 and no longer hidden by the thick arc,
  buttons, chart pills, ticket buttons and inputs ≥ 44 px tall, small print 12.5 → 13 px.
- Checks: `s_prime_test.js` 10/10, `s_prime_panic_test.js` 17/17, `s_prime_tickets_test.js` 14/14 before and after (tests unchanged).
  Screenshots and the audit: `audits/ux/`. Not run on a real phone.
