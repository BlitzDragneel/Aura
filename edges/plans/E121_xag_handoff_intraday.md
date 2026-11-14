# E121 — Handoff intraday families re-run on silver hourly (common methods E120)

Template: the handoff's gold definitions, on 1h bars (no 15m data). Common trade mechanics for every family:
signal at the close of bar t; entry at the open of bar t+2 ("one full bar later"); stop 2×ATR14, target 6×ATR14
(ATR14 of 1h bars at the signal bar); max hold 4 bars (exit at the close of the 4th bar); no overlapping trades;
stop first when a bar touches both; adverse gaps: if a bar opens beyond the stop/target, fill at the open. CFD costs.

Families (one row each in the result; each counted):
1. Price breakout: close > prior 16-bar high → long; close < prior 16-bar low → short. Variants N ∈ {16, 32}.
2. Compression: prior 16-bar range / ATR14 in the bottom 20% of its trailing 500-bar distribution, then a close
   beyond that 16-bar range → trade the break. Variants: plain, + confirmation (the next bar also closes beyond; entry
   one full bar after the confirmation bar).
3. Accepted retest: a breakout as in 1 (N = 16); within the next 4 bars the low (high for shorts) comes within
   0.25 ATR of the broken level and the bar closes back beyond it → trade the retest close. One variant.
4. Failed auction: bar t sweeps the prior 16 bars' high (low) by ≥ 0.1 ATR, closes back inside the prior range, bar
   range ≥ 1.5 ATR, close in the lower (upper) 40% of the bar → short (long). One variant (unconfirmed; there is no
   spot/OI confirmation data for silver futures).
5. Learned price-only direction model: LightGBM multiclass (fixed params: 200 trees, lr 0.05, 15 leaves, min 50 per
   leaf), label over the next 4 bars: up / down / flat with boundary max(12 bp, ½ ATR14); features: log returns over
   1, 2, 4, 8, 16, 32 bars, ATR14/price, 16-bar range position, hour of day, day of week, distance to 32-bar
   high/low in ATR. Train on discovery; threshold = 75th pct of max(p_up, p_down) over validation predictions (no
   outcomes used); trade the larger class when above threshold and its prob > p_flat.
6. Movement-timing watch: LightGBM binary on the same features, label |4-bar move| > max(40 bp, 2 ATR14); watch when
   prediction > 75th pct of validation predictions. Control: logistic regression on ATR14/price and hour-of-day
   dummies only (vol-and-clock). Reported: large-move rate overall vs inside watch windows, log loss model vs control,
   in validation and final. Information, not a trade rule.
7. FOMC follow/fade: the reaction from the 14:00 NY statement bar's open to 18:00 NY (4 bars); then FOLLOW and FADE
   variants held 4 bars after that (the handoff's "delayed 4-hour continuation"). CPI/NFP skipped (BLS blocked).
   ~19 events in the hourly sample: cannot reach the trade-count bar; reported as information.
Controls: random entry with the same exits, same count, same hour-of-day, same direction mix (200 draws).
Pass: E120. Selection across families 1–5 & 7 by discovery t (≥ 20 discovery trades).
Total counted variants: 2 + 2 + 1 + 1 + 1 + 2 = 9 trade variants (+ the watch model).
