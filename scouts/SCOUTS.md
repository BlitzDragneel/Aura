# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-25 02:30 UTC. Predictions so far: 1654; scored (horizon passed): 1566. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.758 | 14 | 28.6% | 4.8% | +251 bp/trade |
| DownScout | 0.556 | 75 | 9.3% | 25.4% | -99 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-25T01:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| SEIUSDT | 20% | 16% | 45% | 0% | TURN↑ |
| TRXUSDT | 17% | 14% | 0% | 21% |  |
| ARBUSDT | 17% | 11% | 35% | 0% |  |
| XLMUSDT | 15% | 17% | 33% | 0% |  |
| APTUSDT | 15% | 6% | 34% | 0% |  |
| OPUSDT | 15% | 8% | 38% | 0% |  |
| AAVEUSDT | 13% | 10% | 30% | 0% |  |
| ETCUSDT | 13% | 11% | 34% | 0% |  |
| ATOMUSDT | 13% | 15% | 34% | 0% |  |
| LTCUSDT | 13% | 14% | 26% | 0% |  |
| FILUSDT | 13% | 7% | 28% | 0% |  |
| UNIUSDT | 13% | 7% | 32% | 0% |  |
| WIFUSDT | 12% | 14% | 29% | 0% |  |
| HBARUSDT | 12% | 12% | 34% | 0% |  |
| DOTUSDT | 12% | 14% | 30% | 0% |  |
| TIAUSDT | 12% | 14% | 34% | 0% |  |
| DOGEUSDT | 12% | 12% | 29% | 0% |  |
| LINKUSDT | 12% | 11% | 31% | 0% |  |
| BNBUSDT | 12% | 12% | 28% | 0% |  |
| SOLUSDT | 11% | 13% | 30% | 0% |  |
| BTCUSDT | 11% | 12% | 31% | 0% |  |
| ADAUSDT | 11% | 11% | 31% | 0% |  |
| XRPUSDT | 11% | 13% | 29% | 0% |  |
| AVAXUSDT | 11% | 11% | 30% | 0% |  |
| ETHUSDT | 11% | 12% | 28% | 0% |  |
| INJUSDT | 11% | 10% | 30% | 0% |  |
| SUIUSDT | 11% | 11% | 25% | 0% |  |
| BCHUSDT | 11% | 12% | 24% | 0% |  |
| NEARUSDT | 9% | 10% | 26% | 0% |  |
