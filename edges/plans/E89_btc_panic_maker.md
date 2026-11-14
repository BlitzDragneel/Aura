# E89 — BTC-only panic bounce at 5m/15m, maker exits and volatility gates (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. Builds on E37/E38 (30 coins, FAIL final, watch list). Different because: BTC only (the
owner's asset), a MAKER take-profit exit (cuts the 7 bp taker exit when the bounce comes) and a volatility-regime gate.
Trigger (as E37/E38, research1/lib1): L-bar log return ≤ 10th percentile of its trailing 30 days (thresholds recomputed
daily); limit buy at c·exp(−k·σ), σ = 168-bar std of log returns (known at the signal close), valid W = 3 bars, fills only
if a bar's low trades below it (maker 0.02%). Hold H = 1 day (288 × 5m / 96 × 15m).
## Grid (32 variants)
tf {5m: L ∈ {24, 288}; 15m: L ∈ {24, 96}} × k ∈ {2, 4} × exit {TIME: taker exit at the close H bars after the fill;
TP: maker sell limit at the signal close c (the pre-dip price), fills when a later bar's high trades through it, else
TIME} × gate {NONE; HIVOL: 1h-equivalent σ (σ × √(bars per hour)) above its trailing 365-day median, known at the signal}.
## Luck check and control
Whole grid re-run with each variant's trigger bars replaced by the same number of random bars in discovery (same k, W,
exits, gate applied after) — 200 runs; real best discovery t ≥ 95th pct of the null bests. Selection/validation/final as
the common rules (5m/15m: both discovery years positive). Funding charged on every settlement held.
