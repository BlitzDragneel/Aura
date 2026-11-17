
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

## Lead — E81 UpScout / DownScout (md5 8c6e9e6c…): FAIL as a trading rule, kept as forward-scored predictors
LightGBM on ~40 technical features, 30 liquid coins, 24 h horizon; one configuration; train 2020–23 → 2024, train 2020–24 → 2025–26.
| Scout | AUC 2024 | AUC 2025–26 | Brier skill 2025–26 | top-2% trades after costs 2024 | 2025–26 |
|---|---|---|---|---|---|
| UpScout (≥ +1σ in 24 h) | 0.618 | 0.612 | +0.016 | +121 bp, t 2.20 | +118 bp, t 1.29 |
| DownScout (≤ −1σ) | 0.607 | 0.567 | +0.001 | −112 bp, t −1.75 | +28 bp, t 0.43 |
| Trend turn up | 0.816 | 0.797 | +0.128 | +137 bp, t 1.46 | +47 bp, t 0.43 |
| Trend turn down | 0.807 | 0.808 | +0.148 | −93 bp, t −1.74 | −6 bp, t −0.13 |
Read with care: much of the AUC is a volatility forecast (when a big move comes, either way) and, for turns, the label
needs the trend to be down/up now, which the model sees. Direction skill is small. UpScout is the closest to useful
(positive both years) but misses t ≥ 2 in 2025–26 → not tradeable; both scouts run live as public, forward-scored
predictions (bot-state branch, scouts/) and feed no bot until their forward record shows skill.

## Lead — E82 fast scouts on 15-minute candles (md5 e4eabd0f…): FAIL as a trading rule, run live as information
Same model on 15m bars, 4 h horizon, 30 coins; train 2022–23 → 2024, train 2022–24 → 2025–26.
2025–26: FastUp AUC 0.623 (top-2% calls −24.7 bp after costs, t −1.70), FastDown 0.614 (−7.2 bp), turn-up 0.807 (−33.7 bp),
turn-down 0.817 (−19.3 bp, t −1.95). They see big moves coming as well as the hourly scouts, but 4-hour moves are too
small to pay costs. Live: every 15 minutes on GitHub (bot-state/fast_scouts/), and on demand at the Live API `/scouts`.

## Lead — E83 US index overnight drift (md5 40fdf85f…): FAIL after CFD costs (real before costs)
SPY/QQQ/IWM/DIA daily 2000–2026, buy the close / sell the next open; 12 variants; chosen IWM weekday nights.
Gross: +4.8 / +6.6 / +5.3 bp a night (t 3.8 / 2.9 / 2.3) in 2000–15 / 2016–20 / 2021–26 — the anomaly is real, and the day
session (open→close) lost in every period. Net as an Exness CFD (0.015% spread + 6.5%/yr financing per night): +1.3 / +3.1 /
+1.8 bp (t 1.07 / 1.38 / 0.80) → FAIL. With a zero-commission ETF broker at auction prices: 2021–26 +3.3 bp/night, +7.7%/yr,
max drawdown −18% (t 1.45) vs buy-and-hold +6.1%/yr, −33%. Not a pass; a low-cost broker variant stays on the watch list.

## Lead — E84 volatility-managed holding (md5 3badc45b…): FAIL
Exposure = target vol / EWMA vol (cap 1× or 2×), BTC/ETH, 24 variants. Chosen ETH tv 40% hl 10 cap 1×: Sharpe 1.17 vs 1.06
(2020–23), 0.82 vs 0.70 (2024), −0.10 vs −0.02 (2025–26); drawdown −56/−38/−55% vs −80/−48/−68%. Luck check fails: the
best Sharpe gain (+0.11) is far below shifted-volatility runs (95th pct +0.51) — the benefit is just holding less, not timing.

## Lead — E85 trend/volatility long-or-cash controller from the external handoff (md5 fb92a37b…): FAIL as an edge, works as a drawdown limiter
Rule exactly as given in OMEGA-HANDOFF (12–14 Nov): exposure = share of positive 20/60/120-day returns × min(1, 10% / max(vol20, vol60)).
One configuration, costs 0.10% (BTC) / 0.05% (gold) of turnover, BTC funding charged. Sharpe, CAGR, max drawdown:
| | controller | buy & hold | volatility-only |
|---|---|---|---|
| BTC 2020–23 | 1.25, +8.5%, −11% | 0.80, +35%, −79% | 0.76, +7.4%, −19% |
| BTC 2024 | 1.44, +11%, −6% | 1.47, +90%, −29% | 1.55, +16%, −7% |
| BTC 2025–26 | −0.09, −0.7%, −8% | −0.14, −14%, −54% | −0.26, −3%, −19% |
| Gold 2001–17 | 0.52, +3.6%, −23% | 0.61, +9.8%, −44% | 0.72, +6.9%, −30% |
| Gold 2018–21 | 0.53, +3.7%, −11% | 0.59, +8.2%, −19% | 0.61, +5.6%, −13% |
| Gold 2022–26 | 1.09, +8.7%, −8% | 0.91, +17%, −27% | 1.07, +11%, −14% |
Drawdowns are 3–7× smaller than holding, but returns are much lower and the trend part does not beat the simpler
volatility-only sizing in 2024 (BTC) or 2018–21 (gold). Same conclusion as the handoff: a risk-control tool, not an edge.

## BTC bot — E86–E98: day and swing nothing passed; holding: btc_gold_invvol PASS grade B (paper)
Common rules `plans/E86_common_btc.md` (e0ce60bc). Code `edges/research_btc/`, results `edges/results/E86…E98_result.json`.
166 unique variants (178 rows in attempts.jsonl, validation/final rows included). Costs: taker 0.07% per side, maker 0.02%
only on trade-through, funding on every settlement. Mean = bp per trade after costs; t = week-clustered (daily: Newey–West).
FOMC dates come from federalreserve.gov. **CPI/NFP not tested** (bls.gov 403, FRED connection reset; no dates typed from memory).

| Plan (md5) | Horizon | Var. | Best / chosen | Luck (real vs null p95) | 2024 | 2025–26 | Verdict |
|---|---|---|---|---|---|---|---|
| E86 handoff rules 15m (856f2ace) | day | 5 | breakout / compression / comp+conf / retest / failed auction, one config each | all below random-entry p95 | −12…−17, t −3…−9 | −13…−17, t −7…−11 (n 800–3,200); gross ≈ 0 | FAIL |
| E87 handoff models (7d82df2f) | day | 5 | A: price-only 3-class LightGBM | — | −17.1, t −3.57, n 295 | −14.3, t −3.35, n 215 | FAIL |
| E88 weekend/CME gap/Monday/Asia range 1h (4acf1760) | day | 14 | WEEKEND LONG +12.4 t 0.58 | 0.58 vs 2.41 | +12.5 t 0.42 | info −16.5 t −0.74 | FAIL |
| E89 BTC panic 5m/15m maker TP + vol gate (118e7893) | day | 32 | 5m L24 k4 TP HIVOL +29.2 t 2.12 n 192 | 2.12 vs 3.47 | +7.7 t 0.68 | info −3.0 t −0.32 | FAIL |
| E90 quiet-window maker reversion 15m (19486196) | day | 10 | none > 0 (−7…−9 bp, win 75–80%) | — | — | — | FAIL |
| E95 CME gap FOLLOW, 1 config (284b07db) | day | 1 | +35.1 t 0.72 n 115 (idea from E88's discovery) | 0.72 vs 1.20 | +196 t 3.42 n 26 | info −31.6 t −0.84 n 42 | FAIL |
| E96 movement-watch + stop-entry breakout (2da1f15f) | day | 8 | none > 0 (−13…−20) | — | −9…−22 | −13…−19 | FAIL |
| E91 post-shock drift daily (59a46b87) | swing | 32 | DN k2 FOLLOW H5 +149 t 1.15 n 43 | 1.15 vs 2.76 | −143 t −0.81 | info +153 t 1.33 n 20 | FAIL |
| E92 1–5 d mom/rev vol-targeted (18e5542b) | swing | 16 | N3 MOM long-only NW t 0.89 | 0.89 vs 1.86 | +8.8 bp/d t 0.93 | info −5.5 bp/d | FAIL |
| E93 BTC vs gold (PAXG) relative (7f41b26f) | swing | 16 | none positive in all of 2021–23 | — | — | — | FAIL |
| E98 dip in uptrend (cbb9fb91) | swing | 18 | none with n ≥ 30 and 3/4 years positive | — | — | — | FAIL |
| E94 holding combos (86293976) | hold | 8 | chosen H2 (E85 controller) | SMA timing fails shifted check | Sh 1.55 vs 1.53 | Sh −0.01 vs −0.08, CAGR −0.2% | FAIL (return < 0) |
| E97 H6 inverse-vol BTC/gold on untouched 2014–19 (9792bb1a) | hold | 1 | H6 (selected after seeing 2024–26, stated in plan) | allocation, no timing claim | (E94: Sh 2.13 vs 1.53, DD −8.5% vs −29%) | (E94: Sh 0.56 vs −0.08, DD −32% vs −54%) | **PASS → grade B** |

Handoff comparison, Sep–Oct 2026, account % at 6 bp/side (handoff in brackets): breakout 270 trades −25.6% (383, −29.6%);
compression 72, −11.5% (137, −14.6%); compression+confirmation 60, −7.8% (16, −1.6%); accepted retest 223, −21.9% (96, −8.1%);
failed auction 99, −5.2% (94, −4.6%); price-only model 15 trades, −0.30% (1, +0.25%). Over 2022–26 every family's gross
was 0 ± 3 bp, so the losses are costs. Movement timing (E87-B): big-move rate in the watch windows was 52% vs a 34% base
in 2025–26 (Sep–Oct 2026: 51% vs 32%; Nov: 47% vs 29%). Here the model BEAT the vol/clock control on log loss (0.613 vs 0.630),
which is the opposite of the handoff. That makes it information for sizing; it is not direction (E96: trading it loses).
FOMC 4 h follow, gross: 2024–25 +85 bp → 2026 −5 bp (handoff +64 → −13), n = 39 meetings 2022–26.

**Passed: btc_gold_invvol (hold, grade B, paper, max_leverage 1).** On the first UTC day of each month, set the BTC weight
to (1/σ60_BTC) / (1/σ60_BTC + 1/σ60_gold); gold (PAXG) gets the rest; long only, 1×. 2014–19, judged once: Sharpe 0.90 vs
BTC 0.88, CAGR +14.6% vs +46.3%, max DD −30% vs −84%, 4 of 6 years positive. 2020-09–23: Sharpe 0.71 vs 0.70, DD −28% vs −79%.
Weak points: it was picked after seeing 2024–26; the Sharpe edge is tiny outside 2024–26; returns are much lower in bull
markets. It is a drawdown tool. Leverage (2020–26): 1× DD −32%, 2× −57%, 3× −74%, 5× −92%, 10×/20×/40× wiped out.
Files: `bots/strategies/btc_gold_invvol.py`, `tests_bots/test_btc_gold_invvol.py` (weights and timing equal the research
for all 70 months 2021–26), approved.json entry. Paper only: the runner does not yet size orders by weight.

**Per horizon (the content intended for `edges/assets/BTC/FINDINGS.md`; the harness blocked this bot from creating that
file, so the lead should create it from this section):**
- *Day:* nothing passed. Gross edge ≈ 0 for every breakout-type rule; mean-reversion rules win 75–80% of trades but lose on
  rare deep moves; the weekend and CME clocks are not special; every rule that looked good in 2024 (gap follow +196 bp,
  FOMC follow, panic bounce) weakened or reversed in 2025–26. Best evidence remains the 30-coin E37/E38 watch rules. The
  BTC bot should log the E87-B movement-watch flag as a "stand aside / size down" input only.
- *Swing:* nothing passed. Best-evidence rule, LABELLED FAILED: go long for 5 days after a ≥ 2σ daily fall (E91). It made
  +153 bp per trade in 2025–26 (n 20, t 1.33), lost in 2024, and failed the luck check. Paper-log only.
- *Hold:* btc_gold_invvol (grade B, paper). The E85 controller is rejected as an edge: 2014–19 Sharpe 1.56 with DD −10%,
  but CAGR ≤ 12% and flat in 2025–26. SMA200 timing failed the shifted-signal check.
- *Current market (data to 3 Nov 2026):* BTC 77,442, which is 38% below the 6 Oct 2025 high of 124,628. It is −30% over a
  year but +22% over 120 days and above its SMA200 (73,151). The last 20 and 60 days are negative (−6.8%, −4.7%). Volatility
  is 27% annualised over 20 days and 33% over 60 days. The E85 controller would hold ~10% exposure. The inverse-vol BTC weight
  was 0.38 on 1 Oct 2026 and is 0.35 now.

## Gold (XAU) bot — E100–E115: nothing passed on any horizon (day, swing, hold)
Common rules `plans/E100_common_xau.md` (md5 78d284f7…). Code `edges/assets/XAU/code/`. Numbers
`edges/results/E101…E115_result.json` plus `E101_perp_description.json`; md5s in `assets/XAU/code/plan_md5.json`.
304 gold variants are logged in attempts.jsonl; 24 are empty rows from a first E114 run with a timestamp bug, rerun.
Costs: CFD 0.02%/side plus 6.5%/yr financing per NY rollover (stress 2×); daily rules 0.05% of turnover. Periods per the
brief. Day rules were searched on PAXG 2020–23 (hourly correlation with GC 0.984) and checked on GC 1h 2026.
Not available: Dukascopy (not attempted); BLS calendars answer 403, so CPI/NFP/PPI were skipped. FOMC dates come from
federalreserve.gov. Fetched: PAXG 15m, Binance XAUUSDT perp 15m/1h + funding, Yahoo DXY/^IRX/^TNX (`code/fetch_xau.py`).
**`edges/assets/XAU/FINDINGS.md` could not be created: this agent's file tool refuses new .md report files. This section
is the full findings, and the lead should copy it there.**

**E101 handoff re-run** (account %, 10k, 25 risk/trade, 6 bp/side):
| family | handoff Sep–Oct 26 | re-run, same sample (perp 15m) | PAXG 2025-01→26-10 | GC 1h 2026 |
|---|---|---|---|---|
| price-only model | 71 tr −0.71% | 14 tr −0.35% | 236 tr −4.9% (at CFD 2 bp: +5.5 bp/tr, t 1.52) | 25 tr −2.0% |
| break-even/side | ≈5.2 bp | 5.3 bp (14 tr) | 4.7 bp | <0 |
| breakout | 433 −36.3% | 272 −24.2% | 2,962 −255% | 299 −8.9% |
| compression | 118 −13.8% | 152 −14.5% | 1,646 −142% | 140 −4.3% |
| accepted retest | 82 −5.3% | 217 −19.5% | 2,298 −190% | 232 −6.2% |
| failed auction | 100 −8.2% | 97 −8.0% | 979 −89% | 75 −1.1% |
In NY 08–12 the model made +0.09% on 2 trades vs a constant short on the same bars −0.24%. Shorting every 08:00 NY lost
(−1.3% perp, −52% PAXG), so the claim that "constant short beat the model" is not reproduced. Weekend windows were flat
73.9% (perp) / 59.9% (PAXG) vs 82.8% claimed. The movement watch BEAT its vol/clock control on 15m (log loss 0.453 vs
0.476 perp, 0.510 vs 0.537 PAXG; large-move rate 21.8% → 38.4% in watch windows) but not on GC 1h (0.433 vs 0.411).
Perp vs futures (11 months, too short to judge): ρ 0.984; it trades 0.42% below GC; 29% of its hours fall in the CME
closure, with volatility 9 vs 35 bp/h; funding is paid every 4 h, about **+12.7%/yr paid by longs**.

| Plan | Horizon | Idea | Var. | Discovery best | Luck (real vs null p95) | Verdict |
|---|---|---|---|---|---|---|
| E102 | day | FOMC follow/fade 4 h | 4 | follow 60 m +14 bp, t 1.49 (26 ev.); 2024 +13 (8), 2025–26 +30 (16) | — | FAIL (t, events) |
| E103 | day | sessions Asia/London/NY, opens, outside-US | 16 | OUTUS long +0.7 bp, t 0.38 | 0.38 vs 0.13 | FAIL (nothing ≥ cost) |
| E104 | day | London fix 10:30/15:00 | 16 | AM fade −1.0 bp (gross +3) | −0.4 vs 0.29 | FAIL |
| E105 | day | CME break gap fade/follow | 12 | fade big gaps 2 h +1.2, t 0.58 | 0.58 vs 0.12 | FAIL |
| E106 | day | session range breakout, vol gate, maker fade | 20 | maker fade −0.4 (gross +3.6) | not needed | FAIL |
| E107 | day | intraday momentum | 12 | all < 0 | — | FAIL |
| E114 | day | hourly panic bounce / spike fade | 24 | spike-fade limit k3 H12 +20 bp, t 1.89 | 1.89 vs 3.41 | FAIL (luck) |
| E108 | swing | TSMOM 5–250 d, vol 10%, CFD-financed | 12 | 250 d long/flat, NW t 1.97 | 1.97 vs 1.85 | FAIL (t < 2) |
| E109 | swing | post-shock drift/reversal | 32 | 3σ down, follow 1 d +33 bp, t 1.87 | 1.87 vs 2.43 | FAIL (luck) |
| E110 | swing | DXY trend / 10y yields | 10 | DXY < MA200 long/flat, t 0.92 | 0.92 vs 1.77 | FAIL |
| E111 | hold | 8 trend/vol controllers + E85 | 9 | none beats B&H AND matched vol-only in 2016–20 and 2021–26 | only 12-1 mom ok | FAIL |
| E112 | hold | seasonality (months, Aug–Feb, TOM, weekday) | 5 | best-6 months on−off t 2.52 | 2.52 vs 3.46 | FAIL (reverses 2016–20) |
| E113 | hold | vol-managed gold (contaminated: E85/E111 control) | 2 | excess Sharpe 0.62 vs B&H 0.49 | 0.13 vs 0.08 gain ✔ | not a pass (2016–20 0.76 < 0.79) |
| E115 | hold | rotation gold/silver/cash | 3 | worse than gold in all periods | fails | FAIL |
Disclosure: the hold plans (E111/E112/E113/E115) and E102 report every registered variant in validation/FINAL by design.
None was selected from those numbers and none passed.

Holding, unfunded, cash in T-bills — Sharpe / CAGR / max DD for 2000–15 | 2016–20 | 2021–26:
- **buy & hold:** 0.57/9.3%/−44% | 0.86/12.4%/−17% | 0.75/13.0%/−27%.
- **via CFD swap 6.5%:** 0.21/2.3%/−58% | 0.42/5.2%/−25% | 0.40/5.8%/−31%.
- **vol-only 10%:** 0.78/7.3%/−29% | 0.87/8.3%/−13% | 1.04/10.2%/−13%.
- **E85:** 0.70/4.8%/−23% | 0.68/5.0%/−11% | 1.10/8.5%/−8%.

**Best-evidence rules (all LABELLED NOT PASSED, paper-watch only, nothing in approved.json, no strategy file):**
- *Day:*
  - Long gold outside US hours (17:00 → 08:00 NY): +0.7 / +7.4 / +5.8 bp (PAXG), +5.4 bp (GC 2026); t never ≥ 2, and the
    split was already seen in E3/E5.
  - The 15m price-only model: positive only if costs stay ≤ ~4.7 bp/side.
  - FOMC 1-hour follow: few events.
  - Gross intraday edges are 0–4 bp against a 4 bp CFD round trip: gold day-trading is a cost problem.
- *Swing:* 12-month trend, long/flat with a 10% vol target (t 1.97). The 6.5%/yr CFD financing is the main drag.
- *Hold:* vol-managed gold, min(1, 10%/max(vol20, vol60)) with cash in T-bills (E113).
  - It halves drawdowns (−13% vs −27% in 2021–26) and raises Sharpe in 2000–15 and 2021–26; luck check ok; whole-sample
    bootstrap p = 0.052.
  - It misses 2016–20 and is contaminated, so it is a drawdown limiter, not an edge. It gives up CAGR in bull runs
    (10.2% vs 13.0%).
  - Hold gold unfunded: CFD swaps and perp funding (≈ 6.5–12.7%/yr) eat most of gold's long-run return.
- *Leverage:* nothing passed, so there is no table. 20× (≈ −4.5% liquidation) and 40× (≈ −2%) are liquidated by ordinary
  bad gold days.

## Silver (XAG) bot — E120–E128: nothing passed on any horizon (day, swing, hold)
Common methods `plans/E120_common_xag.md` (8cb3848d). Code `edges/research_xag/`, numbers `results/E121–E128_result.json`.
197 logged attempts, about 170 distinct variants (E121 was run twice after a bug fix: FOMC window and in-sample model
selection; both runs are logged). Costs: CFD 0.04%/side for silver and 0.02% for gold + 6.5%/yr financing per night;
maker variants use perp costs. Hourly data is 1h only (no 15m) and is short, and the bar was not lowered for it.
BLS calendars returned 403, so CPI/NFP were skipped. FOMC dates are from federalreserve.gov.

| Plan | md5 | Var. | Discovery best | Luck (95th pct) | Validation | Final | Verdict |
|---|---|---|---|---|---|---|---|
| E121 handoff families 1h | 214c2b88 | 9 | failed auction −3.6 bp, t −0.4 (model's discovery = training, excluded) | grid t 0.97 | breakout −2.0; compr+conf +22.4 (t 1.1); model +1.6 (t 0.4) | info: breakout −16.6 (t −2.2), model −9.8 (n 393) | FAIL |
| E122 break gap / silver fix / ORB | 3528118b | 24 | ORB NY hi-vol +2.3, t 0.2 | grid t 1.15 | not promoted | info −25.7 | FAIL |
| E123A hourly shocks × vol gate | ead0af26 | 24 | z3 FADE high-vol h4 +19.3, t 1.2 (n 40) | grid t 1.70 | not promoted | — | FAIL |
| E123B maker dip limit (perp) | ead0af26 | 4 (+4 mirror) | k3 H4 +25.4 bp, t 3.47, n 254 | random −0.0 bp | **+44.9, t 2.82, n 108** | **−4.7, t −0.41, n 168 (ex-top5% −27.8)** | FAIL at FINAL → grade C watch |
| E124 gold/silver ratio MR + trend | 99ad36a4 | 18 | trend L20 silver +0.1 bp/day, t 0.03 | grid t 1.71 | −4.0 | info −1.9 | FAIL |
| E125 momentum/reversal + post-shock | 997a208b | 28 | MOM L10 long +2.4 bp/day, t 1.34 | grid t 2.43 | −2.3 | info +0.1 | FAIL |
| E126 hold: E85 / improvements / rotation | 13cd962b | 13 | E85: Sharpe 0.26/0.31 (val/final) vs B&H 0.63/0.46; best B 0.50; best rotation 0.47 | Sharpe 0.52 / 0.64 | — | — | FAIL |
| E127 residual reversal 1–5 d | cdd9350a | 12 | best t −0.37 | grid t 1.36 | −3.8 | info −3.1 | FAIL |
| E128 hold: MA gates (silver/gold/both) | 349a4ae4 | 12 | gold-MA200 + vol size Sharpe 0.44 | Sharpe 0.66 | — | — | FAIL |

- *Day:* the handoff's gold findings carry over to silver. Breakouts lose most, there is no direction edge, and the
  movement-timing model sees big moves (21–27% hit rate vs 14%) but has worse log loss than a vol-and-clock control.
  The cost share is the same as gold's (8 bp ≈ 10.6% of the average 4 h move), so the missing edge, not costs, is the
  problem. The maker dip limit (E123B) is the only rule that passed validation; it failed 2026.
- *Swing:* ratio mean reversion and ratio/residual trades are all negative. Silver momentum/shock rules fail the luck check.
- *Hold:* E85 as written fails (2%/yr, drawdown −15% vs −57%). Trend gates whipsaw on silver. The best-evidence risk
  tool is vol-only sizing (20% target: final Sharpe 0.48 vs 0.46, drawdown −31% vs −57%). Holding gold beat holding
  silver on Sharpe in every period.
- *Perp (info, too short to judge):* Binance XAGUSDT Jan–Oct 2026 saved to /home/user/data/metals/XAGUSDT_perp_*.parquet:
  about $790M per day, 0.993 hourly correlation with COMEX. **Longs paid about 20%/yr in funding** (4-hourly; 6.3% in
  Jan 2026). Weekends are quiet (11 vs 49 bp mean |hourly move|).
- *Leverage:* nothing passed, so there is no table. Silver fell −31% close-to-close on 30 Jan 2026. The watch rule's
  worst 2026 intrabar move was −16%, which liquidates 5× and above; 20×/40× die on ordinary days (2σ ≈ 4%).

## Lead — E140 gold pyramiding: add on strength, trail one stop (md5 791d7764…): FAIL
Owner's question: a signal trader starts small, adds while the move continues and exits fast when it turns. Tested on
XAUUSDT perp 1-minute (Dec 2025–Nov 2026) and PAXG 1-minute (2021–2025), momentum entries (5m close beyond the 60-min
range) and a random-entry control, trailing stop 1×ATR(5m), max 4 h, spread 0.20 USD per unit (each add pays it).
- XAU FINAL (Sep–Nov 2026), mean R per trade: SINGLE −0.02 (win 34%); PYR k0.5 N6 +0.71 (t 2.66, win 18%).
  But the RANDOM-entry pyramid did as well or better: +0.76 (t 4.35). The gain is gold's 2026 trend, not the entry.
  Doubled spread turns every momentum pyramid negative (−0.14 to −0.22 R).
- PAXG 2021–2024: every pyramid loses heavily (−0.5 to −0.9 R, t ≈ −10 to −12); 2025 (the big gold rally) positive.
  Pyramiding is a bet that the market trends: it pays in trend years and bleeds in ranges.
- Typical trade: 80% of pyramid trades lose; the average per unit of peak risk is negative (−0.3 to −0.45); a few big
  trend days pay for everything.
- At the trader's size (balance $560, 0.1 lot = 10 oz per unit), taking every momentum signal wiped the account within
  the first days of every period, every variant.
Verdict: FAIL (does not beat random entries; does not survive double costs). Recorded for the owner: adding to winners
only works while gold trends, and at 0.1 lot per add on a $560 account one choppy day ends it.

## Lead — E141 learn-from-losses cycle on gold pyramiding (md5 d32d08c1…): FAIL
Reflection on E140's DISCOVERY trades only (80 buckets examined: hour, weekday, 24h trend efficiency, volatility
percentile, daily-trend agreement). Losses and wins clustered in different places on the two gold series (perp: weekends
good; PAXG: weekends worst), so the only bucket ranking well on both was hour = 08 UTC. Filtered rule: XAU validation
+0.33R (t 0.48), FINAL −0.85R (t −4.5); PAXG validation −1.29R. The "lesson" from the losses did not carry forward.
New tool: edges/lib/reflect.py (counts every bucket it looks at) for future cycles.

## Lead — E142 movement forecast and WATCH-armed breakouts, BTC and gold (md5 5f8d4899…): forecasts of SIZE work, trading FAIL
15-minute bars; LightGBM trained on TRAIN, tuned on VALIDATION, judged on FINAL (BTC 2025–Nov 2026, gold perp Sep–Nov
2026, PAXG 2025). Control = volatility + clock only.
**When/how much (works):** big-move WATCH (top quarter of predictions):
| | base rate of a big 4h move | inside WATCH | median 4h range in WATCH vs outside | days with a WATCH |
|---|---|---|---|---|
| BTC | 34.6% | 54.1% | $1,266 vs $829 | 599 of 671 |
| Gold perp | 23.7% | 42.2% | $35.8 vs $18.6 | 64 of 74 |
| PAXG | 19.0% | 34.8% | $24.7 vs $13.0 | 260 of 334 |
AUC 0.66 (BTC) / 0.75 (gold) / 0.73 (PAXG) for 4h; 0.76–0.79 for "big move by the end of the day". Range-size error is
26–37% lower than "same as the last 4–8 h", but only 1–4% lower than the volatility+clock control (significant on BTC
4h/day and PAXG; not on the short gold-perp sample). An external claim of a 17–21% cut vs a vol/clock control is not
reproduced here. Most of the forecast is "volatility clusters and follows the clock".
**Which way (does not work):** direction AUC 0.51–0.53 everywhere; on gold perp the confident-direction calls were right
49% (4h). "Reaches +$4/+$7 before −$4/−$7" was predicted no better than by the control.
**Trading (all FAIL), FINAL mean per trade after costs:** WATCH-armed breakout BTC −14.5 bp (gross −0.5; t −11), gold
−0.9 bp at 2 bp/side (gross +3.2), +2.7 bp at a tight 0.20 USD round trip (t 1.52; validation −1.0 → fail), PAXG −20.
Every-bar breakout (control) −16 / −4 / −23. WATCH + direction model: +15 bp gross in training, −1 to −5 gross out of
sample (overfit). Fading the break: negative. WATCH roughly halves the breakout's losses but the break itself has no
follow-through after costs.
Use: WATCH is kept as an alarm ("a big move is likely in the next 4 hours; direction unknown") on the asset desks.

## Lead — E143 direction from positioning: top traders vs crowd, open interest (md5 2a8b2b87…): FAIL, one gold lead (grade C watch)
New data: Binance futures metrics (5m OI, top-trader and all-account long/short ratios, taker ratio), BTC 2022–Nov 2026,
gold perp Dec 2025–Nov 2026. 24 variants, entries at the next 15m open, 1m/5m path, random-entry control.
- BTC: every rule negative on FINAL after 0.07%/side. Before costs: follow-smart-vs-crowd 4h +2.3 bp, fade-crowd 24h
  +8 bp (train +35, validation +54, final +8: decaying). Model with positioning: AUC 0.537 (4h) / 0.531 (24h) vs
  price-only 0.533 / 0.506; confident calls right 55.5% (4h), not enough for the costs (−13.6 bp/trade, t −14).
- Gold: positioning made the model worse (AUC 0.50 vs 0.54; short sample). Rules P1–P3, P5: nothing.
- **Lead: P4 "OI-confirmed move" on gold** (open interest jumps ≥ 2σ over 4 h while price moved ≥ 2 ATR: follow the
  move). 4h hold: train −2.3 bp, validation +4.8 bp (t 0.80, n 48), FINAL +10.4 bp after 2 bp/side (t 2.35, n 41, win
  54%; control −5.7). 24h hold: FINAL +66.5 bp (t 2.76, n 16), validation +4.1 (t 0.21). Fails the pass mark (validation
  t < 1.5, tiny n, only 11 months of history, and BTC shows nothing for the same rule), so grade C: paper log only.
Verdict: FAIL. Positioning data adds little direction information on BTC; gold P4 goes to the forward watch list.

## Lead — E144 replication of the gold "OI-confirmed move" lead (md5 b8460baf…): stays grade C (forward paper log started)
Nothing re-tuned. Silver perp (Jan–Nov 2026), same rule: 4h hold FINAL +6.0 bp after 4 bp/side (n 41, t 0.49, win 54%;
random control −4.4), VALIDATION −10.3 (n 55); 24h hold VALIDATION +46.9 (t 1.07, n 28), FINAL +88.7 (t 3.59, n 20;
control +15.9). Gold neighbourhood (z 1.5/2/2.5 × move 1.5/2/3 ATR): FINAL positive in 9 of 9 cells (+3.8 to +14.8 bp),
VALIDATION positive in 5 of 9 (needed 6). Pooled gold+silver 4h: VALIDATION −3.2 bp (n 103), FINAL +8.2 (t 1.31, n 82).
Reading: consistent sign on FINAL in both metals and every nearby setting, strongest for 24h holds, but the Jun–Aug
validation window is flat/negative for 4h holds and samples are small (11 months of these markets exist).
Not promoted. edges/watch/oi_move.py now logs every signal forward as a paper trade (gold and silver, 4h version as
tested) and sends it to the alert channels labelled "watch-list, paper only"; ~50 closed trades decide.

## Lead — E145 "OI-confirmed move" on nine markets it had never seen (md5 2b55cb6a…): FAIL — the gold/silver lead is not replicated
Identical rule, no tuning. After costs, mean per trade (all history since listing):
platinum −8.4 / −11.0 bp (4h / 24h), palladium −14.4 / −25.2, copper −11.1 / −10.2, natural gas −12.8 / −12.4,
crude −31.4 / −42.3, QQQ −13.9 / −3.3, SPY −7.7 / −18.4, ETH −10.8 / +13.2 (t 0.5), SOL −22.9 / −29.3.
Pooled commodities: 4h −13.9 bp (t −5.9, n 820; random control −7.9), 24h −18.1 (t −3.2, n 506; control −2.3). Positive
in 0 of 5 commodity markets for both holds; worse than random entries.
Verdict: FAIL. The E143/E144 result on gold and silver is most likely a period effect (both metals trended hard in
Sep–Nov 2026), not a property of open-interest jumps. The forward paper log (edges/watch/oi_move.py) keeps running as
grade C, now with this evidence against it; it is not to be promoted without ~50 forward trades.

## Lead — E146 weekly gold/silver direction from CFTC positioning (COT, 2006–2026) (md5 41f5fee7…): FAIL
New data (publicreporting.cftc.gov, managed money and producers, acted on the Monday after publication). Annual return
after costs, DISCOVERY / VALIDATION / FINAL (Newey–West t on FINAL):
gold: fade crowded funds −1.2 / +1.8 / −3.6% (t −1.4); follow fund flows −6.1 / +1.8 / −6.9% (t −1.7); follow producers
−1.1 / +1.3 / −4.7% (t −1.4); "long unless crowded" Sharpe 0.59 vs buy-and-hold 0.79 on FINAL.
silver: fade −4.1 / −0.4 / +0.9%; flows −1.6 / −2.8 / +1.7%; follow producers −2.4 / +1.3 / +15.5% (t 1.9, validation
t 0.31: not passed); long-unless-crowded = buy-and-hold. Gold-vs-silver crowding spread: +4.0 / −0.6 / −0.8%.
Verdict: FAIL. Futures positioning does not time gold or silver week to week. Latest (report acted 9 Nov 2026): gold
funds neutral (z −0.45), silver funds unusually light (z −1.6), producers unusually un-hedged in both (z +2.3 / +1.8).

## Lead — E147 the Profit4Life gold template on random entries, and a fib-pullback entry (md5 bf144f09…): fib FAIL; template explains most of the recap
Template from the owner's screenshots: stop 10 USD, targets every 5 USD to +25, recap ticks a win when TP1 is reached
and books the furthest target reached (×10 pips), a loss is −100.
A. 20,000 coin-flip entries on gold (07–20 UTC weekdays, Dec 2025–Nov 2026): TP1 reached before the stop 66.2% of the
   time; recap +42 "pips" per trade; a week of 13 such signals: median +550 recap pips, 10th–90th percentile 0 to
   +1,100, positive in 89% of weeks, 69% ticks. Money result of the same coin flips: −0.22 USD/oz per trade (all out at
   TP1) and −0.23 (fifths, stop to entry after TP1): the 20-cent spread, nothing else.
   Their recaps: week 7 gold 11 rows, 64% ticks, +920; week 8 gold about 12 rows, +2,210 (rows of 340–720 pips are
   beyond TP5, so they book past the last target). Week 7 is inside the coin-flip range; week 8 is above its 90th
   percentile under my capped accounting. Two weeks cannot separate skill from the template.
B. Fib pullback (limit at the 50% / 61.8% retracement of a ≥3 ATR 15m impulse, same template): 50%: train +0.71 USD
   (t 2.3), validation +0.08, FINAL −0.32 (control −0.29); 61.8%: FINAL −0.85. FAIL.

## Lead — E148 replay of the Signal Lab's seven setups on gold (11 months) and BTC (2024–2026) (md5 ea55b16d…)
Unchanged live code replayed bar by bar; R = fifths with the stop moved to entry after TP1, after spread.
Every setup wins 60–70% of the time (the template) and averages about zero: gold −0.15 to +0.32R, BTC −0.07 to +0.09R on
FINAL. By the rule fixed in the plan:
MUTED (negative in validation and final): gold trend-pullback with the trend (FINAL −0.15R, t −2.4), gold big-move
both sides (−0.10 / −0.21R; validation −0.30 / −0.33, t −2.9 / −3.5), BTC trend-pullback with the trend (−0.06R, t −1.9),
BTC stretch-fade with the trend (validation −0.19, t −2.0). These are still alerted as events and scored, with no trade plan.
BACKTEST+ (positive in validation and final, t ≥ 2 on final): gold session-drive with the trend (validation +0.17R,
FINAL +0.32R, t 2.25, n 22; but TRAIN −0.24R, so weak evidence). Nothing on BTC.
Following a big hourly move in gold loses: by the time it shows on a closed 15m bar, the move is mostly done.

## Lead — E149 Signal Lab replay on silver, ETH and SOL + cross-market view (md5 f763f098…)
Same code and rule as E148. FINAL average R per signal (gold / BTC / silver / ETH / SOL):
trend-pullback with trend −0.15 / −0.06 / −0.26 / −0.14 / −0.04 (negative on all five) · breakout with trend
0.00 / −0.03 / −0.27 / −0.15 / −0.19 · breakout against trend +0.12 / +0.01 / +0.07 / −0.03 / −0.01 · fib pullback with
−0.00 / −0.01 / −0.18 / +0.04 / −0.01, against +0.06 / −0.03 / +0.08 / +0.01 / −0.07 · session drive with
+0.32 / +0.03 / −0.05 / +0.06 / −0.06, against negative on all five · daily bias with trend +0.01 / +0.09 / −0.03 /
+0.01 / +0.05 (positive on 4 of 5 but tiny) · big move against −0.21 / +0.01 / −0.44 / −0.10 / −0.17.
Muted on every market (negative on ≥4 of 5): trend-pullback with trend, breakout with trend, fib pullback with trend,
session drive against trend, big move against trend; plus the per-asset muted cells. No cell earned BACKTEST+ beyond
gold's session drive. Pattern: on closed 15-minute bars, joining a move that is already with the trend loses on these
markets; nothing is reliably positive.

## Lead — E150 after a break: accepted or rejected in the next 15 minutes (md5 7641bece…): FAIL
Five markets (gold, BTC, silver, ETH, SOL), lab template and scorer. Pooled FINAL average R per trade: follow after
ACCEPTANCE −0.065 (t −3.0, n 1,310, positive on 0 of 5 markets); fade after REJECTION −0.035 (t −1.7, n 1,625, 1 of 5);
controls: follow every break −0.068, fade every break −0.034. Waiting 15 minutes to see whether a break holds adds
nothing: neither side is predictable from the first minutes after the break.

## Note — external repo Jakeschincariol/day-trader-skill (reviewed 15 Nov 2026)
MIT, 11 Claude skills for US stocks (Yahoo/SEC/House data): scanner, news, entry timer (closed-bar breakouts), exit
planner (stop/target before entry), "time machine" (bootstrap replay of the last 60 days of 5m bars + every past firing),
risk gate, sizing, alerts, paper broker. No edge claim and no test results of its own. Adopted ideas: a per-signal
history line in the Signal Lab (how this setup did on this market's own recent history, from the E148/E149 replays)
and, next, a daily risk gate for the paper record. Its code is not vendored (stocks, Yahoo); kept for reference only.

## Lead — E151 stop-and-reverse after a Signal Lab stop-out (md5 7e70e04b…): FAIL
After every lab trade that hit its stop, trade the other way from the stop price (same R and targets). Pooled FINAL
average 0.00R (n 1,869, t 0.0), VALIDATION −0.05R; random direction at the same moments −0.01R. Gold: validation +0.12R
(t 2.1) but FINAL +0.01R; silver −0.06; BTC +0.02; ETH −0.00; SOL −0.03. A stop-out says nothing about the next move.

## Lead — E152 US news surprises (Forex Factory calendar, 598 events 2020–2026) → gold and BTC direction (md5 c2555513…): FAIL
Data found via GitHub search: ehsanrs2/forexfactory-scraper (high-impact calendar with actual/forecast; times checked).
Entry 2 minutes after the release (fade the dollar surprise) or 5 minutes after (follow the first move), held 1h / 4h.
FINAL (2025–Jan 2026) after costs: gold fade 4h −13.6 bp at the PAXG cost (gross +6.4, right 55.5%, n 119; at a perp's
2 bp/side ≈ +2.4 bp, too small and validation was −0.0 gross); gold follow-5m −17.7 / −18.1 bp; BTC every variant negative
(fade 4h −45.7 bp). The direction of the surprise does not tell where gold or BTC go after the first minutes.
What news DOES give: size. Gold's median 1-hour range after a high-impact USD release is 0.42% vs 0.29% at the same clock
time on other weekdays (+45%, n 664, PAXG 2023–2025). Used as a timing alert ("news in 30 minutes"), not a direction.

## Lead — E153 Smart Money Concepts, causal versions (md5 fd52ca82…): FAIL, plus a scorer bug found and fixed
The library (joshyattridge/smart-money-concepts) has look-ahead: fvg() uses the next candle and swing_highs_lows() a
centred window, so its signals cannot be backtested as-is. Causal rules on 15m bars, five markets, lab template.
Pooled FINAL average R: fair-value-gap retest −0.045 (t −2.2, n 3,038; positive on 1 of 5 markets), with the 1h trend
−0.036; order-block retest −0.024 / with trend −0.038; liquidity sweep and reclaim −0.074 (t −6.2, n 5,796) / with trend
−0.069. Silver, ETH and SOL lost on every rule.
The one positive cell (BTC fair-value-gap retest +0.058R, t 2.7, 76% wins) was an artefact: for a LIMIT entry filled
inside a bar, the scorer also counted targets touched earlier in that same bar. Fixed in edges/auditor/core.py (no
target on the fill bar of a limit fill; market fills unchanged, so E148–E152 are unaffected). Re-run: BTC FVG −0.069R
(t −2.6), gold FVG −0.070R.

## Lead — E154 higher-timeframe filter for the Signal Lab (md5 see registry): FAIL — the bigger trend does not help
From the 15 Nov BTC loss (a pullback BUY inside a 4h/daily downtrend). Five markets, lab replay. Pooled FINAL average R:
signals AGREEING with both the 4h and daily trend −0.035 (n 2,820, positive on 0 of 5 markets); MIXED −0.065; against
both (CONFLICT) −0.036 (n 2,346). Validation: −0.047 / −0.030 / −0.016. Trading with the bigger trend is no better than
against it for these setups; the BTC loss was not caused by ignoring the bigger trend. No filter added.

## Lead — E155 targets from what the market has been doing (owner's request) — ADOPTED (realism, not an edge)
TP1/TP2/TP3 = the move reached before a 1R adverse move in 60% / 40% / 20% of the 4-hour windows of the previous 3 days.
Same signals, gold + BTC + ETH. Pooled FINAL: adaptive −0.031R vs fixed ladder −0.022R (n 4,271), TP1 reached 65.9% vs
65.8%; VALIDATION −0.020 vs −0.015. Within the plan's 0.02R tolerance, so the lab now sends targets sized to the
market's recent behaviour, each with how often it was reached. Neither version has an edge.

## Lead — E156 trading the movement forecast with BTC option straddles (indicative pricing) : FAIL
WATCH (E142 BTC model) entries, 1-day ATM straddle priced at DVOL x m, held 4h, 3% round-trip cost. FINAL (2025–Nov
2026, n 1,527): −1.3% of premium per trade at m 1.0 (t −1.9), −4.2% at 1.2, −6.1% at 1.4 (the realistic short-dated
level); validation −3.9 / −6.1 / −7.5%. Controls (every 4h): −4.5 / −6.6 / −7.9%.
Realised 4h volatility / implied: 0.86 in WATCH windows vs 0.70 in ordinary ones (FINAL). The movement forecast is real,
but the options market already prices more movement than arrives even in WATCH windows, so buying it loses.
The mirror image (selling options in ordinary windows, realised 0.70 of implied) is the textbook volatility premium;
it carries rare, very large losses and needs margin — not suitable for the owner's account; not pursued.

## Lead — E157 does order-book liquidity control movement? (Binance bookDepth archives, BTC 2023–2026, gold 2025–26)
New tool: edges/data/fetch_depth.py (free 30-second depth within ±0.2–5% of price, stored as 5-minute rows).
SIZE: a thin book does mean bigger moves on BTC: median next-4h range 1.25% when depth within ±1% is in its thinnest
fifth vs 0.99% in the middle and 0.95% in the thickest fifth (FINAL, n 64k bars). On gold the reverse (0.39% vs 0.60%),
because gold's book is thinnest in quiet hours.
DIRECTION: on BTC, more bids than asks within 1% predicts the next hour slightly in all three periods (rank IC 0.058 /
0.033 / 0.035 train / validation / final) — the first direction feature consistent everywhere. But most of it is
short-term mean reversion seen through the book (imbalance vs the past hour's return: correlation −0.39 to −0.48); net of
past 15m/1h/4h returns the IC is 0.018 / 0.011 / 0.020. As trades: "follow the book" made +2 to +9 bp gross per trade
(right 53–58%), −5 to −12 bp after 0.07%/side taker costs (FAIL); the opposite ("liquidity magnet") lost. Gold: no
consistent sign (final IC −0.02). Verdict: FAIL as a rule; BTC book imbalance kept as a candidate feature, and as a
maker-only rule for a future test (needs a registered plan: gross 5–9 bp vs 4 bp maker round trip).

## Live review, 17 Nov 2026 (first 2 days of the 15-minute Signal Lab, read from the Observer's journals)
104 signals closed, average −0.25R (t −3.2) — all markets, mostly logged only. Signals SENT with a trade plan: 8, average
−0.74R (6 stopped out): mainly breakouts against the 15m trend, which the backtests had rated "not proven bad" (≈0R)
rather than good; live 12 signals / 4 separate hours at −0.90R. Changes: (1) trade plans now need POSITIVE evidence
(BACKTEST+, EARNED live, or a live PROMISING/CONFIDENT grade); everything else is an alert without a plan; (2) the
self-learning counts signals that fire in the same hour on several markets as one result (they move together; the
07:00 daily-bias signals were 12 signals but 1 moment), and needs 15 separate hours before muting/earning; (3) reasons
quote the real TP1 distance (targets are adaptive now); (4) the journal covers the owner's five markets in detail, other
coins as a summary, a live scoreboard by setup, and the record of signals actually sent.

## Lead — E158 BTC order-book pressure with limit (maker) orders: FAIL
Limit entry at the signal close, filled only if traded through within 15 minutes; limit exit (else market). Net per
trade, VALIDATION / FINAL: z1 follow 1h +1.8 / −2.4 bp (t 0.7 / −1.4); z1 follow 4h +4.0 / +0.6 bp (t 0.8 / 0.2);
z5 follow 1h −3.5 / −3.9; z5 follow 4h +1.6 / +2.3 bp (t 0.2 / 0.5; random direction with the same fills +1.9).
Cheaper execution brings the book signal to about zero, not into profit; fills through a limit select worse trades.
