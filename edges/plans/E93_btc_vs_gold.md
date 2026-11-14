# E93 — BTC vs gold relative moves (swing) (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. Gold proxy: PAXGUSDT 1h (Binance spot, 2020-08 → 2026-10; a gold-backed token, not
XAUUSD — stated). Daily UTC closes for both. rel_N = log return BTC over N days − log return PAXG over N days;
z = rel_N / std(rel_N over the prior 365 days, min 180). Discovery 2020-09 → 2023 (PAXG starts Aug 2020).
## Grid (16): N ∈ {5, 20} × k ∈ {1.5, 2} × mode {CATCH-UP: z ≤ −k → long BTC, z ≥ k → short BTC; MOMENTUM: opposite}
× H ∈ {5, 10} days. Trade BTC perp only (taker + funding), entry next 00:00 UTC open, no overlap.
Information row (not selectable): the same chosen rule as a pair (BTC vs PAXG, PAXG 0.10% per side).
Selection/luck/validation/final as E91 (random days same count; n ≥ 30; ≥ 3 of 4 discovery years — 2020 is a partial year).
