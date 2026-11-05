# E64 — Deribit DVOL (30-day implied vol) spikes and implied-minus-realized vol (BTC, ETH)
Conventions: `E63_common_bot3.md`. Source: Deribit public `get_volatility_index_data` hourly, from 2021-03-24.
**Discovery = 2021-03-24 → 2023-12-31** (source start; ~50% of history; protocol periods kept), VALIDATION 2024, FINAL 2025→.
## Hypothesis: a jump in implied vol marks panic (option buyers paying up) → short-term rebound (complements the panic
bounce); IV far below realized vol after a crash = fear already gone (or vice versa) → direction.
## Trades: BTC perp on BTC DVOL, ETH perp on ETH DVOL, pooled. Entry at ts+1h open after the DVOL hour closes.
## Grid (17 variants)
- A spike: ln(DVOL_t / DVOL_{t-24}) ≥ k, k ∈ {0.15, 0.25, 0.35} → long, H ∈ {12, 24, 72} h → 9
- B level: z of DVOL vs its trailing 720 h ≥ z0, z0 ∈ {2, 3} → long, H ∈ {24, 72} → 4
- C VRP: VRP = DVOL − RV30 (RV30 = std of 1h log returns over 720 h × √8760 × 100). VRP ≤ trailing-365d 10th pct → long,
  H ∈ {24, 72}; VRP ≥ trailing-365d 90th pct → short, H ∈ {24, 72} → 4
## Luck check: DVOL series circularly shifted (200 shifts).
