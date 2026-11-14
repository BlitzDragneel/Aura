# E127 — Silver vs gold short-horizon residual reversal (swing, common methods E120)

Disclosure: written after E124, where ratio TREND-following lost in all three periods (e.g. TREND_L20_PAIR discovery
t −2.33). E124's long-window mirror (buy the 20–120-day laggard) is NOT retested (all its periods are seen). This plan
tests a different construction: a beta-hedged daily residual over 1–5 days, which E124 did not compute. Correlation
with E124's information is acknowledged; the luck check covers this grid only.
Residual e_t = r_SI,t − β_t·r_GC,t, β_t = rolling 250-day OLS beta of silver on gold daily log returns (known at t).
S_t = sum of e over the last K days, z_t = S_t / (std of e over 60 days · √K). z < −1 (silver lagged gold) → long
silver [and short β gold]; z > +1 → the opposite. Enter at close t, hold H days, no overlap.
Grid: K ∈ {1, 3, 5} × H ∈ {1, 5} × legs {PAIR (1 silver, β gold), SILVER only} = 12 variants.
CFD costs both legs (0.04% silver, 0.02% gold per side, financing per night on each leg); stress double.
Evaluation, selection (highest discovery NW t, ≥ 30 trades), luck (shifted grid + random entry), pass: as E124/E120.
