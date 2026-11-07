# OMEGA UX / visual / performance / navigation review — 5–7 Nov 2026

Scope: **OMEGA Prime** (`omega/apps/omega-prime.html`, Claude's lean app) and the **original OMEGA v6.5.105**
(`omega/apps/omega-v6_5-47.html`, 28 pages). Driven with Playwright (Chromium): phone = `devices['Pixel 7']` (412×915 CSS px,
CPU throttled 4× for the timing figures), desktop = 1366×768. Harness: `audits/ux/ux_shoot.js` (re-runnable:
`node audits/ux/ux_shoot.js <app.html> prime|orig <outPrefix> mock|offline quiet|live [scale] [phone|desktop]`).

**What is and is not verified.** The sandbox cannot reach Binance (HTTP 451), so "mock" runs answer Binance with synthetic candles
(prices and percentages in the shots are fake; the coin tiles show odd numbers for that reason). "live" plants the same
signal state as `s_prime_tickets_test.js` (tickets for AAA/BBB/CCC) — illustrative, not market data. CDNs (unpkg) were reachable.
Nothing here was run on a real phone.

Screenshots: `shots/before/` (both apps), `shots/after/` (Prime after the changes), `shots/showcase/` (2× before/after pairs).
Files named `*_DEMO*` / `prime_demo_*` use a fake `approved.json` with rules labelled "DEMO" only to show the rule-book layout.

---

## 1. Headline findings

| # | Finding | App | Severity |
|---|---|---|---|
| 1 | **Offline / blocked network, Prime said "Stand aside — no setup meets the rules" with a "data live" chip** although no scan had run and the data check had read 0 feeds (`readsCheck([])` → "All checked feeds live"). An honest-risk bug: "unknown" was presented as "checked, nothing to do". Same for "Your orders: none of the tested rules is live". | Prime | **High** — fixed |
| 2 | **"Your orders" was 2.5 phone screens down** (verdict → dial → coins → orders), although the README says "directly under the verdict". On a phone the day's orders were invisible without scrolling. | Prime | **High** — fixed |
| 3 | **A Grade C (unproven) plan got the same hero block as a tested signal** ("BTC SHORT at 69,061" in big red), while "Your orders" directly said "No order to place". Contradictory and visually over-weights an unproven plan. | Prime | High — fixed |
| 4 | **Android back button leaves the app** (no history entries). Applies to both apps. | both | High — fixed in Prime |
| 5 | Gold headings (#a8701a on #fffdf7 = **4.13:1**, fails WCAG AA for normal text); dial labels #8a8577 = 3.62:1; dial's "Depressed"/"Booming" labels hidden under the thick selected arc. | Prime | Medium — fixed |
| 6 | Tap targets under 44 px: 24 of 26 chart pills, ticket "I placed it"/"Skip" (≈ 30 px), Save/Restore buttons. | Prime | Medium — fixed (0 small on Today/Chart/Signals/Risk) |
| 7 | Evidence is 7 phone screens of a flat list mixing passed / failed / measuring. | Prime | Medium — grouped with counts and jump buttons |
| 8 | Original opens on the **last page used** (`omega_active_page`), its phone bottom bar is Home / **CREED** / Intel / Journal / More (CREED failed fair tests; the panic watch, the only durable edge, is behind "More" → Edge Lab), "What is actionable?" is card 2 under a "Market pulse" block, and every page is 4–10 screens long. | original | High (recommendations §5) |
| 9 | Original: 4.5 MB, phone (4× CPU) DOMContentLoaded 2.7 s, load 4.0 s, **36 long tasks (3.9 s) in the first 6 s**, longest 807 ms, 58 MB heap, 10.7k DOM nodes at start → 27k CDP nodes after 8 pages. 108–660 text elements under 12 px per page. | original | Medium |
| 10 | Original pulls fonts.googleapis, s3.tradingview.com/tv.js, unpkg lightweight-charts, a **third-party CORS proxy (corsproxy.io)** for the economic calendar, plus Hyperliquid/Kraken/Bybit/OKX/Coinbase and Binance websockets. Offline: no fonts, no charts (it says so), calendar unknown. | original | Medium |

## 2. Performance (measured, Chromium, this sandbox)

| | Prime before | Prime after | Original |
|---|---|---|---|
| File size | 174,804 B | 187,733 B (+7%) | 4,564,970 B (1.06 MB of it an embedded seed, `OMEGA_SEED_B64`) |
| Phone, 4× CPU: DOMContentLoaded / first paint | 460 ms / 176 ms | 279 ms / 180 ms | 2,733 ms / 1,320 ms |
| Phone: long tasks in first 6 s (total, longest) | 5 (399 ms, 108 ms) | 2 (125 ms, 75 ms) | 36 (3,900 ms, 807 ms) |
| JS heap after load / after all pages | 4.8 / 16.2 MB | 4.6 / 15.8 MB | 58.4 / 29.3 MB |
| DOM elements on a page (phone) | 913–1,184 | 921–1,227 | 10,746–12,055 |
| Page errors / console errors (mock) | 0 / 0 | 0 / 0 | 0 / many `ERR_FAILED` + websocket failures (expected in the sandbox) |
| Desktop DOMContentLoaded | 43 ms | 46 ms | 691 ms |
| Offline | works; all visuals are inline SVG (no CDN) — but said "Stand aside / data live" | works; says "No market data — Cannot check today" | works; charts (lightweight-charts from unpkg), fonts and calendar missing |

Prime's charts are hand-drawn SVG, so **Prime needs no CDN at all**; only Binance (fapi.binance.com) for data. Timing
differences of ±100 ms between Prime runs are noise (shared CPU with research jobs).

## 3. Prime: what was changed (implemented, through the kit)

Kit: `omega/kits/prime/prime/` — new `prime_ux.js`, `patch_prime_ux.py`, `omega-prime-base-25oct.html`; README updated.
Chain, reproducible byte for byte: `omega-prime-base-25oct.html` (md5 85d94f81…, recovered from the tickets build and checked)
→ `patch_prime_panic.py` → tickets build (md5 2d6f2dae…, identical to the delivered one) → `patch_prime_ux.py` → `omega-prime.html`.
`patch_prime_ux.py` **asserts the climax, panic-bounce, ticket and Autopilot script blocks are byte-identical** before/after;
the verdict's order (risk stop > event > A > B > C > stand aside) is unchanged — only the last branch gained "no data" / "checking".

| Change | Before → after (shots) |
|---|---|
| Orders directly under the verdict | `showcase/before_phone_today_live.png` → `showcase/after_phone_today_live.png` |
| Honest no-data verdict + note over the orders; "data live" only if a feed was read; "signals checked HH:MM" chip | `showcase/before_phone_today_offline.png` → `showcase/after_phone_today_offline.png` |
| Grade C as a dashed paper card with "Not an order" | `before/prime_phone_today.png` → `after/prime_phone_today.png` |
| The rule book on Signals (A/B/C, live state, tap to jump); research rules from `edges/approved.json` under their grade, collapsed | `showcase/before_phone_signals.png` → `showcase/after_phone_signals_rulebook_DEMO.png` |
| Evidence grouped Passed / Being measured / Failed with counts + jump buttons | `before/prime_phone_evidence.png` → `after/prime_phone_evidence.png` |
| Back button: `#today`, `#signals`… with history (checked: Today→Signals→Evidence, back, back = Signals, Today) | — |
| Contrast + tap targets + dial labels | small taps on Today/Chart/Signals 2/24/2 → 0/0/0; text < 12 px on Today 11 → 6, Evidence 33 → 0 |

**Tests** (unchanged files): before 10/10, 17/17, 14/14; after 10/10, 17/17, 14/14 (`node s_prime_test.js`,
`node s_prime_panic_test.js`, `node s_prime_tickets_test.js`, default file = the kit's `omega-prime.html`).

### New tested edges — design
- Prime cannot read files at runtime (opened from the phone's files), so the list is **embedded at build time**:
  `python3 patch_prime_ux.py omega-prime.html omega-prime.html <path>/edges/approved.json` refreshes only the
  `PRIME EDGES` block (fields kept: id, name, grade, plan, tf, status, max_leverage, margin_usdt, evidence; `</` escaped).
- The ids `climax_a`, `panic_h1`, `panic_h3` (already in `edges/approved.json`) map onto Prime's own watches and add their
  bot status ("bots: paper/testnet") to the row; any other rule appears as one line inside a collapsed
  "N more from the research list (Prime does not watch them yet)" under its grade, and as a row in Evidence
  ("Added by the research"). **No tickets are generated for them** — Prime only writes tickets for rules it has code for.
- Next step when a new rule earns a live watch in Prime: give it a module like `prime_panic.js` and a `where:` card id in
  `builtins()`; or read its signals from the Live API (§4).

## 4. Prioritized recommendations — Prime (impact × effort)

| Priority | Recommendation | Impact | Effort | Status |
|---|---|---|---|---|
| P1 | Items in §3 | high | low | **done** |
| P2 | **Optional Live API source** (`omega/live_api`, http://127.0.0.1:8787): a Settings field "Data source: Binance direct / OMEGA Live API (URL + token)". Use `/crypto/klines` + `/crypto/top` for the scans (same candle shape after mapping `{t,o,h,l,c,v}`; keep only `closed:true` bars so the rules see exactly what they see now), `/health` for the data chip (it names which source is down), `/fx/quote?symbol=XAUUSD` for a gold/forex line on Today, `/signals` for approved rules Prime does not watch itself. Keep Binance-direct as the default and as the parity reference; any source switch must rerun the parity checks (H1/H3 trade-for-trade). Note the service is HTTP on the LAN: from a `file://` page Chrome allows it, but the phone needs `OMEGA_API_HOST=0.0.0.0` + token (README). | high (Binance 451 / mobile networks) | medium | recommended |
| P3 | "0 coins scanned" counts as a successful scan (an empty `ticker/24hr` answer gives "Scanned 0 coins … 0 new signals" and the verdict can say Stand aside). Treat `universe().length < 20` as a failed read. This is inside the frozen climax/panic blocks, so it needs a deliberate logic patch + test. | medium | low | recommended |
| P4 | On no data the dial's needle rests on "Normal" with "Reading the market…" — grey the dial out until the first read. | low | low | open |
| P5 | Desktop Today: verdict + orders in the left column, market/coins/events in the right (uses the 1366 px width; today everything stacks). | medium | low | open |
| P6 | Ticket slip: put "Cancel if unfilled at …" and "Sell at …" as one bold line each with a countdown; add "copy price" button (fewer typing errors on Binance). | medium | low | open |
| P7 | Autopilot checkboxes in Evidence are 24 px inside a 44 px row; make the whole row the label. | low | low | open |
| P8 | Add a web manifest + service worker only if Prime is served over https (not for `file://`). | low | medium | open |

## 5. The original (v6.5.105) — recommendations with exact changes (for the bug bot / Maro; not applied)

Ordered by impact × effort. Line numbers are in `omega/apps/omega-v6_5-47.html` (v6.5.105).

1. **Open on Home, always** (design rule 7: an obvious starting point). Today `navigate` stores `omega_active_page` and the boot
   restores it (lines 9529–9562, 18923–18948), so the app can open on Research Lab. Change: at boot, ignore the saved page
   unless it is `command` (keep saving it for "Continue where you were" as a link on Command).
2. **Phone bottom bar = the decisions** (line 19362). Proposed:
   `var items = [['command','⌂','Home'],['edgelab','✦','Signals'],['rguard','⛨','Risk'],['journal','▤','Journal'],['__more','☰','More']];`
   CREED stays one tap away in More (its engine untouched). Reason: CREED failed fair tests (E29/E31); the panic watch,
   the only durable edge, is currently behind More → Edge Lab.
3. **Back button**: in `navigate(p)` (line 18942) add `try{ if(location.hash !== '#'+p) history[history.state ? 'pushState' : 'replaceState']({p:p}, '', '#'+p); }catch(e){}`
   and once at boot `window.addEventListener('popstate', function(){ var p = location.hash.slice(1); if(p && document.getElementById('page-'+p)) navigate(p); });`
   (guard against re-pushing during popstate with a flag, as Prime does with `show(p, true)`).
4. **Command: put "What is actionable?" (card 2) first, above "Market pulse"**, and show the panic-bounce state in it
   (the strip at the bottom "Panic-bounce watch … 3 need you" is easy to miss and overlaps the bottom bar on phones).
5. **Honest no-data state** as in Prime: when the scans failed, Command's "Nothing actionable right now … waiting is a position"
   should read "Cannot check: no market data since HH:MM".
6. **Readability**: 30–88% of text elements on the audited pages are under 12 px on a phone (Autopilot 660 of 812, Positioning Desk
   317 of 359). Set a floor: `@media(max-width:600px){ body{font-size:15px} small,.hint,.muted,.sub{font-size:13px!important} }`
   and `button,.btn,[onclick]{min-height:44px}` (Autopilot: 101 of 110 controls are below 44 px). `--text-dim:#8995A8` on
   `#11151B` is 6.0:1 (passes); the 9–10.5 px sizes are the problem, not the colours.
7. **Performance**: decode `OMEGA_SEED_B64` (1.06 MB gzip-base64) lazily on first need instead of at boot, and defer page renderers
   until their page is opened; the 807 ms longest task and 36 long tasks at start come from boot work on a 4× slower CPU.
   Inline or self-host lightweight-charts (≈160 KB) so charts draw offline; drop Google Fonts (system fonts) to save a blocking request.
8. **Privacy / reliability**: the economic calendar goes through `corsproxy.io` (a third party sees every request). Prefer the
   Market Clock's official BLS/FOMC dates (already in the file and used by Prime) or the Live API.
9. **Design rule 7**: the original is the dark-dashboard shell the rule warns against. If Maro wants the change, port Prime's
   paper/ink palette (variables only: `--bg:#f3efe3; --panel:#fffdf7; --text:#1c2230; --gold:#8f5e12 …`) as a "Paper" theme in Settings.
10. **Dismissable banner** "This copy of OMEGA started empty…" shows on every load until "Got it"; fine, but it pushes the
    first decision further down — show it once per device.

## 6. Navigation summary

| | Prime before | Prime after | Original |
|---|---|---|---|
| Taps to the day's orders (phone) | 0 taps, but ~2.5 screens of scrolling | 0 taps, first screen under the verdict | no tickets; panic watch: More → Edge Lab (2 taps + scroll) |
| Starting page | Today, always | Today, always | last page used |
| Android back | leaves the app | previous page | leaves the app |
| Pages | 5 | 5 | 28 |
