# BTC — findings (from edges/RESULTS.md, research of 14 Nov 2026)

Source of truth: the matching section of edges/RESULTS.md; result files in edges/results/.

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

