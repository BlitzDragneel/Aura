# Fast scouts (15-minute candles, 4-hour horizon) — forward record

Updated 2026-11-17 04:00 UTC. Predictions so far: 1015; scored (horizon passed): 986. Models trained to 2026-11-03. Every prediction is written before its outcome is known. Information only: no bot trades these.

| Scout | forward AUC | flagged calls | hit rate when flagged | base rate | paper P&L of flags after costs |
|---|---|---|---|---|---|
| UpScout | 0.821 | 34 | 82.4% | 10.0% | +242 bp/trade |
| DownScout | 0.550 | 15 | 53.3% | 21.3% | +28 bp/trade |

Skill is real only if forward AUC stays above 0.55 and flagged hit rates stay above the base rate over hundreds of scored calls (history: UpScout AUC 0.61, DownScout 0.57 in 2025–26).

## Latest call (2026-11-17T03:45 UTC)

| coin | P(up move 4h) | P(down move 4h) | P(trend turns up) | P(trend turns down) | flags |
|---|---|---|---|---|---|
| AAVEUSDT | 15% | 12% | 0% | 30% |  |
| UNIUSDT | 15% | 11% | 0% | 32% |  |
| TIAUSDT | 14% | 8% | 0% | 24% |  |
| OPUSDT | 13% | 7% | 0% | 19% |  |
| ARBUSDT | 12% | 8% | 0% | 26% |  |
| SUIUSDT | 11% | 7% | 0% | 23% |  |
| HBARUSDT | 10% | 7% | 0% | 23% |  |
| WIFUSDT | 10% | 5% | 0% | 22% |  |
| XLMUSDT | 10% | 6% | 0% | 22% |  |
| SEIUSDT | 9% | 7% | 0% | 21% |  |
