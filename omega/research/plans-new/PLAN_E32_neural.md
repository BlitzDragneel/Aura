# PLAN E32 — a neural network that learns daily trades (written 2026-10-27 before any model is trained)
DATA: the E28 daily panel (903 USDT perpetuals incl. 163 delisted, top 100 by dollar volume each day, costs 0.10% a side, real
funding, 5% delisting penalty). Inputs at each close: the 33 E28 features plus 1- and 7-day funding, each turned into its
cross-sectional percentile rank that day (35 inputs). Label: the coin's next-day return, as a cross-sectional percentile rank.
STAGES (as E28): TRAIN 2021-01-01 → 2023-12-31; SELECT on 2024; FINAL 2025-01-01 → 2026-09-30 once. The final period has not
been used by any daily rule.
MODELS: sklearn MLPRegressor (ReLU, Adam, early stopping inside the training years, seed 32), hidden layers (16), (32, 16),
(64, 32) × L2 alpha 1e-4, 1e-2 = 6 models, plus a linear ridge model (reported, not selected). The one with the best 2024
weekly t of the trading rule below is the only model run on the final period. Every model counts as a try (total so far:
9,240 daily rules in E28).
TRADING RULE: rank coins by the model's score each day; hold 10 long and 10 short (5 USDT each on 100 USDT), daily band × 3
(E28 round 3's executable form). Also reported: long-only top 10.
LUCK CHECK: the whole pipeline (6 models, same selection) retrained on labels shuffled within each day, 3 times; its best 2024 t
is reported beside the real one.
PASS: final weekly t ≥ 2.0, net mean > 0, positive in 2025 and 2026, and the 100 USDT version's max drawdown < 35%.
