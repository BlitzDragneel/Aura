# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-17 03:55 UTC. Predictions so far: 957; scored (horizon passed): 870. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.840 | 12 | 33.3% | 5.6% | +277 bp/trade |
| DownScout | 0.468 | 68 | 8.8% | 31.7% | -126 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-17T02:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| FILUSDT | 19% | 7% | 0% | 21% |  |
| HBARUSDT | 19% | 10% | 41% | 0% | TURN↑ |
| BTCUSDT | 17% | 9% | 0% | 19% |  |
| TRXUSDT | 16% | 12% | 0% | 20% |  |
| DOGEUSDT | 16% | 8% | 0% | 18% |  |
| ETCUSDT | 15% | 11% | 34% | 0% |  |
| BCHUSDT | 15% | 8% | 0% | 24% |  |
| OPUSDT | 15% | 6% | 45% | 0% | TURN↑ |
| INJUSDT | 15% | 11% | 0% | 30% |  |
| ADAUSDT | 14% | 9% | 0% | 19% |  |
| ETHUSDT | 13% | 7% | 0% | 20% |  |
| BNBUSDT | 13% | 8% | 0% | 16% |  |
| AVAXUSDT | 13% | 9% | 33% | 0% |  |
| WIFUSDT | 13% | 9% | 0% | 20% |  |
| APTUSDT | 13% | 6% | 36% | 0% |  |
| SUIUSDT | 13% | 9% | 29% | 0% |  |
| LTCUSDT | 13% | 12% | 0% | 22% |  |
| XRPUSDT | 13% | 6% | 0% | 16% |  |
| LINKUSDT | 13% | 9% | 28% | 0% |  |
| DOTUSDT | 12% | 7% | 0% | 23% |  |
| SOLUSDT | 12% | 6% | 0% | 17% |  |
| ATOMUSDT | 12% | 12% | 0% | 28% |  |
| SEIUSDT | 12% | 9% | 27% | 0% |  |
| XLMUSDT | 11% | 9% | 29% | 0% |  |
| TIAUSDT | 10% | 7% | 0% | 16% |  |
| ARBUSDT | 10% | 6% | 32% | 0% |  |
| NEARUSDT | 9% | 8% | 25% | 0% |  |
| AAVEUSDT | 9% | 9% | 25% | 0% |  |
| UNIUSDT | 7% | 5% | 0% | 12% |  |
