# PLAN E5 — six markets studied one by one: a profile each, and one honest strategy test each
Written 2026-10-20 before computing any per-market statistic below.
Markets: XAU/USD (gold file, sha256 743289eb…877d2f, hourly, Jul 2020 – Oct 2026) and five Binance spot coins from the
15-minute files (creed15_2/3: DOGE, LINK, LTC, ADA, AVAX), resampled to hours, Jan 2020 (AVAX: Sep 2020) – Oct 2026.
Data status, stated honestly: these series were used before (CREED rules, a flow cross-check, a scalping description,
gold plans E2/E3), but none of the per-market rules below has been computed on them.
Profile (descriptive, whole period, every figure also split 2020–2023 vs 2024–2026 to show if it is stable):
  return and movement by UTC hour; sessions (Asia 00–08, London 08–13, US 13–21, late 21–24); weekdays; typical hourly and
  daily ranges; behaviour after big hourly moves (|z| ≥ 2.5) and after 24-hour breakouts (next 4 and 24 hours); trend or
  reversion (variance ratio over 24 hours); link to the market (crypto: equal-weight index of the 20 majors); taker-buy
  imbalance and the next hour (crypto); volume; costs and sizing on 100 USDT.
Strategy test, per market. Seven rules, positions without stops, costs per side 0.10% (crypto), 0.02% (gold):
  R1 long the session with the best 2020–2023 average; R2 short the session with the worst; R3 follow a 24-hour breakout
  (close beyond the prior 24-hour high/low) for 24 hours; R4 fade it for 24 hours; R5 follow a |z| ≥ 2.5 hour for 4 hours;
  R6 fade it for 4 hours; R7 long above / short below the 200-hour average (switching costs counted).
  Each market's rule = the one with the highest weekly t on 2020–2023 (it must be positive there). Judged ONCE on
  2024-01-01 → 2026-10-18 by weekly P&L: pass if t ≥ 2.40 (one-sided 5% split over 6 markets) and the result is positive
  in 2024, in 2025 and in 2026 so far. Reported whatever happens; nothing is changed after seeing 2024–2026.
