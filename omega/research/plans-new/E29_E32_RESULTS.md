# Results E29–E32 (26–27 Oct 2026): CREED, real liquidity, a neural network — all FAIL
Every plan written and fingerprinted before its data; each judged once.

## CREED diagnosis (design data: app engine replayed on 20 majors, creed15, 2020–2026, 5,053 on-time setups)
+1R before the stop 49% (a fair coin 50%), +2R 32% (33%), +3R 24% (25%), target ~5R 17.5% (~17%): price after a CREED setup
behaves like a driftless random walk. +0.003R before costs, −0.118R after (costs 0.121R a trade). 99% of setups sweep the 1-hour
pullback zone; the 52 real 4-hour liquidity sweeps lost −0.49R gross. Breakeven barely matters (raw +0.017R).

## E29 (03874f64…): 30 untouched coins (E29_untouched_coins.json), Oct 2023 → Sep 2026, 3,122 setups
As taught −0.100R. C2 (longs, BTC 24h ≤ −1%) −0.037R t −0.32 FAIL. C5 (≤ −2%) −0.063R t −0.37 FAIL. Same-moment benchmark ≈ the same.
## E31 (08e44400…): 30 more untouched coins (E31_untouched_coins.json), 2,802 / 3,685 setups
As taught −0.118R (t −2.27). U1 (longs + panic gate) −0.164R t −1.46 FAIL. U2 (volatility buffer + longs + panic gate) −0.016R
t −0.10 FAIL. The volatility buffer did not make stops cheaper (median cost 0.080R vs 0.073R): stop width is set by the sweep's
wick. In panics, holding the coin at CREED's moments made ≈ 0: the panic edge lives in H1's limit entry, not in being in a panic.
→ CREED stays as taught (byte-identical); v6.5.102 shows the measured odds at the top of its desk.

## E30 (e84fdd70…): real liquidity, 10 coins
L1 thin book → bigger move: rank correlation 0.013 (2023–24), 0.028 (2025–26). L2/L3 imbalance direction (18 variants, luck-best
t −1.56): pick imb1 fade 24 h, discovery t +0.04 → final −14.3 bp t −1.78 FAIL. L4 forced deleveraging (18 variants, luck-best
0.73): pick price −5%/1 h with OI −1%, long 4 h: discovery +75 bp t 1.80 → 2024 +83 bp but n 72, t 0.99 → not promoted, FAIL
(same direction as the panic bounce; too rare on 10 coins). L5 positioning (4 variants): pick fade account ratio +17.5 bp t 1.58 →
2024 −4.3 bp t −0.28 FAIL.

## E32 (3a3151c0…): neural network, daily, 33 inputs (the plan said 35; E28's 33 features already include both funding inputs)
2024 t of the six networks: +0.82, −0.77, +0.90, +0.41, +1.02, +0.42 (ridge −0.21); selected (64, 32) α 1e-4. FINAL 2025-01 →
2026-09: −9.6 bp/day (gross +12.4, funding −16.7, costs 5.3), t −0.98, drawdown −68% FAIL. Long-only −20.3 bp/day. Luck (labels
shuffled, 3 runs): best 2024 t 0.06, 1.75, −0.30 — the real 1.02 is inside luck's range.

## Process notes
- Background processes do not survive the end of a turn here: a download and the first network run were killed at a turn's end
  (the data file came out truncated; rebuilt from cached files; the converter now closes its file properly).
- The panic-gate job was killed once for memory while four jobs ran; rerun alone.
- Prime already carried E28 round 5 and an earlier E30/E29 row from a previous turn; the duplicates were removed and the original's
  research card was corrected from 9,240 to 12,480 E28 rules with round 5's row.

## E33 (d119dc90…): forced deleveraging on 60 coins it had never been run on — FAIL
Rule frozen from E30 L4: hour return ≤ −5% (ln) and OI down ≥ 1% over the hour → long at the close, sell 4 h later; 0.20% costs.
60 coins (E33_coins.json), Oct 2023 → Sep 2026, 59,853 coin-days of open interest. 2,063 events: −3.3 bp a trade (median +18.1,
winners 52%), weekly t −0.10; 2023 +60, 2024 +39, 2025 −74, 2026 −47 bp. The same ≥5% falls without the OI drop: −29.7 bp
(2,119). Without the best 5% of events −72.6 bp; worst events −28% to −36% in 4 hours. Forced selling adds ~0.26% over a plain
fall but neither is an edge; like every daily effect it faded in 2025–26. The panic bounce H1 differs: limit 2σ lower, 24-hour hold.

## E34 (9693ae6d…): delta-neutral funding harvest — FAIL
Spot long + perp short, top k by trailing funding, rebalance every R days, 0.5% per pair round trip, capital = 2 × notional.
Discovery 2021–24 (36 variants; luck-best t 3.60): pick k1 L3 R30 m20%: +8.78%/yr, t 6.02, worst 30 d −0.20%.
FINAL 2025-01 → 2026-09: −17.07%/yr (1×), t −1.27, worst 30 d −33.27%; 2025 +0.01%, 2026 −39.9%. Most rebalances found nothing
above 20%/yr; held coins earned +1–3% a month; DEXEUSDT (held from 2026-06-25) paid −20.8% in a day and −64.6% in 30 days.
Last 90 days −0.48% a day. → The Bridge shows live funding as information only (funding_monitor); no harvest bot.

## E35 and E36 (64259a7e…), with the new liquidity-scaled cost model — both FAIL
E35 new-listing fade (823 listings since 2021; luck-best t −1.41): pick e3 H30 stop +50%: discovery +2.56% a trade (median
+13.5%, 63% winners, t 1.10, 2021 negative); FINAL 2025–26: n 466, +2.51% (median +3.44%, 56% winners), t 1.02, 2025 +6.54%,
2026 −1.76%, worst −76%, without the best 5% −1.43%. Without the stop, single trades lost 300–640% (squeezes): the stop is
essential and still not enough.
E36 pairs mean reversion (luck-best t 0.78): pick Lb20 z2.5 Hm10: discovery +1.80%/yr t 0.50; FINAL −2.09%/yr t −0.51, dd −10%.
Environment: costs now scale with each coin's liquidity (fee 0.05% + slippage 0.02–0.40% per side); jobs run in the
foreground (background processes end with each turn); one job at a time (4 GB, 1 CPU).
