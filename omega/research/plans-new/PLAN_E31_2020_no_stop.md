# PLAN E31 — 2020, never used for H1/H3 outside the 25 design coins: the rules, and the no-stop small-seat account
Written 2026-10-26 AFTER E26 failed and after exploring why (E26's −10% stop caused chains of stopped trades; the same
account without a stop grew 100 → 576 in 2021–2026). That no-stop account was found by looking, so it is tested here on
data it has never seen.
DATA: Binance archive, USDT perpetuals, hourly, 2019-10 → 2021-01 (warm-up to 2019-12; volume-0 candles missing).
EXCLUDED: the 25 design coins (climax25 list), BTCUSDT and ETHUSDT.
SIGNALS: 2020-01-01 → 2020-12-31. Rules exactly as in E25/E26 (H1 limit 2σ, 3 h, 24 h; H3 q5 + breadth 20%, breadth over all
coins with data, at least 5).
TEST 1 (per trade, m = 2): weekly t ≥ 1.96, net mean > 0, positive in both halves of 2020. Costs as E25.
TEST 2 (accounts, no stop, m = 2: H1 and H3): E26 addendum D's account (5 USDT seats, up to 20, seats reset each Monday,
0.15% (H1) or 0.23% (H3) per trade, delisting 5% against) WITHOUT the disaster stop; 500 random accounts built the same way,
also without a stop. PASS: ends above ≥ 97.5% of random accounts, above 100, max drawdown < 35%.
If too few coins exist (fewer than 30 with data in 2020 after exclusions), report "not testable".
