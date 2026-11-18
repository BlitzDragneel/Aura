# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-18 21:58 UTC. Predictions so far: 1102; scored (horizon passed): 986. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.842 | 13 | 30.8% | 5.2% | +262 bp/trade |
| DownScout | 0.542 | 68 | 8.8% | 28.1% | -126 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-18T20:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| FILUSDT | 24% | 16% | 40% | 0% | TURN↑ |
| HBARUSDT | 21% | 25% | 40% | 0% |  |
| APTUSDT | 20% | 16% | 42% | 0% | TURN↑ |
| BTCUSDT | 17% | 26% | 39% | 0% |  |
| ETHUSDT | 16% | 19% | 39% | 0% |  |
| TRXUSDT | 16% | 22% | 0% | 28% |  |
| LTCUSDT | 15% | 26% | 39% | 0% |  |
| AVAXUSDT | 14% | 25% | 36% | 0% |  |
| OPUSDT | 14% | 12% | 39% | 0% |  |
| BNBUSDT | 13% | 24% | 34% | 0% |  |
| XRPUSDT | 13% | 23% | 29% | 0% |  |
| DOTUSDT | 13% | 21% | 33% | 0% |  |
| ARBUSDT | 13% | 17% | 40% | 0% | TURN↑ |
| SOLUSDT | 13% | 18% | 31% | 0% |  |
| XLMUSDT | 13% | 22% | 27% | 0% |  |
| DOGEUSDT | 12% | 20% | 28% | 0% |  |
| WIFUSDT | 12% | 23% | 29% | 0% |  |
| SUIUSDT | 12% | 24% | 27% | 0% |  |
| LINKUSDT | 12% | 26% | 31% | 0% |  |
| ETCUSDT | 12% | 19% | 33% | 0% |  |
| ADAUSDT | 12% | 28% | 31% | 0% | DOWN |
| SEIUSDT | 11% | 23% | 27% | 0% |  |
| AAVEUSDT | 11% | 29% | 27% | 0% | DOWN |
| BCHUSDT | 11% | 16% | 25% | 0% |  |
| NEARUSDT | 10% | 13% | 29% | 0% |  |
| ATOMUSDT | 10% | 26% | 25% | 0% |  |
| UNIUSDT | 10% | 11% | 24% | 0% |  |
| INJUSDT | 9% | 13% | 25% | 0% |  |
| TIAUSDT | 7% | 14% | 27% | 0% |  |
