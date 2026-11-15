# UpScout / DownScout (hourly candles, 24-hour horizon) — forward record

Updated 2026-11-15 09:27 UTC. Predictions so far: 783; scored (horizon passed): 638. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.724 | 4 | 25.0% | 3.1% | +178 bp/trade |
| DownScout | 0.571 | 3 | 66.7% | 38.4% | +638 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-15T08:00 UTC)

| coin | P(up move 24h) | P(down move 24h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| TRXUSDT | 13% | 47% | 29% | 0% | DOWN |
| FILUSDT | 10% | 37% | 21% | 0% | DOWN |
| BTCUSDT | 10% | 41% | 20% | 0% | DOWN |
| AAVEUSDT | 9% | 27% | 0% | 37% |  |
| SOLUSDT | 9% | 35% | 22% | 0% | DOWN |
| DOGEUSDT | 9% | 36% | 23% | 0% | DOWN |
| APTUSDT | 9% | 34% | 21% | 0% | DOWN |
| WIFUSDT | 9% | 28% | 21% | 0% | DOWN |
| UNIUSDT | 9% | 31% | 0% | 41% | DOWN TURN↓ |
| SUIUSDT | 9% | 47% | 19% | 0% | DOWN |
| ETHUSDT | 9% | 30% | 23% | 0% | DOWN |
| XRPUSDT | 9% | 28% | 0% | 30% | DOWN |
| BCHUSDT | 9% | 34% | 24% | 0% | DOWN |
| TIAUSDT | 9% | 37% | 16% | 0% | DOWN |
| OPUSDT | 9% | 33% | 24% | 0% | DOWN |
| ARBUSDT | 9% | 30% | 20% | 0% | DOWN |
| DOTUSDT | 8% | 36% | 20% | 0% | DOWN |
| LTCUSDT | 8% | 39% | 17% | 0% | DOWN |
| SEIUSDT | 8% | 45% | 18% | 0% | DOWN |
| INJUSDT | 8% | 34% | 16% | 0% | DOWN |
| BNBUSDT | 8% | 52% | 0% | 55% | DOWN TURN↓ |
| NEARUSDT | 8% | 31% | 0% | 40% | DOWN TURN↓ |
| ADAUSDT | 8% | 40% | 21% | 0% | DOWN |
| ETCUSDT | 8% | 42% | 20% | 0% | DOWN |
| LINKUSDT | 8% | 42% | 0% | 40% | DOWN TURN↓ |
| XLMUSDT | 8% | 43% | 0% | 51% | DOWN TURN↓ |
| HBARUSDT | 8% | 43% | 20% | 0% | DOWN |
| AVAXUSDT | 7% | 46% | 16% | 0% | DOWN |
| ATOMUSDT | 7% | 42% | 16% | 0% | DOWN |
