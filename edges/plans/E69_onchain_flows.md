# E69 — On-chain exchange flows and activity (CoinMetrics community), daily, BTC & ETH
Conventions: `E63_common_bot3.md`. Source: community-api.coinmetrics.io (FlowInExNtv, FlowOutExNtv, SplyExNtv, AdrActCnt),
daily 2018 →. Entry D+1 04:00 UTC for day-D values.
## Hypothesis: big net outflows from exchanges (coins withdrawn to custody) precede strength; big inflows (coins sent to sell)
precede weakness; rising activity leads price.
## Signals: NF7 = 7-day sum of (In − Out) / SplyExNtv; z of NF7 vs trailing 365 d. dS30 = 30-d change of ln SplyExNtv.
A7 = 7-d mean active addresses / prior 28-d mean − 1, z vs trailing 365 d.
## Grid (22 variants)
- Out: z(NF7) ≤ −k → long; In: z(NF7) ≥ k → short; k ∈ {1.5, 2, 2.5}, H ∈ {3, 7, 14} d → 18
- Supply: dS30 ≤ trailing-365-d 10th pct → long, H ∈ {7, 14} → 2
- Activity: z(A7) ≥ 2 → long, H ∈ {7, 14} → 2
BTC and ETH pooled, each on its own metrics. Luck check: metrics circularly shifted (200 shifts).
