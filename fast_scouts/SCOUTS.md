# Fast scouts (15-minute candles, 4-hour horizon) — forward record

Updated 2026-11-11 14:00 UTC. Predictions so far: 406; scored (horizon passed): 377. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.823 | 28 | 78.6% | 12.5% | +202 bp/trade |
| DownScout | 0.740 | 5 | 0.0% | 14.9% | -232 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-11T13:45 UTC)

| coin | P(up move 4h) | P(down move 4h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| XLMUSDT | 21% | 27% | 0% | 39% | DOWN TURN↓ |
| WIFUSDT | 19% | 21% | 0% | 34% |  |
| ADAUSDT | 19% | 20% | 0% | 34% |  |
| DOTUSDT | 19% | 22% | 0% | 36% |  |
| TRXUSDT | 19% | 19% | 27% | 0% |  |
| SEIUSDT | 19% | 22% | 0% | 35% |  |
| LTCUSDT | 18% | 22% | 0% | 35% |  |
| SOLUSDT | 18% | 21% | 0% | 35% |  |
| OPUSDT | 18% | 21% | 0% | 34% |  |
| NEARUSDT | 18% | 23% | 0% | 38% |  |
| SUIUSDT | 18% | 19% | 0% | 32% |  |
| BNBUSDT | 18% | 20% | 0% | 32% |  |
| HBARUSDT | 18% | 21% | 0% | 34% |  |
| FILUSDT | 18% | 18% | 0% | 31% |  |
| BTCUSDT | 17% | 20% | 0% | 30% |  |
| APTUSDT | 17% | 19% | 0% | 32% |  |
| ATOMUSDT | 17% | 20% | 0% | 34% |  |
| ETCUSDT | 17% | 19% | 0% | 29% |  |
| BCHUSDT | 17% | 21% | 27% | 0% |  |
| DOGEUSDT | 17% | 19% | 0% | 31% |  |
| XRPUSDT | 17% | 21% | 29% | 0% |  |
| LINKUSDT | 16% | 20% | 26% | 0% |  |
| ETHUSDT | 16% | 17% | 27% | 0% |  |
| AAVEUSDT | 16% | 22% | 23% | 0% |  |
| TIAUSDT | 14% | 20% | 0% | 34% |  |
| ARBUSDT | 14% | 18% | 0% | 35% |  |
| AVAXUSDT | 14% | 18% | 27% | 0% |  |
| UNIUSDT | 12% | 18% | 0% | 33% |  |
| INJUSDT | 10% | 16% | 20% | 0% |  |
