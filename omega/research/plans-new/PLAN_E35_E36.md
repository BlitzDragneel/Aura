# PLANS E35 and E36 (written 2026-11-02 before any result of either rule)
COMMON: Binance archive daily panel (903 USDT perpetuals incl. 163 delisted, 2020-11 → 2026-10-18; volume-0 candles missing),
real funding (longs pay, shorts receive), 5% penalty against a position held into a delisting.
NEW COST MODEL (more precise than the flat 0.10%): per side = 0.05% fee + slippage by the coin's median daily dollar volume
over the 30 days before the trade: ≥ $1B 0.02%; ≥ $100M 0.05%; ≥ $10M 0.15%; below 0.40%.
STAGES: DISCOVERY 2021-01-01 → 2024-12-31 (every variant counted; a luck check); the best weekly t → FINAL 2025-01-01 →
2026-09-30, once. Bars below. Reported whatever happens, with why.

E35 NEW-LISTING FADE. A listing = a perpetual whose first archive candle is on or after 2021-01-01 (true new listings only).
Short at the close of day e after the first candle (e ∈ {1, 3, 7}), hold H days (H ∈ {14, 30}) or until the coin's last traded
day; stop s ∈ {none, +50%}: if a day's high reaches entry × 1.5, exit at max(stop, that day's open) plus slippage.
Grid 12. Trades are events; weekly t on trade results grouped by entry week (weeks without trades count as 0).
Luck check: the same grid entering on random days 60+ days after listing (ordinary coins, not new ones).
PASS: final mean > 0, weekly t ≥ 2.0, positive in 2025 and 2026 (≥ 10 trades each); worst single trade and the result
without the best 5% reported.

E36 PAIRS MEAN REVERSION. Each month: the 30 coins with the highest 30-day dollar volume (E28 universe), and among their
435 pairs the 20 with the highest correlation of daily log returns over the previous 60 days. Spread = ln(A) − ln(B);
z = (spread − its Lb-day mean)/its Lb-day stdev, Lb ∈ {10, 20}. Open when |z| ≥ ze (ze ∈ {1.5, 2.0, 2.5}): short the rich
leg, long the cheap leg, equal notional; close when z crosses 0 or after Hm days (Hm ∈ {5, 10}). Grid 12. Capital split into
20 pair slots; a slot holds 0.5 per leg (1× gross). Luck check: the same grid on 20 RANDOM pairs of the 30 each month.
PASS: final yield > 0, weekly t ≥ 2.0, positive in 2025 and 2026, max drawdown > −25%.
