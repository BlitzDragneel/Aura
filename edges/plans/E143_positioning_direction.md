# E143 Direction from positioning: top traders vs the crowd, open interest (BTC and gold perps)
New information, not used in any earlier plan: Binance futures "metrics" (5-minute): open interest, top-trader
long/short ratio by position (top_pos) and by account (top_acct), all-account long/short ratio (crowd), taker
buy/sell volume ratio. A value stamped T is treated as known only at the 15-minute bar closing at or after T + 5 min.

Data and periods: BTC 2022-2023 TRAIN / 2024 VALIDATION / 2025-01 -> 2026-11-03 FINAL; gold perp (XAUUSDT)
2025-12-11 -> 2026-05 TRAIN / Jun-Aug VALIDATION / Sep -> 13 Nov 2026 FINAL (short; pass mark not lowered).
Definitions: z(x) = (x - mean 7d) / std 7d on 15m bars. div = log(top_pos) - log(crowd).
doi4 = OI change over 4h (%); r4 = price change over 4h.

Fixed rules (entry next 15m open, one trade at a time per rule, stop 1.5 ATR14, target 3 ATR14, max hold 4h; also a
24h-hold version with stop 3 ATR, no target):
 P1 follow smart vs crowd: z(div) >= +1.5 long; <= -1.5 short.
 P2 fade the crowd: z(log crowd) >= +2 short; <= -2 long.
 P3 follow top traders' change: 4h change of log(top_pos) z >= +2 long; <= -2 short.
 P4 OI-confirmed move: z(doi4) >= +2 and |r4| >= 1 ATR(1h-equivalent = 2 ATR14): follow r4's sign.
 P5 OI flush: z(doi4) <= -2 and |r4| >= 2 ATR14: fade r4's sign (liquidation/covering exhaustion).
 P6 model: LightGBM direction (4h and 24h) on E142's price features + positioning features (levels z, 1h/4h/24h
    changes of log top_pos, top_acct, crowd, taker, OI, div), compared with the price-only model: AUC on FINAL, and
    trades when confidence is in the top 25% (VALIDATION threshold). Control C: same number of entries per month at
    random times and sides (seed 143).
Costs per side: BTC 0.07%; gold 0.02% (also 0.0025% tight). Funding ignored for 4h; for 24h holds charged at the
recorded 8h/4h rates where the file exists, else stated.
Pass: FINAL mean > 0 after costs with week-clustered t >= 2, VALIDATION > 0 with t >= 1.5, beats control C.
Variants: 2 assets x (5 rules x 2 holds + 2 model horizons) = 24, all logged.
