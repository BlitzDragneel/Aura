# OMEGA handover — 20 Oct 2026 (build v6.5.84)

This updates the 19 Oct handover (build v6.5.82), which is attached unchanged at the end for history. **Where they
conflict, this part wins.**

**Upload to the next chat:**
- this file;
- `OMEGA_RESEARCH_COMPLETE_2026-10-19.md` and `OMEGA_PRD_2026-10-19.md`. Both are still valid; rounds 19–20 are in section 4 below;
- `omega-v6_5-47.html` (the app, now v6.5.84);
- `omega-buildkit-2026-10-20.tar.gz` (module sources, patches, tests, fixtures; extract to `/home/claude/omega48`);
- `omega-research-edge-2026-10-20.tar.gz` (the 19–20 Oct research code, plans E1 and E2, results; extract to `/home/claude/edge`);
- `omega-research-2026-10-19b.tar.gz` (rounds 1–18; extract to `/home/claude/research`);
- when research needs them, the data files from the phone (section 7), plus **the gold file** (`omega-history-gold1h-*.json.gz`) once downloaded.

The full research narrative for 19–20 Oct is in the Claude Doc "OMEGA edge research, 19–20 Oct 2026", in her claude.ai artifacts.

---

## 0. Update, 20 Oct evening: plan E2 done — both methods FAILED on gold
- **File:** `omega-history-gold1h-2026-10-20.json.gz`, sha256 `743289eb44a674bba4611da47116731e103d6e336e339e3d03a568d21f877d2f`.
  - XAU/USD only: 40,000 hours, 2020-07-15 → 2026-10-20, 0 candles corrected or dropped.
  - Marked incomplete; silver not downloaded.
- **Addendum A** (md5 `3d83c638db0a07f464c8af6f93c875e6`, written before the run): E2 runs once on this file. Older gold downloaded later cannot rerun or overturn it.
- **Result** (`plans/E2_result.json`, md5 `23404d1d52da7c19a1d04176f7c1a4ba`), 100 USDT, true 1%, 0.05% a side:
  - **M1, 5-unit method:** 100 → 47.4; worst fall 53%; 424 trades; 0 of 7 years positive; beat 88.0% of 200 coin flips. **FAIL.**
  - **M2, new method:** 100 → 74.3; worst fall 30%; 371 trades; 2 of 7 years positive; beat 89.5%. **FAIL.**
  - At 0.10% a side: 20.0 and 48.4.
- **Holding gold** over the same window gained +128% (1,807 → 4,125).
- **App:** not yet recorded. In v6.5.85, add round 21 to the research record and replace the Breakout Desk's "Next clean test" gold card with the result. Step 2 of section 8 is done.

## 0b. Update, 20 Oct late: plan E3 failed; plan E4 waiting for data
- **Plan E3** (md5 `6713849dcf77ed55b23a7fc4107b9586`, `plans/e3_run.py`, `E3_result_gold.json`): three ideas on the same gold file, all **FAILED**.
  - H1 overnight drift: t 1.08 at 0.02% a side, needed 2.13.
  - H2 forced-selling rebound: only 4 events.
  - H3 weekend gap fade: about 0.
- **Descriptive split on gold:** before costs, holding outside US hours made +103% (log), holding during 13:00–20:00 UTC made −21%. Holding all the time made +82%.
- **Plan E4** (md5 `0f11ee8e135340aa745c831482f4b5c0`) tests that split once on untouched data:
  - silver hourly (XAG/USD), and gold before 2020-07-15;
  - test A: the weekly (outside − US-hours) difference, t ≥ 1.65 and positive in half the years;
  - test B: long outside US hours at 0.005% a side.
- **Data needed:** she presses "Download gold & silver hourly" again (it continues gold back from July 2020, then fetches silver), then "Save file". Record the sha256 first and run each set once.
- **Script:** `plans/e4_run.py` is not yet written; write it from the plan before opening the file.

## 0c. Update, 20 Oct night: v6.5.85, Market Profiles; plan E5 found no strategy; plan E6 records the session split
- **Current build: v6.5.85** (see `OMEGA_v6_5_85_CHANGES.md`).
  - New page Market Profiles (`OMEGA_MPROF`): gold, DOGE, LINK, LTC, ADA, AVAX, each with live data, a 24-hour clock, behaviour, drivers, how to trade and size it, what was tested, and the E6 forward record.
  - The Breakout Desk gold card now serves plan E4.
  - Research record rounds 21–23.
  - All 19 suites pass; 26-page crawl clean.
- **Plan E5** (md5 `1e94469c…`, `dossier.py` → `plans/E5_dossiers.json`): seven rules per market, chosen on 2020–23 and judged once on 2024–26. **No market passed.**
  - **Common to all six**, before costs, on data already used: gains outside US hours, a drift down during 13:00–21:00 UTC.
  - Examples: AVAX's US session −62%/yr (0 of 7 years up); ADA's Asia session +34%/yr (6 of 7); gold's late session up 7 of 7 years.
- **Plan E6** (md5 `893c6251…`): the app records each day's outside and US-hours returns for the six markets from 21 Oct 2026; judged once after 26 weeks (on or after 21 Apr 2027).
  - Confirmed per market at t ≥ 1.65; overall, pooled, at t ≥ 2.0.
  - A timing fact, not a trading rule.
- **Waiting on her:** the plan E4 file (Download again on the Breakout Desk gold card: older gold, then silver).
- **Kit:** `mprof_src.js`, `mprof.js`, `goldh85.js`, `patch85.py`, `s85_test.js`, `fixtures/E5_dossiers.json`. `tools/crawl.js` now covers 26 pages.

## 0d. Update, 20 Oct late night: v6.5.86 — both directions; plan E7: no short-only rule passed
- **Current build: v6.5.86** (`OMEGA_v6_5_86_CHANGES.md`). Each Market Profile has a "Both directions" section.
- **Plan E7** (md5 `4601481e…`; `anatomy.py` → `plans/E7_anatomy.json`; kit fixture `fixtures/E7_anatomy.json`):
  - **Short-only rules failed on all six markets:** blow-off, failed breakout, downtrend US hours, breakdown in a downtrend.
  - **Long against short:** the short sides of plan E5's two-sided rules were no better than the long sides.
  - **Movement is close to symmetric:** about half the hours up; the average up hour equals the average down hour.
  - **Sharp hours by market:** DOGE's are spikes up (best 24 hours +960%, Jan 2021); LTC's, LINK's and gold's are drops.
  - **Swings of 10%+:** typical falls −16% to −18%, typical rallies +20% to +23%.
  - **Shared crash:** LINK, LTC, ADA and DOGE all had their worst hour together, 2021-05-19 12:00 UTC.
  - **Timing:** 44–57% of big hours, both directions, come in US hours.
- **The user asked why only buys were studied.** Shorts were in most tests from the start. E7 made the short side explicit.
- **Next:**
  - the plan E4 file (silver and older gold);
  - BTC, ETH, SOL, BNB and XRP: their 15-minute file (`creed15_1`) is on her side; with it they can get profiles too.

## 0e. Update, 20 Oct midnight: v6.5.87 — the Autopilot runs everything
- **What was found:** the climax watch, Market Watch, Breakout Desk, gold download and Market Profiles' record ran on their own timers, outside the Operator.
- **Fix:** `autocov.js` (`OMEGA_AUTOCOV`) registers them as Operator jobs: `climax`, `bdesk`, `mprof`, `mwatch` (live lane) and `goldh` (heavy lane).
  - 35 jobs in total.
  - Shown in the Autopilot page's job table, each with its own on/off switch.
  - s87 tests it; all 21 suites pass.
- **For her:**
  - Brain automation on, screen kept on, phone on a charger;
  - Chrome excluded from battery saving;
  - one OMEGA tab only;
  - the app works only while open.

## 0f. Update, 21 Oct: plans E8–E10, market states (no app change)
- **Plan E8** (md5 `382ef5d2…`, `states.py` → `plans/E8_states.json`): four market states from the 20-major index, and one rule each. **None passed.**
  - **No state predicts the next week reliably.** Booms kept going in 2020–21 but not since.
  - **Closest, D1 capitulation bounce:** depressed and −10% in 3 days → buy the 5 hardest-hit coins for 3 days. +16%/yr (t 1.23) on 2020–23, +32%/yr (t 2.05) on 2024–26.
- **Plan E9** (md5 `9a88b776…`, `e9_run.py`): D1 unchanged on the 324 perpetuals. **FAILED** (−53.5%, t −0.24): it bought LUNA twice in May 2022.
- **Plan E10** (md5 `dd6b6bcc…`): in a capitulation, buy BTC, ETH, SOL, BNB and XRP equally for 3 days.
  - Runs once on `omega_history_creed15_1` when she uploads it.
  - The export button was removed in an earlier build; the file should be in her Downloads from 19 Oct.
- **Market state on 2026-10-18:** CORRECTING (20-major index 7-day −9.3%, above its 200-day average).

## 0g. Update, 21 Oct: v6.5.88 — Research files card; plan E10 data source
- **The missing file:** she could not find `creed15_1`, and its export no longer exists in the app.
- **PLAN_E10_addendum_A** (md5 `81652285…`, written before any data): E10 now uses daily closes from the app's wide data store.
- **New card on the Breakout Desk:** "Research files to send (plan E10)". It fetches any missing coins, then saves `omega-history-daily25-*.json.gz` (the 25 studied coins, daily, from Jan 2020).
- **When the file arrives:**
  - record its sha256;
  - run E10 once on BTC, ETH, SOL, BNB and XRP: E8's state definition from these five coins' own index, then the rule and pass mark as written.
- **Kit:** `rdl.js`, `patch88.py`, `s88_test.js`. All 22 suites pass.

## 0h. Update, 21 Oct: plan E4's data changed (addendum B)
- **Second gold file:** sha256 `fd5f3984…`, 42,811 hours from 2020-01-24, complete. Twelve Data's hourly gold starts there.
- **Silver:** not on Twelve Data's free plan.
- **PLAN_E4_addendum_B** (md5 in `plans/`):
  - S2, gold before July 2020, is dropped: about 25 weeks, under the 2-year minimum. Not run and not looked at.
  - S1, silver, becomes Binance's XAGUSDT perpetual, hourly from 7 Jan 2026, from Settings → "Export price history for research".
  - About 41 weeks, so low power.
- **Waiting on her, two files:**
  - the research export (silver, for E4);
  - `omega-history-daily25-*` (for E10; v6.5.88 Breakout Desk card).

## 0i. Update, 21 Oct: plan E10 FAILED; another session's simulation checked
- **The original file arrived:** `omega_history_creed15_1` (sha256 `5e9fa47e…`; BTC, ETH, SOL, BNB, XRP; 15-minute).
  - PLAN_E10_addendum_B (md5 `12a77dea…`, written before reading it) runs E10 on this original source.
  - Addendum A (the app's daily file) is not used.
- **E10 result** (`e10_run.py` → `plans/E10_result.json`): **FAIL.**
  - 23 trades, 14 winners, average +0.54% a trade.
  - Total +7.3%, weekly t 0.28.
  - Before 2024 −6.2%; from 2024 +14.5%.
  - May 2022 (Terra) lost −12.8% and −15.1% even on the biggest coins.
- **The capitulation family is closed:**
  - E8 D1 (t 2.05, short of 2.40);
  - E9 on the 324 perpetuals (fail, LUNA);
  - E10 on the top 5 (fail).
  - The hourly climax reversal (a coin-level flush that closes strong) stays the only direction rule that passed.
- **Another session's files** (LIVE_ACCOUNT_SIMULATION_REPORT.md, COST_MODEL_CORRECTION.md, account_*.csv), checked:
  - their report's figures recompute exactly from their ledger;
  - their cost correction concerns their own `omega_pyramid_combos.py`; this session's engines charge 0.10% on every fill, as labelled;
  - their climax trades are on 58 coins from the earlier development set (2020 on), none in the 324-perpetual exports, so they match none of this session's 756 signals;
  - their conclusion, nothing promoted to live, agrees with this session's.
- **Note:** the `omega-v6_5-47.html` she uploaded is v6.5.75 (an old copy). The latest is v6.5.88.

## 0j. Update, 21 Oct: plans E11 and E12 (BTC/ETH); another AI's 'Edge Discovery Lab' proposal reviewed
- **The proposal** (pasted by her, from another AI) maps onto OMEGA as follows.
  - **Already done:** strategy competition, adversarial tests, untouched data and counting every try (sweeps, nulls, plans E1–E12); regime detection (E8: no state predicts); edge decay (forward records with retirement rules).
  - **Needs the Market Watch export:** Market X-ray, liquidations and cross-exchange.
- **E11 absorption** (md5 `3eb4fbcb…`): **FAIL.**
  - Gross effect about +0.04% per 4 h trade, in the right direction, below the 0.10% round trip.
  - After costs −0.057% a trade, weekly t −1.71, negative in both periods and on both coins.
- **E12 stop-outs** (md5 `9e08a3f3…`):
  - After a stop-out, price reached +1R the trade's way within 24 h in 39% (obvious stops) and 37% (fixed 1.5 ATR) of cases. On shuffled prices: 45% and 44%. Mostly noise; real markets continue past stops slightly more than chance.
  - **Hunt effect, obvious against fixed:** +0.92 points, 95% CI +0.14 to +1.72. Real, but about 1 case in 100 stop-outs.
  - About 70% of 0.5–3 ATR stops are hit within 48 h of a random entry.
- **Script:** `e11_e12.py` → `plans/E11_E12_result.json`.

## 0k. Update, 21 Oct: first Market Watch export, too short to test (no plan spent)
- **File:** `omega-watch-2026-10-14-to-2026-10-21.json.gz`, sha256 `53d25589…`. Decoder: `edge/mwload.py` (Float32 little-endian, 60 × fields per hour).
- **Coverage:**
  - live minute data 47 of 10,080 minutes (0.5%), in two sessions: 19 Oct 20–22 UTC and 21 Oct 01 UTC;
  - 56 liquidations over all 25 coins; 4 book snapshots per coin; 0 events;
  - open interest and long/short ratios at 5 min, 18 Oct 02:45 → 21 Oct 01:30.
- **Why so little:** the recorder captures only while OMEGA is open and on screen; phones pause background pages.
- **No E-plan was written or run on it.**
- **Next:** a week with high coverage. The Market Watch page shows "Recorded X hours of the last 24 hours"; aim for close to 24.
  - Best on a PC that doesn't sleep, with the tab visible; or a phone with the screen kept on, on a charger, OMEGA in front.
  - Positioning history (open interest, long/short) fills back 30 days by itself.

## 0l. Update, 21 Oct: plan E13 ready for the first full Market Watch week
- **PLAN_E13_market_watch.md** (md5 `4390a4e4…`), written before any usable recording.
  - **Minimum to run:** 5 days with BTC live in ≥ 80% of minutes; otherwise it is not run.
  - **Q1:** do liquidation flushes rebound when open interest falls?
  - **Q2:** absorption on the futures tape (15 minutes, costs 0.10% round trip).
  - **Q3:** does Coinbase BTC lead Binance (descriptive)?
- **Script:** `plans/e13_run.py <omega-watch file>`.
  - It refused the 47-minute file.
  - On synthetic recordings with planted effects it found all three: Q1 +0.78% against −0.06% (planted +0.8% / −0.1%), t 9.8; Q2 t 7.1; Q3 r 0.99 against 0.17.
  - Synthetic files are not kept.
- **Waiting on:** a week of continuous recording (an always-on computer with OMEGA open).

## 0m. Update, 21 Oct: second Market Watch export; liquidation hypotheses; E13 addendum A
- **Second export:** sha256 `53e73e31…`, 442 live BTC minutes. Unbroken 21 Oct 01:32–08:18 UTC (406 min); 863 liquidations. Too short for E13.
- **Explored that night (hypotheses only):**
  - $4.3M liquidated on 25 coins (shorts $2.66M, longs $1.64M) while BTC moved about 0.6%.
  - Liquidations follow price: across coins, corr(price change, long − short $) = −0.39.
  - Heavy tail: the top 5% of minutes hold 70% of the dollars.
  - Big short-squeeze bursts after quick rises: 2 of 3 dropped within 30 min.
  - BTC open interest +1.15% overnight, so leverage rebuilt fast.
- **PLAN_E13_addendum_A** (md5 `14a3500…`):
  - excludes 21 Oct 01:00–08:59 UTC;
  - allows several exports to be merged (5 qualifying days, not necessarily consecutive);
  - adds Q4, short-squeeze exhaustion (the mirror of Q1);
  - adds Q5, thin hours against busy hours (descriptive).
- **`plans/e13_run.py`** takes several files.
  - Verified on a synthetic recording with long flushes and short squeezes: both found (t 6.4 and 15.3), and refused at n < 30 as designed.
  - Refuses her two real exports merged (36 usable BTC minutes).
  - Previous version kept as `e13_run_v1.py`.

## 0n. Update, 21 Oct: v6.5.89 — Market Read, Brain and Autopilot upgrades (current build)
- **Market Read** (`OMEGA_MREAD`, `mread.js`) covers 11 markets, with:
  - liquidity levels (week/day/72h/24h extremes, equal highs and lows, round numbers), order-book depth and walls, and crowding (funding, OI change, long/short);
  - an honest read and a liquidity ladder;
  - level memory: hourly pools, scored a day later for whether price reached them.
- **Autopilot jobs `mread` and `mwdays`** (full Market Watch days, with an export reminder).
- **The gold download** stops on silver's paid-plan answer.
- **The Brain:** `KN.earlier` gains E1–E13 (39 studies), 6 new lessons (20) and 3 new Mind lessons. Research record rounds 26–28.
- **Kit:** `mread.js`, `goldh89.js`, `patch89.py`, `s89_test.js`; `tools/crawl.js` now covers 27 pages. All 23 suites pass; crawl clean.
- **Next session:**
  - run plan E13 when 5 full Market Watch days have arrived (`plans/e13_run.py`, merges several exports);
  - read Market Read's level-memory hit rates after a few weeks (forward, self-measured);
  - judge E6 and the forward records after 26 weeks (mid-April 2027).

## 0o. Update, 22 Oct: v6.5.90 (current build)
- **Her report:** the app sticks; no OMEGA signals in about 3 weeks (only CREED).
  - **Sticking:** caused by v6.5.87's `mwatch` job forcing Market Watch full mode on. Fixed: it now respects the switch.
  - **Silence:** by design. OMEGA Signals fires only on Research-Lab conditions rated held-out-of-sample, and none qualify now.
- **Plan E14** (top 5 coins; `dossier_top5.py`, `anatomy_top5.py` → `plans/E14_*.json`): no rule passed on any of the five.
  - US hours carry the most trading. Aggressive buying is 49–50% everywhere.
  - The US-hours drift down (gold, altcoins) does not hold for BTC, ETH or XRP.
  - Now on Market Profiles.
- **Plan E15** (forex majors, md5 `12f0c70f…`): the download was added in v6.5.90. Run it once on her `omega-history-metals-fx1h-*` file.
- **Kit:** `autocov90.js`, `goldh90.js`, `mprof90_src.js`, `mprof90.js`, `patch90.py`, `s90_test.js`, `fixtures/E14_*.json`. All 24 suites pass; crawl clean.

## 0p. Update, 22 Oct: v6.5.91 (current build): Daily Plan; Market Watch back on under the Autopilot (light)
- **She wants** daily, honest signals with long/short awareness, and the Autopilot to run everything.
- **Daily Plan** (`dplan.js`, `OMEGA_DPLAN`):
  - market state from E8's definitions on the top-5 daily index;
  - a side per coin by state and the 200-hour average;
  - entries at Market Read's liquidity pools, stop 0.5 ATR, target the opposite pool, R:R ≥ 1.5;
  - Grade C (unproven);
  - forward record plan E16 (md5 `884bd4e2…`): judge once after 50 trades or 26 weeks, in localStorage `omega_dplan_v1`.
- **Where it shows:** the top of Market Read and of the Analysis page. Autopilot job `dplan`, hourly.
- **`mwatch` job:** switches Market Watch on in LIGHT mode (kline_1m) when off.
- **What has passed fair tests, still only two:** the climax reversal and the funding harvest (income faded).
- **Kit:** `dplan.js`, `autocov91.js`, `patch91.py`, `s91_test.js`. All 25 suites pass; crawl clean.

## 0q. Update, 22 Oct: v6.5.92 (current build): Risk Guard, Growth Bot, automatic exports
- **`rguard.js` (`OMEGA_RGUARD`, page Risk Guard):**
  - rules: 0.5% risk (1% after 30 clean), 2 open, −2% day, −5% week, review at −20%;
  - Growth Bot, plan E17 (md5 `27f13c9a…`): takes new climax (A) and Daily Plan (C) trades, reads their records only, localStorage `omega_rguard_bot_v1`;
  - pre-trade check and journal (`omega_rguard_mine_v1`);
  - automatic exports (`omega_rguard_exports_v1`).
- **Autopilot jobs:** `rguard` (15 min) and `autoexp` (2 h). All 26 suites pass; the 28-page crawl is clean.
- **She asked for these; plan for the next session (Claude decides the order):**
  1. **Analysis page and charts overhaul, a "Market Cockpit" per coin:**
     - candlesticks (1 h / 15 m), with volume bars coloured by aggressive buying;
     - Market Read's liquidity levels on the price axis, labels de-conflicted;
     - the order-book depth profile at the right edge;
     - the Daily Plan setup as shaded entry/stop/target zones;
     - session shading;
     - a strip with funding, open-interest change, long/short ratio, ATR and range against a typical day;
     - tidy the existing setup cards, one clean card per setup, grounded visuals, an obvious start;
     - check that the Autopilot drives every Analysis job.
  2. **An event calendar** (CPI, FOMC) in Market now.
  3. **A monthly review page:** what earned, what failed, what was retired.
  4. **Run plans when their files or milestones arrive:** E13 (5 full Market Watch days), E15 (forex file), E16 (50 Daily Plan trades), E17 (50 bot trades or 26 weeks).

## 0r. Update, 22 Oct: v6.5.93 (current build): Market Cockpit on the Analysis page
- **`cockpit.js` (`OMEGA_COCKPIT`):** one clean chart per coin, with:
  - candles and US-hours shading;
  - volume split by aggressive side;
  - liquidity levels with labels kept apart;
  - an order-book column;
  - the Daily Plan's position box;
  - a strip of ten figures and one setup card.
- **Autopilot job:** `cockpit`, hourly.
- **Watches the Analysis page directly,** because core pages don't run the extra-page navigation hook.
- All 27 suites pass; the 28-page crawl is clean.
- **Still planned:**
  - tidy the older setup cards further down the Analysis page;
  - an event calendar (CPI, FOMC) in Market now;
  - a monthly review page;
  - run E13, E15, E16 and E17 at their milestones.

## 0s. Update, 22 Oct: v6.5.94 (current build): Events ahead and the Monthly review
- **`review.js` (`OMEGA_REVIEW`):**
  - next CPI and FOMC from `OMEGA_MARKETCLOCK.DATA` (official dates, v6.5.79);
  - event-risk window from 2 h before to 1 h after, as advice in Market now and the pre-trade check (`rguard94.js`); the bot is unchanged;
  - the monthly review on the Risk Guard page.
- **Written in an interrupted attempt,** then reviewed and tested before release.
- **Checks:** all 28 suites pass (s93, s89 and s87 need a 130 s timeout); the 28-page crawl is clean.
- **Next fixed dates:** Fed 28 Oct 2026 18:00 UTC; CPI 10 Nov 2026 13:30 UTC.
- **Still planned:**
  - tidy the older setup cards lower on the Analysis page;
  - run E13, E15, E16 and E17 at their milestones.

## 0t. Update, 22 Oct: v6.5.95 (current build): tidier Analysis scanner
- **Unread markets** fold into one compact card; markets with a reading come first. Data cards are unchanged.
- **Checks:** all 29 suites pass (s93, s89 and s87 need a 130 s timeout); the 28-page crawl is clean.
- **Build work planned in this session is complete.**
- **What remains is evidence, at its milestones:**
  - E13: 5 full Market Watch days, exported automatically;
  - E15: the forex file, saved automatically when the download completes;
  - E16: 50 Daily Plan trades;
  - E17: 50 bot trades or 26 weeks;
  - E6 and the forward records: mid-April 2027.
- **Possible later polish, data cards only:** compact the scanner's cards with data once she has seen them full of real readings on her phone.

## 0u. Update, 25 Oct: v6.5.96 (current build): data check, baseline, fill stress
- **Competitor audit (pasted, another AI):** reviewed without browsing (no web access here).
  - **Taken:** baseline, fill stress, data checks.
  - **Not taken:** a unified engine refactor; AI ranking.
- **`truth.js` (`OMEGA_TRUTH`):**
  - job freshness for all Autopilot jobs;
  - per-market candle age (over 2 h is stale) and futures-mark-to-spot-index gap (over 0.5% is flagged);
  - Growth Bot against holding BTC (`omega_truth_v1` keeps t0, btc0, eq0);
  - fill stress at +0.05% and +0.15% a side, using the new `nt` field on bot trades.
  - Autopilot job `truth`, every 30 min.
- **Checks:** all 30 suites pass; the 28-page crawl is clean.
- **She reports some data is not live or correct, but which data is not known.**
  - Next session: ask for a screenshot of the Data check card and of any value she believes is wrong.
  - Then trace that value's source in code and fix it there.

## 0v. Update, 25 Oct: OMEGA Prime, Claude's own version, delivered next to the unchanged v6.5.96
- **What:** `omega-prime.html`, source in `/home/claude/prime` (packed as `omega-prime-kit-2026-10-25.tar.gz`).
- **Pages:** Today (verdict first), Chart, Signals (climax Grade A on the top-40 perpetuals; Daily Plan Grade C), Risk, Evidence.
- **Storage:** everything under `prime:`, so it is separate from the original build.
- **Built** from six modules of v6.5.96, plus its own core, design and Autopilot.
- **Accuracy bug found:** the data check skips failed reads (`if(!A || A.err) return`).
  - Fixed in Prime.
  - NOT fixed in v6.5.96, which she asked to keep. Offer the one-line port.
- **Checks:** `s_prime_test.js`, 10 checks pass. v6.5.96 is unchanged; all 30 of its suites passed earlier.

## 0w. Update, 25 Oct: v6.5.97 (her build): the data-check fix ported; both apps compared
- **`patch97.py`:** a failed read is now a problem in the data check, as in Prime.
  - All 31 suites pass; the crawl is clean.
  - Slow suites: s93, s89 and s87 need 130 s, s92 90 s, s70 60 s.
- **Measured, original against Prime:**
  - size 4,403 KB against 137 KB;
  - load 530 ms against 70 ms;
  - requests in 30 s, 484 against 77;
  - heap 30 MB against 2 MB;
  - pages 28 against 5; Autopilot jobs 42 against 6.

## 0x. Update, 25 Oct: the path simulator. Plans E18 and E19 both FAILED, but its range and crash parts held twice
- **What it is:** filtered historical simulation.
  - EWMA volatility (λ 0.94) and hour-of-day factors.
  - A shock library of real (close, high, low) hours scaled by volatility; direction neutral.
  - Scripts `e18_run.py` and `e19_run.py`; numba; 50M+ paths in about 1–2 min.
- **E18** (md5 `1d0b2050…`; top 5 coins; calibration 2020–23, test 2024–26), 50/90/99 coverage 54.2/89.3/99.1, tails 0.94%. Fail on:
  - the 50% band;
  - touch ECE (about 3 pts high);
  - Brier skill ≈ 0 against the base rate.
  - A normal model with constant volatility scored 78.6/97.2/99.4.
- **E19** (md5 `9cb6eb9a…`; 20 unseen majors; mean-reverting variance with persistence 0.99; quarterly 2-year library):
  - coverage 54.0/90.6/98.8, tails 1.19%;
  - upside touches over-predicted by 3–5 pts (the altcoins fell in 2024–26);
  - FAIL.
- **Diagnosis:**
  - the middle is too wide because independent hours ignore the small hour-to-hour snap-back (variance ratio < 1);
  - direction neutrality cannot match trending periods.
- **Next, E20:**
  - block bootstrap (consecutive runs of real hours), so the snap-back is kept;
  - tested once on the 324 perpetuals (final4), never used for the simulator.
- **Usable now** (ranges and crash rate held in both tests): risk ranges, worst cases, account futures.
- **Not usable:** setup odds, which are no better than a constant base rate.

## 0y. Update, 25 Oct: plan E20, Bitcoin as the father coin. FAILED, but informative
- **Plan:** md5 `aa0cb65c…`, `plans/E20_result.json`.
- **W1, BTC below its 200-day average** (alts' next 30 days: on −3.5%, off +2.3%):
  - t 0.99, against 2.0 needed: FAIL;
  - but the alt gate beat holding on Sharpe and max drawdown in both halves;
  - 2020–23: +394% against +137%, drawdown −75% against −89%;
  - 2024–26: −51% against −61%, drawdown −76% against −85%.
- **W2 (BTC 15% off its 90-day high) and W3 (50-day below 200-day)** were weaker.
- **Lead:** corr(BTC today, alts next day) = −0.08; same day 0.81. BTC does not lead at the daily scale.
- **The 2024–26 alt bleed** happened while BTC was above its 200-day average.
  - The next hypothesis is alt strength against BTC (the alt/BTC ratio's trend).
  - BTC peaked at 124,659 on 2025-10-06; it stood at 82,116 on 2026-10-18.
- **Proposed:** an early-warning panel in Prime that shows only tested warnings.
  - W1 qualifies as a risk view (drawdown reduction in both halves), not as a proven edge.

## 0z. Update, 25 Oct: plan E21, the deep inverse scan. 73 rules both ways; 1 candidate; FAILED on 324 other coins
- **Files:** md5 `4c783c20…`; `e21_lib.py`, `e21_scan.py`, `e21_test.py` → `plans/E21_discovery.json`, `E21_test.json`.
- **Discovery** (25 majors, gross): the only consistent losers in both periods are SELL-AFTER-SHARP-FALL rules.
  - Examples: momentum-down shorts, breakdown shorts, 3σ-down shorts; t −3 to −9.
  - So buying after sharp falls wins before costs in both periods, but the edge shrank to about 0.01–0.3% a trade in 2024–26.
  - RSI<30 longs and sweep-of-low longs were positive but tiny after 2024.
  - Breakouts, buying strength, sessions and weekdays have no consistent direction either way.
- **The one candidate:** buy after the 24 h return is in its bottom 10% (720 h lookback), hold 24 h.
  - Gross +0.84% (t 7.0) and +0.32% (t 3.8).
  - Test, 324 perpetuals, 2024–26, net of 0.20%: −0.005% a trade, weekly t 1.40, years −0.05/−0.07/+0.05. FAIL.
- **Lesson:** the market's one robust directional tendency is that panic selling gets overdone.
  - Broadly it is about equal to taker costs.
  - The climax filter (3σ, 3× volume, close in the top 40%) selects the extremes, where the bounce exceeds costs.
- **Next hypothesis (not run):** the same reversal with maker or limit entries (costs about 0.04–0.10%), with realistic fills.
  - A limit fills only if price trades through it. That is the adverse-selection risk.

## 0za. Update, 25 Oct: plan E22. TWO PASSES: the panic bounce pays with limit entries (H1) or market-wide panic (H3)
- **Files:** md5 `690f3809…`; `e22_lib.py`, `e22_dev.py`, `e22_test.py`, `e22_robust.py` → `plans/E22_kept.json`, `E22_test.json`, `E22_robust.json`.
- **Base signal:** the coin's 24 h return in its bottom q of the prior 720 h (daily thresholds); hold 24 h.
- **Discovery** (25 majors): 21 of 22 variants net positive in both periods.
  - Kept: H1 limit k2 W3, H2 q2, H3 q5 breadth ≥ 20%.
- **Test** (324 perps, 2024-01 → 2026-10, net, Bonferroni bar 2.13):
  - **H1, PASS.** Buy limit at C·exp(−2σ_hourly); fills only if a candle in the next 3 h trades below it; exit 24 h after the fill; costs 0.12%.
    - 17,482 trades, +0.361% a trade, t 4.34, years +0.26/+0.06/+0.57%, 53% winners.
  - **H3, PASS.** q5 and at least 20% of coins in their bottom 10% in the same hour; taker 0.20%.
    - +0.219%, t 3.63, years +0.10/+0.09/+0.36%.
  - **H2 (q2, taker), FAIL.** +0.094%, t 1.81.
- **H1 robustness:**
  - with funding (0.03%/day): +0.331%, t 4.23;
  - WITHOUT the best 5% of trades: −0.86% (it depends on big rebounds; take every signal);
  - 66% of coins with 20+ trades positive;
  - daily portfolio at 10% of equity: ×2.09 over 2.8 y, max drawdown −5.5%, Sharpe 2.69, about 10 trades per active day.
- **Caveats:**
  - Survivorship: delisted perps are missing. A check needs the data.binance.vision archive and network access.
  - At 100 USDT the 5 USDT minimum prevents taking every signal.
  - Forward confirmation is still needed.
- **Next:**
  1. survivorship test with delisted coins;
  2. a forward paper record in Prime (grade B: passed a test, unconfirmed);
  3. an account simulation under the 100 USDT constraints (slots, minimum order).

## 0zb. Update, 25 Oct: plans E23 and E24, "Two Seats" (her method: one or two of the right coins). Both FAILED; the lesson is crash risk
- **E23** (md5 `d2a43ced…`; `e23_build.py`, `e23_run.py`).
  - Setup: H1 signals, at most 2 seats, ranked by deeper fall + bigger volume surge + more liquid; seats 25% (primary) or 50%.
  - 324 perps, 2024–26: ranked 100 → 16.0 (worst drawdown −88%) and beats 0% of 500 random-pick accounts (random median 78.8). FAIL.
  - 50% seats: 100 → 0.5.
  - 25 majors (check): ranked 1,727 against random median 1,546 (beats 66%).
- **Exploration** (E23 data): the ranking features raise BOTH the average bounce and the crash share.
  - Deepest-fall quintile: +0.68% mean, but 4.8% of trades lose more than 20%; worst −93% in 24 h.
  - Concentrated seats turn the fat left tail into ruin. Taking all signals diversified it away (×2.09).
- **E24** (md5 `2c917ff5…`; `e24_build.py`; fresh data: perps 2021–23, 27 coins, 898 fills).
  - Setup: 10% seats and a −10% disaster stop.
  - Arm A (rank for the bounce): 100 → 126.2, drawdown −9.2%, beats 96% of random (97.5% needed); 2022 −1.6%. FAIL, narrowly.
  - Arm B (inverse, calmest first): 112.7, beats 19%. FAIL.
- **Conclusion:** the information at the panic says how VIOLENT it is, not which coin will bounce. Concentration mostly adds risk.
- **Next for her account size:** many small seats (as many as the 5 USDT minimum allows) instead of two big ones, with a disaster stop.
  - Test it forward (paper) or on the delisted-coin archive (needs data.binance.vision).

## 1. Standing rules (all still in force; 14–16 added 20 Oct)
1. Never fabricate data. Say what is verified and what is not, including "not run on a real phone".
2. Her phone number is never stored or written anywhere. The guard `tools/nophone.js` holds only hashes; run it on every build and package.
3. Exports and backups never contain API keys.
4. The Twelve Data key goes in the FULL build only. It never goes in lite builds, dev tools, research bundles, memory, backups or downloaded files.
5. The council never places or blocks trades.
6. Paper trading only. OMEGA never places orders; it shows orders for her to place herself.
7. Never change her three CREED desk markets automatically.
8. CREED's method stays byte-identical unless she asks. She gave permission on 11 Oct to change it where the data shows improvement; none has shown it.
9. Only trades actually taken count in win/loss.
10. Don't just add features: the point is that it works. Push back honestly and cut what doesn't earn its place.
11. **Always deliver builds as `omega-v6_5-47.html`.**
12. Claude is the overseer. Other AIs' reports, and other Claude sessions' reports, are views to verify, not to follow.
13. She gives full autonomy and wants honest pushback.
14. **Plan before data, once.** Every new test is written down with its pass mark and fingerprinted (md5) before its data is read. It is run once. No rule, cost or period changes after seeing a result; a changed rule is a new rule and needs new data. Every try is counted.
15. **Count by week, not by trade.** Trades in the same week share the market's move. Trade-level t-statistics overstated a "pass" (t 3.0) that was t 0.55 by week.
16. **Account-realistic and true risk, both reported.** One market at a time, as she trades. Binance's 5 USDT minimum order silently raises risk on small accounts, so always report a true fixed-risk result next to the minimum-order result.

---

## 2. Where things stand (20 Oct 2026, v6.5.84)
- **Still the only things that passed tests fixed in advance:**
  - **the funding harvest:** its income has collapsed since 2025;
  - **the climax reversal:** the only direction rule; on paper since 19 Oct 12:00 UTC.
- **Breakout Desk (v6.5.83):** setups A (72-hour breakout, US hours, her 5-unit method) and B (momentum burst, US hours, pyramid) were nominated from the 2024–2026 hourly data. Both **FAILED** plan E1 on 2021–2023 (A 100 → 49.1, B 27.2). They are marked failed in v6.5.84 and kept as a forward record only.
- **The new management method** (limit entry 0.5 ATR back, 3 ATR stop, no adding, half off at +1R, 3 ATR trail) made 100 → 125 on the 2025–26 unseen half at a true 1% risk. It **also failed E1** (100 → 71.4).
- **CREED:** the 5-unit method, pyramiding and trailing do not make it positive in either period. CREED is unchanged.
- **Next clean test: plan E2 on gold hourly.** The rules were frozen first. The download is in v6.5.84 (bottom of the Breakout Desk) and the analysis script `plans/e2_run.py` is dry-run tested. Waiting on her file.
- **Hourly crypto history is used up** for new direction rules: the 324-coin set, 2021–2026. New claims need new data (section 8).

---

## 3. Builds since v6.5.82 (both delivered as `omega-v6_5-47.html`)

### v6.5.84 — E1 result, correction, gold download (patch84.py, `bdesk84.js`, `goldh.js`, `OMEGA_GOLDH`), the current build
- **Setups A and B FAILED:**
  - each card shows a FAILED status, a "RECORD ONLY" label and a red box with the E1 numbers and "Do not trade it";
  - the banner, Start-here panel and OMEGA Signals line say the same;
  - no alerts and no menu badge for a failed setup;
  - the paper accounts keep running.
- **Correction:** A's 180.5 came from the 5 USDT minimum rounding 238 of 623 trades above 1% risk. A true 1% gives ×1.08.
- **Gold and silver hourly download** (XAU/USD, XAG/USD; Twelve Data; module `OMEGA_GOLDH`):
  - uses the app's key and shared queue (`OMEGA_TD.acquire('history')`);
  - waits out and retries a per-minute limit; stops cleanly at the daily limit;
  - resumes from IndexedDB `omega_goldh` (pressing Download again continues from the oldest stored hour);
  - checks every candle (drops impossible ones, makes highs and lows consistent);
  - saves `omega-history-gold1h-YYYY-MM-DD.json.gz` in the research format (volume 0);
  - refuses to save if the key or any credential-like field would be in the file.
- **Research record:** round 20; the heading now reads rounds 1–20.
- **Tests:** s84 has 16 checks; s82 and s83 were adjusted (see the change note). All 18 suites pass; crawl clean; phone guard clean.
- **Bugs s84 found and fixed:** progress not shown after a daily-limit stop; a failed setup showed "TOO EARLY" before its first check.

### v6.5.83 — the Breakout Desk (patch83.py, `bdesk.js`, `OMEGA_BDESK`)
- **The page:** "Breakout Desk" (menu under OMEGA Signals, palette entry, badge), with:
  - a Start-here panel;
  - two setups, each with an hourly candle chart and the plan's levels drawn on it (entry, stop, +1R bank 3 and add 1, +2R and +3R adds, the 72-hour line, the live stop, shaded risk and reward);
  - an order table for any account and risk, which warns when the 5 USDT minimum forces more risk;
  - a paper account per setup (100 USDT, 1%, one market at a time, Binance rules, funding read for every hour held).
- **Data:** reads the climax watch's hourly store (`omega_climax`), so there is no second download. Its own state is in `omega_bdesk`.
- **Judging:** from 20 Oct 2026 03:00 UTC; 26 weeks; z ≥ 1.96 to confirm; retired on a weekly average ≤ 0 or a fall of 46% (A) or 56% (B).
- **Parity:** the app's code reproduces `edge/live.py` trade for trade (99 and 60 trades on 40 coins, Jul–Sep 2025), hour by hour with random 1–30 hour gaps between checks.
- **Research record:** round 19, including the CREED result.

---

## 4. Research since the last handover (19–20 Oct; code in `omega-research-edge-2026-10-20`)
Costs 0.10% a side plus hourly funding unless stated. "Unseen half" means Jul 2025 – Oct 2026; choices were made on Jan 2024 – Jun 2025.

| Study | Result |
|---|---|
| New listings with spot (Bybit hand-off check) | 81 of 199 new perps have Binance spot. Shorts pay funding in the first week (−198%/yr mean). Filtered harvest +3%/yr gross, about 0 after fees. Do not track. |
| Order flow (7-day taker-buy share, long/short fifths) | t 2.6 where found; FAILED on 165 unseen coins (t 0.72, other session). |
| Carry, 1-week reversal, 4-week momentum, extreme-funding fade, crash bounce, shorting new listings | None holds in both halves. |
| Climax reproduction | 440 trades, +1.6% before costs (record +1.8%). About 20 flush events a year; one trade dipped 72% inside its 12 hours; +0.3% a trade in 2026. |
| 100 → 10,000 maths | With no edge, at most a 1% chance for any method. Climax at 10% margin × 5: typical 5-year end about 480, 0% reach 10k. Deposits ($100/month at 10% ≈ 6 years) are the realistic route. |
| Scalping (20 majors, 15m, 2024–26) | Best predictable move +0.04% against a 0.04–0.10% round trip; correlation −0.015. Fees win. |
| Sweeps and fakeouts (324 perps) | A flush closing in the top 40% +1.34% (12 h); closing at the low −0.29%. Fakeout short wins 56% but averages −0.18%; with a stop above the sweep −0.13R. Breakouts and breakdowns lose. |
| Tournament (15 entries → best 10 → top 5 at 5R) | First half +0.09 to +0.15R; unseen half −0.005 to −0.074R. |
| Management techniques | Scaling out doubles wins and lowers profit; break-even and tight stops hurt; pyramiding helped only momentum bursts. On shuffled prices every technique lost the cost of trading. |
| 792-combination sweep (22 entries × 6 filters × 6 managements) | 47% positive in the first half (0.4% shuffled), 5% in the unseen half. Best three: t 2.5–3.0 by trade, 0.44–0.55 by week. |
| Autopsy | 85–88% of each result is caused after entry (market ~30%, coin ~45–50%). 14 pre-entry measures, linear and ML, explain nothing out of sample. Forced selling is the exception: deeper and market-wide flushes rebound more. |
| Live accounts (one market, 100 USDT) | A ended 180.5 with the minimum-order effect (true 1%: ×1.08), worst fall 31%; B 144.3 (true 1% ≈ 150), worst fall 37%. Coin-flip: 96% and 91%. More risk lost money (A at 10%: 15). From 10 USDT, half the starts went to zero. |
| CREED (own engine, 4,696 on-time setups, 20 coins) | As taught −0.006R (2020–23) and −0.106R (2023–26). 5-unit method −0.049 and −0.120R with 44–48% winners. Pyramid and trail not positive in both periods. |
| Management search (7 parts, 1,944 combos × 12 entries = 23,328 accounts, true 1%) | Best on first half: 500–640 → 43–86 on the unseen half. Limit retest entry and a 3 ATR stop helped in both halves; adding on strength hurt. |
| New method (parts chosen on the first half) | A's entry, unseen half: 125 (worst fall 18%); 10/10 six-month starts grew; 14/14 one-part variants grew; 97% of coin-flips; shuffled prices lost; all-signal average about 0. |
| **Plan E1** (md5 d1c0b7d7…, 2021–23, 14 coins) | **A 49.1 (beat 9%), B 27.2 (2%), new method 71.4 (76%): all FAILED.** |

---

## 5. Method lessons from these two days
- **Selection on used data fails.** Every "best" picked on the first half (tournament, sweep, management search) collapsed on the next half or the earlier years. Report the selection procedure's result, not the winner's.
- **Controls make results readable:** shuffled prices (what the mechanics do without structure), coin-flip direction (does the direction call add anything), random pick among simultaneous signals, and changing one part at a time.
- **Small accounts change results:** minimum orders, leverage caps and a single position at a time can turn a positive all-signal average into a loss, or a zero average into a gain. Model the account she actually has.
- **Tooling:** in this workspace a background job dies when a tool call ends. Run long jobs inside one call (≤ about 280 s) and make them resumable from files (`grid3.py` writes `grid3.jsonl` and skips what is done).

---

## 6. Code map additions
**Build kit (`/home/claude/omega48`):**
- `bdesk.js` (v6.5.83 module) and `bdesk84.js` (v6.5.84 version); `goldh.js`.
- `patch83.py` (from v6.5.82) and `patch84.py` (from v6.5.83).
- `s83_test.js`, `s84_test.js`, `fixtures/bdesk40.json` (40 coins, Jul–Sep 2025, with the Python reference trades).
- `creed83.js`: the CREED replay with the extra exits; it ran on v6.5.83, and CREED is unchanged since.
- `tools/crawl.js` now covers 25 pages, including `bdesk`.
- **Running tests:**
  - `HARNESS=<kit>/tools NODE_PATH=<dir with node_modules/playwright> node sNN_test.js <build>`;
  - Node Playwright 1.56.0 (`npm install playwright@1.56.0`), browsers at `/opt/pw-browsers`;
  - `s70_test.js` loads `/home/claude/fake_idb.js`, so copy `tools/fake_idb.js` there first.
- **Current suites:** s49, s50, s58, s60, s62, s67, s69, s70, s71, s73, s77, s78, s79, s80, s81, s82, s83, s84.

**Research edge archive (`/home/claude/edge`; scripts read the exports from `/mnt/user-data/uploads/`):**
- **Loading and engines:**
  - `load.py`: export decoder;
  - `engine2.py`: hourly features, the 22 entry signals and filters, numba trade simulator; reads `hourly2024f.pkl`, which is rebuilt from the exports and not shipped;
  - `live.py`: the USDT live-account simulator with Binance rules; the app's desk matches it;
  - `engine3.py`: parameterised management (`P()`), `sim_all` outcomes for every signal, the one-market `account`, `Bars` and `Book`.
- **Studies:**
  - `harvest.py`, `daily.py`, `port.py` (new listings);
  - `panel.py`, `hyp.py` (cross-sectional ideas);
  - `climax.py`, `growth.py` (climax and growth maths);
  - `mech.py` (sweeps and fakeouts);
  - `stage3.py`, `stage4.py`, `stage5.py` (management and sizing);
  - `sweep2.py` (792 sweep, real and shuffled);
  - `check3.py`, `autopsy.py`;
  - `livegrid.py`, `livenull.py` (live accounts, coin flips);
  - `grid3.py` (23,328 management search, resumable);
  - `mkfixture.py` (the desk's parity fixture).
- **Plans:**
  - `plans/PLAN_E1_older_years.md` (+ `.md5`), with `E1_result.json`;
  - `plans/PLAN_E2_gold_hourly.md` (+ `.md5`);
  - `plans/e2_run.py` (`python3 e2_run.py <gold file>`; dry-run output in `E2_result_DRYRUN.json`).
- **Results:** `sweep_real.jsonl`, `sweep_null.jsonl`, `livegrid.jsonl`, `livenull.jsonl`, `grid3.jsonl`, `newmethod.json`, `newmethod_checks.json`, `creed83_part2–5.json`.

---

## 7. Data files
- **Unchanged:** see the 19 Oct section 7 below.
- **Used again on 19–20 Oct:** final4 a–d + young (hourly perps) and creed15 2–5 (15-minute majors).
- **Not shipped:** the 250 MB hourly caches; the scripts rebuild them.
- **Next:** the gold file from v6.5.84. The workspace cannot reach Twelve Data, so it must come from her phone.

---

## 8. Next steps, in order
1. **Install v6.5.84** on the phone and open the Breakout Desk once to check it draws. Real-phone check still outstanding.
2. **Plan E2:** she presses "Download gold & silver hourly" (it resumes if the daily allowance runs out), then "Save file", and sends the file.
   - Record its sha256.
   - Run `python3 plans/e2_run.py <file>` **once**.
   - Report the result whatever it is.
   - Record it as round 21 in the app and in the research record.
3. **Keep the forward records running** and judge nothing before 26 weeks (about mid-April 2027): the climax reversal, harvest 5 and 10, C028 and C016, the model and shadow book, and the desk's failed setups (record only).
4. **Market Watch:** the first 7-day export (liquidations, open interest, order book). The one cause visible before entry is forced selling; this is where to look for more of it.
5. **New untouched data, each with a plan written first:**
   - delisted coins from Binance's public archive (this also fixes survivorship);
   - Bybit or OKX hourly candles;
   - coins listed from now on;
   - forex hourly.
6. **Do not search the used hourly crypto history for new direction rules.**
7. **Still needed from her:**
   - a decision on an always-on device;
   - the real-phone check;
   - the first Market Watch export;
   - the gold file.

## 9. Known limits (additions)
- The desk's paper accounts follow Binance's 5 USDT minimum on a 100 USDT account, as in research, so their "1%" is above 1% on volatile coins. The order table states the effective risk.
- Twelve Data gives no volume for metals, so E2 uses a breakout with no volume filter. How far back Twelve Data serves gold hourly is unknown until downloaded.
- E1 had only 14 coins with 2021–2023 bars: small, but fixed in advance.
- No build has been run on a real phone.

---

# Previous handover (19 Oct 2026, build v6.5.82), unchanged

# OMEGA handover — 19 Oct 2026 (build v6.5.82)

This hands OMEGA over to a new Claude account. It covers:
- the rules that must stay in force;
- where the app and the research stand;
- everything changed since v6.5.70, plus a short history of the builds before it;
- where every file is;
- exactly what to do next.

**Two companion documents** go with it:
- `OMEGA_RESEARCH_COMPLETE_2026-10-19.md`: every research round (1–18), its method and results, what passed, what we
  know about the market, and open hypotheses;
- `OMEGA_PRD_2026-10-19.md`: what the app is for, its rules, each module's requirements, how anything is judged,
  non-goals, open issues and the roadmap.

**What to upload to the new chat:**
- this file and the two companion documents;
- `omega-v6_5-47.html` (the current app, v6.5.82);
- `omega-buildkit-2026-10-19.tar.gz` (module sources, patches, tests and fixtures, for building the next version;
  refreshed for v6.5.82);
- `omega-research-2026-10-19b.tar.gz` (research code, plans, results and the test ledger; refreshed for v6.5.82);
- when research needs them, the data files from the phone (section 7), including the three Bybit files (downloaded 19 Oct).

---

## 1. Standing rules (Margaret's, all still in force)
1. Never fabricate data. Say what is verified and what is not, including "not run on a real phone".
2. Her phone number is never stored or written anywhere. Not in files, memory, tests or messages, and the number
   itself never appears. The guard `tools/nophone.js` holds only hashes. Run it on every build and package.
3. Exports and backups never contain API keys.
4. The Twelve Data key goes in the FULL build only. It is never in a lite build, the dev tools, research or
   verification bundles, memory, backups or downloaded files. (The two archives here were scanned: no key.)
5. The council never places or blocks trades.
6. Paper trading only. OMEGA never places orders. It shows orders for her to place herself.
7. Never change her three CREED desk markets automatically.
8. CREED's method stays byte-identical unless she asks. On 11 Oct she gave permission to change or add to CREED where
   the data shows it improves it.
9. Only trades actually taken count in win/loss. Rejected and not-taken setups stay visible as data only.
10. Don't just add features: the point is that it works and is profitable. Push back honestly and cut what doesn't
    earn its place.
11. **Always deliver builds under the file name `omega-v6_5-47.html`.** The browser keeps her data by file name.
12. Claude is the overseer. Other AIs' reports are outside views to verify, not to follow. Several had material errors.
13. She gives full autonomy and wants honest pushback.

---

## 2. Where things stand

**The only thing that has repeatedly passed untouched tests is the funding harvest:** hold a coin and short its
perpetual, so price moves cancel, and collect the funding that leveraged buyers pay. It passed:
- round 7 (+12.0% a year, z 4.14);
- round 8 (10 pairs, +8.8%, z 3.38);
- round 10 (with the basis counted, z 4.28);
- round 12 (blended with RSI(5) dip-buying, z 3.31 and 3.90 on 125 untouched coins).

**Its income has collapsed recently.** On the 140 validation coins, the 10-coin harvest made:
- +18.2% in 2020, +47.2% in 2021, −1.8% in 2022, +2.9% in 2023, +11.7% in 2024;
- **+0.7% in 2025 and −1.8% in 2026 so far.**

BTC's own Binance funding was about 12% a year in 2024, 5.1% in 2025 and 2.3% so far in 2026. Round 15 tested
whether Bybit raises that yield: it did not (failed the final). Round 18 found that the 2025–26 funding income sat in
new listings with no Binance spot market, which the harvest cannot hedge.

**Round 16 found the first direction rule to pass all three stages: the climax reversal.**
- **The rule:** a coin's perpetual falls 3σ or more on 3× volume or more, and the hour closes in the top 40% of its
  range; buy at the next open and hold 12 hours.
- **Results (a year over the market):**
  - 25 coins: +2.5%, z 2.30;
  - 140 coins: +7.4%, z 2.54;
  - final on 324 untouched coins: +5.3%, z 2.35 against a bar of 2.326.
- **Caveats:** it passed only just, and its profit is concentrated in the bigger rebounds.
- **What it really is** (round 17): 95% of its signals come in market-wide flushes, and the profit is the market's
  rebound after the flush, not the coin beating the market.
- **Status:** on paper since v6.5.78, from 19 Oct 2026 12:00 UTC. Since v6.5.82 its signals also show first on OMEGA
  Signals. Details are in PLAN16.md and section 4.

**Before round 16, every rule that predicts direction failed on new coins** (rounds 2–14). Each looked good where it was found,
then faded or reversed on untouched coins. The latest was round 14's capitulation rule, which failed its final test
(z −0.27) on 324 untouched coins.

**CREED has no edge after costs when taken as shown.** Its +0.47R replay headline came from setups shown hours later
but priced at the earlier close. Taken as shown it made +0.015R before costs and −0.085R after (2,497 setups).
No entry variant or exit change fixed that (section 5).

**Running on paper in the app now:**
- funding harvest, 5-coin and 10-coin (OMEGA Strategy page);
- round-12 blends C028 and C016 (OMEGA Strategy page);
- the climax reversal (Edge Lab, Market Watch and OMEGA Signals; forward from 19 Oct 2026 12:00 UTC);
- the round-14 machine-learning model across coins (Edge Lab shadow book, forward from 18 Oct 2026; not an edge);
- the BTC trend benchmark (OMEGA Strategy; a benchmark, not an edge).

**Untouched data is used up.** Every Binance coin and year has now been used in a test, so a new rule can only be
proven on forward weeks or on coins listed after 19 Oct 2026.

Forward weeks began 18–19 Oct 2026. Nothing is judged before 26 weeks (Edge Lab: EDGE only after 8+ forward weeks
clear the bar).

---

## 3. Builds since v6.5.70 (all delivered as `omega-v6_5-47.html`)

### v6.5.71 — honest CREED numbers, round 14 so far, two research downloads (patch71.py)
- **CREED history replay version 10.**
  - Each replay measures setups **shown on time** separately: shown on the same 15-minute close as the setup, so
    the entry is a price you could really take. Internally that is `lag === 0`.
  - For those setups it also measures: breakeven off, the three take-profit tiers, and the share reaching +1R.
  - Stored as `out.onTime = { n, share, all, early, late, beOff, tiers, reach1 }`. Older replays (v < 10) re-run.
- **CREED history card (Autopilot page).** It now leads with "CREED's honest record: setups shown on time". The old
  total is labelled "Total as taught (counts hindsight)".
- **On-time figures everywhere CREED is quoted.** The signal list and creedRecord use them, and the scoreboard's
  CREED line counts on-time setups only.
- **CREED Backtest: new Entry setting (`#creedBtEntryWhen`).**
  - "When CREED shows the setup" is the default. A late setup is entered at the close of the candle it appears on,
    and skipped if price is already past its stop or target (`BT.skippedLate`).
  - "As taught" keeps the old entry.
  - The status line and journal notes say which ran (`btEntryText()`, `BT.entryWhen`).
  - CREED's gates, levels and desk markets are unchanged.
- **Download "Round 14 final test"** (`final4export.js`, `OMEGA_FINAL4EXPORT`), 5 files:
  - hourly perpetual candles, premium index and funding for final3's 125 coins that have a perpetual (4 files);
  - perpetuals listed since 1 Apr 2025 whose coin was never used (1 file). Excludes the 166 used coins, the 155
    final3 coins, stablecoin/fiat/wrapped/gold/leveraged tokens, non-COIN underlyings and metals.
- **Download "CREED research data"** (`creed15export.js`, `OMEGA_CREED15EXPORT`): 15-minute spot candles for the 25
  studied coins from Jan 2020, in 5 files.
- The research record and the Edge Lab's built-in knowledge gained round 14 and the CREED finding.

### v6.5.72 — capitulation watch (patch72.py, `capwatch.js`, `OMEGA_CAPWATCH`) — removed in v6.5.82
- Round 14's candidate rule, watched live on the perpetuals of all 291 research coins, at the top of the Edge Lab.
  - Signal: a fall of ≥5 hourly standard deviations with the premium ≤ its 30-day 5th percentile.
  - Trade: buy at the next open, hold 12h, 20 slots × 5%.
- It uses its own IndexedDB, `omega_cap`.
- It reproduces the research engine trade for trade (42 trades, `fixtures/capwatch25.json`).
- Forward record from 19 Oct 2026.

### v6.5.73 — the model across coins in the shadow book (patch73.py, `xsmodel.js`, `xsmodel.min.json`)
- A frozen gradient-boosting model:
  - 124 trees, 28 rank-normalised daily features, about 72 KB in the app;
  - trained once on weeks known by 11 Oct 2026; the app never retrains it.
- Each Sunday it goes long the top fifth and short the bottom fifth.
- In the shadow book as "research: model across coins (round 14)", judged only on weeks after 18 Oct 2026.
- Its predictions match the research code exactly on 1,500 coin-Sundays (`fixtures/xsmodel_ref.json`).

### v6.5.74 — round 14's final results recorded (patch74.py)
- **Capitulation watch marked FAILED.**
  - Final test on 324 untouched coins: −1.5% a year, z −0.27, 2025 −27%, worst fall −47%.
  - Off by default (config key `omega_capwatch_cfg_v2`). When on, it only records ("FIRED (recorded only)"): no
    BUY NOW and no alerts.
- Knowledge and the research record gained:
  - the final result;
  - the Asian-session dip failure;
  - CREED's entry and exit variants failing (section 5).
- CREED's 1R breakeven was kept: removing it was not a proven improvement (+0.044R, t 1.15).

### v6.5.75 — Round 15 Bybit funding download (patch75.py, `bybitexport.js`, `OMEGA_BYBITEXPORT`)
- "Round 15: Bybit funding" on the OMEGA Strategy page, in 3 files:
  - `by-seen`: the 166 coins used before;
  - `by-final`: the 125 untouched coins;
  - `by-new`: the 199 new listings.
- It calls `GET api.bybit.com/v5/market/funding/history?category=linear&symbol=X&endTime=E&limit=200` and pages
  backwards to 2020.
- File format `omega-bybit-funding`:
  - `markets[{sym, fund:{t, r}}]`, where `t` is minute deltas and `r` is the rate × 1e7;
  - `missing[]` for coins with no Bybit perpetual, and `skipped[]`.
- Tested only against a mock. **Not yet verified on Bybit's live API.** If a file comes back empty, the request
  format is the first suspect.

### v6.5.76 — today (patch76.py)
- Harvest card: a "Round 15" note with the recent years on 140 coins and the fall in BTC funding. It says the
  ranking window stays at 30 days.
- Research record: new round-15 entry.
- Built-in knowledge:
  - 2,208 rules in all;
  - the round-15 study;
  - the harvest lesson now gives the 2024 → 2026 funding fall;
  - the Edge Lab count now covers rounds 1–15 and CREED.
- No rule, trade, CREED setting, key handling or storage changed.

**Checks on v6.5.76 (v6.5.77's are in its section):**
- suites: s49 11/11, s50 5/5, s58 9/9, s60 9/9, s62 7/7, s67 15/15, s69 21/21, s70 21/21, s71 16/16, s72 11/11,
  s73 7/7;
- 108 script blocks pass `node --check`; phone guard clean;
- opened in Chromium at 412 px with no page errors and no sideways scroll.

Not run on a real phone.

### v6.5.77 — Market Watch, the recorder (patch77.py, `watch.js`, `OMEGA_WATCH`)
This answers Margaret's direction: "gather all the data necessary and cross reference it to find what really makes the
moves … watch everything".

**New page "Market Watch".** Once started it records whenever the app is open, and it resumes after a reload
(config `omega_watch_cfg_v1`; IndexedDB `omega_watch` with stores min, pos, book and events). For each watched coin
(default the 25 studied coins, up to 60) it records, per minute:
- spot and perpetual aggressive buy and sell USDT;
- large orders: one taker order ≥ max(10k, 0.02% of 24h volume), with a split fill counted once;
- the largest order each minute;
- the top-20 book imbalance, depth and spread;
- mark price, index, premium and funding;
- liquidations, for the coin and for the whole market (a sample);
- Coinbase BTC, ETH and USDT prices.

**Every 15 minutes:**
- 5-minute open interest, global long/short ratio, top-trader position ratio and taker buy/sell ratio (30-day
  backfill);
- a 500-level liquidity map (setting).

**Flight recordings.** They open on a 60-second move of 4σ or more, or 10M USDT of market liquidations in 60 seconds.
Each one keeps 30 minutes before and 60 after, second by second, with context and outcomes. Up to 150 are kept.

**Other features:**
- a "What's moving it now" table, with a plain factual read;
- export of 1/3/7 days as `omega-watch-….json.gz`, read by `research/watch16.py`;
- Full mode (every trade, a few GB a day) and Light mode (1-minute candles);
- keeps the screen on while recording.

**Liquidation feed fixed.** Binance split its futures WebSocket in 2026: market streams moved to
`wss://fstream.binance.com/market/...` and public ones (depth) to `/public`. The legacy `/ws` and `/stream` addresses
ended on 23 Apr 2026. OMEGA_DERIV's liquidation feed was on the old address, so it had most likely been dead since
April. It now uses `/market/ws/!forceOrder@arr` and reports "live" only on data.

**Verification status:**
- s77 27/27 (Node, with the exchanges mocked), plus every earlier suite;
- Chromium with mocked WebSockets and REST.
- Not verified against live Binance or Coinbase, or on a phone.

### v6.5.82 — audit, fixes and trim (patch82.py), the current build
Margaret asked for a full check: find errors, make sure readings are accurate, and remove what isn't needed.

**Audit.** All 24 pages were opened in Chromium at 412 px, twice: offline, and with a simulated Binance. The script is
`tools/crawl.js`: `node tools/crawl.js <build.html> offline|fake <out.json>`. Checked on each page:
- page errors and console errors;
- readings showing NaN, undefined, Infinity or "[object Object]";
- sideways scrolling.

Result: none, before or after the changes. The research-facing text was read against the research files.

**Removed** (the sources stay in the build kit):
- **The capitulation watch** (`capwatch.js`): it failed its final test and only recorded.
- **Seven research downloads whose data has been collected and used:**
  - futures data, and "the rest in one run";
  - round 14 final test (`final4export.js`);
  - CREED research data (`creed15export.js`);
  - Bybit funding (`bybitexport.js`);
  - untouched coins (`untouchedexport.js`);
  - forex history (`fxexport.js`).
- **The older-history, fresh-coin and new-coin download buttons.** Their timers are gone. Their coin lists
  (`LONG`, `FRESH`, `FRESH2`) stay, because `OMEGA_WIDE` and the data stores read them.
- **The funding carry card and its Autopilot job.** `OMEGA_CARRYXS.render()` now removes the card, and `register()`
  returns true without adding a job. The data helpers stay, because the harvest uses them.

**Kept:** the research report export, the price history export (`omega-history`), the Market Watch export and backups.

**Corrected text:**
- The research record heading names what passed: the harvest (rounds 7, 8, 10; with dip-buying in round 12) and the
  climax reversal (round 16).
- The carry row now says carry failed rounds 5 and 7.
- The harvest title and Brain note now name rounds 7, 8 and 10.
- The Positioning Desk no longer says the harvest is the only pass.
- The OMEGA Strategy panel no longer says "There is no OMEGA strategy yet".
- Built-in knowledge round labels are fixed in `mkknowledge.py`: sweep fade r2, with-the-sweep r3, carry r4,
  buy-and-hold r6.

**Added:** OMEGA Signals shows the climax reversal's signals first (`#climaxSigBody`, rendered by `climax.js`).

**Tests:**
- new s82 7/7;
- s71 cut to 11, and now checks that the downloads were removed on purpose;
- s62, s67, s78 and s79 updated for the intended text changes;
- **s72 is retired** (it tested the removed capitulation watch);
- all other suites pass;
- 104 script blocks pass `node --check`; no duplicate ids; phone guard clean.

The file is about 100 KB smaller. Not run on a real phone.

### v6.5.81 — round 18, the outside report (patch81.py)
**Changes:**
- The harvest card answers the new-listing question: the income is in coins with no Binance spot.
- The research record and knowledge include round 18 (2,240 rules and studies).
- s79's check now allows later round numbers.

**Tests:** s81 3/3, plus all earlier suites.

### v6.5.80 — round 15's Bybit result (patch80.py)
**Changes:**
- The harvest card states the venue result (passed validation, failed the final).
- It also describes where funding was paid in 2025–26.
- Research record and knowledge updated.

**Tests:** s80 4/4.

### v6.5.79 — round 17, what moves the market (patch79.py, `clock.js`, `OMEGA_MARKETCLOCK`)
**Market Watch: "When the market moves" card.**
- The hour map comes from round 17.
- **Upcoming events:**
  - CPI 2026–27 from the BLS schedule, 08:30 ET;
  - FOMC 2026–27 from the Fed calendar, 14:00 ET (2027 tentative);
  - monthly options expiry, last Friday 08:00 UTC;
  - funding settlements;
  - the CME weekend close (Fri 16:00 CT) and open (Sun 17:00 CT).
- New York and Chicago times are converted with US daylight saving.

**Other changes:**
- Flight recordings are tagged with CPI, FOMC and expiry hours (`OMEGA_MARKETCLOCK.tags`, used by `watch.js`).
- The climax card explains its anatomy.
- Knowledge and the research record include round 17.
- Tests: s79 9/9, plus all earlier suites.

**Event dates to extend later** (in `clock_data.json`, built from `research/macro_dates.py`):
- CPI through Dec 2027;
- FOMC through Dec 2027.

### v6.5.78 — round 16's result on paper (patch78.py, `climax.js`, `OMEGA_CLIMAX`)
**Climax reversal watch.** It sits at the top of the Edge Lab, with a copy on Market Watch.
- **Coverage:** every Binance USDT coin perpetual (from exchangeInfo; underlyingType COIN, metals excluded).
- **Data:** hourly klines topped up each hour, kept 950 hours (IndexedDB `omega_climax`, config `omega_climax_cfg_v1`,
  on by default).
- **Rule and book:** identical to the research engine, with 61-trade parity in `fixtures/climax25.json`.
- **Signals:** BUY (paper), plus an alert.
- **Forward record:** from FREEZE_H = 19 Oct 2026 12:00 UTC, judged weekly against the market.

**Also:** the research record and knowledge gain round 16. Tests: s78 13/13, plus every earlier suite.

### Earlier builds in this run (one line each)
- **v6.5.48** fixed the stop used by CREED's "as it could be taken" figures.
- **v6.5.49** added the Strategy Workshop.
- **v6.5.50** added the history export for research.
- **v6.5.52** added the outside-research record.
- **v6.5.55** added the funding-carry card (round 4). It later failed rounds 5 and 7.
- **v6.5.56** recorded the 2019–2023 test (nothing passed).
- **v6.5.58** added the Positioning Desk page.
- **v6.5.59–60** added the funding harvest and the BTC trend benchmark.
- **v6.5.61–62** recorded round 8 (10-pair harvest passed).
- **v6.5.66** let each futures download file be saved on its own.
- **v6.5.67** recorded rounds 10–11.
- **v6.5.68** added the untouched-coins download and the week's order list.
- **v6.5.69** put the round-12 winners C028/C016 on paper.
- **v6.5.70** added the Edge Lab: built-in knowledge of every rule tested, a self-search for untested edges, and the
  shadow book.

Each build has its own `OMEGA_v6_5_NN_CHANGES.md` in the build kit.

---

## 4. Research results since the last handover

### Round 14 (PLAN14.md, addenda A–F)
**F1, a coin's capitulation** (hourly, long only, 60 candidates):
- the screen kept 21 of 120 across families 1–4 (about 6 expected by chance);
- one passed validation: z ≤ −5 with the premium ≤ 5th percentile, hold 12h — +19.4% a year over the market,
  z 3.04 (cumulative bar 2.90 at n_v 27);
- **FAILED the final test on final4** (324 coins, run once): alpha −1.49% a year, z −0.27, costs doubled −4.51%,
  2025 −27.3%, worst fall −46.6%;
- descriptive only: the 125 final3 coins alone gave +4.18% (z 1.45); the 199 new listings −3.38%.

**F2–F4 failed:** the market's capitulation, premium extremes, and hourly cross-sectional reversal (which lost
heavily to costs).

**F5, listing age:** 0 of 10 survived. Survivorship biases this family against the short, so it can't be judged
fairly on these files.

**F6, the walk-forward ML model:**
- validation z 2.42 (bar 2.39);
- final3: +37.8% a year, z 2.89 against a bar of 3.29 (final3 has been used for 101 finalists), so it FAILED the bar;
- now forward-tracked only.

**F7, short-squeeze fades** (shorting 5-sigma up-hours): none survived. Pumps kept going.

**Outside rules checked:**
- **Asian-session dip** (−2.5% hour between 00:00 and 08:00 UTC, buy, hold 12h): trade-level t 5–6, but week by week
  z 1.22 and 0.56. −17.7% a year with costs doubled. It lost in 2023, 2025 and 2026. The trade-level t was inflated
  because the trades bunch in the same hours.
- **Gold SMA50>200:** no alpha against simply holding gold (Newey-West t −0.6 to +0.6).

### CREED (`omega48/creed14.js` replays CREED's own app code on the 15-minute files)
Re-run on Oct 2023 – Oct 2026, 3,268 on-time setups:
- **As coded:** −0.135R a trade after costs (−0.015R before). Win rate 11%, target hit 10.6%.

| Variant | R a trade after costs |
| --- | --- |
| Longs only | −0.107R |
| Capitulation sweeps | −0.177R |
| Perpetual at a discount | −0.028R (67 trades) |
| Shorts only | −0.171R |

| Exit | R a trade after costs | Wins |
| --- | --- | --- |
| No breakeven | −0.091R | 18.1% (gross +0.029R) |
| Breakeven at 2R | −0.123R | |
| Target 2R | −0.169R | 31.8% |
| Target 1.5R | −0.158R | 38.5% |

- **Her "1R is messing with it" question:** removing breakeven is +0.044R better, t 1.15. That is not significant, so
  the 1R breakeven stays (CREED unchanged).
- **None reached a final test.** CREED's Jan 2020 – Sep 2023 data (in creed15) was being kept as the clean final
  test for any CREED variant, but the outside report checked in round 18 used it. It is no longer clean. A future
  CREED variant must be judged on forward data.

### Round 18 (PLAN18.md; outside report in research/outside/; outside_flow_check.py, outside_flow_check.json)
The other assistant's report "Edge research, 19 Oct 2026" included `flow_tracker.py` and `new_listings_spot.csv`.

**Order-flow rule** (7-day taker-buy share, long top 20% / short bottom 20%, weekly, liquid perps):
- reproduced on final4: +46.8% a year, t 2.95;
- **failed** on the 165 coins it never used (one pre-registered look): +5.3%, t 0.72, −0.4% with costs doubled;
- round 12's S497/S499 had failed as well. Not tracked.

**New listings:**
- Shorts pay funding early: mean −116% a year in days 0–7.
- The H10 income on new listings (2026 +27%) came only from the 118 without Binance spot. On the 81 with spot:
  −2.0% (2025), −2.8% (2026).
- The spot list is the report's own check; this workspace cannot reach Binance.

**CREED's reserved data has been touched.** The report's "20 major coins, spot, 2020–2026" check used creed15
2020–2023, which was being kept for CREED's final test.

### Round 17 (PLAN17.md; descriptive; round17.py, round17b.py, macro_dates.py; results round17.json, round17b.json)
**Data:** 165 seen coins, hourly 2020 to Oct 2026; final4 untouched.

**What explains a move:**
- The market explains a median 60% of a coin's hourly move (R²); the coin's own aggressive flow adds about 6 points.
  In 2026 the market explains 45%.
- Flow imbalance and last-hour return predict the next hour in reverse: rank IC −0.02 and −0.05. The effect fades
  after 2024 and is too small after costs.

**When moves happen:**
- Busiest 13:00–16:00 UTC: at 14:00, 2.9% of hours have a 3σ move.
- Also busy: 00:00 and 08:00 UTC.
- Quietest 03:00–11:00 UTC. Weekends are about 20% calmer.

**Scheduled events:**
- **CPI hour:** median 1.3× a normal hour; up in 75% of releases (baseline 51%); 2022 averaged −1.55%.
- **FOMC hour:** median 1.9×; up 70% (baseline 52%); mean +0.9% (t 3.6), fading to flat in 2025–26.
- **Options expiry:** no distinct effect. Fridays from 08:00 UTC had +0.62% over the next 24h, against +0.13% for any
  day.
- **CME gap fill:** not supported (353 weekends).

**After big moves:**
- On average, no drift.
- Rejected 3σ spikes lagged the market −1.85% over 72h (t −2.7, n 309).
- After 3σ market falls, the market made +0.83% over the next 24h (t 2.6).

**Climax anatomy:** 95% of signals come in market-wide flushes. Against the market the coins made −0.34% (t −1.7);
raw they made +1.72% (t 2.7). The rule rides the market rebound. z ≤ −8 was worst (−1.3%, t −4.1).

**Hypotheses for forward testing:**
- H17-1: the CPI hour rises.
- H17-3: rejected spikes lag.
- H17-4: the climax without z ≤ −8.

**Ledger:** 10 description entries.

### Round 16 (PLAN16.md; frozen addendum A text in PLAN16_frozen_A.md, md5 in PLAN16.md5)
Margaret's direction: find what moves the market and test whether trading on it makes a difference. The test used
hourly perpetual footprints:
- taker-buy share;
- volume against its median;
- premium quantiles;
- close location;
- 72-hour lows and 168-hour highs;
- 12-hour net-flow change.

**18 candidates,** each against a "twin" (the same setup without the footprint). Code in `round16.py`, stages
describe, screen, valid and final.

**Description** (11,615 dips with z ≤ −3 on 25 coins):
- **All dips:** the next-24-hour alpha is +0.05%, so a dip alone pays nothing.
- **Heavy aggressive selling** (tb < 0.40): −0.25% (se 0.09).
- **The coin falling alone:** +0.55% (se 0.34).
- **The hour closing near its high:** +0.28% (se 0.14).

**Screen:** only G 12h passed (the climax wick, now named the climax reversal).
- F, the spot-led breakout, met the bar (+8.5%, z 2.55) but did not beat the plain volume breakout. The premium
  footprint did not help.
- Absorption, exhaustion, flow divergence, flush and stop-run all failed.

**Validation (140 coins, bar 1.645):** G 12h passed, +7.40%, z 2.54.

**Final (final4, run once, bar 2.326 = Φ⁻¹(1 − 0.05/5)):** G 12h PASSED.
- +5.28% a year, z 2.35, costs doubled +4.62%, 440 trades;
- mean +1.78%, median +0.64%, 58% winners.

**Descriptive checks** (`round16_diag.py`):
- robust to entering 1–2 hours late, and to the volume threshold;
- close location ≥ 0.5 is stronger and ≥ 0.7 weak;
- without the best 10% of trades, the mean is +0.13% (final4);
- on spot bars, 25 coins: 87 trades, +2.49% a trade, 72% winners, z 1.58.

**Ledger:** round 16's screen, validation and final are in `ledger14.json`. **final4 has been used three times**
(F1, G and round 15's BEST10) and is closed to new tests.

### Round 15 (PLAN15.md, addenda A–C and results): DONE, no new edge
- **Venue family:**
  - Y10: −3.76% a year against H10 (t −1.3);
  - SPLIT: −1.88% (t −1.3);
  - BEST10: +5.33% (t 7.39) on validation, then +0.71% (t 1.25 against 2.13) on the final.
- **Why BEST10 failed:** Bybit paid more on 39% of coin-days on the 140 coins, but only 12% on final4.
- **Addendum C** raised the final bar to count round 16's use of final4. The addendum B bar (1.96) was also not met.

### Round 15 lookback family (addendum B)
- **Family 2, harvest ranking window,** validated on 140 coins (bar 2.39 for 6 candidates):
  - L7: −4.11% a year against H10 (z −7.13);
  - L14: −1.96% (z −5.30);
  - L60: +1.01% (z 1.62).

  **No finalists.** The 30-day ranking stays.
- **Family 1, venue,** waiting for the Bybit files. Candidates:
  - Y10: harvest on Bybit;
  - BEST10: each coin shorted on the better-paying venue; a venue switch costs 0.06% a side twice;
  - SPLIT: half Binance, half Bybit.

  Each is judged as the weekly difference against H10. Validation needs all of: difference > 0, and > 0 with costs
  doubled; t ≥ 2.39; the candidate's own return positive in at least half of the full years. The final test is on
  final4 (its second use), at bar Φ⁻¹(1 − 0.05/(1 + n_finalists)).

### Outside reports verified this run
- Gold, ADA trend, Wednesday bias and forex: none carried forward.
  - Gold: no alpha.
  - ADA-type trend was weak (t 1.0–1.9) with coins picked after seeing results.
  - Wednesday long: looked at in round 1.
  - Forex: failed in round 11.
- Strict-search result: nothing cleared its bar.
- 100-strategy sweep: its own winners deteriorated in 2025–26.
- Asian dip: failed (above).
- **19 Oct "research findings".** It agrees with ours: no confirmed edge. Point by point:
  - volume-spike reversal = our F1 (failed);
  - sweep/reclaim = CREED and rounds 2–3 (failed);
  - premium fade turns negative at 20 bp costs, as our F3 found;
  - ML has no net edge;
  - its "portfolio combination" idea already exists as C028/C016;
  - we already hold BTC/ETH data from Jan 2020.

  Its question about funding units is answered. Binance settles at 00/08/16 UTC, minute 0, and the median rate is
  0.0090% (BTC) and 0.0100% (ETH) per 8h, about 12% a year in 2024. Our decoding is right.

---

## 5. Research method (keep this discipline)
- **The plan is written before the data is seen** (PLAN*.md, fingerprinted with .md5). Changes are dated addenda
  written before the affected data is opened.
- **Stages:** screen (design coins) → validation (coins not used for design) → final on untouched data, **run once**.
- **Bars:** one-sided Bonferroni.
  - Validation uses the round's cumulative n_v.
  - Final uses Φ⁻¹(1 − 0.05/n), where n is the number of finalists on that file.
  - final3 has 101 looks (bar 3.29). final4 has been used three times: F1 (round 14), G (round 16) and BEST10 (round 15). **Do not run new tests on final4**; new rules need forward data or new coins.
- **The ledger** is `research/ledger14.json`: 189 entries since round 14, prior 2,046 rules in rounds 1–13. Every
  test is added with `h14engine.ledger_add`.
- **Judging:**
  - weekly alpha against the equal-weight market (β = cov/var, ddof 1);
  - Newey-West t, lag 2, on weekly sums;
  - trade-level t-stats are not valid when trades bunch in time.
- **Costs:**
  - perpetual 0.06% a side;
  - event trades 0.10% a side;
  - harvest 0.11% spot + 0.06% perpetual a side;
  - every test is also run with costs doubled.
- **Hourly engine (h14):** 20 slots × 5%, no re-entry, deepest first; entry at the next open; hold H; funding at
  settlements in (entry, exit].
- **CREED:**
  - rules: closes 2, window 6, bufferAuto, pivot 2, lookback 150, minRR 3, maxRR 7, minStructure 8;
  - walkExit is stop-first, breakeven at 1R;
  - "lag" = bars between acceptance and when CREED shows the setup. As-taught entry uses the acceptance close,
    which is hindsight when lag > 0.

---

## 6. Code map

**Folder layout the scripts expect (paths are hard-coded):**
- Extract the research archive to `/home/claude/research`. 51 scripts point there.
- Extract the build kit to `/home/claude/omega48`. `mkknowledge.py` and `mkmodel.py` write there.

The build kit was refreshed for v6.5.82 and re-checked from a fresh extract (section 6, release checklist).

### Research (`omega-research-2026-10-19b.tar.gz`)
- **Plans:** `PLAN.md`, `PLAN2–5, 7–18.md` (+ `.md5`), `PLAN16_frozen_A.md`, `PLAN16_DRAFT.md`.
- **Loaders:** `omega_history.py` (`load()`: the app's export format), `bybit15.py` (Bybit file decoder).
- **Engines:** `engine.py` (`nw_t` etc.), `r12data.py` / `r12lib.py` (daily data and harvest), `h14data.py`
  (hourly cache; index stored in seconds), `h14engine.py` (`run_events`, `run_tranches`, `verdict`, `screen_ok`,
  `valid_ok`, `ledger_add`).
- **Round 14:**
  - `round14_hourly.py` (screen / valid / screen7 / valid7), `round14_daily.py` (F5), `round14_ml.py` (F6),
    `mkmodel.py`, `null14.py`, `asiandip14.py`, `round14_final4.py`;
  - CREED: `creed14_judge.py`, `creed14x_judge.py`.
- **Round 15:** `round15.py`, `bybit15.py`.
- **Round 16:** `round16.py` (stages describe, screen, valid, final; `--dry`), `round16_diag.py`.
- **Round 17:** `round17.py`, `round17b.py`, `macro_dates.py` (CPI and FOMC dates, converted to UTC).
- **Round 18:** `outside_flow_check.py`; the outside report and its files are in `outside/`.
- **Market Watch:** `watch16.py` decodes the app's `omega-watch` exports.
- **Results:** `round14_*.json`, `asiandip14.json`, `creed14_design.json`, `creed14x_design.json`,
  `round15_valid.json`, `round15_final.json`, `round16_*.json`, `round17.json`, `round17b.json`,
  `outside_flow_check.json`, and every earlier round's json/txt.
- **App knowledge:** `mkknowledge.py` writes `omega48/knowledge.min.json`, which the patch puts into the app as
  `var KN = …`.
- **Checksums:** `data/SHA256SUMS_round14.txt`, `data/futures/SHA256SUMS`, `data/final3/SHA256SUMS`.
- **The hourly cache (`cache14/`) is not included** (600 MB). `h14data.py` rebuilds it from the data files.

### Build kit (`omega-buildkit-2026-10-19.tar.gz`)
- Module sources: `capwatch.js`, `xsmodel.js` + `xsmodel.min.json`, `edgelib.js`, `edgelab.js`, `final4export.js`,
  `creed15export.js`, `bybitexport.js`, `harvest*.js`, `carryxs*.js`, `btctrend.js`, `posdesk.src.js`,
  `workshop.js`, `knowledge.min.json`, and others.
- `clock.js` + `clock_data.json` (market clock), `s79_test.js`;
- `climax.js` (climax reversal), `s78_test.js`, `fixtures/climax25.json`;
- `watch.js` (Market Watch), `s77_test.js`; research side `research/watch16.py` (export decoder).
- `creed14.js`: CREED replay on the 15-minute files (research tool, not in the app).
- **Sources of removed modules are kept for reference:** `capwatch.js`, `final4export.js`, `creed15export.js`,
  `bybitexport.js`, `untouchedexport.js`, `fxexport.js`, `futexport.js`, `carryxs*.js`. They are not in v6.5.82.
- `patch48.py` … `patch82.py`. Each makes build N from build N−1: `python3 patchNN.py <prev.html> <new.html>`.
  - Each patch asserts every anchor appears exactly once.
  - Each restamps the version and build time.
- **Tests:** `s48…s82_test.js` + `fixtures/`.
  - Run each with `HARNESS=<dir with smoke.js, fake_idb.js> node sNN_test.js <build.html>`.
  - `tools/` holds `smoke.js`, `fake_idb.js`, `nophone.js` and `crawl.js` (the 24-page audit).
  - Browser checks use Playwright with Chromium (`NODE_PATH` must reach the playwright package), with all network
    mocked.
  - **Current suites:** s49, s50, s58, s60, s62, s67, s69, s70, s71, s73, s77, s78, s79, s80, s81, s82.
  - **Retired:** s72 (capitulation watch, removed). s48, s55, s56 and s59 belong to older builds.
- Change notes `OMEGA_v6_5_48…82_CHANGES.md`.
- The app HTML is not in the kit, because it holds the Twelve Data key. Use the delivered `omega-v6_5-47.html` as
  the base for patch83.

**Release checklist (every build):**
1. Patch from the previous build.
2. Run all current suites.
3. Run `node --check` on every `<script>` block, and check for duplicate element ids.
4. Run the phone guard on the build.
5. Run `tools/crawl.js` offline and with the fake exchange: no errors, no NaN or undefined readings, no overflow.
6. Write the change note.
7. Deliver as `omega-v6_5-47.html`.

---

## 7. Data files (on Margaret's phone; re-upload when research needs them)

Paths are where the research code expects each file under `research/data/`:

| File(s) | What | Used for |
| --- | --- | --- |
| `futures/studied.json.gz` | 25 studied coins (BTC and ETH included): daily + funding | design (seen many times) |
| `futures/fresh-a, fresh-b, new-a, new-b, new-c` | 140 coins: daily + funding | validation (used) |
| `futures/metrics` | BTC/ETH positioning | round 10 |
| `fresh/`, `fresh2/`, `older/`, `hist`, `hist2`, `forex/` | earlier rounds | used |
| `final3/final3.json.gz` (+ `final3b/final3-2026-10-19`) | 155 untouched spot coins (125 with perpetuals), daily from 2020 | final, 101 looks (bar 3.29) |
| `final4/omega-history-final4-a/b/c/d-2026-10-19` + `final4-young-2026-10-19` | hourly perpetual candles, premium and funding: 125 final3 perpetuals + 199 listed since Apr 2025 | final, used three times (F1, the climax reversal, BEST10); **closed** |
| `creed15/creed15-1…5` | 15-minute spot candles, 25 coins, Jan 2020 → Oct 2026 | CREED design = Oct 2023 on; Jan 2020 – Sep 2023 was kept back, but the outside report used it (round 18), so it is no longer clean |
| `bybit/by-seen`, `by-final`, `by-new` (19 Oct, sha256 in data/bybit/SHA256SUMS) | Bybit funding: 166 + 115 + 181 coins, from Mar 2020 | round 15 (done) |

The sha256 of every round-14 file, and of the futures and final3 files, is in the research archive
(`data/SHA256SUMS*`). All of them verified on 19 Oct. Check them again on re-upload.

---

## 8. Next steps, in order
Rounds 15–18 are done (results in section 4 and in `OMEGA_RESEARCH_COMPLETE_2026-10-19.md`).

1. **Keep the paper rules running and judge them only on forward weeks.** Nothing is judged before 26 weeks (about
   mid-April 2027). This covers:
   - the climax reversal (Edge Lab, from 19 Oct 2026 12:00 UTC);
   - harvest 5 and 10, C028 and C016 (OMEGA Strategy, from 18 Oct 2026);
   - the model and the shadow book (Edge Lab).

   For the OMEGA Strategy cards, a rule then retires if its weeks average ≤ 0, and is confirmed at z ≥ 1.96. It
   retires at any time on a 10% fall from its forward peak. In the Edge Lab, a rule retires after 26 flat weeks or on
   a 15% fall. Retirement is permanent.
2. **Market Watch data.** Margaret keeps it recording (ideally on a device that stays awake) and exports 7 days at a
   time. Read the exports with `research/watch16.py`. The flight recordings are the raw material for the event study
   that history cannot answer: do liquidations plus falling open interest, and order-book behaviour, mark the end of
   a flush?
3. **Forward hypotheses** (judged on new weeks only, never on old data):
   - H17-1: the CPI hour rises;
   - H17-3: rejected 3σ spikes lag the market for 3 days;
   - H17-4: the climax reversal without the z ≤ −8 single-coin collapses.
4. **Still needed from Margaret:**
   - a real-phone check: do the feed labels say "live", and does the climax card show a status line;
   - a decision on an always-on device or a small server (the app watches only while open);
   - the first 7-day Market Watch export;
   - the capital amount, for sizing.
5. **Honest outlook.** After 18 rounds, rules that predict direction don't survive new coins, with one narrow
   exception (the climax reversal, which rides the market's rebound after flushes). Being paid to supply leverage
   works, but pays mostly in boom years. Ideas still open, each needing a plan written first and forward data:
   - harvest sizing by funding level;
   - CREED variants (2020–2023 is no longer clean, so forward data only).

   **Untouched history is used up.** More history does not substitute for an untouched test.

## 9. Known limits
- No build has been run on a real phone; all testing is in Node and headless Chromium with mocked exchanges.
- The app works only while it is open. 24/7 watching would need a server.
- The workspace cannot reach Binance, Bybit or OKX, so all market data comes through her phone's downloads.
- **Survivorship:** the coin sets are coins trading now.
- **Basis** is ignored in the harvest tests (about 0.05% a year on large coins), apart from delistings.
