# PLAN E25 — addendum A (written 2026-10-25 before any archive file was listed or downloaded)
1. SYMBOLS: USDT-margined perpetuals = archive folders under data/futures/um/monthly/klines/ named ^[A-Z0-9]+USDT$ (dated
   delivery contracts with "_" excluded). Stablecoin pairs are kept (the plan says every perpetual), and the result without
   them is also reported.
2. FILES: monthly 1h files 2023-10 → 2026-09, daily 1h files 2026-10-01 → 2026-10-18 (the October monthly file does not exist yet).
   2023-10 → 2023-12 serves only as warm-up for thresholds, σ and the 30-day age rule; no trade signals before 2024-01-01.
3. DELISTED = a coin whose last archive candle is before 2026-10-11 00:00 UTC (a week before the end, so a coin merely missing the
   last few daily files is not called delisted). Trades on a coin that is still trading and whose hold runs past 2026-10-18 are
   dropped, as in E22.
4. HOLD EXITS: (a) c[f+24] present → research rule unchanged. (b) the coin's data ends before f+24 (delisted) → exit at the last
   available close − 5%. (c) a gap inside the hold: if the gap is longer than 24 hours → exit at the last close before the gap
   − 5%; otherwise exit at the first close at or after f+24. Same for H3 with t in place of f.
5. DATA CHECK (the plan's precondition): needs the final4 files from Maro's device. Until they arrive, everything is prepared
   (download, symbol list fingerprinted) but NO returns are computed and the test is NOT run.
6. If the S3 listing and the files disagree (a listed file that 404s), the file is retried 3 times, then logged as missing and
   the coin's data treated as having a gap there.
