# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-15 21:50 UTC. Predictions so far: 841; scored (horizon passed): 725. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.800 | 11 | 36.4% | 4.8% | +290 bp/trade |
| DownScout | 0.545 | 8 | 50.0% | 37.8% | +418 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-15T20:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| TRXUSDT | 15% | 25% | 36% | 0% |  |
| FILUSDT | 11% | 24% | 30% | 0% |  |
| XRPUSDT | 9% | 13% | 30% | 0% |  |
| WIFUSDT | 9% | 21% | 0% | 33% |  |
| DOGEUSDT | 9% | 15% | 0% | 30% |  |
| HBARUSDT | 9% | 20% | 0% | 39% | TURN↓ |
| DOTUSDT | 8% | 14% | 0% | 29% |  |
| INJUSDT | 8% | 15% | 24% | 0% |  |
| AVAXUSDT | 8% | 21% | 0% | 40% | TURN↓ |
| ETHUSDT | 8% | 15% | 0% | 30% |  |
| ADAUSDT | 8% | 19% | 0% | 37% |  |
| APTUSDT | 8% | 19% | 31% | 0% |  |
| SOLUSDT | 8% | 17% | 0% | 34% |  |
| SEIUSDT | 8% | 20% | 0% | 38% |  |
| SUIUSDT | 8% | 18% | 0% | 33% |  |
| LINKUSDT | 8% | 17% | 0% | 33% |  |
| BTCUSDT | 8% | 20% | 0% | 41% | TURN↓ |
| UNIUSDT | 8% | 11% | 0% | 28% |  |
| LTCUSDT | 8% | 17% | 0% | 32% |  |
| ETCUSDT | 8% | 16% | 0% | 32% |  |
| BCHUSDT | 8% | 14% | 0% | 31% |  |
| ATOMUSDT | 8% | 18% | 0% | 42% | TURN↓ |
| TIAUSDT | 7% | 18% | 0% | 41% | TURN↓ |
| AAVEUSDT | 7% | 15% | 0% | 32% |  |
| ARBUSDT | 7% | 12% | 0% | 27% |  |
| BNBUSDT | 7% | 18% | 21% | 0% |  |
| OPUSDT | 7% | 13% | 28% | 0% |  |
| XLMUSDT | 7% | 17% | 0% | 37% |  |
| NEARUSDT | 6% | 15% | 0% | 36% |  |
