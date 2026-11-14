# E85 — Trend/volatility long-or-cash controller from the external handoff (lead, 14 Nov 2026)
Source: OMEGA-HANDOFF (12–14 Nov 2026, another assistant's research, reconstructed from memory; its own files are lost).
Rule, exactly as written there, one configuration, no tuning:
  participation_t = share of {20, 60, 120}-day returns that are positive (0, 1/3, 2/3, 1)
  scale_t = min(1, 10% / max(vol20_t, vol60_t)), vol = annualised std of daily log returns (sqrt 365 BTC, sqrt 252 gold)
  exposure_t = participation_t × scale_t (long or cash, never short, never above 1×), held over the NEXT day (1-day lag).
Assets: BTC (Binance USDT-M perpetual daily closes, funding charged on exposure), gold (Yahoo GC=F daily closes).
Costs: 0.10% of turnover for BTC, 0.05% for gold; stress run at double.
Comparators: buy-and-hold; volatility-only (exposure = scale_t); trend-only (exposure = participation_t).
Periods: BTC discovery 2020–23, validation 2024, final 2025-01 → 2026-11; gold discovery 2001–17, validation 2018–21,
final 2022 → 2026-11 (the handoff already looked at gold 2022–25 and BTC 2024–26: stated, not hidden).
Pass (all, in validation AND final): Sharpe above buy-and-hold AND above the volatility-only control, and max drawdown at
least 25% smaller than buy-and-hold. This is a holding/risk tool, not a day-trading signal.
