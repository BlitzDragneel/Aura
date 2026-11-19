# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-19 03:29 UTC. Predictions so far: 1131; scored (horizon passed): 1015. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.841 | 13 | 30.8% | 5.0% | +262 bp/trade |
| DownScout | 0.555 | 68 | 8.8% | 27.5% | -126 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-19T02:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| FILUSDT | 25% | 19% | 40% | 0% | TURN↑ |
| APTUSDT | 18% | 18% | 35% | 0% |  |
| HBARUSDT | 17% | 24% | 37% | 0% |  |
| TRXUSDT | 16% | 27% | 0% | 30% |  |
| OPUSDT | 15% | 12% | 33% | 0% |  |
| ARBUSDT | 15% | 20% | 39% | 0% |  |
| BTCUSDT | 15% | 33% | 35% | 0% | DOWN |
| BNBUSDT | 13% | 32% | 32% | 0% | DOWN |
| NEARUSDT | 12% | 19% | 26% | 0% |  |
| XRPUSDT | 12% | 18% | 29% | 0% |  |
| LTCUSDT | 12% | 31% | 27% | 0% | DOWN |
| ETHUSDT | 12% | 28% | 27% | 0% | DOWN |
| ETCUSDT | 12% | 25% | 27% | 0% |  |
| SOLUSDT | 11% | 18% | 25% | 0% |  |
| DOGEUSDT | 11% | 23% | 24% | 0% |  |
| LINKUSDT | 11% | 27% | 27% | 0% |  |
| WIFUSDT | 11% | 23% | 28% | 0% |  |
| XLMUSDT | 11% | 24% | 31% | 0% |  |
| BCHUSDT | 11% | 20% | 30% | 0% |  |
| AVAXUSDT | 11% | 25% | 27% | 0% |  |
| DOTUSDT | 10% | 23% | 25% | 0% |  |
| ADAUSDT | 10% | 22% | 28% | 0% |  |
| ATOMUSDT | 10% | 30% | 0% | 41% | DOWN TURN↓ |
| SUIUSDT | 10% | 24% | 23% | 0% |  |
| UNIUSDT | 10% | 11% | 19% | 0% |  |
| AAVEUSDT | 10% | 24% | 20% | 0% |  |
| SEIUSDT | 9% | 21% | 22% | 0% |  |
| INJUSDT | 9% | 13% | 23% | 0% |  |
| TIAUSDT | 8% | 13% | 26% | 0% |  |
