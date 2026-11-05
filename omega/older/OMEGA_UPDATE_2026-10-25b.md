# OMEGA — update, 25 Oct 2026 (afternoon). Read after OMEGA_CARRYOVER_2026-10-25.md.

## Checked
- Bundle intact; the loose Prime file and note match the bundle copies (md5). Original build reports v6.5.97 · 2026-10-25 10:47 UTC.
- Prime: s_prime_test.js 10/10.
- Original build, the 31 current suites: 27 pass in full. s77: 26/27, the one check needs research/watch16.py.
  s67, s69, s79 stop on missing reference files (research/partB_fresh.json, round12_final.json, round17.json; s69 passed its
  first 8 checks first). These 4 files are NOT in the carry-over bundle: a bundle gap, not a build fault (the build is unchanged).
- Network from Claude's sandbox: github.com and pypi.org work; every Binance address (fapi, data.binance.vision,
  data-api.binance.vision), bybit, okx, bls.gov and dukascopy do NOT resolve, though some are on the allowed list.

## Written down before any data (md5 in the .md5 files)
- PLAN E25 survivorship (H1/H3 with delisted perpetuals) b9c9e56ba637f0860cf497709a7b6f79
- PLAN E26 many small seats (5 and 10 USDT seats, −10% stop) 41209e27c2efff1e0556bff6a7941778
- PLAN E27 US CPI release hours (size first, trade second) 64f8ca998598618037e0380ed97b7f31

## New: OMEGA Recorder 1.0.0 (omega-recorder-1.0.0.tar.gz)
FastAPI + SQLite, public Binance data only. Records symbols and delistings, hourly candles (all), 1-minute candles (top 40),
mark/funding (5 min), funding history, open interest and long/short ratios (top 40), liquidations (stream), order-book
summaries (top 10); backfills from data.binance.vision including delisted coins. Serves /health, data endpoints, /panic, the
H1/H3 forward paper record (/signals), events, and exports in the research loader's format. 13 tests pass; H1/H3 match the
research engine trade for trade. Never run against real Binance (unreachable from the sandbox): run `selfcheck` first.
