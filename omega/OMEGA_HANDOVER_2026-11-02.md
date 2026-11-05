# OMEGA — full handover (2 Nov 2026)
Read this first. It replaces OMEGA_CARRYOVER_2026-10-25.md; the older OMEGA_HANDOVER_2026-10-20.md (in `older/`) keeps the
history before 25 Oct. Every number below was measured; anything not verified is marked.

## 1. Who and what
- **Maro**, Scarborough, Tobago. Builds single-file HTML PWAs, works on Android Chrome and a Windows PC. Claude is lead developer.
- **OMEGA:** a trading research and decision system. **It finds no trades by itself beyond the rules that passed fair tests,**
  and the research below explains why signals are rare.
- **Account in mind:** 100 USDT, small risk per trade.

## 2. What exists (all in this bundle)
| Piece | File | Version / state | Checks |
|---|---|---|---|
| **Original OMEGA** (Maro's version) | `apps/omega-v6_5-47.html` (always this name) | **v6.5.105**, build 2026-11-02 21:50 UTC | full run on this build: 35 of 39 suites pass in full, s77 26/27; 28-page crawl 0 errors |
| **OMEGA Prime** (Claude's lean version) | `apps/omega-prime.html` | panic watch + trade tickets + full Evidence | 10 + 17 + 14 checks pass |
| **OMEGA Recorder** (FastAPI market recorder) | `recorder/` | 1.0.1 | 14 tests |
| **OMEGA Bridge** (Exness MT5 + Binance futures control, Windows) | `bridge/OMEGA-Bridge-1.1.zip` | 1.1 | 12 tests |
**None of these has been run on a real phone, against the live Binance API, or against a real MT5 terminal** (Claude's sandbox
cannot reach them). First real runs: on Maro's devices, demo/testnet, watching.

### 2a. Original OMEGA, v6.5.98 → v6.5.105 (patches in `kits/original/`, each `python3 patchNNN.py <prev> <new>`)
- **98** Panic-bounce watch (E22 H1/H3, grade B) under the climax card on Signals, Edge Lab, Watch; Autopilot job `panic`;
  stored as `omega_panic_v1`; same code as Prime's watch (trade-for-trade parity with the research engine).
- **99** E26's result in the panic card (keep it on paper).
- **100** "Why signals are rare" research card (Signals, Edge Lab).
- **101** Market Watch recorder: spot-stream address rotation, backup from 1-minute candles when streams are dead (never
  overwrites stream data), `diag` in every export (feeds, errors, backup hours), a card notice. Reason: the 19–26 Oct export
  held 0 minute rows (live streams delivered nothing on that device).
- **102** CREED reality check at the top of the CREED desk (coin-flip chart, measured results). **CREED's engine is
  byte-identical** (checked by s102). E28 count corrected to 12,480 with round 5.
- **103–105** Research card rows for E33, E34, E35, E36.
- Test suites `s49…s105` (39 current) in `kits/original/`; harness tools in `kits/original/tools/`; run them with
  `HARNESS=<kit>/tools node sNN_test.js <build>` (s102 also takes `PREV=<older build>` to prove CREED's engine unchanged).
  Full run on v6.5.105 (2 Nov): 35 pass in full. **s67, s69, s79 and one s77 check need
  research files missing since the 25 Oct bundle:** `watch16.py`, `partB_fresh.json`, `round12_final.json`, `round17.json`.
- **Maro's Twelve Data key is inside the HTML** (installed on request earlier; backups exclude it). Anyone sent the file gets it.
- The charts library loads from a CDN; offline, Analysis/Simulation/Growth charts do not draw (the app says so).

### 2b. OMEGA Prime
- **Today:** verdict (risk stop > event hold > grade A climax > grade B panic bounce > grade C Daily Plan > stand aside), then
  **"Your orders":** trade tickets for live signals of tested rules only — Binance USDT-M futures, 1× isolated, exact price,
  size (default 5 USDT), cancel time, sell time; SELL NOW first; "I placed it"/"Skip"; exit notifications; scoreboards (paper
  and placed). CREED and the Daily Plan never get tickets.
- **Signals:** climax (A), panic bounce H1/H3 (B) with a breadth gauge and forward record, Daily Plan (C).
- **Evidence:** every test with its result (ledger complete through E36).
- Built by `kits/prime/prime/patch_prime_panic.py` from the 25 Oct Prime (`omega-prime.html`, md5 85d94f81…): adds
  `prime_panic.js`, `prime_tickets.js`, and the changed `prime_post.js`/`prime_shell.html`. Storage under `prime:`.

### 2c. OMEGA Bridge 1.1 (Windows, Python)
- Controls **Exness via MT5** (official MetaTrader5 package; finds suffixed symbols like XAUUSDm; sizes by lots or by money at
  risk) and **Binance USDT-M futures** (signed REST; exchange rounding; stop and target as close-only orders).
- **Guard on every order:** demo/testnet until `live: true` per venue; a stop required; risk ≤ 1 USD, Binance size ≤ 10 USD, ≤ 3
  open positions per venue, daily loss limit 5 USD; kill switch (`KILL_and_close_all.bat` or a `KILL` file); preview first,
  `confirm=true` to send; every attempt logged. **Secrets only in the Windows Credential Manager**; config refuses secrets.
- Claude Desktop connector (MCP: status, price, positions, preview_order, place_order, close_position, kill_switch,
  order_log, funding_monitor). Funding monitor = information only (E34 failed).
- README inside the zip: setup in ~15 minutes. Binance key: futures trading only, **never withdrawals**.

### 2d. OMEGA Recorder 1.0.1 (FastAPI + SQLite)
Records Binance perpetuals (candles, funding, OI, ratios, liquidations, book summaries), backfills from data.binance.vision incl.
delisted coins, serves /health, /panic, /signals (H1/H3 forward paper record), exports in the research format. Volume-0 candles
treated as missing. Best on a small always-on server (Europe/Asia region; Binance blocks US addresses).

## 3. What the evidence says (every test planned and fingerprinted before its data, run once)
**PASSED**
- **Climax reversal (grade A):** 3σ hourly drop, 3× volume, close in the top 40%; buy next open, hold 12 h. Passed on 324 untouched coins.
- **Panic bounce H1/H3 (grade B):** E22 (+0.36%/trade H1, t 4.34; H3 +0.22%, t 3.63) and **E25 survivorship** with 143 delisted
  coins (883 coins): H1 +0.32% (t 4.54), H3 +0.30% (t 4.08). E25's data check against final4: exact (median and 99.9th pct 0).
  Caveats: lives on the big rebounds (without the best 5% each loses ~0.7%/trade); single trades lost 77–93%.
**FAILED (with the reason)**
- **E26** H1 as a 100 USDT account (5/10 USDT seats, −10% stop): drawdowns 56%/59%, 4 of 6 years; 2021 made most of it.
- **E28** daily-trading search, **12,480 rules** in 5 rounds (cross-sectional, composites, executable portfolios, limit entries,
  BTC/ETH timing): small-coin and funding-carry effects were 2021–22 phenomena; daily direction never pays costs; validation 2024 failed.
- **CREED** (E29, E31): after a setup price moves like a fair coin (+1R before stop 49% vs 50%); −0.118R, −0.100R, −0.118R a trade
  on three coin sets (~11,000 setups); longs-only, BTC-context, panic-gated and volatility-buffer variants all failed on untouched coins.
- **E30** real liquidity: order-book depth (13,690 coin-days) predicts neither direction nor useful size; crowd positioning failed;
  **E33** forced deleveraging on 60 untouched coins: −0.03%/trade (t −0.10).
- **E32** neural network on 33 daily measures: final −0.10%/day, within luck's range.
- **E34** funding harvest (delta-neutral): 2021–24 +8.8%/yr; 2025–26 −17%/yr (one flip: −64.6% in a month).
- **E35** new-listing fade: +2.5%/trade in 2025–26 but t 1.02, 2026 negative, worst −76%. **E36** pairs: −2.1%/yr.
- **E15** forex majors hour by hour: all five fail. **E13** Market Watch: not run (0 minute rows; see 101). E3/E14 and earlier: in the old handover.
**Monte Carlo (100,000 accounts, real weekly history):** CREED at 1% risk loses half in 76% of accounts in a year; no strategy
reached 1,000,000 from 100 in 5 years; H1's 2022–26 account path was slightly worse than holding BTC.
**Main lessons:** size is predictable, direction is not; panic selling gets overdone (the only durable edge found); "small win
every day" strategies (grids, funding harvest, high-win-rate bots) carry rare blow-ups; plan first, count every try, check luck.
Full numbers: `research/plans-new/E28_LOG.md`, `research/plans-new/E29_E32_RESULTS.md` (E29–E36), `research/plans-new/*_result.json`.

## 4. Standing rules
1. **Never fabricate data;** say what is verified and what is not ("not run on a real phone").
2. **Plan before data:** write it, fingerprint it (md5), run once, count every attempt, report true results with costs.
3. **Paper first.** OMEGA itself places no orders. The Bridge can, but demo/testnet by default; live is Maro's switch.
4. **No secrets** in files, backups or chats; no phone number anywhere (guard `kits/original/tools/nophone.js`, hashes only).
5. **The original is always delivered as `omega-v6_5-47.html`.** CREED's method stays byte-identical unless Maro asks.
6. **Other AIs' reports are views to verify, not to follow.**
7. **Design:** grounded in the subject, real visuals, an obvious starting point; not the generic dark-dashboard shell.

## 5. Claude's environment (as of 2 Nov 2026)
- Reachable: data.binance.vision, its S3 listing (s3-ap-northeast-1.amazonaws.com), github, pypi. **Refused:** fapi.binance.com
  (451), bls.gov (403); stream hosts unreachable.
- **Background processes end when a turn ends:** run jobs in the foreground with checkpoints, one per turn if long.
- 1 CPU, 4 GB: one heavy job at a time.
- **The sandbox resets between chats:** the archive data (~1 GB) must be downloaded again. Scripts expect the working folder
  `/home/claude/e25` (copy them there): `research/e25kit/listsyms.py` → `dl.py` (2023-10 → 2026-10 hourly) → `build.py`;
  `dl_old.py` (2020-11 → 2023-09) → `build_old.py` (joins both into `hourly_e26.pkl`); `e28/build_daily.py` (daily panel),
  `e28/dl_fund.py` → `e28/build_funding.py` (funding); liquidity: `e29_e32/dl_liq.py` (depth, metrics; folder `/home/claude/liq`),
  `e29_e32/dl33.py` (OI for 60 coins). About 30–40 minutes of downloads in total; run them in the foreground.
- **Connectors:** Text to Quant connected (each call needs Maro's approval in the app); Interactive Brokers added but sign-in
  incomplete; Webull not installed. **No Exness, MT5, Binance, Bybit, OANDA or TradingView connector exists** in the directory.

## 6. Open items and next steps (in order)
1. **Forward record of the tickets:** install Bridge 1.1 (Exness demo + Binance testnet), keep Prime open on the PC, place each
   ticket on testnet, tap "I placed it". **50 closed tickets** decide whether H1/H3 holds in today's market.
2. **Market Watch on the device:** install v6.5.105, start recording, screenshot the three feed pills; E13 needs 5 days with
   live streams (a PC that stays awake is surest). Addendum B (backup minutes) is already written.
3. **Missing research files** (four, above) to run the last 4 suites.
4. Optional: the recorder on a small server for 24/7 records; E27 (CPI) needs the BLS release-date page from Maro.
5. Ideas not yet tested: on-chain flows, options data (new data sources, not more passes over the same candles).

## 7. Bundle contents
`apps/` both apps · `bridge/` Bridge 1.1 zip · `recorder/` · `kits/original/` patches 98–105, modules, tests s49–s105, tools,
fixtures, change notes · `kits/prime/` Prime kit (build, modules, tests, parity data) · `research/` plans and results
(plans-new), scripts (e25kit), the 25 Oct research archive · `older/` the 20 Oct handover, the 25 Oct carry-over and all
update notes 25 Oct → 2 Nov.

## 8. Paste this to start the next chat
> I'm continuing OMEGA. I've uploaded the handover bundle. Read `OMEGA_HANDOVER_2026-11-02.md` first. Current: original
> v6.5.105, Prime with tickets, Bridge 1.1. Next: [the item from section 6 you want].
