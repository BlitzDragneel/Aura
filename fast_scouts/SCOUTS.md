# Fast scouts (15-minute candles, 4-hour horizon) — forward record

Updated 2026-11-26 12:44 UTC. Predictions so far: 1856; scored (horizon passed): 1827. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.699 | 36 | 77.8% | 11.1% | +235 bp/trade |
| DownScout | 0.621 | 26 | 30.8% | 19.7% | -199 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-26T12:15 UTC)

| coin | P(up move 4h) | P(down move 4h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| SEIUSDT | 24% | 30% | 0% | 39% | DOWN TURN↓ |
| TRXUSDT | 16% | 26% | 24% | 0% | DOWN |
| LINKUSDT | 16% | 19% | 0% | 32% |  |
| BCHUSDT | 15% | 22% | 24% | 0% |  |
| DOTUSDT | 15% | 23% | 0% | 38% | TURN↓ |
| WIFUSDT | 15% | 17% | 0% | 29% |  |
| LTCUSDT | 15% | 17% | 25% | 0% |  |
| HBARUSDT | 15% | 17% | 0% | 30% |  |
| AAVEUSDT | 14% | 21% | 26% | 0% |  |
| INJUSDT | 14% | 21% | 27% | 0% |  |
| ADAUSDT | 14% | 20% | 0% | 34% |  |
| APTUSDT | 14% | 19% | 0% | 32% |  |
| NEARUSDT | 13% | 19% | 20% | 38% | TURN↓ |
| TIAUSDT | 13% | 18% | 23% | 0% |  |
| XRPUSDT | 12% | 18% | 23% | 0% |  |
| OPUSDT | 12% | 19% | 0% | 34% |  |
| BNBUSDT | 12% | 19% | 22% | 0% |  |
| ARBUSDT | 12% | 19% | 21% | 0% |  |
| FILUSDT | 12% | 18% | 0% | 32% |  |
| SUIUSDT | 11% | 16% | 21% | 0% |  |
| DOGEUSDT | 11% | 16% | 0% | 30% |  |
| BTCUSDT | 11% | 19% | 22% | 0% |  |
| SOLUSDT | 11% | 17% | 21% | 0% |  |
| ETHUSDT | 11% | 19% | 0% | 34% |  |
| AVAXUSDT | 11% | 18% | 21% | 0% |  |
| ATOMUSDT | 10% | 20% | 21% | 0% |  |
| ETCUSDT | 10% | 13% | 0% | 28% |  |
| UNIUSDT | 8% | 13% | 18% | 0% |  |
| XLMUSDT | 8% | 17% | 19% | 0% |  |
