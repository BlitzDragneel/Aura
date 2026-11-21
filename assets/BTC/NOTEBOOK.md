# What I know about Bitcoin (BTC)

Built automatically from the research findings, the approved rules and my own forward record. No language model; no invented directions.

## What the research found

- Source of truth: the matching section of edges/RESULTS.md; result files in edges/results/.

## Day trades

- Common rules plans/E86_common_btc.md (e0ce60bc). Code edges/research_btc/, results edges/results/E86…E98_result.json.
- 166 unique variants (178 rows in attempts.jsonl, validation/final rows included). Costs: taker 0.07% per side, maker 0.02%
- only on trade-through, funding on every settlement. Mean = bp per trade after costs; t = week-clustered (daily: Newey–West).
- FOMC dates come from federalreserve.gov. CPI/NFP not tested (bls.gov 403, FRED connection reset; no dates typed from memory).
- | Plan (md5) | Horizon | Var. | Best / chosen | Luck (real vs null p95) | 2024 | 2025–26 | Verdict |
- | E86 handoff rules 15m (856f2ace) | day | 5 | breakout / compression / comp+conf / retest / failed auction, one config each | all below random-entry p95 | −12…−17, t −3…−9 | −13…−17, t −7…−11 (n 800–3,200); gross ≈ 0 | FAIL |
- No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.
- My own record: 129 readings scored; big moves followed 15% of them, 13% after a WATCH (31 WATCH readings) - too few to judge yet.

## Swing trades (1-20 days)

- No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.
- My own record: 109 readings scored; big moves followed 17% of them, 19% after a WATCH (42 WATCH readings) - too few to judge yet.

## Holding (weeks-months)

- Tested rule I can call: btc_gold_invvol (grade B, status paper). Evidence: edges/results/E94_result.json; edges/results/E97_result.json; edges/results/E97_leverage.json; edges/assets/BTC/FINDINGS.md
- My own record: no readings scored yet (each is scored once its horizon has passed).

## Habits I measure myself

- Over the last 20 days the busiest session was Asia (average hourly move 0.38%) and the quietest London (0.28%).
- A typical day ranges 2.6% from low to high (last 60 days); 45% of those days closed higher.
- Over the last 30 days the price moved -29.9% (a fact, not a forecast).

## Right now

- Price 56084.9; volatility regime extreme (hourly ATR 1.595% of price, 97.9th percentile).
- Bitcoin trades 24/7; weekend liquidity is thinner.

## My calls so far

- no calls yet: no tested rule for this asset has fired
