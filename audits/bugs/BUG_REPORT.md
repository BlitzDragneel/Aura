# OMEGA original: bugs, duplicates and misinformation audit (5–7 Nov 2026)
Bot: bugs / errors / duplicates / misinformation. Target: `omega/apps/omega-v6_5-47.html`, v6.5.105 → **v6.5.107**
(patches `kits/original/patch106.py`, `patch107.py`; tests `s106_test.js`, `s107_test.js`; notes `OMEGA_v6_5_106_CHANGES.md`,
`OMEGA_v6_5_107_CHANGES.md`). OMEGA Prime was not edited: its issues are in section 6 for the UX bot.

## 1. Suite results (node 22, Playwright Chromium; one suite at a time; `HARNESS=kits/original/tools`, `PREV=<v6.5.105>`)
| | v6.5.105 (before) | v6.5.106 | v6.5.107 (delivered) |
|---|---|---|---|
| Suites passing in full, of the 44 files s48…s105 | 34 | 34 (+s106 13/13) | 34 (+s106 13/13, +s107 6/6) |
| s70 with its hard-coded `/home/claude/fake_idb.js` pointed at `tools/fake_idb.js` | 21/21 | 21/21 | 21/21 |
| s102 CREED engine byte-identical to v6.5.105 | pass | pass | pass |
| 28-page crawl, offline and with mocked feeds | 0 page errors, 0 duplicate element ids | same | same, 0 CSP violations |

So **35 of the handover's 39 current suites pass** at every step, matching the handover. The same 9 files fail before and after:
- **Missing research files (known):** s67 (`partB_fresh.json`), s69, s79 (`round17.json` / `round12_final.json`), s77 one
  check (`watch16.py`). All hard-code `/home/claude/research/`.
- **Not current suites (superseded on purpose by later builds, not in the 39):** s48 (needs two builds: `OLD NEW`), s55, s56,
  s59 (carry/harvest cards changed or retired in v6.5.82), s72 (the capitulation-watch script block no longer exists).
- s70 only fails because of the hard-coded `/home/claude/fake_idb.js` path. Fix for the kit: use
  `process.env.HARNESS + '/fake_idb.js'` as the other suites do.
- **Flaky:** s92's browser check failed once on v6.5.106 (Risk Guard inputs read `//100` instead of `100/98/100`: a fill-timing
  race) and passed on the next two runs and on the full v6.5.107 run. Patches 106/107 do not touch the Risk Guard.
- The lead's removal of the Twelve Data key broke no suite (no suite needs a key; the app says "No Twelve Data key" correctly).
- Crawl console noise: 2 WebSocket errors per crawl (`wss://stream.binance.com`, unreachable in the sandbox; expected).

## 2. Bugs and errors
**Medium**
- **B1. Two cards shared one `<style id="pbCss">`** (panic card ~line 33002, research card ~line 33055). Each creates it only
  if missing, from two independent 1-second timers, so whichever ran first won: when the research card won, the panic
  gauge lost its `.pgauge` rules. **Fixed in 106** (research card now `id="rareCss"`; s106 checks both styles exist).
- **B2. Backups carried the WhatsApp number and the Discord webhook URL; a crafted backup could set the webhook and keys**
  (security A1/A2; `buildBackup`/`restoreAllData` ~lines 9711–9820). **Fixed in 107** (see the change note; s107).
- **B3. Chart library from unpkg without SRI; no CSP** (security A3/A4). **Fixed in 107** (SRI hash verified from unpkg and
  jsDelivr; a CSP limited to scripts/frames/plugins; `connect-src` left open on purpose so typed webhooks/recorder/Live API
  addresses keep working; TradingView widget checked under the CSP).

**Low (not changed)**
- **B4. Twelve Data install stub sets `omega_td_key_installed_v1 = 1` without a key** (~line 29759, after the lead's key
  removal). Harmless now; if a key-carrying build is ever delivered again, browsers that ran this one will never auto-install.
- **B5. Day boundaries are UTC** (`today()` = `toISOString().slice(0,10)` in the Autopilot, Risk Guard daily loss, 65 places).
  For Maro (Tobago, UTC−4) the "day" resets at 20:00 local. Consistent and labelled UTC in most places; worth one line in
  Settings. The daily digest (line ~13165) is the only local-day calculation, deliberately.
- **B6. s92 Risk Guard input race** (above): the page fills its inputs after the test reads them on a slow run.
- **B7. Hard-coded `/home/claude/...` paths** in s67, s69, s70, s77, s79 (kit hygiene).
- **B8. Dead code:** `carryxs` `register(){ return true; /* … */ var O = … }` (~line 31329) keeps a retired job body that never
  runs; the storage card's fallback backup (~line 16922) only runs if `backupAllData` is missing (it always exists).
- Storage quota: handled centrally (a `localStorage.setItem` wrapper ~line 1721 plus the journal budget/IndexedDB archive);
  no unguarded failure found. Offline: no page errors with every request aborted; charts say they need the CDN.
- No NaN/undefined/Infinity/`[object Object]` on any of the 28 pages, offline or with feeds.

## 3. Duplicates
- **No duplicate top-level definitions** across the 118 inline scripts (acorn parse: functions, `var/let/const`, classes,
  `window.X =`). The many same-named helpers (`el`, `esc`, `render`, `lsGet`…) are inside separate IIFEs.
- `window.navigate` is wrapped 12 times (lines 9530 → 32718) and `OMEGA_JOURNAL_RENDER` twice: intentional chains (each calls
  the previous), not overrides. Fragile but working.
- No duplicate Autopilot job ids (s106 checks all ids are unique; every module guards with `J.some(id)`); no duplicate element
  ids on any page; no duplicate rows in the research card (E35/E36 sit before E34 in the list: order only).

## 4. Misinformation (text that contradicted the measured evidence)
| # | Where (v6.5.105) | Said | Evidence | Status |
|---|---|---|---|---|
| M1 | Autopilot job label (~31785) | "Funding harvest (the rule that passed its untouched test)" | E34: delta-neutral harvest 2025–26 −17%/yr, worst 30 d −33%, one flip −64.6% in a month | **Fixed 106**: "record only: passed rounds 7, 8, 10; failed E34 on 2025–26" |
| M2 | Harvest card heading/chip (~31742–31743), top of OMEGA Strategy | "passed untouched tests…", green chip "passed its untouched test" | same | **Fixed 106**: heading adds "FAILED on 2025–26 (E34)", chip "failed its 2025–26 test (E34) · kept as a record", red "Read this first" line |
| M3 | Round 12 winners card + label + Round 12 summary (~31984, 32006, 31572) | "passed on 125 untouched coins", no E34 | half of each winner is the harvest | **Fixed 106** (notes added; history kept) |
| M4 | Research record heading (~31046) | "what passed: the funding harvest … Everything else failed" | E34 | **Fixed 106**: "…the harvest then FAILED on 2025–26 (E34, −17% a year)" |
| M5 | Round list lesson (~31499) | "being paid for supplying leverage is [a law]" | E34 | **Fixed 106** |
| M6 | "Why signals are rare" footer (~33044) | "Next ideas not yet run: BTC/ETH timing…; H1/H3 on every perpetual" | both run: E28 round 5 (failed); E25/E26 on 883–903 perps | **Fixed 106**: lists on-chain flows and options data (handover §6) |
| M7 | Signal plan (~6673) and Simulation plan (~9294) | breakeven stop makes the rest "risk-free" | the app's own note (~22414): a stop is not a guaranteed exit; gaps, slippage, fees, funding | **Fixed 106** |
| M8 | Futures page (risky-leverage gap) | sizing defaults 5% margin × 10× (half the account per position), settings to 25×; no word on the evidence | CREED −0.10 to −0.12R/trade; 76% of accounts lose half in a year at 1% risk; E26 at 1× fell 56–59% | **Fixed 106**: red "Leverage — what the tests say" card on the Futures page |
| M9 | Brain pinned notes (~31737, 31963) | harvest "passed" notes stay pinned | E34 | **Fixed 106**: one pinned correction note (once) |
| — | Historical round rows (rounds 7, 8, 10, 12) | "PASSED" with their numbers | true as measured then | kept (now followed by E34 wherever shown prominently) |

Checked and correct: E28 = 12,480 rules (no 9,240 left); "8,660 tries" refers to rounds 1–3 (E28_LOG line 33, correct);
903 perps incl. 163 delisted; E22/E25/E26/E29–E36 figures in the research card match `research/plans-new/E29_E32_RESULTS.md`
and the handover; CREED reality check (49% vs 50%, −0.118R/−0.100R/−0.118R) correct; version stamps consistent (2 places).

## 5. Remaining (not fixed, by choice)
- Security A5 (proxied prices should be marked unverified and kept out of tickets/Autopilot), A6–A8 (escape the dormant
  journal fallback renderer, the two `esc()` variants without `"`, `r.reason` into innerHTML at ~5920), A10 (service worker
  file not shipped). Low risk today; each needs its own small patch and test.
- Kit hygiene: B7 paths, s48/s55/s56/s59/s72 marked obsolete in the kit, s92 race.
- Missing research files for s67/s69/s79/s77.

## 6. OMEGA Prime issues (for the UX bot; Prime not edited)
- **P1 (misinformation, medium).** `apps/omega-prime.html` Evidence ledger (currently line ~903):
  `['pass', 'Funding harvest', 'Passed, but its income has faded since 2025. Not used here.']` contradicts its own E34 row.
  Replace with:
  `['fail', 'Funding harvest (rounds 7, 8, 10, 12; then E34)', 'Passed untouched tests on 2020–26 data carried by 2021; run again on 2025–26 as a delta-neutral harvest (E34) it lost 17% a year (worst 30 days −33%, one funding flip −64.6% in a month). Not used here.'],`
  and move it next to the E34 row (or delete it and keep only E34).
- No "risk-free", guarantee, stale version or wrong E28 count found in Prime; its ledger figures for E22/E25/E28 match.
