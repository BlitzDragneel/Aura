# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-17 13:28 UTC. Predictions so far: 986; scored (horizon passed): 899. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.838 | 13 | 30.8% | 5.6% | +262 bp/trade |
| DownScout | 0.485 | 68 | 8.8% | 30.7% | -126 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-17T12:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| OPUSDT | 27% | 5% | 46% | 0% | TURN↑ |
| TRXUSDT | 16% | 7% | 0% | 15% |  |
| INJUSDT | 14% | 10% | 0% | 21% |  |
| BTCUSDT | 12% | 6% | 26% | 0% |  |
| FILUSDT | 11% | 5% | 0% | 19% |  |
| ETHUSDT | 11% | 5% | 21% | 0% |  |
| SOLUSDT | 10% | 8% | 0% | 26% |  |
| HBARUSDT | 10% | 7% | 27% | 0% |  |
| AVAXUSDT | 10% | 7% | 0% | 21% |  |
| ATOMUSDT | 10% | 5% | 19% | 0% |  |
| ETCUSDT | 10% | 7% | 21% | 0% |  |
| WIFUSDT | 10% | 5% | 15% | 0% |  |
| ADAUSDT | 10% | 6% | 0% | 20% |  |
| BNBUSDT | 10% | 5% | 18% | 0% |  |
| APTUSDT | 10% | 4% | 0% | 16% |  |
| XLMUSDT | 10% | 8% | 0% | 20% |  |
| DOGEUSDT | 10% | 5% | 18% | 0% |  |
| LTCUSDT | 9% | 7% | 0% | 20% |  |
| DOTUSDT | 9% | 5% | 0% | 17% |  |
| SUIUSDT | 9% | 7% | 0% | 20% |  |
| NEARUSDT | 9% | 6% | 0% | 18% |  |
| ARBUSDT | 8% | 5% | 0% | 15% |  |
| SEIUSDT | 8% | 5% | 18% | 0% |  |
| XRPUSDT | 8% | 5% | 0% | 18% |  |
| AAVEUSDT | 8% | 12% | 0% | 28% |  |
| LINKUSDT | 8% | 7% | 0% | 18% |  |
| BCHUSDT | 8% | 8% | 0% | 21% |  |
| UNIUSDT | 8% | 6% | 0% | 21% |  |
| TIAUSDT | 7% | 4% | 13% | 0% |  |
