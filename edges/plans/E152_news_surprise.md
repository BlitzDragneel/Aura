# E152 US news surprises -> gold and Bitcoin direction (new data: Forex Factory calendar with forecasts)
Source: ehsanrs2/forexfactory-scraper high-impact calendar CSV (third-party scrape, 2020-01 -> 2026-01, times checked:
NFP/CPI at 12:30/13:30 UTC, FOMC at 18:00/19:00 UTC). USD events with numeric Actual and Forecast only.
Strength sign (strong US economy / hawkish = +1): actual > forecast for NFP, ADP, CPI, Core CPI, PPI, Core PPI, Core PCE,
Average Hourly Earnings, Retail Sales, Core Retail Sales, ISM Manufacturing, ISM Services, Flash PMIs, JOLTS, GDP;
actual < forecast for Unemployment Rate and Unemployment Claims; equal = no trade. Federal Funds Rate: higher than
forecast = +1. Events at the same minute: the sum of signs (0 = no trade).
Rules (entry at the open of the minute 2 minutes after the release, so the first spike is not traded):
 N1 fade-the-dollar for gold: gold direction = -strength; N2 same for BTC; held 60 min and 240 min.
 N3 follow the first 5 minutes: direction of the move from release to release+5m, entry at +5m, held 60 / 240 min,
    gold and BTC (the handoff's "delayed continuation", without its event subset).
Data: gold = PAXG spot 1m 2021-01 -> 2025-11 (a gold-backed token; cost 0.10%/side, and shown at 0.02%), XAU perp 1m
2025-12 -> 2026-01 appended; BTC = Binance perp 5m (0.07%/side).
Periods: DISCOVERY 2021-2023, VALIDATION 2024, FINAL 2025-01 -> 2026-01. Week-clustered t.
Pass: FINAL > 0 after base cost with t >= 2, VALIDATION > 0 with t >= 1.5, sign right in > 50% of events on FINAL.
A pass becomes a Signal Lab "NEWS" setup (paper, BACKTEST+) using the live faireconomy weekly calendar.
8 variants (N1, N2 x 2 holds; N3 x 2 assets x 2 holds = 12 counted).
