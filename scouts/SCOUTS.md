# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-16 09:45 UTC. Predictions so far: 899; scored (horizon passed): 783. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.828 | 12 | 33.3% | 6.3% | +277 bp/trade |
| DownScout | 0.489 | 65 | 9.2% | 35.2% | -130 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-16T08:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| TRXUSDT | 29% | 13% | 46% | 0% | UP TURN↑ |
| FILUSDT | 23% | 9% | 47% | 0% | TURN↑ |
| XRPUSDT | 18% | 9% | 0% | 20% |  |
| BTCUSDT | 17% | 11% | 36% | 0% |  |
| INJUSDT | 16% | 11% | 37% | 0% |  |
| LTCUSDT | 16% | 15% | 37% | 0% |  |
| SOLUSDT | 16% | 7% | 41% | 0% | TURN↑ |
| WIFUSDT | 16% | 7% | 37% | 0% |  |
| BNBUSDT | 15% | 11% | 32% | 0% |  |
| LINKUSDT | 14% | 13% | 35% | 0% |  |
| OPUSDT | 14% | 7% | 42% | 0% | TURN↑ |
| DOGEUSDT | 14% | 9% | 0% | 16% |  |
| HBARUSDT | 13% | 13% | 0% | 22% |  |
| ETHUSDT | 13% | 9% | 31% | 0% |  |
| ETCUSDT | 13% | 15% | 33% | 0% |  |
| BCHUSDT | 13% | 9% | 34% | 0% |  |
| XLMUSDT | 13% | 15% | 0% | 25% |  |
| DOTUSDT | 13% | 7% | 37% | 0% |  |
| SEIUSDT | 13% | 16% | 0% | 27% |  |
| SUIUSDT | 13% | 13% | 0% | 21% |  |
| ADAUSDT | 13% | 12% | 30% | 0% |  |
| AAVEUSDT | 12% | 10% | 0% | 15% |  |
| APTUSDT | 12% | 8% | 0% | 16% |  |
| ATOMUSDT | 11% | 13% | 28% | 0% |  |
| AVAXUSDT | 11% | 12% | 31% | 0% |  |
| NEARUSDT | 10% | 13% | 0% | 25% |  |
| UNIUSDT | 9% | 6% | 0% | 12% |  |
| TIAUSDT | 7% | 9% | 28% | 0% |  |
| ARBUSDT | 7% | 10% | 26% | 0% |  |
