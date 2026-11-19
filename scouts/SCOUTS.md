# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-19 21:36 UTC. Predictions so far: 1189; scored (horizon passed): 1102. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.846 | 13 | 30.8% | 4.6% | +262 bp/trade |
| DownScout | 0.559 | 70 | 8.6% | 25.3% | -119 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-19T20:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| APTUSDT | 26% | 16% | 42% | 0% | TURN↑ |
| HBARUSDT | 20% | 22% | 39% | 0% |  |
| FILUSDT | 20% | 15% | 34% | 0% |  |
| ARBUSDT | 19% | 16% | 47% | 0% | TURN↑ |
| OPUSDT | 18% | 11% | 36% | 0% |  |
| TRXUSDT | 18% | 13% | 38% | 0% |  |
| LTCUSDT | 18% | 22% | 36% | 0% |  |
| BTCUSDT | 17% | 23% | 34% | 0% |  |
| ETHUSDT | 14% | 20% | 34% | 0% |  |
| ATOMUSDT | 13% | 16% | 30% | 0% |  |
| XRPUSDT | 13% | 16% | 26% | 0% |  |
| ETCUSDT | 12% | 20% | 26% | 0% |  |
| BNBUSDT | 12% | 19% | 27% | 0% |  |
| LINKUSDT | 12% | 16% | 25% | 0% |  |
| DOGEUSDT | 11% | 15% | 26% | 0% |  |
| SOLUSDT | 11% | 13% | 25% | 0% |  |
| XLMUSDT | 11% | 19% | 28% | 0% |  |
| WIFUSDT | 11% | 19% | 28% | 0% |  |
| SEIUSDT | 11% | 16% | 31% | 0% |  |
| BCHUSDT | 11% | 13% | 27% | 0% |  |
| DOTUSDT | 10% | 17% | 26% | 0% |  |
| AVAXUSDT | 10% | 17% | 25% | 0% |  |
| NEARUSDT | 10% | 10% | 22% | 0% |  |
| AAVEUSDT | 10% | 17% | 28% | 0% |  |
| SUIUSDT | 10% | 14% | 23% | 0% |  |
| ADAUSDT | 10% | 14% | 20% | 0% |  |
| TIAUSDT | 9% | 14% | 30% | 0% |  |
| UNIUSDT | 9% | 11% | 31% | 0% |  |
| INJUSDT | 8% | 11% | 16% | 0% |  |
