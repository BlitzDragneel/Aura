# E142 Movement forecast and WATCH-armed breakouts: BTC and gold, intraday (owner's request, 14 Nov 2026)
Goal: predict how much BTC and gold will move within the day, and catch big moves/breakouts as they start.
Everything below is fixed before the test data is read.

## Data, 15-minute signal bars, finer bars for the trade path
- BTC: Binance perp 5m (2022 -> 3 Nov 2026). TRAIN 2022-2023, VALIDATION 2024, FINAL 2025-01 -> 2026-11.
- GOLD: XAUUSDT perp 1m (11 Dec 2025 -> 13 Nov 2026). TRAIN -> 2026-05, VALIDATION Jun-Aug 2026, FINAL Sep -> 13 Nov 2026
  (short: reported as such, pass mark not lowered).
- PAXG (gold token, proxy) 1m: TRAIN 2021-2023, VALIDATION 2024, FINAL 2025 (longer check of the gold result).

## Features (known at the bar close; price, volatility, clock; BTC also taker-buy share)
returns over 1/4/16/96 bars, ATR14/price, realised vol 4h/24h/7d and their ratios, bar range/ATR, position inside the
24h range, distance to the 24h high and low in ATR, 4h range / 24h range (compression), hour and weekday (cyclic),
volume / 24h mean volume; BTC only: taker-buy share over 1 and 16 bars.
Control model ("vol + clock"): 24h realised vol, ATR14/price, hour, weekday only.

## Forecast targets (LightGBM, default-like fixed settings: 300 trees max, early stop on VALIDATION, lr 0.03, 31 leaves)
For horizons H = 4h, 8h and "rest of the UTC day":
 A. size: log(high-low range over H / price): mean absolute error vs the control and vs "same as the last H".
 B. big move: |close-to-close move over H| > max(40 bp, 2 ATR): AUC, and hit rate inside WATCH
    (WATCH = prediction >= 75th percentile of VALIDATION predictions) vs the base rate. H = 4h is the WATCH used below.
 C. direction: sign of the move over H: AUC and accuracy on the most confident 25%.
 D. reach: P(price reaches +X before -X within 8h) for gold X = 4, 7 USD (40, 70 "pips" of 0.10) and BTC X = 0.5%, 1%.
Reported for FINAL; a forecast "works" if it beats the control on FINAL by more than its bootstrap noise (weekly blocks).

## Trading rules (one trade at a time, 4h max hold, stop 1.5 ATR, target 3 ATR, stop-first on the fine bars)
 T1 WATCH-armed breakout: while WATCH is on at a bar close, rest a buy-stop at the prior 4h high and a sell-stop at the
    prior 4h low for the next hour; first touched is the entry (both in one fine bar = skipped, counted).
 T2 control: the same breakout orders at every bar (no WATCH).
 T3 WATCH + direction model: at a WATCH bar, enter at the next open in the direction model's side if its confidence is
    in its top 25% (VALIDATION threshold).
 T4 control: WATCH bar, random side (seed 142).
 T5 fade: T1's levels, opposite side (sell the break of the high), same stop/target.
Costs per side: BTC 0.07% (taker + slippage); gold perp/CFD 0.02% (brief) and also shown at a tight 0.0025% (0.20 USD
round trip); PAXG 0.10%. Funding ignored for <= 4h holds (stated).
Pass: FINAL mean > 0 after costs, week-clustered t >= 2, VALIDATION > 0 with t >= 1.5, beats its control.
Variants counted: 3 datasets x (3 horizons x 3 targets + 2 reach) forecasts + 3 x 5 rules.
