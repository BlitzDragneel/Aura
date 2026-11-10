# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-10 23:23 UTC. Predictions so far: 319; scored (horizon passed): 203. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.648 | 1 | 0.0% | 4.9% | -73 bp/trade |
| DownScout | 0.327 | 1 | 0.0% | 34.0% | +286 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-10T22:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| XRPUSDT | 23% | 10% | 50% | 0% | TURN↑ |
| BCHUSDT | 23% | 10% | 39% | 0% |  |
| DOTUSDT | 21% | 12% | 35% | 0% |  |
| SOLUSDT | 21% | 13% | 38% | 0% |  |
| TRXUSDT | 20% | 16% | 36% | 0% |  |
| ETHUSDT | 19% | 14% | 37% | 0% |  |
| DOGEUSDT | 18% | 13% | 36% | 0% |  |
| BTCUSDT | 17% | 15% | 38% | 0% |  |
| FILUSDT | 17% | 10% | 35% | 0% |  |
| HBARUSDT | 17% | 11% | 37% | 0% |  |
| INJUSDT | 17% | 14% | 34% | 0% |  |
| XLMUSDT | 17% | 10% | 35% | 0% |  |
| ADAUSDT | 16% | 12% | 35% | 0% |  |
| TIAUSDT | 16% | 9% | 38% | 0% |  |
| SEIUSDT | 16% | 11% | 36% | 0% |  |
| APTUSDT | 16% | 13% | 34% | 0% |  |
| ETCUSDT | 16% | 10% | 39% | 0% |  |
| LTCUSDT | 16% | 11% | 35% | 0% |  |
| LINKUSDT | 16% | 12% | 36% | 0% |  |
| BNBUSDT | 15% | 14% | 36% | 0% |  |
| WIFUSDT | 15% | 10% | 34% | 0% |  |
| SUIUSDT | 15% | 12% | 32% | 0% |  |
| AVAXUSDT | 15% | 11% | 30% | 0% |  |
| AAVEUSDT | 15% | 12% | 32% | 0% |  |
| NEARUSDT | 14% | 10% | 35% | 0% |  |
| OPUSDT | 14% | 11% | 30% | 0% |  |
| ATOMUSDT | 13% | 8% | 0% | 23% |  |
| UNIUSDT | 12% | 14% | 35% | 0% |  |
| ARBUSDT | 12% | 14% | 31% | 0% |  |
