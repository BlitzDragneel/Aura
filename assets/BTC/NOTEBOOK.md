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
- My own record: 229 readings scored; big moves followed 14% of them, 11% after a WATCH (62 WATCH readings).

## Swing trades (1-20 days)

- No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.
- My own record: 209 readings scored; big moves followed 15% of them, 15% after a WATCH (142 WATCH readings).

## Holding (weeks-months)

- Tested rule I can call: btc_gold_invvol (grade B, status paper). Evidence: edges/results/E94_result.json; edges/results/E97_result.json; edges/results/E97_leverage.json; edges/assets/BTC/FINDINGS.md
- My own record: 58 readings scored; big moves followed 24% of them - too few to judge yet.

## Habits I measure myself

- Over the last 20 days the busiest session was New York (average hourly move 0.46%) and the quietest London (0.33%).
- A typical day ranges 2.7% from low to high (last 60 days); 48% of those days closed higher.
- Over the last 30 days the price moved -25.4% (a fact, not a forecast).

## Right now

- Price 58959.0; volatility regime normal (hourly ATR 0.821% of price, 44.7th percentile).
- Bitcoin trades 24/7.

## My calls so far

- no calls yet: no tested rule for this asset has fired
