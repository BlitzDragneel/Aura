# E66 — Perp premium index extremes (premiumIndexKlines, hourly, 60 coins)
Conventions: `E63_common_bot3.md`. Source: data.binance.vision futures/um premiumIndexKlines 1h (2020 →), 60 coins
(the 30 5m coins + 30 older large coins listed in `edges/research3/fetch_sources.py`, fixed before the data).
## Different from E30/E33 (OI, positioning ratios), E34 (funding harvest) and bot-2's E54 (8h funding, weekly): this is the
**hourly** perp-vs-index premium — a forced-flow dislocation measure — and the trade horizon is 4–24 h.
## Signal: p = premium close of hour t (perp/index − 1). z vs own trailing 720 h (excluding t).
## Hypothesis: perp trading at an extreme discount to spot = forced perp selling → price (and premium) mean-reverts up;
extreme premium = crowded leveraged longs → down.
## Grid (24 variants)
- Z-long: z ≤ −k, k ∈ {3, 4, 5}, H ∈ {4, 12, 24} → long → 9
- Z-short: z ≥ k, same → short → 9
- Raw: p ≤ −0.3% or ≤ −0.6% → long, H ∈ {4, 12, 24} → 6
## Luck check: each coin's premium series circularly shifted by one common random offset (100 shifts).
