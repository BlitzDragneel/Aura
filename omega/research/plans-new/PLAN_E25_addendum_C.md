# PLAN E25 — addendum C (written 2026-10-25 before any comparison of prices and before any returns, signals or trades)
1. DATA CHECK, standing in until the final4 files arrive: fixtures/bdesk40.json (40 perpetuals, hourly, 2025-05 → 2025-10, cut by
   research/mkfixture.py from the final4-based hourly table) against the archive's closes for the same coin and hour (volume > 0).
   PASS: at least 95% of the fixture's hours found in the archive, median |close ratio − 1| < 0.01% and 99th percentile < 0.1%.
   FAIL → stop, no run, report.
2. If it passes, E25 runs ONCE now. When the final4 files arrive, the plan's own check (all final4 coins, all hours) is run and
   reported; if it fails, this E25 result is VOID (not re-run on adjusted data without a new written plan).
3. Side-report lists, fixed now by name (E25_exclusions.json): stablecoin pairs = USDCUSDT; non-crypto = the 181 stock, ETF,
   index, metal, commodity and FX contracts listed there (pre-IPO contracts included; ambiguous names that are also crypto
   tokens, such as DIA, T, C, ON, are left as crypto).
