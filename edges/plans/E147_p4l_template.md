# E147 How the Profit4Life gold signals work: their template on random entries, and a fib-pullback entry
From the owner's screenshots: gold signal = entry zone, stop 10 USD (100 "pips") from the zone, targets every 5 USD
(TP1 +5 ... TP5 +25), recap counts a tick when TP1 is reached and books the furthest target reached as the pips; a
loss is booked as -100. Their charts show M5/M15 impulse legs with Fibonacci retracements (50-61.8%) and extensions.
Data: XAUUSDT perp 1m, TRAIN 2025-12-11 -> 2026-05, VALIDATION Jun-Aug, FINAL Sep -> 13 Nov 2026. Spread 0.20 USD.
A. Template arithmetic (no skill): 20,000 random entries (seed 147), random side, 07:00-20:00 UTC weekdays, at market.
   Stop -10, targets +5..+25 step 5, 24h limit, stop-first on 1m bars. Report: share reaching TP1 before the stop
   ("win rate" as the recap counts it), recap pips per trade (furthest target reached x10, or -100), and the money
   result per trade for three ways of trading the same signal: all out at TP1; equal fifths at each target with the
   stop moved to entry after TP1; hold everything for TP5.
B. Fib pullback (their apparent method), fixed before data: on 15m bars an impulse = a leg of >= 3 ATR14 within 8 bars
   that makes a new 8-bar extreme; rest a limit order at the 50% retracement of the leg for 2 hours (cancelled if price
   makes a new extreme first by another ATR); trade in the leg's direction with the same template. Variants: 50% and
   61.8% entry. Same three accountings + recap pips. Control: random entries matched by hour and count.
Pass (B): money result per trade > 0 for the fifths-with-breakeven accounting on FINAL with week-clustered t >= 2,
VALIDATION > 0 (t >= 1.5), and above the control. A is descriptive.
