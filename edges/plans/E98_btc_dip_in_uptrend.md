# E98 — BTC dip-in-uptrend swing (1–20 days) (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. Daily UTC bars. Signal on day d: close ≤ (1 − X) × max(close over the prior 30 days)
(first day of crossing only), and trend filter. Entry next 00:00 UTC open, exit at the close H days later, taker + funding,
no overlap. Long only.
## Grid (18): X ∈ {10%, 15%, 20%} × filter {NONE, SMA200: close(d) > SMA200(d)} × H ∈ {5, 10, 20}.
Selection: best discovery t (mean > 0, n ≥ 30, ≥ 3 of 4 years positive). Luck: whole grid with signal days replaced by
random days (same count, same filter applied to the random day), 200 runs; real best ≥ 95th pct. Control: random days.
VALIDATION 2024 (> 0, t ≥ 1.5) → FINAL once. Week-clustered t on trades.
