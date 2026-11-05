# E67 — Taker buy/sell imbalance (klines taker-buy volume), 1h, liquid top-100 perps
Conventions: `E63_common_bot3.md`. Data: `tbv`/`v` of the 1h klines already on disk (order flow, not price).
Universe: top 100 by trailing 30-day quote volume at each month start (survivorship-free, incl. delisted).
## Signal: r = tbv / v per hour; z = (r − mean_168) / sd_168 (trailing, excl. t); σ-move m = 1h log return / σ168.
## Hypotheses: (X) extreme taker selling into a drop = seller exhaustion → bounce; (M) extreme taker imbalance = informed
flow → continuation.
## Grid (18 variants)
- X: z ≤ −k, k ∈ {2, 3}, with price filter {none, m ≤ −2}, H ∈ {4, 12, 24} → long → 12
- M: z ≥ k → long, z ≤ −k → short (one rule), k ∈ {2, 3}, H ∈ {4, 12, 24} → 6
## Luck check: each coin's r series circularly shifted by a common random offset vs prices (100 shifts).
