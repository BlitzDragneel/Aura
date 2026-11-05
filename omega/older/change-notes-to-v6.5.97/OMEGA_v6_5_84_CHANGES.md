# OMEGA v6.5.84: plan E1's result, the 180.5 correction, and the gold hourly download (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.84 · build 2026-10-20 09:52 UTC. Made with `python3 patch84.py <v6.5.83 build> <new build>` (uses
`bdesk84.js` and `goldh.js`). Nothing outside the Breakout Desk, its gold card and the research record was changed.

## Changes
1. **Setups A and B are marked FAILED.**
   - **Why:** plan E1 ran them once on 2021–2023, with the rules frozen and the pass mark written and fingerprinted first (md5 `d1c0b7d7e0085060681320dc8e381b9d`). A went 100 → 49.1 and B 100 → 27.2. They beat 9% and 2% of coin-flip accounts, against 95% needed.
   - **On the page:** each card shows a FAILED status, a "RECORD ONLY" label and a red box with the numbers and "Do not trade it". The Start-here panel, the banner and the OMEGA Signals line say the same.
   - **Still running:** the paper accounts keep running as a forward record.
   - **Quiet:** no alerts and no menu badge for a failed setup.
2. **Correction: setup A's 180.5.**
   - That figure came from 100 USDT accounts where Binance's 5 USDT minimum rounded 238 of 623 trades above 1% risk.
   - At a true 1% risk, A makes ×1.08. B is barely affected (about 150 at a true 1%).
   - The evidence box now says this; its heading is "What the research found before the clean test".
3. **New: gold and silver hourly download** (bottom of the Breakout Desk; module `OMEGA_GOLDH`). It feeds plan E2.
   - **Source:** XAU/USD and XAG/USD 1-hour candles (UTC) from Twelve Data, 5,000 hours a request, back until Twelve Data has no more (or 2005). About 20–40 requests.
   - **Key and limits:** it uses the key already set in OMEGA and the app's shared Twelve Data queue. A per-minute limit is waited out and retried (up to 3 times). A daily limit stops cleanly.
   - **Resumes:** progress is kept in IndexedDB `omega_goldh`. Pressing Download again continues from the oldest stored hour. "Start over" clears it.
   - **Checks every candle:** one per hour, in order. Impossible candles are dropped, and highs and lows are made consistent; the counts go into the file.
   - **Saves** `omega-history-gold1h-YYYY-MM-DD.json.gz` in the research format (tf 60, the same encoding as the other history files; volume 0, because metals have none at Twelve Data).
   - **Never saves the key:** saving is refused if the file would contain the key or any credential-like field.
4. **Research record:** round 20 (the management search, the new method, the correction and plan E1). The heading now reads rounds 1–20.

## Plan E2 (in the research archive and the build kit)
`PLAN_E2_gold_hourly.md`, md5 `a065c880bfa39435532e8c529cd4ad51`, written before any gold hourly data existed.
- **Entry:** a 72-hour breakout in US hours, with no volume filter.
- **M1:** the owner's 5-unit method.
- **M2:** the new method (limit entry 0.5 ATR back, 3 ATR stop, half off at +1R, 3 ATR trail).
- **Account:** a true 1% risk, 0.05% costs a side (0.10% also reported).
- **Pass, for each method:** the account ends above 100, beats 97.5% of 200 coin-flip accounts, and at least half the calendar years end positive.
- **Analysis script:** `plans/e2_run.py`, dry-run successfully on a synthetic file made by the app's own encoder.

## Verification
- **Suites:** all 18 pass: s49, s50, s58, s60, s62, s67, s69, s70, s71, s73, s77, s78, s79, s80, s81, s82, s83, s84.
  - s82's heading check now accepts rounds 1–18, 1–19 or 1–20.
  - s83 tests the judging rules with A's failure mark set aside.
- **s84 (16 checks):**
  - the failure marks and the correction;
  - no alerts for failed setups;
  - datetimes read as UTC;
  - candle checks;
  - an encoding round trip, cross-checked by the Python research decoder;
  - paging with a minute-limit retry, a daily-limit stop with progress kept, and resuming from the oldest stored hour;
  - the file format with no key, and a save refused when a credential would leak;
  - a browser run: Download, Save, and the gzip file read back (6,200 and 3,000 hours, no key); both setups show FAILED; no NaN, no overflow, no page errors.
- **Bugs found and fixed by s84:**
  - after a daily-limit stop, the card did not show the progress that had been kept;
  - a failed setup showed "TOO EARLY" before its first check.
- **Other checks:** `node --check` passes on all 106 script blocks; no duplicate ids; phone guard clean; 25-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.**

## Files
- **New:** `bdesk84.js`, `goldh.js`, `patch84.py`, `s84_test.js`, `PLAN_E2_gold_hourly.md`.
- **Updated:** `s82_test.js`, `s83_test.js`.
- `bdesk.js` and `patch83.py` stay as they were, so v6.5.83 can still be rebuilt.
