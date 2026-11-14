# E100 — Gold (XAU) research bot: common rules for E101–E113 (written 14 Nov 2026, before any test below was run)
Binding: edges/ASSETS_BRIEF.md, edges/PROTOCOL.md. Code: edges/assets/XAU/code/. Results: edges/results/E1xx_result.json.

## Data (no fabrication; what is missing is said)
- GC_1d (Yahoo GC=F settlement closes 2000-08 → 2026-11-13). 2000–07 bars are often flat-filled (o=h=l=c, v=0): daily
  rules use CLOSES ONLY. GC_1h (Yahoo, 2024-06-24 → 2026-11-13, CME hours; the daily break is 17:00–18:00 Chicago =
  22–23 UTC winter / 21–22 UTC summer, handled with zoneinfo).
- PAXG_1h / PAXG_15m (Binance PAXGUSDT spot, 2020-08-28 → 2026-10-31): a 24/7 gold-backed token, used as a PROXY for the
  gold PRICE (hourly log-return correlation with GC 0.984). XAUUSDT_perp_15m/1h + funding (Binance USD-M, 2025-12-11 →
  2026-11-13): too short to judge anything; used for the handoff replication on its own sample and description only.
- DXY_1d (Yahoo DX-Y.NYB), IRX_1d (13-week T-bill yield), TNX_1d (10-y yield), 2000 → 2026-11: honest USD/cash proxies.
- FOMC statement dates parsed from federalreserve.gov (fomccalendars.htm + fomchistorical2020.htm), scheduled only.
  BLS (CPI, NFP, PPI) schedule pages answer HTTP 403 from this machine → CPI/NFP/PPI tests are SKIPPED (not typed from memory).
- Not available: Dukascopy XAUUSD bid/ask (brief: do not try), so the handoff's "native XAUUSD replay" cannot be redone exactly.

## Periods (from the brief, fixed)
| data | DISCOVERY | VALIDATION | FINAL (once) |
|---|---|---|---|
| GC daily | 2000-08 → 2015-12 | 2016 → 2020 | 2021-01 → 2026-11 |
| PAXG 1h/15m | 2020-08 → 2023-12 | 2024 | 2025-01 → 2026-10 |
| GC 1h | 2024-06 → 2025-06 | 2025-07 → 2025-12 | 2026-01 → 2026-11 |
Day rules are SEARCHED on PAXG discovery only; validation PAXG 2024; FINAL = PAXG 2025-01 → 2026-10 (t ≥ 2, primary,
week-clustered) AND GC 1h 2026-01 → 2026-11 mean > 0 (secondary, the real futures; reported with its t; small sample).
GC 1h 2024-06 → 2025-12 is reported as information. Already seen: plans E3/E5 (Oct 2026, old handover) looked at XAU/USD
hourly 2020-07 → 2026-10 descriptively and found "up outside US hours, down 13–21 UTC". Any session split that matches
that pattern is therefore NOT untouched in validation/final; it is labelled so and can at best be grade B.

## Costs (vehicle = XAUUSD CFD / gold futures; brief)
- Base: spread 0.02% per side; financing 6.5%/yr ÷ 360 per night held across 17:00 New York (rollover), long or short.
- Stress: double both. Information: PAXG 0.10%/side; Binance XAUUSDT perp taker 0.05% + 0.02% slippage per side.
- Daily rules: 0.05% of turnover (brief) + CFD financing per day held for swing rules; HOLDING rules are judged as an
  unfunded holding (ETF/physical-like, 0.05% of turnover, cash earns the 13-week T-bill when out) and the CFD-financed
  number is reported too.

## Statistics and pass mark (brief + PROTOCOL; never lowered for small samples)
- Intraday: mean net per trade, week-clustered t (bt.tstat_weekly). Daily: daily net return series, Newey–West t (10 lags).
- PASS needs: FINAL mean > 0 with t ≥ 2; VALIDATION mean > 0 with t ≥ 1.5; ≥ 60% of calendar years positive (halves for
  hourly GC); FINAL without the best 5% of trades reported; beats the plan's control (day/swing: random-time or
  circularly-shifted-signal control, real ≥ 95th percentile; hold: Sharpe above buy-and-hold AND above volatility-only
  with drawdown ≥ 25% smaller than buy-and-hold); ≥ 100 FINAL trades or ≥ 50 with t ≥ 3 (intraday).
- Luck check in DISCOVERY: best t of the real grid vs the 95th percentile of the best t of the same grid on null data
  (null defined per plan, ≥ 200 replicates unless stated).
- Selection: in discovery only variants with t ≥ 2 and ≥ 60% positive years are eligible; ≤ 2 per plan go to
  validation; the one with the higher validation t that meets validation goes to FINAL; FINAL is run once.
- Grades: A all; B passes with one weak point (stress cost, GC secondary, years, trade count, contaminated period);
  C = discovery + validation only (watch list). Every evaluated variant is logged with bt.log_attempt.
- Leverage table (bt.leverage_table, mae-based) for anything that passes.
