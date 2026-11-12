# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-12 18:57 UTC. Predictions so far: 493; scored (horizon passed): 377. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.739 | 4 | 25.0% | 4.5% | +178 bp/trade |
| DownScout | 0.516 | 1 | 0.0% | 27.3% | +286 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-12T17:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| XRPUSDT | 22% | 17% | 35% | 0% |  |
| SOLUSDT | 21% | 20% | 34% | 0% |  |
| TRXUSDT | 21% | 15% | 42% | 0% | TURN↑ |
| BTCUSDT | 20% | 18% | 34% | 0% |  |
| FILUSDT | 20% | 16% | 33% | 0% |  |
| BCHUSDT | 20% | 13% | 40% | 0% | TURN↑ |
| XLMUSDT | 19% | 16% | 31% | 0% |  |
| WIFUSDT | 18% | 16% | 31% | 0% |  |
| TIAUSDT | 18% | 13% | 32% | 0% |  |
| APTUSDT | 18% | 16% | 30% | 0% |  |
| SUIUSDT | 17% | 17% | 31% | 0% |  |
| UNIUSDT | 17% | 16% | 30% | 0% |  |
| BNBUSDT | 17% | 21% | 27% | 0% |  |
| DOGEUSDT | 17% | 19% | 32% | 0% |  |
| DOTUSDT | 17% | 15% | 30% | 0% |  |
| LINKUSDT | 17% | 17% | 29% | 0% |  |
| ETHUSDT | 17% | 19% | 33% | 0% |  |
| HBARUSDT | 16% | 19% | 29% | 0% |  |
| SEIUSDT | 16% | 15% | 32% | 0% |  |
| AVAXUSDT | 16% | 15% | 32% | 0% |  |
| ADAUSDT | 16% | 17% | 29% | 0% |  |
| ATOMUSDT | 16% | 16% | 0% | 25% |  |
| OPUSDT | 15% | 16% | 26% | 0% |  |
| LTCUSDT | 15% | 18% | 29% | 0% |  |
| NEARUSDT | 14% | 12% | 29% | 0% |  |
| INJUSDT | 13% | 12% | 30% | 0% |  |
| ETCUSDT | 13% | 18% | 26% | 0% |  |
| AAVEUSDT | 12% | 15% | 21% | 0% |  |
| ARBUSDT | 12% | 12% | 25% | 0% |  |
