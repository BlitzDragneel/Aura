
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

## Research bot 3 — E63–E70: new data sources (all FAIL; E66 and E68-F6 go on the watch list, grade C)
Sources reachable without keys: `edges/research3/SOURCES.md` (Binance Vision premium/spot/metrics, Coinbase, OKX, Deribit DVOL,
DefiLlama, alternative.me, CoinMetrics community, blockchain.com, mempool; **blocked:** fapi.binance.com 451, api.bybit.com 403,
CryptoCompare needs a key). Fetcher `edges/research3/fetch_sources.py` → `/home/user/data/{premium_1h,spot_1h,coinbase_1h,
deribit_dvol,fear_greed,stablecoins,coinmetrics}`. Common rules `plans/E63_common_bot3.md` (e24aabc9): entry at the first open
after the data is public, `bt` costs and funding, week-clustered t, luck check = the external series **circularly shifted**
against prices and the whole grid rerun (best-t null). Mean = bp per trade after costs.

| Plan | md5 | Var. | Discovery best (mean, t, n) | Luck: real vs null 95th | Validation 2024 | Final 2025→ | Verdict |
|---|---|---|---|---|---|---|---|
| E63 Fear & Greed, BTC+ETH daily | 87cd0ef5 | 27 | L fng≤10 H7d +794, t 2.11, n 28 | 1.53 (n≥30) vs 3.46 | — | — | FAIL (luck) |
| E64 Deribit DVOL spike / IV−RV (disc. from 2021-03-24) | 032aef2a | 17 | B z≥3 H24 +76, t 1.12, n 81 | 1.12 vs 2.33 | — | — | FAIL (luck) |
| E65 Coinbase premium BTC/ETH 1h | d5d72c7e | 24 | follow W720 k2 H12 +27.0, t 2.42, n 1,199, all 4 yrs + | 2.42 vs 1.54 ✔ | W720 k2 H24 +62.2, t 2.49, n 202 | +6.7, t 0.34, n 358 (0.5/d), ex-top-5% −37 | FAIL (final) |
| E66 perp premium index, 60 coins 1h | b2f5c77b | 24 | Raw prem ≤ −0.6% long H12 +340, t 6.21, n 772 | 6.21 vs 2.63 ✔ | prem ≤ −0.3% H12 +140, t 2.49, n 209 | +49.2, t 1.47, n 1,111 (1.7/d), ex-top-5% −65; 2025 +102, 2026 +20 | FAIL (final) — grade C watch |
| E67 taker buy/sell imbalance, top-100 1h | 01cabcb1 | 18 | X z≤−3 & move≤−2σ H24 +43.6, t 0.61; momentum all t −6…−20 | null stopped (cannot change verdict) | — | — | FAIL |
| E68 filters on H1 / climax | e7e10cb0 | 16 | H1 + DVOL ≥ 1-yr p70: +501 vs base +110, t 3.30 (improvement 391 vs null p95 81) | ✔ (also H1+stable>0, CLX+FNG≤25) | H1+F6 +170 vs base +35, t 2.06, n 5,417 | +106 vs base +18, t 1.32, n 4,919, ex-top-5% −16; 2025 +323, 2026 +15 | FAIL (final) — grade C watch |
| E69 CoinMetrics exchange flows/activity | 17d4d7e0 | 22 | Out z≤−2 H14d +337, t 1.46, n 24 | 1.22 (n≥30) vs 3.19 | — | — | FAIL (luck) |
| E70 hold BTC vs cash by regime (owner request) | 47e31da4 | 12 | R1 stablecoin 30-d growth > 0, weekly: Sharpe 0.84 vs B&H 0.78, CAGR 37.6% vs 34.0%, max DD −60% vs −79%; ON-minus-OFF t 0.81 | 0.84 vs 1.39 | — | — | FAIL (luck) |

Notes. (1) **Side finding, E68 base rules over all ~880 perps with my implementation of the protocol text:** panic bounce H1
discovery +127 bp t 3.38 → 2024 +35 bp t 0.56 → 2025-26 +18 bp t 0.59 (50 fills/day); climax 2020-23 +126 t 1.65 → 2024 +120
t 1.41 → 2025-26 +109 t 0.78. Both still have a positive mean but neither is significant out of sample — the forward-ticket record
is needed before trusting them with money. (2) E66 (buy coins whose perp trades ≥0.3% under the index, hold 12 h) and E68-F6
(take H1 only when BTC DVOL is in the top 30% of its year) both look like the same thing seen through new data: crash rebounds;
they lived in 2025 and faded in 2026. Watch list only, no approved.json entry. (3) No plan passed, so no leverage table is
justified; at the drawdowns seen (single trades −60…−85%, mae up to −85%) 20× and 40× would liquidate on the first bad trade.
(4) E66's 24 discovery rows are logged twice in attempts.jsonl (rerun after a crash fix, identical code/numbers); E67's shift null
was stopped once it could not change the verdict. Code `edges/research3/`, results `edges/results/E63…E70_result.json`.

## Research bot 2 — E50–E55: trend, momentum, cross-section, positioning (slower timeframes) — all FAIL
Plans (md5): common rules `E50_common_bot2.md` bd067228…, E50 2daeedca…, E51 bac0f5b6…, E52 d80e1d85…, E53 791a5907…,
E54 d76471e5…, E55 0607685d…. Code `edges/research2/`. Crypto-only universe (stocks/ETFs/metals/stablecoins excluded,
`edges/research2/excluded.json`), survivorship-free top-N by 30-day volume, liquidity costs, real funding, 5% delisting penalty.
Selection: weakest discovery year (needs t ≥ 2 and every year > 0), luck check vs ≥ 200 null grids, ≤ 3 promoted.
Unique variants 512 (E50 192, E51 48, E52 128, E53 60, E54 36, E55 48); attempts.jsonl also holds 96 superseded E50 4h runs
(funding over-charge bug in my code, fixed) and 14 duplicate logs from restarted jobs.

| Plan | Idea | Luck check | Eligible / validation | 2025–26 (FINAL, info only unless promoted) | Verdict |
|---|---|---|---|---|---|
| E50 | own-trend (TSMOM) BTC/ETH/top-10, 1d & 4h, vol target | best +8.5 bp/day = 70th pct (need 95th) | 10 eligible, none promoted | BTC R60 L/S 4h: +4.2 bp/day t 0.54, CAGR +6.4%, DD −28% (BTC hold −14.6%, −54%) | FAIL |
| E51 | Donchian + ATR trail, 4h, 10 majors | random entries + same stop beat it (p95 +123 bp) | 0 eligible (2022 / 2020–21 losses) | N100 ×3 both: −42.5 bp/trade t −0.58, n 422 | FAIL |
| E52 | weekly / 4-weekly cross-section mom & rev, top-100 | passed (97th pct) | 0 eligible (best t 1.45) | 2026: short leg held RAVEUSDT (~50× in a week) → book lost >100% in a day | FAIL |
| E53 | ALT/BTC ratio trend | 37th pct | 0 eligible | +2.3 bp/day t 0.91, CAGR +7.9%, DD −18%; 2024 negative | FAIL |
| E54 | funding as contrarian signal (level, own-history z, market gauge) | passed (97th pct) | 3 promoted (funding level = E28 carry): 2024 t 0.33 / −0.39 / −0.87 | best: −8.6 bp/day, CAGR −43%, DD −73% | FAIL |
| E55 | BTC→alt lead-lag 5m/15m | 13th pct | 0 eligible: gross ≈ 0 bp, net −19 to −32 bp/trade | not run | FAIL |

Why: crypto trend following earns the market's drift, but no more than a shifted signal with the same long bias (E50). The
catch-up from BTC to alts is gone by the next bar's open (E55). Breakouts add nothing over a random entry with the same stop
(E51). Cross-sectional and funding effects were 2020–22 phenomena (E52, E54, as in E28). Market-neutral books with short alt
legs carry squeeze-ruin risk (E52, April 2026). Holding BTC lost 14.6%/yr in 2025–26; trend and ratio rules would have lost less
or made a little, but not significantly: a risk view, not an edge. No leverage table: nothing passed, and 20×/40× on any
of these books would have been liquidated: worst single days at 1× were −16.6% (E50 trend book), −16.8% (E54) and −4.5% even for
the low-risk E53 ratio book, which is already at 20×'s liquidation line (5% − 0.5% margin); 40× (2.0%) dies on ordinary days.

## Lead — E80 exit lab (md5 69205601…): FAIL
480 exit variants (hold 6–72 h × take-profit × stop × trailing stop) on the two passed rules, 923 perps, real costs and funding.
- **Panic bounce H1:** the best exit in 2020–23 is the original one (sell 24 h after the fill, no TP, no stop; +109 bp, t 3.02).
  Every take-profit, stop or trailing stop lowered t; stops hurt most (the edge lives in the deep rebounds). 2024 +31 bp (t 0.50),
  2025–26 +21 bp (t 0.69, n 39,383).
- **Climax:** TP +2% within 6 h had the best discovery t (3.46 vs 1.72 for the original 12 h hold, random-entry p95 1.58), but
  2024 −10 bp (t −0.13) and 2025–26 −23 bp (t −0.67, n 1,267), while the original exit made +126 / +109 bp. A quick TP cut the winners.
- **Conclusion:** keep the original exits; tighter stops or quick take-profits make these rules worse, and no exit design rescues their fading edge.
