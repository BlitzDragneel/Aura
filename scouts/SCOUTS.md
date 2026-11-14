# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-14 10:40 UTC. Predictions so far: 667; scored (horizon passed): 551. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.711 | 4 | 25.0% | 3.6% | +178 bp/trade |
| DownScout | 0.540 | 1 | 0.0% | 28.7% | +286 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-14T09:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| INJUSDT | 10% | 13% | 27% | 0% |  |
| TRXUSDT | 10% | 12% | 28% | 0% |  |
| SOLUSDT | 8% | 25% | 26% | 0% |  |
| BCHUSDT | 7% | 18% | 25% | 0% |  |
| DOTUSDT | 7% | 24% | 27% | 0% |  |
| XRPUSDT | 7% | 20% | 27% | 0% |  |
| DOGEUSDT | 7% | 26% | 21% | 0% |  |
| WIFUSDT | 7% | 30% | 21% | 0% | DOWN |
| FILUSDT | 7% | 29% | 20% | 0% | DOWN |
| ETHUSDT | 7% | 20% | 22% | 0% |  |
| BNBUSDT | 7% | 25% | 25% | 0% |  |
| TIAUSDT | 7% | 22% | 17% | 0% |  |
| APTUSDT | 6% | 27% | 24% | 0% |  |
| ATOMUSDT | 6% | 19% | 18% | 0% |  |
| UNIUSDT | 6% | 19% | 28% | 0% |  |
| LTCUSDT | 6% | 18% | 22% | 0% |  |
| BTCUSDT | 6% | 25% | 22% | 0% |  |
| AAVEUSDT | 6% | 18% | 31% | 0% |  |
| SEIUSDT | 6% | 21% | 23% | 0% |  |
| OPUSDT | 6% | 27% | 24% | 0% |  |
| XLMUSDT | 6% | 15% | 21% | 0% |  |
| HBARUSDT | 6% | 27% | 18% | 0% |  |
| ADAUSDT | 6% | 24% | 21% | 0% |  |
| SUIUSDT | 5% | 21% | 19% | 0% |  |
| ETCUSDT | 5% | 23% | 20% | 0% |  |
| LINKUSDT | 5% | 24% | 18% | 0% |  |
| AVAXUSDT | 5% | 13% | 22% | 0% |  |
| NEARUSDT | 5% | 16% | 20% | 0% |  |
| ARBUSDT | 5% | 15% | 19% | 0% |  |
