# E108 — Time-series momentum with volatility targeting on gold futures, daily (swing)
Common rules E100. GC_1d closes. Signal at settlement t: sign of the L-day return, L ∈ {5, 10, 20, 60, 120, 250};
mode long/short or long/flat; exposure = signal × min(1, 10% / EWMA vol (20-day halflife, annualised √252)), cap 1×.
Earn close t → close t+1 (traded post-settle ≈ settle; 1-day-lag result reported as robustness).
Costs: 0.05% of turnover + CFD financing 6.5%/yr/360 × |exposure| per calendar night (stress double). 12 variants.
Control/luck: the signal series circularly shifted by a random offset ≥ 250 days (500 replicates): real best NW t vs
95th pct of the null best t (discovery); in FINAL the chosen rule's mean must beat the 95th pct of its own shifted nulls.
Also report against buy-and-hold with the same vol targeting (long-only vol-target).
