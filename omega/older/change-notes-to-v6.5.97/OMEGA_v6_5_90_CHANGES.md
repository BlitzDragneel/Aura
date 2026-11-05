# OMEGA v6.5.90 — the app no longer sticks; the top 5 coins; forex download (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.90 · build 2026-10-22 01:39 UTC. Made with `python3 patch90.py <v6.5.89 build> <new build>`. It uses
`autocov90.js`, `goldh90.js` and `mprof90.js` (generated from `mprof90_src.js`, the E5/E7 data and `fixtures/E14_*.json`).

## Why the app stuck (fixed)
- **Cause:** v6.5.87's Autopilot job started Market Watch whenever the Autopilot ran, ignoring Market Watch's own switch (off by default). In full mode that streams every trade of 25 coins on spot and futures, plus order books, which is heavy for a phone.
- **Fix:** the job now keeps the recorder running only when it was switched on in Market Watch. Otherwise it reports "Off: switch it on in Market Watch to record (light mode is easiest on a phone)".

## Why OMEGA gives no signals (explained, not changed)
- OMEGA Signals issues a signal only when a condition fires that the phone's Research Lab rated "held out-of-sample".
- The research since then found almost nothing that holds on unseen data, so the gate stays shut. That is the honest state, not a malfunction.
- The page itself says either "N tested conditions are eligible" (waiting for one to fire) or "No condition has held out-of-sample yet".

## Market Profiles: the top 5 coins (plan E14, md5 `368a4474…`)
- **BTC, ETH, SOL, BNB, XRP now come first,** 11 markets in total.
- **Each new profile has:** live data, the clock, sessions, a new **"Who trades it, and when"** table (share of all trading and of aggressive buying by session), behaviour, both directions, what drives it, how to trade and size it, and plan E14's verdict.
- **Plan E14's verdict:** eleven rules (seven two-sided, four short-only), chosen on 2020–23 and judged on 2024–26. **None passed on any of the five.**
- **Findings:**
  - US hours carry 36–42% of trading and the biggest moves.
  - Aggressive buying is 49–50% in every session.
  - The US-hours drift down seen in gold and the altcoins does not hold for BTC, ETH or XRP.
- **Start-here text** updated to cover the eleven markets.

## Research download: + the five forex majors (plan E15, md5 `12f0c70f…`)
- **Symbols:** EUR/USD, GBP/USD, USD/JPY, AUD/USD and USD/CAD added to the Twelve Data hourly download, which the Autopilot also runs.
- **File:** saved as `omega-history-metals-fx1h-*`.
- **Plan E15** profiles and tests them once, like E14, at 0.015% a side.

## Brain and record
- `KN.earlier` gains E14 and E15.
- Research record round 29; the heading now reads rounds 1–29.

## Verification
- **s90 (4 checks):** the Autopilot doesn't start Market Watch unless switched on; the top 5 render with E14 figures, the who-trades-it table, both directions, FAILED, no NaN; forex in the download and its Autopilot job; round 29, E14 and E15 in the Brain.
- **All 24 suites pass** (s49…s90). Version, round and wording checks in s84, s85, s86, s87 and s89 were widened for the new markets and symbols, not weakened.
- **Other checks:** 110 script blocks pass the syntax check; no duplicate ids; phone guard clean; 27-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.**
