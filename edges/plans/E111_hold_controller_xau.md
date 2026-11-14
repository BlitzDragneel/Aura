# E111 — Holding gold or cash: improved trend/vol controllers (registered variants, judged vs buy-and-hold and vol-only)
Common rules E100. GC_1d closes, holding as an unfunded position (0.05% of turnover; cash earns the 13-week T-bill from
^IRX when not invested). Weekly decisions are not used; daily rebalance only when |Δexposure| ≥ 0.10 (all variants).
  V1 SMA200: long if close > 200-day mean. V2 Faber 10-month: month-end close > 10-month mean, held for the next month.
  V3 12-1 momentum: month-end 12-month return excluding the last month > 0. V4 E85 participation {60,120,250} × 10% vol.
  V5 E85 original lookbacks {20,60,120} × 15% vol target. V6 participation {60,120,250} × 15% vol.
  V7 V1 × 15% vol target. V8 dual: long if 12-month gold return > 12-month T-bill return (absolute momentum vs cash).
Controls: buy-and-hold; volatility-only at the SAME target as the variant (10% or 15%); for V1–V3, V8 vol-only = B&H.
Pass (E100 hold): in VALIDATION and FINAL, Sharpe (daily, cash-inclusive) > buy-and-hold AND > matched vol-only, max
drawdown ≥ 25% smaller than buy-and-hold. Luck: discovery Sharpe gain over matched vol-only vs 95th pct of the same gain
with the trend signal circularly shifted (300 replicates). The E85 rule is re-reported on these periods.
CFD-financed numbers (6.5%/yr) reported to show what holding through a CFD costs.
