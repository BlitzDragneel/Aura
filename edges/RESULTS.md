
## Research bot 1 — E37–E46: short-timeframe reversals and intraday timing (all FAIL)
Plans in `edges/plans/E37…E46_*.md` (common methods in each), code in `edges/research1/`, numbers in `edges/results/E<nn>_result.json`.
156 discovery variants counted (attempts.jsonl). Costs per `bt.round_trip_cost` (maker only when price trades through the limit).
Periods: 5m-based discovery 2022–23, 1h-based 2020–23; validation 2024; final 2025-01 → 2026-11.
Mean = bp per trade after costs; t = week-clustered.

| Plan | md5 | Var. | Discovery winner (mean, t, n, trades/day) | Luck: real vs random 95th pct | Validation | Final (chosen) | Verdict |
|---|---|---|---|---|---|---|---|
| E37 panic limit 5m | 946e62f6 | 24 | L288 k4 W3 H288: +72.6, t 2.56, 2,859, 4.1/d | 2.56 vs 0.29 | +93.8, t 1.83 | +31.8, t 1.05, n 3,345, 5.0/d, without best 5% −32.7 | FAIL (final t < 2) |
| E38 panic limit 15m | 32308a7d | 24 | L96 k2 W3 H96: +76.3, t 2.53, 3,158 | 2.53 vs 0.99 | W12: +85.5, t 1.70 | L96 k2 W12 H96: +2.8, t 0.10, n 4,095 | FAIL |
| E39 panic limit 4h (all perps) | d7ce76c1 | 24 | L6 k1 W6 H6: t 3.15 | 3.15 vs 3.91: **below luck** (random limit buys did as well in 2020–23) | +37.3, t 0.62 | info only: +11.6, t 0.47 | FAIL |
| E40 breadth panic 15m | 1dad56f5 | 16 | L96 b20 q5 H96: +92.5, t 2.63, 2,599 | no random variant had mean > 0 | +90.8, t 1.56 | +24.7, t 0.74, n 3,287, without best 5% −44.1 | FAIL |
| E41 climax 15m | a0ec9e97 | 8 | Z3 H12: +33.6, t 1.38, n 186 (0.3/day; V3 = V5: every such bar has more than 5× volume) | 1.38 vs 1.15 | not promoted | — | FAIL (discovery) |
| E42 climax 4h | ee37d5ec | 8 | Z3 V5 H3: +31.0, t 0.29, n 114 | 0.29 vs 1.96 | not promoted | — | FAIL |
| E43 funding-settlement windows | b3097a75 | 18 | none with mean > 0 (best w120 PRE-LOW −1.3, t −0.27) | — | — | — | FAIL |
| E44 US cash open (DST-correct) | 2288834e | 12 | FADE hold 2h big pre-move: +18.8, t 1.73 | 1.73 vs 0.93 | not promoted (t < 2) | — | FAIL |
| E45 turn of month | 763ec85e | 6 | N3 M1: +358, t 4.84, n 450 | 4.84 vs 2.81 | −36.5, t −0.19 | info only: −292, t −2.65 (2024–26 all negative) | FAIL |
| E46 5m wick/cascade | cebd78ca | 16 | CASCADE K6 V5 H48: +44.8, t 1.91, n 1,082 | no random variant had mean > 0 | not promoted | — | FAIL |

What this shows: the panic bounce does show up at 5m and 15m (and the market-wide 15m version). It gets past the luck check in
2022–23, was positive in every calendar year 2022–2026 and trades about 5 times a day. But its 2025–26 edge (+3 to +32 bp)
is too small to be significant, and without the best 5% of trades it loses. These are watch-list ideas, not tradable rules.
At 4h the panic trigger adds nothing beyond buying limit dips at random times. Climax at 15m/4h, 5m wick and cascade
spikes, funding windows and the US open did not pay costs. Turn of month was a 2020–23 effect and went negative after that.

Leverage (information only, E37/E38/E40 final trades, 5% margin per trade): 1× no liquidations (drawdown 10–15%); 2× already
liquidates; at **20× 29–31% of trades hit the liquidation distance and the account goes to about 1 USDT; 40× liquidates about
60% of trades**. Worst intrabar move −83% (Oct 2025 wick). Nothing from E37–E46 goes into approved.json.
