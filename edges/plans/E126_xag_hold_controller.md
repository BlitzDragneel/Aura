# E126 — Silver holding: E85 controller as written, then pre-registered improvements, and silver-vs-gold rotation
(common methods E120)

Daily closes, exposure decided at close t, earned close t → t+1, long or cash only, never above 1×. Cost 0.05% of
turnover (base) / 0.10% (stress). CFD version (info): also 6.5%/yr financing on exposure.
A. E85 exactly as written (1 configuration): exposure = share of positive {20, 60, 120}-day returns × min(1, 10% /
   max(vol20, vol60)), vol annualised with √252.
B. Pre-registered improvements (6 variants), because silver's ~34% annual vol keeps a 10% target near 0.3× forever:
   vol target τ ∈ {15%, 20%, 25%} × lookbacks {(20, 60, 120), (50, 100, 200)}; same formula otherwise.
   Selection by discovery Sharpe; control = volatility-only with the same τ.
C. Rotation (6 variants): hold the metal (silver or gold) with the higher L-day return, L ∈ {60, 120, 250},
   re-decided every 5 trading days (Fridays' closes); variant CASH: hold nothing if the winner's L-day return ≤ 0;
   variant ALWAYS: always hold the winner. Cost 0.05% of turnover per switch side. Comparators: buy-and-hold silver,
   buy-and-hold 50/50 gold/silver (monthly rebalanced), buy-and-hold gold.
Pass (holding, from the brief): VALIDATION and FINAL: Sharpe above buy-and-hold silver AND above the volatility-only
control (A, B) / above 50/50 (C), max drawdown ≤ 0.75× buy-and-hold silver's, and FINAL mean daily return > 0 with
Newey–West t ≥ 2, VALIDATION t ≥ 1.5. Luck (B, C): best discovery Sharpe vs the same grid with signals circularly
shifted (200 shifts). Counted variants: 1 + 6 + 6 = 13.
