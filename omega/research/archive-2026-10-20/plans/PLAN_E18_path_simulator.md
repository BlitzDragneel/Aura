# PLAN E18 — does a path simulator built on each coin's own measured rules match reality? (written before running)
Written 2026-10-25. Data: omega_history_creed15_1 (BTC, ETH, SOL, BNB, XRP; Binance spot 15-minute → hourly open/high/low/
close), 2020 – Oct 2026. Calibration: 2020-01-01 → 2023-12-31. Test, run ONCE: daily forecast origins at 00:00 UTC from
2024-01-01 to 2026-10-17 (24 hours ahead each), every coin with complete data.
MODEL (fixed in advance; nothing tuned on the test years):
- Volatility: EWMA variance, λ = 0.94 (RiskMetrics), causal (each hour uses returns up to the hour before).
- Hour-of-day pattern: s_h = sqrt(mean(r²/σ²)) per UTC hour, per coin, from calibration only.
- Shock library per coin from calibration hours: z = log(C/Cprev)/(σ·s_h), u = log(H/Cprev)/(σ·s_h), d = log(L/Cprev)/(σ·s_h);
  z de-meaned (direction neutral), u and d shifted by the same amount. Real fat tails, real intrahour ranges.
- Path: 10,000 paths per origin, 24 hourly steps. Each step draws one library hour (z, u, d), scales by the current simulated
  σ and the hour's s_h, records the hour's high/low, moves the close, and updates σ by the same EWMA (volatility feeds itself).
EVENTS per origin, with σ24 = √24·σ(origin) and barriers at k·σ24 above and below the origin close, k ∈ {0.5, 1.0}:
  touch-up (high reaches the upper barrier within 24 h), touch-down, and up-first (upper before lower; an hour that reaches
  both counts as down first, the same convention in simulation and reality). Plus the 24-hour close return.
PASS — all three:
 (a) Coverage: realized 24-hour returns fall inside the simulated central 50%, 90% and 99% ranges at those rates within
     2 percentage points (all coins pooled), and within 4 points for each coin.
 (b) Calibration: for each event family (touch-up, touch-down, up-first, each k), expected calibration error over 10 bins
     ≤ 0.02, and Brier score better than the baseline (the event's constant frequency in the calibration years).
 (c) Tails: realized 24-hour returns beyond the simulated 99% range occur between 0.4% and 2.0% of the time (pooled).
Reported for comparison only: a normal-distribution model with constant calibration volatility.
Reported whatever happens. A pass makes it fit for odds and account futures in OMEGA Prime; a fail means fix or do not ship.
