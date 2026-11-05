# PLAN E28 — new angles: the inverse, the entry method, BTC leading, and when the market moves (written before running)
Written 2026-10-26 after E25 confirmed H1/H3 (data check vs final4: PASS). Nothing below has been run.
DATA: the E25 archive set (USDT perpetuals, delisted included, volume-0 candles missing; data md5 b0cc408e…), hourly.
DISCOVERY 2023-11-01 → 2025-04-30. CONFIRMATION 2025-05-01 → 2026-10-18, run ONCE, only for variants kept in discovery.
Rules common to all: signals at an hour's close; coins with 30+ days of data; no overlapping trades per coin per variant;
exits as E25 (delisted: last close with 5% against the trade; gap > 24 h: last close before it, 5% against).
Costs: limit entries 0.12% round trip (maker + taker + slippage); market entries 0.20%.

FAMILY A — the inverse of H1 ("blow-off fade", SHORT): a coin's 24-hour return in its own TOP 10% (720-hour thresholds set
daily); a SELL limit at C·exp(+kσ) (σ = 168 prior hourly returns); fills if a candle in the next 3 hours trades ABOVE it;
covered at the close 24 hours after the fill. k ∈ {1, 2, 3}. (Funding not counted, as in H1.)
FAMILY B — the entry method without the panic (is H1's edge the panic or the limit order?): every day at 00:00 UTC, for every
coin, a BUY limit at C·exp(−k·σ·√24) valid 24 hours; filled if a low trades below it; sold at the close 24 hours after the fill
hour. k ∈ {1, 1.5, 2}.
FAMILY C — BTC leads, alts follow (catch-up): in an hour when BTC's return is ≥ +2σ_BTC, BUY at the close every coin whose
same-hour return is below a quarter of BTC's; when BTC's return is ≤ −2σ_BTC, SELL every coin that fell less than a quarter of
BTC's fall. Hold h ∈ {1, 4} hours. Variants: {up-long, down-short} × {1, 4} = 4.
SELECTION (discovery): a variant qualifies if net mean > 0 and weekly t ≥ 2.0; each family keeps its qualifier with the
highest t. m = number of families with a kept variant (0–3).
CONFIRMATION, run once: PASS if weekly t ≥ the one-sided Bonferroni bar (α 0.05/m), net mean > 0, and positive in both halves
(2025-05 → 2025-12 and 2026-01 → 2026-10). Reported whatever happens, with the result without the best 5% of trades.

DESCRIPTIVE (no pass/fail; knowledge for the app, each checked for stability between the two periods):
D1 When the market moves: median |hourly return| and median hourly range by UTC hour and by weekday, for BTC, ETH and the
   median coin; stability = rank correlation of the hour profile between discovery and confirmation.
D2 BTC and the market: same-hour beta and correlation of each coin to BTC; next-hour correlation (does BTC lead by an hour?);
   on the 15-minute majors (creed15 files 1, 3, 4, 5; file 2 missing) the same at 15 minutes.
D3 Movement after big moves: for |hourly z| ≥ 3, the next 1/4/24-hour |return| relative to normal (size persistence).
