# PLAN E22 — making the panic bounce pay: limit entries, extremes only, market-wide panic (written before running)
Written 2026-10-25 after E21 (buying after a coin's bottom-10% 24-hour return: real before costs, but ≈ costs on other coins).
Signal base: the coin's 24-hour log return in its bottom q of the previous 720 hours (thresholds updated daily, causal).
Hold 24 hours, exit at market; no overlapping trades within a coin; coins listed 30+ days.
H1 limit entry (q 10%): a buy limit at C·exp(−k·σ), σ = the coin's hourly standard deviation over the prior 168 hours,
   k ∈ {0.5, 1, 2}; it fills only if a candle in the next W ∈ {3, 6} hours trades BELOW the limit (low < limit); entry at the
   limit; exit 24 hours after the fill hour at market. Costs 0.12% round trip (0.02% maker + 0.05% taker + 0.05% slippage).
   Unfilled signals are no trade. 6 variants.
H2 extremes (taker, 0.20%): q ∈ {5%, 2%, 1%} × volume filter {none, last 24 hours' volume ≥ 2× its 720-hour median}
   × close filter {none, the signal hour closes in the top half of its range}. 12 variants.
H3 market-wide panic (taker, 0.20%): q ∈ {10%, 5%} and at least b ∈ {20%, 40%} of the universe's coins with data are in their
   own bottom 10% in the same hour (the universe = the 25 majors in discovery, the perpetuals in the test). 4 variants.
DISCOVERY on the 25 majors (creed15_1–5), 2020-03 → 2023-12 and 2024-01 → 2026-10-18: a variant qualifies if its NET mean per
   trade is > 0 with weekly t ≥ 2.0 in BOTH periods; each hypothesis keeps its qualifier with the highest min(t, t).
TEST, run ONCE: the kept variants (m ≤ 3) on the Binance perpetuals of the final4 files, 2024-01-01 → 2026-10-18, net of costs.
   Pass: weekly t ≥ the one-sided Bonferroni bar (α 0.05/m), net mean > 0, and positive in 2024, 2025 and 2026.
Reported whatever happens.
