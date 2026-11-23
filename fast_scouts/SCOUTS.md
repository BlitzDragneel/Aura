# Fast scouts (15-minute candles, 4-hour horizon) — forward record

Updated 2026-11-23 11:10 UTC. Predictions so far: 1624; scored (horizon passed): 1595. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.691 | 36 | 77.8% | 10.5% | +235 bp/trade |
| DownScout | 0.627 | 16 | 50.0% | 20.9% | +27 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-23T10:45 UTC)

| coin | P(up move 4h) | P(down move 4h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| TRXUSDT | 19% | 20% | 0% | 33% |  |
| ETCUSDT | 17% | 23% | 0% | 36% |  |
| INJUSDT | 16% | 22% | 0% | 39% | TURN↓ |
| ETHUSDT | 16% | 25% | 27% | 0% |  |
| SOLUSDT | 16% | 22% | 0% | 35% |  |
| ADAUSDT | 16% | 22% | 0% | 36% |  |
| ARBUSDT | 15% | 27% | 23% | 0% | DOWN |
| XLMUSDT | 15% | 21% | 26% | 0% |  |
| SUIUSDT | 15% | 31% | 0% | 40% | DOWN TURN↓ |
| APTUSDT | 15% | 38% | 25% | 0% | DOWN |
| BCHUSDT | 15% | 22% | 0% | 36% |  |
| BNBUSDT | 15% | 29% | 30% | 0% | DOWN |
| AVAXUSDT | 14% | 29% | 26% | 0% | DOWN |
| WIFUSDT | 14% | 30% | 26% | 0% | DOWN |
| LINKUSDT | 14% | 22% | 0% | 37% |  |
| BTCUSDT | 14% | 21% | 26% | 0% |  |
| HBARUSDT | 14% | 20% | 25% | 0% |  |
| DOTUSDT | 14% | 24% | 24% | 0% |  |
| ATOMUSDT | 14% | 19% | 0% | 33% |  |
| SEIUSDT | 14% | 22% | 27% | 0% |  |
| UNIUSDT | 13% | 26% | 26% | 0% | DOWN |
| XRPUSDT | 13% | 20% | 24% | 0% |  |
| AAVEUSDT | 13% | 21% | 24% | 0% |  |
| LTCUSDT | 13% | 21% | 0% | 39% | TURN↓ |
| DOGEUSDT | 13% | 23% | 24% | 0% |  |
| TIAUSDT | 12% | 16% | 24% | 0% |  |
| FILUSDT | 12% | 30% | 24% | 0% | DOWN |
| OPUSDT | 12% | 30% | 0% | 39% | DOWN TURN↓ |
| NEARUSDT | 12% | 37% | 25% | 0% | DOWN |
