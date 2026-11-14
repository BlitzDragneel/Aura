# E113 — Volatility-managed gold holding (confirmatory; CONTAMINATED — grade C at most)
Written after E111. Honest status: the "volatility-only" exposure min(1, 10%/max(vol20, vol60)) was a CONTROL in E85
(lead) and E111 (this bot) and its Sharpe was seen in every period (above buy-and-hold in all of them). Nothing here is
untouched, so this plan can at most give a grade C ("best-evidence holding rule / risk tool"), never a PASS.
Rule (fixed, no new parameters): exposure_t = min(1, 10% / max(vol20, vol60)) (annualised √252 from daily GC=F
settlement log returns), decided at settle t, rebalanced only when |Δ| ≥ 0.10; unfunded holding, 0.05% of turnover;
cash earns the 13-week T-bill (^IRX). Secondary (reported, not chosen): 15% target.
Tests: (1) luck — discovery (2000-08 → 2015) excess-return Sharpe gain over buy-and-hold vs the same rule with the
volatility series circularly shifted by ≥ 250 days (500 replicates): real ≥ 95th pct; (2) validation 2016–20 and FINAL
2021 → 2026-11: excess Sharpe above buy-and-hold and max drawdown ≥ 25% smaller; (3) whole-sample significance of the
Sharpe difference by a 20-day block bootstrap (2,000 replicates), one-sided p reported; (4) 1-day-lag robustness;
(5) CFD-financed version reported (6.5%/yr on exposure).
