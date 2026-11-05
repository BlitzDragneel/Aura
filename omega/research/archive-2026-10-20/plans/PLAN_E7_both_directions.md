# PLAN E7 — both directions: how each market falls and rises, and a short-only strategy test
Written 2026-10-20, before computing anything below. Markets and data as plan E5 (gold hourly Jul 2020 – Oct 2026;
DOGE, LINK, LTC, ADA, AVAX hourly from the 15-minute files, Jan 2020 – Oct 2026). Data status: already used, but no
short-only rule below has been computed on it.
Part 1, anatomy (descriptive, whole period and split 2020–23 / 2024–26): share of up hours and days; average up hour vs
down hour; the worst and best 1% of hours; the biggest 24-hour drop and rise; how long declines (peak to trough, 10%+ for
coins, 3%+ for gold) and rallies last and how deep they go; volatility in the 24 hours after a big down hour vs after a big
up hour; in which session the big down and big up hours happen; the direction split of plan E5's two-sided rules.
Part 2, short-only rules (costs per side 0.10% coins, 0.02% gold; no funding credit, which usually favours shorts, so
results are if anything understated):
  S1 blow-off short (mirror of the climax reversal): an hour up 3σ or more (σ of the 168 hours before), on 3× the 168-hour
     median volume (coins only; gold has no volume), closing in the bottom 40% of its range → short at the next open,
     cover 12 hours later.
  S2 failed breakout: the hour's high exceeds the prior 24-hour high but it closes back below it → short at the next open,
     cover 24 hours later.
  S3 downtrend, US hours: on days when the 13:00 UTC bar opens below the 200-hour average, short the bars opening
     13:00–20:00; flat otherwise.
  S4 breakdown in a downtrend: a close below the prior 72-hour low while below the 200-hour average → short at the next
     open, cover 24 hours later.
  Each market's rule = the highest weekly t on 2020–2023 (must be positive there); judged ONCE on 2024-01-01 →
  2026-10-18: pass if t ≥ 2.40 and positive in 2024, 2025 and 2026. Positions do not overlap. Reported whatever happens.
