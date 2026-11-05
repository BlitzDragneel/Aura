# OMEGA v6.5.101 — Market Watch recorder: backup when the live streams are dead (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.101 · build 2026-10-26 18:31 UTC. Made with `python3 patch101.py <v6.5.100 build> <new build>`.

## Why
The export `omega-watch-2026-10-19-to-2026-10-26` (sha256 d374b74f…) held **0 minute rows** for all 25 coins and no market
rows or flight recordings, although the app was open on 4 days (its order-book snapshots, taken with ordinary requests,
are there: 93 per coin, 20, 22, 23 and 26 Oct). Minutes are kept 14 days, so nothing was pruned: the live streams
(websockets) delivered nothing on that device. Ordinary requests worked. The cause could not be checked from Claude's
sandbox (it cannot reach any stream host): the card's feed pills on that device would have said it ("blocked",
"connected but no data", "reconnecting").

## Changed (Market Watch only, plus two rows in the research card)
1. **Spot stream addresses rotate:** `:9443` → `:443` → `data-stream.binance.vision` when the stream never comes alive.
   A connection that stays silent for 90 s is closed, so the rotation happens.
2. **Backup from 1-minute candles:** while a feed is not live, every minute its empty minutes are filled from the exchange's
   1-minute candles (Binance spot, with data-api.binance.vision as second host; Binance futures; Coinbase closes): close,
   taker buy/sell volume, trade count, spot high/low, BTC/ETH market prices. **Never overwrites stream data**, only minutes
   since recording started. Liquidations, large orders and flight recordings still need the live stream.
3. **Every export has `diag`:** each feed's state, messages, bytes, last error, close code, whether it was ever live, address
   rotations and address; the backup's counts; a daily log (last 30 days) of live and dead minutes per feed, and the hours the
   backup filled per coin and feed (last 8 days). A file now explains itself.
4. **The card says when the backup is on** and what it cannot capture.
5. **Research card:** E15 FAILED (forex majors) and E13 WAITING (with the reason).
Research side: `mwload.py` no longer crashes on coins with no rows; `e13_run.py` reports "not run" for such files.

## Tests
New **s101** (7): dead streams → minutes filled with the exchange's exact values; no overwrite; the three addresses;
the export holds rows and diag with the backup's hours; the card's notice; E15/E13 rows. All earlier suites: 32 of 36
pass in full (s67, s69, s79 and one s77 check need research files missing from the bundle). Crawl 28 pages: 0 errors.
117 script blocks, 0 syntax errors. Phone guard clean. **Not run on a real phone, and not against the real streams.**
