# E92 — BTC short-horizon daily momentum / reversal with volatility targeting (swing) (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. Different from E50 (TSMOM lookbacks 10–120 days, already FAIL) and E28 (cross-section
and composites): single asset BTC, short lookbacks only.
Position for day d+1 (held 00:00→00:00 UTC) = mode × sign(log return over the last N days) × min(2, 40% / σ20_ann).
## Grid (16): N ∈ {1, 2, 3, 5} × mode {MOMENTUM +1, REVERSAL −1} × {LONG-SHORT, LONG-ONLY (negative → cash)}.
Costs 0.10% of turnover + funding on the position. Daily Newey–West t (10 lags) on the daily net return. Selection: best
discovery NW t with mean > 0 and ≥ 3 of 4 years positive. Luck: signal circularly shifted (≥ 90 days) and the whole grid
re-run, 200 shifts, real best ≥ 95th pct. Control for long-only = vol-targeted always-long; for long-short = shifted.
Pass: common rules with daily NW t in place of week-clustered t (VALIDATION t ≥ 1.5, FINAL t ≥ 2).
