# E68 — New-data regime filters on the PASSED panic bounce H1 and climax reversal
Conventions: `E63_common_bot3.md`. Base rules fixed exactly as PROTOCOL.md / E22 / climax.py define them, all 1h perps:
- H1: 24 h log return ≤ coin's trailing 720 h 10th pct (updated daily) → limit at C·exp(−2σ168) valid 3 h, fills only if a
  low trades below it, exit at the close 24 h after the fill. Maker entry 0.02%, taker exit + slippage; funding charged.
- Climax: 1h z = lr/σ168 ≤ −3, volume ≥ 3× median of prior 168 h, close in top 40% of range → buy next open, exit 12 h
  later (open of bar i+13). Taker both sides.
## Filters (evaluated at signal time, known then): 8 per base rule = 16 variants
F1 stablecoin total supply 30-day growth > 0 · F2 stablecoin 30-d growth > its trailing-365-d median · F3 BTC exchange
netflow (CoinMetrics In−Out) 7-day sum < 0 · F4 FNG ≤ 25 · F5 FNG ≤ 40 · F6 BTC DVOL ≥ its trailing-365-d 70th pct ·
F7 BTC DVOL 24 h change ≥ +10% · F8 FNG ≥ 50 (opposite-side sanity filter).
DVOL filters: discovery from 2021-03-24.
## Selection: filter must raise discovery mean AND its own discovery t ≥ unfiltered-equivalent luck: compare against 200
random filters that keep the same fraction of trades (random subsets) — ≥95th pct of mean improvement. Promote ≤3 (pooled
over both base rules); improvement counts only per the common-conventions rule (passes pass mark and beats base in
VALIDATION and FINAL).
