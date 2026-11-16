# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-16 02:09 UTC. Predictions so far: 870; scored (horizon passed): 754. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.822 | 12 | 33.3% | 6.5% | +277 bp/trade |
| DownScout | 0.515 | 37 | 13.5% | 36.5% | -225 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-16T01:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| TRXUSDT | 21% | 23% | 41% | 0% | TURN↑ |
| FILUSDT | 15% | 14% | 42% | 0% | TURN↑ |
| WIFUSDT | 12% | 13% | 34% | 0% |  |
| HBARUSDT | 11% | 23% | 0% | 26% |  |
| BCHUSDT | 11% | 13% | 0% | 27% |  |
| BTCUSDT | 11% | 16% | 26% | 0% |  |
| ATOMUSDT | 10% | 22% | 0% | 32% |  |
| XRPUSDT | 10% | 13% | 0% | 29% |  |
| DOGEUSDT | 10% | 16% | 0% | 29% |  |
| LINKUSDT | 9% | 21% | 22% | 0% |  |
| SOLUSDT | 9% | 14% | 28% | 0% |  |
| BNBUSDT | 9% | 18% | 23% | 0% |  |
| SUIUSDT | 9% | 21% | 0% | 31% |  |
| DOTUSDT | 9% | 14% | 25% | 0% |  |
| LTCUSDT | 9% | 26% | 26% | 0% |  |
| XLMUSDT | 9% | 23% | 0% | 34% |  |
| INJUSDT | 9% | 21% | 27% | 0% |  |
| APTUSDT | 9% | 13% | 27% | 0% |  |
| ADAUSDT | 8% | 22% | 26% | 0% |  |
| ETHUSDT | 8% | 15% | 27% | 0% |  |
| SEIUSDT | 8% | 24% | 0% | 31% |  |
| ETCUSDT | 8% | 25% | 21% | 0% |  |
| AAVEUSDT | 8% | 12% | 0% | 17% |  |
| OPUSDT | 8% | 12% | 35% | 0% |  |
| TIAUSDT | 7% | 17% | 0% | 31% |  |
| AVAXUSDT | 7% | 19% | 0% | 34% |  |
| NEARUSDT | 6% | 15% | 0% | 31% |  |
| ARBUSDT | 6% | 14% | 18% | 0% |  |
| UNIUSDT | 5% | 9% | 0% | 18% |  |
