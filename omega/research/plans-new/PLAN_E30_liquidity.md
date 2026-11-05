# PLAN E30 — real liquidity: order-book depth and forced deleveraging (written 2026-10-27 before any depth or metrics data
# has been looked at; the download is running)
DATA: Binance archive, USDT-M futures, 10 coins (BTC, ETH, SOL, BNB, XRP, DOGE, ADA, AVAX, LINK, LTC):
- bookDepth (snapshots ~every 30 s of resting notional within ±1/2/3/4/5% of price), reduced to hourly medians;
  2023-01-01 → 2026-09-30.  - metrics (5-minute open interest, top-trader and account long/short ratios, taker ratio);
  2020-09-01 → 2026-09-30.  - hourly klines from the E25/E26 archive data.
STAGES: depth — DISCOVERY 2023-01 → 2024-12, FINAL 2025-01 → 2026-09 (once). metrics — DISCOVERY 2020-09 → 2023-12,
VALIDATION 2024, FINAL 2025-01 → 2026-09 (once). Every variant counted; a luck check (shuffled signals) per family.
Costs 0.10% a side; funding ignored for holds ≤ 24 h, charged for longer.
L1 SIZE (descriptive, the expected one): thinness = total notional within ±1% / its own 30-day median. Does a thin book predict
  a bigger next-24h move? Rank correlation per coin, pooled; reported with discovery and final.
L2 DIRECTION: imbalance = (bid − ask)/(bid + ask) within ±1%, ±2%, ±5%. Long the coin when imbalance is in its own top 10%
  (30-day window), short in the bottom 10%; hold 1, 4 or 24 h; sign + (follow the heavier side) or − (fade it). 18 variants;
  the best weekly t in discovery goes to final. PASS: weekly t ≥ 2.0, net > 0, positive in 2025 and 2026.
L3 THIN-SIDE: price tends to move toward the thinner side? = L2 with sign −; included in L2's grid.
L4 FORCED DELEVERAGING (the historical version of E13 Q1): an hour where price fell ≥ x and open interest fell ≥ y (positions
  forced out) → long for H hours; compared with the same price falls without an OI drop. x ∈ {2%, 3%, 5%}, y ∈ {0.5%, 1%, 2%},
  H ∈ {4, 24}: 18 variants; best weekly t in discovery → validation 2024 (t ≥ 1.65, same sign) → final once (t ≥ 2.0, net > 0,
  positive in 2025 and 2026). Mirror for squeezes (rose ≥ x, OI fell) reported, not tested.
L5 CROWD POSITIONING: top-trader long/short ratio in its own top/bottom 10% (30-day) → fade it for 24 h; account ratio the
  same. 4 variants; same stages and bars as L4.
Reported whatever happens, with why each failed.
