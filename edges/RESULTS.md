
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
