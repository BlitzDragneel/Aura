# E101 — Re-run of the external handoff's gold families (replication; no new search)
Common rules E100. Three panels:
A. XAUUSDT perp 15m, the handoff's OWN sample/split: train 2025-12-11 → 2026-06-30, select Jul–Aug 2026, evaluate
   Sep–Oct 2026, check Nov 1–13 2026 (the handoff's Nov 1–12). Costs 6 bp/side (stress 12) as the handoff, funding charged
   from the file for positions open at 00/08/16 UTC; CFD costs (E100) reported too.
B. PAXG 15m, brief periods: train 2020-08 → 2023, select 2024, evaluate 2025-01 → 2026-10.
C. GC 1h adapted (no 15m futures data): train 2024-06 → 2025-06, select 2025-07 → 12, evaluate 2026; bars are 1h so
   "16 bars" = 16 h and max hold = 4 bars.
Trade engine (handoff): signal at the close of bar t; entry at the open of bar t+2 ("one full bar later"); stop 2×ATR14,
target 6×ATR14 from entry; max hold 16 bars (4 h); stop first when both are touched in one bar; if a bar opens beyond the
stop it fills at the open (adverse gap); no overlapping positions. Account view: 10,000, risk 25 per trade incl. costs,
notional ≤ 1×, non-compounding → "account %" comparable with the handoff tables.
Families (one configuration each, written here):
1. Learned price-only direction model: LightGBM multiclass (num_leaves 15, 200 trees, lr 0.03, min_data_in_leaf 200,
   seed 0). Label on the forward 16-bar close return: up > b, down < −b, else flat; b = max(12 bp, ½·ATR14/close).
   Features: log returns over 1,2,4,8,16,32,96 bars; ATR14/close; realised vol 16 and 96 bars; position in the 16- and
   96-bar range; distance to the 96-bar mean in ATRs; hour (sin, cos); weekday. Trade the larger of P(up), P(down) when
   it is ≥ q; q ∈ {0.40,0.45,0.50,0.55,0.60} chosen on the select period (max net total with ≥ 10 trades), then
   evaluate once. Break-even cost per side = gross mean / 2 (handoff claim ≈ 5.2 bp).
2. Movement-timing watch: label |16-bar forward return| > max(40 bp, 2·ATR14/close). LightGBM binary (same features);
   control = logistic regression on ATR14/close, rv16, rv96, hour dummies, weekday dummies. Watch threshold = 75th pct of
   the select-period predictions. Report large-move rate overall vs inside watch windows, and log loss model vs control
   (handoff: 32.9% vs 56.1%; control log loss better 0.5878 vs 0.5923).
3. Price breakout: close above the max high of the prior 16 bars → long; below the min low → short.
4. Compression: (16-bar high − low)/ATR14 in the lowest 20% of its trailing 960 bars; a breakout (as 3) within the next
   8 bars. 4b +confirmation: the bar after the breakout also closes beyond the level (signal at that bar).
5. Accepted retest: after a breakout of level L, within the next 8 bars a bar trades back to L and closes beyond it in
   the breakout direction → signal.
6. Failed auction: bar high exceeds the prior 16 bars' max high by ≥ 0.1 ATR, closes back below that max, bar range ≥
   1.5 ATR, close in the bottom 40% of the bar → short (mirror → long).
7. NY 08–12 (New York time) opportunities: the price-only model's signals in that window vs a constant SHORT on the
   same signal bars (handoff: constant short +2.72% beat the model +1.76%), and constant short/long at every 08:00 NY bar.
8. Weekends: share of 16-bar windows labelled "flat" (rule 1's boundary) starting Sat/Sun vs weekdays (claim 82.8%).
Macro follow/fade is plan E102. Nothing here is promoted to a trading rule unless it would also pass E100 on panel B
(it would then need its own plan).
