# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-15 17:12 UTC. Predictions so far: 812; scored (horizon passed): 696. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.724 | 4 | 25.0% | 3.0% | +178 bp/trade |
| DownScout | 0.569 | 7 | 57.1% | 39.2% | +550 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-15T16:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| TRXUSDT | 23% | 34% | 32% | 0% | DOWN |
| FILUSDT | 12% | 29% | 0% | 33% | DOWN |
| SOLUSDT | 12% | 21% | 0% | 34% |  |
| APTUSDT | 11% | 26% | 0% | 34% |  |
| OPUSDT | 11% | 22% | 0% | 25% |  |
| XRPUSDT | 10% | 18% | 0% | 23% |  |
| DOTUSDT | 10% | 20% | 0% | 26% |  |
| DOGEUSDT | 10% | 24% | 0% | 27% |  |
| WIFUSDT | 10% | 23% | 0% | 28% |  |
| ETHUSDT | 10% | 18% | 0% | 27% |  |
| LTCUSDT | 10% | 25% | 0% | 36% |  |
| AVAXUSDT | 10% | 26% | 0% | 38% | TURN↓ |
| SUIUSDT | 10% | 24% | 0% | 32% |  |
| ADAUSDT | 9% | 22% | 0% | 31% |  |
| ETCUSDT | 9% | 23% | 0% | 36% |  |
| UNIUSDT | 9% | 13% | 0% | 23% |  |
| BCHUSDT | 9% | 18% | 0% | 28% |  |
| BTCUSDT | 9% | 29% | 0% | 44% | DOWN TURN↓ |
| HBARUSDT | 9% | 24% | 0% | 32% |  |
| SEIUSDT | 9% | 21% | 0% | 34% |  |
| BNBUSDT | 8% | 24% | 0% | 37% |  |
| LINKUSDT | 8% | 22% | 0% | 30% |  |
| TIAUSDT | 8% | 22% | 0% | 31% |  |
| AAVEUSDT | 8% | 19% | 0% | 30% |  |
| XLMUSDT | 8% | 24% | 0% | 35% |  |
| ATOMUSDT | 8% | 24% | 0% | 38% | TURN↓ |
| INJUSDT | 8% | 20% | 0% | 42% | TURN↓ |
| ARBUSDT | 7% | 18% | 0% | 24% |  |
| NEARUSDT | 7% | 16% | 0% | 31% |  |
