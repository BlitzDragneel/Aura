# E156 Trading the movement forecast without a direction: BTC option straddles during WATCH (indicative)
The only result that keeps holding (E142, handoff): BTC WATCH windows contain bigger moves than normal. A straddle
(ATM call + put) profits from movement in either direction if the realised move beats what the options cost.
WATCH = E142's BTC big-move model (same features/settings, trained 2022-2023, threshold = 75th pct of 2024 validation
predictions), one entry per 4 hours at most. Control: every 4th hour at the same clock hours (all windows).
Pricing (no historical option quotes here, so INDICATIVE): buy a 1-day ATM straddle at entry, Black-Scholes with implied
vol = DVOL (Deribit 30-day BTC index, hourly, known at entry) x m, sell it after 4 hours at the same m x DVOL then.
m = 1.0, 1.2, 1.4 shown as cost sensitivity (short-dated ATM IV is usually above DVOL; 16 Nov 2026 snapshot: 4-day ATM
~51% vs DVOL 38%, ratio ~1.35). Trading cost 3% of premium round trip (stress 6%).
Also reported: realised 4h volatility / DVOL in WATCH vs control windows.
Periods: VALIDATION 2024, FINAL 2025-01 -> 2026-11-03. Pass (as a research candidate for paper options tracking):
FINAL mean P&L per straddle > 0 at m = 1.4 with week-clustered t >= 2, VALIDATION > 0, WATCH above control.
