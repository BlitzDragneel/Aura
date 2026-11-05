# OMEGA — carry-over to the next chat (25 Oct 2026)

Read this first. Full detail is in `OMEGA_HANDOVER_2026-10-20.md` (sections 0a–0zb are the newest updates, top to bottom).

## Who and what
- **Maro,** Scarborough, Tobago. Builds single-file HTML PWAs with no dependencies. Claude is the lead developer.
- **OMEGA:** a trading research and decision app. **Paper only:** it never places orders and holds no keys.
- **Account in mind:** 100 USDT, 0.5–1% risk per trade.

## The two apps
| File | What it is |
|---|---|
| `omega-v6_5-47.html` | **The original build, v6.5.97** (build 2026-10-25 10:47 UTC): 28 pages, the research lab (Research Lab, Edge Lab, Market Watch recorder, downloads), CREED, Market Profiles, Market Read, Daily Plan, Risk Guard / Growth Bot, Cockpit, data check. All 31 test suites pass. Always delivered under this file name. |
| `omega-prime.html` | **OMEGA Prime,** Claude's own lean version: 5 pages, verdict-first, graph-paper design. Its storage is separate under the `prime:` prefix. Its Autopilot runs 6 jobs. `s_prime_test.js` passes all 10 checks. |
Measured: Prime is 137 KB against 4.4 MB, opens in 70 ms against 530 ms, sends 77 requests against 484 in 30 s, and uses 2 MB against 30 MB of memory.

## What the evidence says (every test written down first, run once, counted)
**Passed a fair test**
- **Climax reversal (round 16):** a 3σ hourly drop, 3× volume, a close in the top 40%; buy the next open, hold 12 h. It passed on 324 untouched coins. It runs on paper in both apps.
- **Funding harvest:** passed, but its income has faded since 2025.
- **E22 H1:** after a coin's 24 h return falls into its bottom 10%, a buy limit 2σ below the price, filled only if price trades through it within 3 h, held 24 h.
  - **+0.36% a trade net, t 4.34,** positive in 2024, 2025 and 2026, on 324 perpetuals.
- **E22 H3:** the same panic at q5, only when 20%+ of coins panic together. +0.22% a trade net, t 3.63.
- **Open caveats on H1 and H3:**
  - survivorship (delisted coins are missing from the data);
  - they depend on the biggest rebounds (without the best 5% of trades, H1 loses);
  - at 100 USDT the 5 USDT minimum prevents taking every signal.

**Failed:** breakouts, momentum, reversals, sweeps and fakeouts, sessions, pyramiding and the 5-unit method, shorts, market states (E8), the capitulation bounce (E9, E10), absorption (E11), the top-5 coins with 11 rules each (E14), the path simulator for setup odds (E18, E19), the BTC father-coin warning (E20, t 0.99, though it cut drawdowns), the broad inverse scan (E21), and Two Seats (E23 100 → 16; E24 A 126, beating 96% of random against 97.5% needed).

**Key lessons**
- **Size is predictable; direction is not.** Hourly direction correlation is about −0.02; size correlation about +0.3; the next day's range about 0.7.
- **Panic selling gets overdone.** Only extremes, limit entries or market-wide panics clear the fees.
- **Violent panics bounce more AND collapse more.** Concentration turns that into ruin; diversification (many small seats) keeps the edge.
- **The simulator is trustworthy for ranges and crash rates** (90% and 99% bands, tails), not for setup odds.

## Next, in order
1. **The survivorship test:** H1 and H3 including delisted perpetuals. Needs `data.binance.vision` added to Claude's allowed network domains.
2. **"Many small seats":** H1 with as many 5–10 USDT seats as 100 USDT allows, plus a −10% disaster stop. Written down first; tested on the delisted-inclusive data or forward.
3. **Into OMEGA Prime:** H1 and H3 as **Grade B** (passed a fair test, unconfirmed), with a forward paper record.
4. **Path simulator v3:** a block bootstrap (consecutive real hours), tested once on data it has never used. Ranges and account futures first; setup odds only if they beat the base rate.
5. **Early warnings:** alts against BTC (the ALT/BTC trend), and breadth (share of coins above their averages). One written test each.
6. **Milestones already running:**
   - E13 (5 full Market Watch days);
   - E15 (the metals/forex file from the app);
   - E16 (50 Daily Plan paper trades);
   - E17 (Growth Bot: 50 trades or 26 weeks);
   - E6 and the forward records: mid-April 2027.

## Upload at the start of the next chat
1. `omega-carryover-2026-10-25.tar.gz` (this bundle). It holds both apps, this note, the handover, the change notes, the build kit, the research archive and the Prime kit.
2. **Data files from your device, for the tests:**
   - `omega_history_creed15_1…5_2026_10_19_json.gz` (25 majors, 15-minute);
   - `omega_history_final4_a/b/c/d/young_2026_10_19_json.gz` (324 perpetuals, hourly);
   - `omega-history-gold1h-2026-10-21_json.gz`;
   - any new exports the app has saved (Market Watch, metals/forex).
3. **Optional:** a backup from each app, and screenshots of anything that looks wrong (especially the Data check card).

## Standing rules
1. **Never fabricate data:** say what is verified and what isn't, including "not run on a real phone".
2. **Plan before data:** fingerprint (md5), run once, count every attempt, count by week, report true fixed-risk results.
3. **Paper only;** no orders.
4. **No secrets:** no API keys in files or backups, and no phone number anywhere (the guard `tools/nophone.js` holds hashes only).
5. **The original build is always delivered as `omega-v6_5-47.html`.**
6. **Other AIs' reports are views to verify, not to follow.**
7. **Design:** grounded in the subject, real visuals, an obvious starting point; not the generic dark-dashboard shell.

## Paste this to start the next chat
> I'm continuing OMEGA. I've uploaded the carry-over bundle and my data files. Read `OMEGA_CARRYOVER_2026-10-25.md` first, then the handover's newest sections. Next: run the survivorship test on E22 H1/H3 with delisted coins (I've allowed `data.binance.vision`), then the "many small seats" test, written down before running, as before.
