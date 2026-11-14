# E114 — Hourly panic bounce / spike fade adapted to gold (day/swing ≤ 24 h)
Common rules E100. PAXG_1h search (2020-08 → 2023), validation 2024, FINAL PAXG 2025-01 → 2026-10 (+ GC_1h 2026
secondary). σ = std of the prior 720 hourly log returns. Trigger at the close of hour t: r_t ≤ −k·σ (DOWN, trade LONG =
panic bounce) or r_t ≥ +k·σ (UP, trade SHORT = spike fade), k ∈ {3, 4}. Entry: MKT = open of t+1; LIM = limit at
C_t·exp(∓2σ) valid 3 bars, filled only if a bar trades THROUGH it (low < limit for longs). Hold H ∈ {6, 12, 24} h after
entry, exit at the close. One position at a time per side. Trades whose holding window would include the CFD weekend
closure (Fri 17:00 → Sun 18:00 New York) are skipped (signal in PAXG's weekend hours ignored).
2 sides × 2 k × 2 entries × 3 holds = 24 variants. Costs CFD 0.02%/side + financing per 17:00 NY rollover; stress 2×.
Luck: the same grid with the trigger hours replaced by random hours (same count per variant, weekend rule kept), 200
replicates; real best t vs 95th pct. FINAL control: random-time entries, same side/entry/hold, mean ≥ 95th pct.
