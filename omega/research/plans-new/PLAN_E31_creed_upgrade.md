# PLAN E31 — CREED fixed and gated, judged on 30 more coins CREED has never seen (written 2026-10-27 before any of their data
# and before any CREED replay with these changes)
WHY (E29 + diagnosis): after a CREED setup price behaves like a fair coin; costs (0.12R a trade) come from stops set by a fixed
price-bucket buffer that ignores volatility; shorts lost before costs everywhere; the only context that ever carried an edge is a
panic (E22/E25: H1 +0.32%, H3 +0.30% a trade, delisted coins included).
CHANGES (CREED's levels, sweep, acceptance, targets and as-taught exit otherwise unchanged; app v6.5.101 engine):
- FIX 1, volatility buffer: buffer = 0.25 × the 15-minute ATR (mean true range of the last 96 bars) instead of the price bucket.
  It moves stops beyond ordinary noise and changes which sweeps count, exactly as the fixed buffer does now.
- FIX 2: longs only.
- GATE (panic): a long setup is taken only if at its decision bar (a) the coin's 24-hour return is in its own bottom 10% (E22's
  thresholds: previous 720 hourly 24-hour returns, set at 00:00 UTC), or (b) at least 20% of all USDT perpetuals with data are in
  their own bottom 10% in that hour (H3's breadth, archive data, delisted coins included).
CANDIDATES (m = 2): U1 = as-taught buffer + longs + gate.  U2 = volatility buffer + longs + gate.
REPORTED: CREED as taught on these coins; U0 = volatility buffer + longs, no gate.
DATA: the 30 coins in E31_untouched_coins.json (ranks 31–60 by liquidity), archive USDT-M 15-minute klines 2023-08 → 2026-09
(August–September 2023 warm-up only), trades 2023-10-01 → 2026-09-30. Costs 0.06% a side, results in R (as all CREED replays).
PASS per candidate: weekly t ≥ 1.96, net mean > 0, positive in 2024, 2025 and 2026 (each with ≥ 10 trades). Also reported:
the same-moment benchmark (same coin, bought at the decision close, held as long as the CREED trade).
If a candidate passes, it becomes "CREED (panic-gated)" beside CREED as taught, on paper, with a forward record; CREED as taught
stays byte-identical. If none passes, the app says so.
