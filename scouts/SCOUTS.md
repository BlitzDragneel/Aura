# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-17 22:25 UTC. Predictions so far: 1015; scored (horizon passed): 928. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.841 | 13 | 30.8% | 5.4% | +262 bp/trade |
| DownScout | 0.504 | 68 | 8.8% | 29.8% | -126 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-17T21:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| FILUSDT | 25% | 5% | 49% | 0% | TURN↑ |
| OPUSDT | 24% | 5% | 43% | 0% | TURN↑ |
| APTUSDT | 22% | 5% | 45% | 0% | TURN↑ |
| HBARUSDT | 20% | 6% | 35% | 0% |  |
| BTCUSDT | 18% | 6% | 39% | 0% |  |
| ETHUSDT | 17% | 6% | 38% | 0% |  |
| TRXUSDT | 15% | 8% | 0% | 16% |  |
| ETCUSDT | 15% | 6% | 33% | 0% |  |
| AVAXUSDT | 15% | 6% | 35% | 0% |  |
| SUIUSDT | 15% | 6% | 28% | 0% |  |
| LINKUSDT | 15% | 6% | 31% | 0% |  |
| INJUSDT | 14% | 6% | 30% | 0% |  |
| BNBUSDT | 14% | 5% | 36% | 0% |  |
| BCHUSDT | 14% | 5% | 30% | 0% |  |
| LTCUSDT | 14% | 6% | 33% | 0% |  |
| ADAUSDT | 14% | 6% | 33% | 0% |  |
| XLMUSDT | 14% | 6% | 30% | 0% |  |
| DOGEUSDT | 13% | 5% | 32% | 0% |  |
| WIFUSDT | 13% | 6% | 33% | 0% |  |
| SOLUSDT | 13% | 6% | 24% | 0% |  |
| SEIUSDT | 13% | 6% | 0% | 18% |  |
| AAVEUSDT | 12% | 7% | 27% | 0% |  |
| DOTUSDT | 12% | 5% | 33% | 0% |  |
| ARBUSDT | 12% | 5% | 31% | 0% |  |
| ATOMUSDT | 12% | 7% | 33% | 0% |  |
| NEARUSDT | 11% | 8% | 28% | 0% |  |
| XRPUSDT | 11% | 5% | 0% | 20% |  |
| UNIUSDT | 10% | 4% | 27% | 0% |  |
| TIAUSDT | 10% | 4% | 31% | 0% |  |
