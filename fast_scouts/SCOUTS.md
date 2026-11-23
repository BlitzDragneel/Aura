# Fast scouts (15-minute candles, 4-hour horizon) — forward record

Updated 2026-11-23 02:30 UTC. Predictions so far: 1595; scored (horizon passed): 1566. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.687 | 36 | 77.8% | 9.2% | +235 bp/trade |
| DownScout | 0.635 | 16 | 50.0% | 21.3% | +27 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-23T02:15 UTC)

| coin | P(up move 4h) | P(down move 4h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| HBARUSDT | 21% | 18% | 43% | 0% | TURN↑ |
| WIFUSDT | 20% | 19% | 38% | 0% | TURN↑ |
| XLMUSDT | 20% | 18% | 45% | 0% | TURN↑ |
| TIAUSDT | 14% | 15% | 34% | 0% |  |
