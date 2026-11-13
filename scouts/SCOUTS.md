# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-13 00:26 UTC. Predictions so far: 522; scored (horizon passed): 406. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.750 | 4 | 25.0% | 4.2% | +178 bp/trade |
| DownScout | 0.522 | 1 | 0.0% | 28.1% | +286 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-12T23:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| TIAUSDT | 24% | 19% | 0% | 28% |  |
| BTCUSDT | 20% | 22% | 33% | 0% |  |
| BCHUSDT | 20% | 17% | 32% | 0% |  |
| ATOMUSDT | 20% | 19% | 0% | 27% |  |
| TRXUSDT | 20% | 17% | 39% | 0% |  |
| XLMUSDT | 19% | 19% | 0% | 28% |  |
| AVAXUSDT | 19% | 14% | 35% | 0% |  |
| SOLUSDT | 18% | 21% | 30% | 0% |  |
| SEIUSDT | 17% | 14% | 30% | 0% |  |
| OPUSDT | 17% | 16% | 0% | 30% |  |
| ADAUSDT | 17% | 17% | 0% | 29% |  |
| XRPUSDT | 17% | 17% | 31% | 0% |  |
| BNBUSDT | 16% | 20% | 26% | 0% |  |
| FILUSDT | 16% | 14% | 32% | 0% |  |
| ETHUSDT | 15% | 18% | 33% | 0% |  |
| LINKUSDT | 15% | 17% | 0% | 32% |  |
| LTCUSDT | 15% | 17% | 0% | 28% |  |
| UNIUSDT | 15% | 13% | 24% | 0% |  |
| WIFUSDT | 15% | 14% | 34% | 0% |  |
| DOGEUSDT | 15% | 17% | 32% | 0% |  |
| HBARUSDT | 14% | 17% | 28% | 0% |  |
| SUIUSDT | 14% | 14% | 31% | 0% |  |
| ETCUSDT | 14% | 18% | 0% | 28% |  |
| APTUSDT | 14% | 15% | 26% | 0% |  |
| NEARUSDT | 13% | 14% | 27% | 0% |  |
| DOTUSDT | 13% | 15% | 32% | 0% |  |
| INJUSDT | 12% | 12% | 27% | 0% |  |
| AAVEUSDT | 12% | 13% | 23% | 0% |  |
| ARBUSDT | 12% | 13% | 0% | 31% |  |
