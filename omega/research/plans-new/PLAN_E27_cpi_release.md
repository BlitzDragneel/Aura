# PLAN E27 — US CPI release hours in crypto (written before running)
Written 2026-10-25. No CPI dates have been collected yet; none are assumed here.
EVENT LIST: every US CPI release from 2020-03 to 2026-10-18 taken from the official BLS release archive (bls.gov), each with
its date and 08:30 New York time converted to UTC (13:30 in winter, 12:30 in summer). The list is fingerprinted (md5) before
any price data is read. Releases moved by shutdowns use their actual date.
RELEASE HOUR = the UTC hourly candle that contains 08:30 New York time. CONTROL HOURS = the same UTC hour on every other
weekday that is not a CPI, FOMC-decision or US-holiday day.
A (size, the expected one — size is predictable): on BTC and ETH (creed15, 2020-03 → 2026-10-18) and on the median of the
perpetuals with data (final4, 2024 → 2026-10-18): the median |hourly log return| in release hours divided by the median in
control hours. PASS: ratio ≥ 1.5 on BTC, ETH and the perpetuals' median, with a permutation p ≤ 0.01 (10,000 shuffles of the
CPI label among release + control days).
B (trade, the doubtful one): if BTC's release-hour return is ≤ −2σ (σ = prior 168-hour stdev), buy BTC at the next hour's open,
hold 24 hours, 0.10% a side. And the mirror (≥ +2σ, sell) reported separately, not tested (shorts failed before).
PASS (too few events for a weekly t): sign test p ≤ 0.05 one-sided AND mean > 0 in both halves
(2020-03 → 2023-06, 2023-07 → 2026-10). Expected events: few; if fewer than 15 qualify, B is reported as "not testable".
WHAT A PASS OF A WOULD MEAN in the apps: a measured "expect N× normal movement" note on CPI days (Prime already holds off
around CPI); it does not say which way.
Reported whatever happens.
