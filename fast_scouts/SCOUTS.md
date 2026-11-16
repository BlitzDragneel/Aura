# Fast scouts (15-minute candles, 4-hour horizon) — forward record

Updated 2026-11-16 11:42 UTC. Predictions so far: 957; scored (horizon passed): 928. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.820 | 34 | 82.4% | 10.7% | +242 bp/trade |
| DownScout | 0.555 | 15 | 53.3% | 22.6% | +28 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-16T11:15 UTC)

| coin | P(up move 4h) | P(down move 4h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| TRXUSDT | 18% | 24% | 0% | 38% | TURN↓ |
| ATOMUSDT | 16% | 21% | 0% | 37% |  |
| SEIUSDT | 15% | 17% | 30% | 0% |  |
| SUIUSDT | 15% | 15% | 0% | 34% |  |
| DOTUSDT | 15% | 18% | 0% | 32% |  |
| ARBUSDT | 14% | 18% | 0% | 33% |  |
| SOLUSDT | 14% | 14% | 0% | 30% |  |
| ETCUSDT | 14% | 18% | 28% | 0% |  |
| AAVEUSDT | 14% | 16% | 0% | 31% |  |
| LINKUSDT | 14% | 15% | 0% | 31% |  |
| XLMUSDT | 14% | 18% | 28% | 0% |  |
| ADAUSDT | 13% | 16% | 27% | 0% |  |
| DOGEUSDT | 13% | 17% | 29% | 0% |  |
| FILUSDT | 13% | 16% | 0% | 29% |  |
| AVAXUSDT | 13% | 14% | 27% | 0% |  |
| UNIUSDT | 13% | 16% | 28% | 0% |  |
| BNBUSDT | 13% | 19% | 27% | 0% |  |
| WIFUSDT | 13% | 14% | 0% | 31% |  |
| BTCUSDT | 13% | 16% | 27% | 0% |  |
| NEARUSDT | 12% | 16% | 0% | 33% |  |
| XRPUSDT | 12% | 15% | 28% | 0% |  |
| TIAUSDT | 12% | 18% | 27% | 0% |  |
| BCHUSDT | 12% | 15% | 27% | 0% |  |
| LTCUSDT | 11% | 18% | 28% | 0% |  |
| ETHUSDT | 11% | 15% | 27% | 0% |  |
| OPUSDT | 11% | 12% | 29% | 0% |  |
| APTUSDT | 11% | 15% | 0% | 28% |  |
| HBARUSDT | 11% | 18% | 26% | 0% |  |
| INJUSDT | 11% | 10% | 26% | 0% |  |
