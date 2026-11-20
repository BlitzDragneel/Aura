# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-20 03:16 UTC. Predictions so far: 1218; scored (horizon passed): 1131. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.848 | 13 | 30.8% | 4.5% | +262 bp/trade |
| DownScout | 0.553 | 75 | 9.3% | 25.0% | -99 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-20T02:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| APTUSDT | 22% | 12% | 45% | 0% | TURN↑ |
| TRXUSDT | 19% | 6% | 35% | 0% |  |
| OPUSDT | 17% | 9% | 38% | 0% |  |
| ARBUSDT | 17% | 16% | 45% | 0% | TURN↑ |
| FILUSDT | 16% | 10% | 37% | 0% |  |
| HBARUSDT | 15% | 15% | 35% | 0% |  |
| LTCUSDT | 15% | 16% | 34% | 0% |  |
| UNIUSDT | 14% | 11% | 37% | 0% |  |
| ETCUSDT | 14% | 12% | 32% | 0% |  |
| SOLUSDT | 13% | 8% | 27% | 0% |  |
| BNBUSDT | 13% | 10% | 33% | 0% |  |
| ETHUSDT | 13% | 11% | 34% | 0% |  |
| BTCUSDT | 13% | 13% | 34% | 0% |  |
| ADAUSDT | 12% | 9% | 27% | 0% |  |
| SUIUSDT | 12% | 10% | 24% | 0% |  |
| DOGEUSDT | 12% | 10% | 30% | 0% |  |
| WIFUSDT | 12% | 10% | 31% | 0% |  |
| AAVEUSDT | 12% | 12% | 29% | 0% |  |
| LINKUSDT | 12% | 10% | 26% | 0% |  |
| DOTUSDT | 12% | 9% | 28% | 0% |  |
| XRPUSDT | 11% | 10% | 28% | 0% |  |
| BCHUSDT | 11% | 8% | 25% | 0% |  |
| TIAUSDT | 11% | 7% | 33% | 0% |  |
| SEIUSDT | 10% | 9% | 23% | 0% |  |
| ATOMUSDT | 10% | 10% | 27% | 0% |  |
| XLMUSDT | 10% | 9% | 23% | 0% |  |
| AVAXUSDT | 10% | 8% | 28% | 0% |  |
| INJUSDT | 10% | 7% | 24% | 0% |  |
| NEARUSDT | 10% | 9% | 27% | 0% |  |
