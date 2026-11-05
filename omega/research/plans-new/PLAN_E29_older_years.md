# PLAN E29 — H1 and H3 in years they were never tested on: 2021-01 → 2023-09, delisted coins included (written before running)
Written 2026-10-26, after E25 (passed, data check passed) and E28 (failed). Data: Binance archive, USDT perpetuals, hourly,
2020-11 → 2026-10 (the E25 download plus 2020-11 → 2023-09, downloaded 25 Oct; volume-0 candles missing), joined per coin.
RULES: E22's H1 and H3 exactly as in E25 (same code path: e25_run.py's run/exit_px, addenda A and B; delisted = last traded
hour before 2026-10-11, so a coin delisted in 2022 counts as delisted).
SIGNALS: 2021-01-01 → 2023-09-30 (2020-11/12 is warm-up only).
WHAT THIS PERIOD HAS SEEN BEFORE (so it is NOT untouched): E22 designed H1/H3 on 25 majors over 2020-03 → 2023-12; E24 used
final4's surviving perpetuals 2021–2023 for a two-seat account built on H1 signals. Therefore the MAIN test EXCLUDES the 25
design coins (climax25 list), and delisted coins (never in any earlier file) are reported separately as the cleanest slice.
BAR (m = 2): weekly t ≥ 1.96, net mean > 0, and positive in each of 2021, 2022 and 2023 (2022 was a bear market: this is the
hard part). Reported whatever happens, with: the 25 design coins alone; delisted coins alone; without the best 5% of trades;
by year; worst 10.
