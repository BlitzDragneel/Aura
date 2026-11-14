# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-14 03:17 UTC. Predictions so far: 638; scored (horizon passed): 522. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.724 | 4 | 25.0% | 3.6% | +178 bp/trade |
| DownScout | 0.540 | 1 | 0.0% | 28.2% | +286 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-14T02:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| SOLUSDT | 22% | 26% | 45% | 0% | TURN↑ |
| UNIUSDT | 18% | 20% | 40% | 0% |  |
| BTCUSDT | 18% | 25% | 37% | 0% |  |
| FILUSDT | 17% | 28% | 40% | 0% | DOWN TURN↑ |
| DOTUSDT | 17% | 25% | 39% | 0% |  |
| TRXUSDT | 16% | 19% | 26% | 0% |  |
| ETHUSDT | 16% | 23% | 38% | 0% |  |
| BNBUSDT | 16% | 26% | 34% | 0% |  |
| ATOMUSDT | 16% | 22% | 33% | 0% |  |
| DOGEUSDT | 16% | 26% | 38% | 0% |  |
| ADAUSDT | 16% | 26% | 35% | 0% |  |
| XRPUSDT | 14% | 20% | 41% | 0% | TURN↑ |
| HBARUSDT | 14% | 29% | 33% | 0% | DOWN |
| OPUSDT | 14% | 27% | 34% | 0% |  |
| LINKUSDT | 13% | 25% | 33% | 0% |  |
| ETCUSDT | 13% | 22% | 33% | 0% |  |
| BCHUSDT | 13% | 18% | 36% | 0% |  |
| AAVEUSDT | 13% | 23% | 31% | 0% |  |
| APTUSDT | 13% | 25% | 34% | 0% |  |
| INJUSDT | 13% | 19% | 0% | 27% |  |
| XLMUSDT | 13% | 18% | 31% | 0% |  |
| TIAUSDT | 13% | 22% | 28% | 0% |  |
| SUIUSDT | 12% | 22% | 32% | 0% |  |
| AVAXUSDT | 11% | 16% | 30% | 0% |  |
| SEIUSDT | 11% | 20% | 31% | 0% |  |
| WIFUSDT | 11% | 23% | 31% | 0% |  |
| NEARUSDT | 9% | 15% | 30% | 0% |  |
| ARBUSDT | 9% | 15% | 32% | 0% |  |
| LTCUSDT | 8% | 19% | 22% | 0% |  |
