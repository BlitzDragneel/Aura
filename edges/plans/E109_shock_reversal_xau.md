# E109 — Post-shock drift / short-term reversal on gold, daily (swing)
Common rules E100. GC_1d closes. Shock day: r_t > k·σ20 (UP) or r_t < −k·σ20 (DOWN), σ20 = std of the prior 20 daily
returns, k ∈ {2, 3}. Trade at settle t: FOLLOW or FADE, hold H ∈ {1, 3, 5, 10} days (exit at the settle t+H); UP and DOWN
shocks separately → 2 × 2 × 4 × 2 = 32 variants. Unit exposure, costs 0.05% per side + CFD financing per night (stress 2×).
Trades counted per event; overlapping events within the hold are skipped. t: NW on the daily return series of the rule
(and per-trade t reported). Luck: random-day control — same number of entries on random days, same direction rule and
hold (1,000 draws), and the grid best t vs best t of grids run on random-day placebo shocks (200 replicates).
