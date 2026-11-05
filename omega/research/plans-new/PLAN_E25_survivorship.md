# PLAN E25 — survivorship: E22 H1 and H3 with delisted perpetuals included (written before running)
Written 2026-10-25, before any delisted data has been downloaded or seen.
WHY: E22's test universe (final4 files) holds only perpetuals still listed on 2026-10-19. Coins that were delisted are
missing, and panic-buying strategies are exactly the kind that buy coins on their way to delisting.

RULES, copied unchanged from E22's kept variants (e22_lib.py):
- H1: 24-hour log return in the coin's bottom 10% of the previous 720 hours (thresholds updated daily, causal); buy limit at
  C·exp(−2σ), σ = hourly stdev over the prior 168 hours; fills only if a candle in the next 3 hours trades BELOW the limit;
  exit at market 24 hours after the fill hour; 0.12% round trip; no overlapping trades within a coin.
- H3: 24-hour return in the bottom 5% AND at least 20% of coins with data in their own bottom 10% in the same hour; buy at the
  signal close (taker), exit 24 hours later; 0.20% round trip.
- Coins listed 30+ days (720 hours of history) before a signal counts.

UNIVERSE: every USDT-margined perpetual with hourly klines on data.binance.vision (futures/um) at any time between
2024-01-01 and 2026-10-18 — listed, delisted and settled alike. The symbol list is taken from the archive's own listing and
fingerprinted (md5 of the sorted list) BEFORE any returns are computed. Breadth for H3 is recomputed on this full universe.
DELISTING RULE (decided now): if a coin's data ends during a hold, the trade exits at the LAST available close, then a further
−5% haircut is charged (a delisting usually ends in a thin, falling market). A coin whose data has a gap > 24 hours during a
hold is treated the same way at the last close before the gap.
DATA CHECK before the run: the archive's candles for coins that ARE in final4 must match final4 closes (median absolute
difference < 0.01%); if not, stop and report, no test.

TEST, run ONCE, period 2024-01-01 → 2026-10-18 (same as E22). m = 2, one-sided Bonferroni bar t ≥ 1.96 (α 0.025 each).
PASS per hypothesis: weekly t ≥ 1.96, net mean > 0, positive in 2024, 2025 and 2026 — the same bar E22 used, on the bigger
universe.
ALSO REPORTED (not pass/fail): the result on delisted coins alone; the share of trades on coins delisted within 90 days of the
trade; the result without the best 5% of trades; the worst 10 trades.
Reported whatever happens. If H1 or H3 fails here, it is demoted from Grade B to "failed" in both apps.
