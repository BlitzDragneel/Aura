# E91 — BTC post-shock drift, daily (swing, 1–10 days) (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. Daily UTC bars from 1h. Shock on day d: z = r_d / σ20 (σ20 = std of the 20 prior daily
log returns). Entry at the next day's 00:00 UTC open, exit at the close H days later, taker both sides + funding, no
overlap (one position at a time per variant).
## Grid (32): shock sign {UP: z ≥ k, DOWN: z ≤ −k} × k ∈ {2, 3} × mode {FOLLOW, FADE} × H ∈ {1, 3, 5, 10}.
Selection: best discovery t with mean > 0, n ≥ 30, ≥ 3 of 4 discovery years positive. Luck: whole grid with shock days
replaced by random days (same count per variant, same directions), 200 runs, real best t ≥ 95th pct. Control =
random-entry same holding. VALIDATION 2024, FINAL 2025 → end (week-clustered t on trades).
