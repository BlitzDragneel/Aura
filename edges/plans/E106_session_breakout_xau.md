# E106 — Session range breakouts with volatility gate, and a maker-only variant (day)
Common rules E100. PAXG_15m, weekdays. Ranges: R1 = Asia range 00:00 UTC → 08:00 London (high/low); trading window
08:00 → 12:00 London. R2 = New York first hour 08:00 → 09:00 NY; trading window 09:00 → 12:00 NY.
Signal: first 15m close beyond the range in the window → enter at the next bar open, FOLLOW (breakout direction) or FADE;
stop at the opposite side of the range (follow) or at range edge ± 1 range (fade); exit at the window end, or at 17:00 NY
(EXIT2). Vol gate: none or ATR(14 days, daily) above its trailing 60-day median. 2 ranges × 2 directions × 2 exits ×
2 gates = 16 variants. Maker-only (4 more): FADE entered with a resting limit at range edge ± 0.1·range, filled only
when a later bar trades THROUGH it; costs then as Binance perp maker 0.02% entry + taker 0.07% exit (info) and CFD.
Luck null: same grid with the range taken from the same clock window on a random other day (200 replicates).
Control (FINAL): random entry time inside the trading window, same direction rule distribution and same exits.
