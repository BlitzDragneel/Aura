# PLAN E13 — addendum B, written 2026-10-26 before any qualifying recording exists
Context: the export omega-watch-2026-10-19-to-2026-10-26 (sha256 d374b74f…) held 0 minute rows: the live streams delivered
nothing on that device. E13 was NOT RUN on it (0 qualifying days). From v6.5.101 the recorder fills empty minutes from the
exchange's 1-minute candles while a stream is down, and each export's diag.daily[day].bh lists the hours the backup filled
per coin and feed ('SYM|s' spot, 'SYM|p' futures; last 8 days). Rules for E13 from now on:
1. Qualification (5 days with BTC data in ≥ 80% of minutes) counts stream minutes ONLY: hours listed in bh for BTCUSDT|s and
   BTCUSDT|p do not count, unless the other feed was live that hour.
2. Q1 and Q4 (liquidation flushes and squeezes) use only hours in which the futures stream was live (not in bh 'SYM|p'):
   the backup has no liquidations, and an empty hour must not read as "no liquidations".
3. Q2 (absorption) may use backup minutes for the futures taker buy/sell volume and close (the same numbers the stream's
   1-minute candles carry); reported separately as stream-only and all-minutes, judged on stream-only.
4. Q3 (Coinbase leads Binance) uses stream minutes only (backup Coinbase closes are candle closes, not trade-by-trade).
5. Everything else in PLAN E13 and addendum A stands.
