# BTC research bot — common conventions for E86–E99 (written 14 Nov 2026, before any E86+ test was run)

Binding: edges/ASSETS_BRIEF.md, edges/PROTOCOL.md. Code: `edges/research_btc/`. Instrument: Binance BTCUSDT USDT-M perp.

## Data and bars
- 1h: `/home/user/data/1h/BTCUSDT.parquet` (2020-01 → 2026-11-03). 5m: `/home/user/data/5m/BTCUSDT.parquet` (2022-01 →).
- 15m bars are built from 5m (`research1/lib1.load_tf`: a 15m bar exists only if all three 5m bars exist).
- Daily bars = UTC days built from 1h (a day exists if ≥ 20 hourly bars exist; close = last close of the day).
- Funding: `/home/user/data/funding/BTCUSDT.parquet` (ends 2026-10-31; later stamps charged at 0.01%/8h to longs).

## Periods (ASSETS_BRIEF, fixed)
BTC 1h/daily: DISCOVERY 2020–2023, VALIDATION 2024, FINAL 2025-01 → end of data. BTC 5m/15m: DISCOVERY 2022–2023,
VALIDATION 2024, FINAL 2025-01 → end. A trade belongs to the period of its entry time.

## Costs
- Taker per side 0.05% + 0.02% slippage (= `bt.round_trip_cost` for BTC's > 1e9 USDT daily volume): 0.14% round trip.
- Maker 0.02% per side, no slippage, only when a later bar trades THROUGH the limit (low < limit for a buy, high > limit
  for a sell); a limit touched but not crossed is NOT filled.
- Funding: each 00/08/16 UTC settlement strictly after entry and at/before exit is charged (long pays the rate, short
  receives), for every hold (not only > 8 h — stricter than PROTOCOL).
- Holding rules (daily exposure series): 0.10% of turnover + funding × exposure.
- Stress = double the per-side fee/slippage.

## Statistics and pass mark
- Intraday/event trades: mean net per trade, week-clustered t (`bt.tstat_weekly`). Daily return series: Newey–West t
  with 10 lags (stated per plan).
- PASS (all): FINAL mean > 0 with t ≥ 2; VALIDATION mean > 0 with t ≥ 1.5; luck check ≥ 95th percentile; positive in
  ≥ 60% of calendar years; FINAL without the best 5% of trades reported; ≥ 100 FINAL trades (or ≥ 50 with t ≥ 3); beats
  the plan's simple control (random-entry / vol-clock for day & swing; buy-and-hold Sharpe AND drawdown for holding).
- Grades A/B/C as in PROTOCOL/brief. Leverage table (`bt.leverage_table`, mae-based) for anything that passes.

## Selection and luck check
- Discovery: every variant logged with `bt.log_attempt(md5, name, "discovery", stats)`; selection = highest discovery t
  among variants with mean > 0, n ≥ 100 (day) / n ≥ 30 (swing), and discovery years positive: both
  years for 5m/15m plans; ≥ 3 of 4 for 1h/daily plans.
- Luck check: the plan's whole grid re-run with each variant's entries replaced by the same number of entries at random
  bar times (same side mix, same exit mechanics), 200 runs; null = best t of each run; real best t must be ≥ its 95th pct.
- Only the selected variant goes to VALIDATION; only if VALIDATION passes (> 0, t ≥ 1.5) does it go to FINAL. Variants
  that do not reach FINAL may be shown on FINAL as "information only" when the plan says so — never re-selected after.
- Rules re-run from the external handoff (E86/E87) are NOT searched: one pre-stated configuration per family, reported
  on all periods at once (that is a replication of a published claim), and judged by the same pass mark.
