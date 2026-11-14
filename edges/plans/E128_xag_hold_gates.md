# E128 — Silver holding with moving-average trend gates, incl. gold-gated silver (common methods E120, pass as E126)

Different from E85/E126 (share of positive 20/60/120-day returns): a single price-vs-moving-average gate, and the idea
that gold's trend leads the precious-metals regime (silver = high-beta gold).
Exposure in silver (long or cash), decided at close t: gate_t × size_t.
Gate source ∈ {SILVER: silver close > its MA, GOLD: gold close > its MA, BOTH: both above}, MA ∈ {100, 200} days.
Size ∈ {FULL: 1, VOL: min(1, 20% / vol60)}. Grid 3 × 2 × 2 = 12 variants. Cost 0.05% of turnover (stress 0.10%),
CFD-financing version reported (info).
Controls: buy-and-hold silver; volatility-only with the same size (FULL → buy-and-hold, VOL → min(1, 20%/vol60)).
Selection: highest discovery Sharpe; luck: same grid with gates circularly shifted (200 shifts), 95th pct.
Pass (validation and final): Sharpe > buy-and-hold silver and > its volatility-only control, max drawdown ≤ 0.75×
buy-and-hold's, final NW t ≥ 2 (validation ≥ 1.5).
