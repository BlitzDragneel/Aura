# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-14 21:31 UTC. Predictions so far: 725; scored (horizon passed): 580. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.718 | 4 | 25.0% | 3.4% | +178 bp/trade |
| DownScout | 0.520 | 1 | 0.0% | 32.2% | +286 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-14T20:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| UNIUSDT | 36% | 19% | 38% | 0% | UP |
| OPUSDT | 31% | 19% | 30% | 0% | UP |
| APTUSDT | 30% | 20% | 32% | 0% | UP |
| TRXUSDT | 29% | 25% | 29% | 0% | UP |
| FILUSDT | 29% | 18% | 31% | 0% | UP |
| WIFUSDT | 29% | 20% | 30% | 0% | UP |
| ARBUSDT | 29% | 19% | 31% | 0% | UP |
| DOTUSDT | 28% | 19% | 29% | 0% |  |
| ADAUSDT | 28% | 21% | 28% | 0% |  |
| TIAUSDT | 27% | 21% | 29% | 0% |  |
| SOLUSDT | 26% | 21% | 28% | 0% |  |
| DOGEUSDT | 26% | 22% | 28% | 0% |  |
| SUIUSDT | 25% | 21% | 26% | 0% |  |
| LINKUSDT | 25% | 21% | 28% | 0% |  |
| BCHUSDT | 24% | 25% | 28% | 0% |  |
| AAVEUSDT | 24% | 17% | 29% | 0% |  |
| HBARUSDT | 24% | 25% | 26% | 0% |  |
| XRPUSDT | 24% | 22% | 28% | 0% |  |
| ETCUSDT | 24% | 22% | 26% | 0% |  |
| ETHUSDT | 23% | 22% | 28% | 0% |  |
| SEIUSDT | 23% | 24% | 26% | 0% |  |
| BNBUSDT | 21% | 22% | 23% | 0% |  |
| LTCUSDT | 21% | 23% | 26% | 0% |  |
| BTCUSDT | 21% | 24% | 22% | 0% |  |
| NEARUSDT | 18% | 20% | 26% | 0% |  |
| ATOMUSDT | 17% | 29% | 23% | 0% | DOWN |
| INJUSDT | 16% | 20% | 24% | 0% |  |
| XLMUSDT | 15% | 26% | 22% | 0% |  |
| AVAXUSDT | 15% | 24% | 23% | 0% |  |
