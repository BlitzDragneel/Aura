# Fast scouts (15-minute candles, 4-hour horizon) — forward record

Updated 2026-11-28 13:30 UTC. Predictions so far: 2030; scored (horizon passed): 2001. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.695 | 36 | 77.8% | 10.3% | +235 bp/trade |
| DownScout | 0.636 | 28 | 28.6% | 19.9% | -190 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-28T13:15 UTC)

| coin | P(up move 4h) | P(down move 4h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| SEIUSDT | 19% | 3% | 50% | 0% | TURN↑ |
| WIFUSDT | 18% | 4% | 38% | 0% | TURN↑ |
| LTCUSDT | 18% | 4% | 36% | 0% |  |
| HBARUSDT | 17% | 4% | 42% | 0% | TURN↑ |
| DOTUSDT | 15% | 5% | 41% | 0% | TURN↑ |
| BCHUSDT | 15% | 4% | 36% | 0% |  |
| APTUSDT | 15% | 4% | 40% | 0% | TURN↑ |
| ETCUSDT | 14% | 5% | 42% | 0% | TURN↑ |
| XLMUSDT | 14% | 4% | 0% | 18% |  |
| ADAUSDT | 13% | 4% | 35% | 0% |  |
| TRXUSDT | 13% | 4% | 32% | 0% |  |
| DOGEUSDT | 12% | 4% | 36% | 0% |  |
| FILUSDT | 12% | 4% | 40% | 0% | TURN↑ |
| INJUSDT | 12% | 3% | 42% | 0% | TURN↑ |
| UNIUSDT | 12% | 3% | 0% | 19% |  |
| NEARUSDT | 12% | 4% | 47% | 0% | TURN↑ |
| TIAUSDT | 12% | 4% | 46% | 0% | TURN↑ |
| ATOMUSDT | 11% | 4% | 0% | 15% |  |
| SUIUSDT | 11% | 4% | 39% | 0% | TURN↑ |
| ARBUSDT | 11% | 3% | 31% | 0% |  |
| LINKUSDT | 11% | 3% | 31% | 0% |  |
| AVAXUSDT | 11% | 4% | 37% | 0% | TURN↑ |
| AAVEUSDT | 11% | 3% | 28% | 0% |  |
| OPUSDT | 9% | 4% | 42% | 0% | TURN↑ |
