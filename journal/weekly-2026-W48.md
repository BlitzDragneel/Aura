# Weekly review 2026-W48 (made 2026-11-23 00:31 UTC)

## Signal Lab, last 7 days (all markets; 'moments' = separate hours = real sample size)

| setup | signals | moments | avg R | t | won | five markets avg R | backtest avg R (BTC / gold) |
|---|---|---|---|---|---|---|---|
| S1 with | 96 | 33 | 0.172 | 1.37 | 0.71 | 0.205 | -0.064/-0.147 |
| S2 against | 41 | 18 | -0.465 | -2.86 | 0.46 | -0.494 | 0.01/0.117 |
| S2 with | 55 | 27 | -0.155 | -0.96 | 0.69 | 0.038 | -0.028/0.001 |
| S3 against | 54 | 24 | -0.186 | -1.29 | 0.44 | -0.048 | -0.067/0.111 |
| S3 with | 32 | 18 | -0.085 | -0.44 | 0.69 | -0.083 | -0.029/0.073 |
| S4 against | 38 | 16 | -0.188 | -1.17 | 0.63 | -0.058 | -0.034/0.06 |
| S4 with | 59 | 24 | -0.113 | -0.76 | 0.63 | 0.013 | -0.012/-0.002 |
| S5 against | 22 | 8 | -0.459 | -1.86 | 0.45 | -0.537 | -0.033/-0.033 |
| S5 with | 37 | 6 | 0.004 | 0.02 | 0.57 | 0.323 | 0.026/0.322 |
| S6 against | 15 | 5 | -0.155 | -0.37 | 0.73 | -0.63 | 0.072/-0.142 |
| S6 with | 56 | 5 | 0.134 | 1.18 | 0.82 | 0.358 | 0.09/0.007 |
| S7 against | 28 | 8 | -0.379 | -1.49 | 0.61 | -0.347 | 0.009/-0.213 |
| S7 with | 41 | 15 | 0.12 | 0.78 | 0.83 | 0.284 | 0.076/-0.104 |

**Signals sent with a trade plan this week:** {'signals': 9, 'moments': 6, 'avg_R': -0.742, 't': -3.86, 'won': 0.22}
**Learning changes this week:** [{'ms': 1794984367620, 'cell': 'S4 with', 'frm': None, 'to': 'muted', 'n': 15, 'avg_R': -0.339, 't': -2.02}, {'ms': 1794987963906, 'cell': 'S4 with', 'frm': 'muted', 'to': None}, {'ms': 1794997873337, 'cell': 'S4 with', 'frm': None, 'to': 'muted', 'n': 16, 'avg_R': -0.28, 't': -1.59}, {'ms': 1795014066495, 'cell': 'S4 with', 'frm': 'muted', 'to': None}, {'ms': 1795143665160, 'cell': 'S2 with', 'frm': None, 'to': 'muted', 'n': 22, 'avg_R': -0.297, 't': -1.65}, {'ms': 1795187759534, 'cell': 'S2 with', 'frm': 'muted', 'to': None}, {'ms': 1795188662009, 'cell': 'S2 against', 'frm': None, 'to': 'muted', 'n': 15, 'avg_R': -0.585, 't': -4.11}, {'ms': 1795315561503, 'cell': 'S4 with', 'frm': None, 'to': 'muted', 'n': 25, 'avg_R': -0.24, 't': -1.6}, {'ms': 1795325472993, 'cell': 'S4 with', 'frm': 'muted', 'to': None}, {'ms': 1795337167615, 'cell': 'S1 with', 'frm': None, 'to': 'earned', 'n': 33, 'avg_R': 0.205, 't': 1.63}, {'ms': 1795386659798, 'cell': 'S1 with', 'frm': 'earned', 'to': None}]

## Recorder (data nobody archives), last 7 days

Coverage: 81 runs per day on average (96 = every 15 minutes).
- BTCUSD: {'rows': 568, 'imbalance_vs_next_hour_corr': -0.016, 'liq_bursts': 40, 'after_burst_same_direction_bp': 28.2, 'spread_bp_widest_hour_utc': 0, 'spread_bp_median': 0.02}
- NAS100: {'rows': 568}
- US30: {'rows': 568}
- XAGUSD: {'rows': 568, 'imbalance_vs_next_hour_corr': -0.005, 'liq_bursts': 19, 'after_burst_same_direction_bp': -10.3, 'spread_bp_widest_hour_utc': 1, 'spread_bp_median': 11.19}
- XAUUSD: {'rows': 568, 'imbalance_vs_next_hour_corr': -0.079, 'liq_bursts': 24, 'after_burst_same_direction_bp': 7.3, 'spread_bp_widest_hour_utc': 7, 'spread_bp_median': 1.85}

## Candle memory forward record (all time; 50% = coin flip, backtest: 52-55% overall, 55-56% on its calls)

| market | scored | right (all) | CALLS right (n) | big-move calls came / base rate |
|---|---|---|---|---|
| XAUUSD | 536 | 0.5 | 0.463 (108) | 0.0 / 0.0 |
| XAGUSD | 536 | 0.573 | 0.57 (256) | 0.0 / 0.0 |
| BTCUSD | 536 | 0.511 | 0.491 (169) | 0.0 / 0.0 |
| NAS100 | 322 | 0.506 | 0.59 (39) | 0.0 / 0.0 |
| US30 | 323 | 0.471 | 0.412 (34) | 0.0 / 0.0 |

Self-reviews this week (what it changed in itself and why):

## Self-review 2026-11-19 00:31 UTC
- XAUUSD: 5913 scored (last 90 days, 152 live); right 51.5% overall, 51.8% on 1860 calls at threshold 0.55. No change (nothing beat the current settings on fresh data).
  worst situations: session New York 49.7% (n 1736), unfamiliar 50.0% (n 1183), session Asia 50.4% (n 1708)
- XAGUSD: 5913 scored (last 90 days, 152 live); right 51.6% overall, 54.4% on 2698 calls at threshold 0.53. No change (nothing beat the current settings on fresh data).
  worst situations: session Asia 49.8% (n 1708), close vote 50.7% (n 3426), session New York 50.8% (n 1736)
- BTCUSD: 5817 scored (last 90 days, 152 live); right 52.0% overall, 54.2% on 1863 calls at threshold 0.55. No change (nothing beat the current settings on fresh data).
  worst situations: close vote 50.3% (n 3746), session Asia 51.5% (n 1680), session London 51.7% (n 1454)
- NAS100: not enough scored predictions yet (143); settings unchanged (0.55, blocked [])
- US30: not enough scored predictions yet (144); settings unchanged (0.55, blocked [])
- wrong calls in the last 7 days: 363; reasons: close vote (the look-alikes were split) 222, high volatility 222, called against the 24h move 191, shock move 167, session New York 155, unfamiliar situation (few close look-alikes) 89, session London 82, session Asia 73, session late 53, news 16
## Self-review 2026-11-20 00:31 UTC
- XAUUSD: 6009 scored (last 90 days, 248 live); right 51.5% overall, 51.8% on 1877 calls at threshold 0.55. blocked situations [] -> ['session New York']
  worst situations: session New York 49.5% (n 1764), unfamiliar 50.2% (n 1202), session Asia 50.3% (n 1736)
- XAGUSD: 6009 scored (last 90 days, 248 live); right 51.9% overall, 54.6% on 2746 calls at threshold 0.53. No change (nothing beat the current settings on fresh data).
  worst situations: session Asia 49.9% (n 1736), close vote 50.9% (n 3492), session New York 51.2% (n 1764)
- BTCUSD: 5913 scored (last 90 days, 248 live); right 52.0% overall, 54.1% on 1890 calls at threshold 0.55. No change (nothing beat the current settings on fresh data).
  worst situations: close vote 50.4% (n 3813), session Asia 51.6% (n 1708), session New York 51.8% (n 1736)
- NAS100: not enough scored predictions yet (233); settings unchanged (0.55, blocked [])
- US30: not enough scored predictions yet (234); settings unchanged (0.55, blocked [])
- wrong calls in the last 7 days: 580; reasons: close vote (the look-alikes were split) 379, high volatility 352, called against the 24h move 318, shock move 260, session New York 212, session Asia 146, session London 138, unfamiliar situation (few close look-alikes) 127, session late 84, news 16
## Self-review 2026-11-21 00:31 UTC
- XAUUSD: 6105 scored (last 90 days, 344 live); right 51.5% overall, 51.8% on 1906 calls at threshold 0.55. No change (nothing beat the current settings on fresh data).
  worst situations: session New York 49.8% (n 1792), unfamiliar 50.0% (n 1221), session Asia 50.0% (n 1764)
- XAGUSD: 6105 scored (last 90 days, 344 live); right 51.9% overall, 54.5% on 2789 calls at threshold 0.53. No change (nothing beat the current settings on fresh data).
  worst situations: session Asia 49.8% (n 1764), close vote 50.9% (n 3565), session New York 51.6% (n 1792)
- BTCUSD: 6009 scored (last 90 days, 344 live); right 52.0% overall, 54.2% on 1909 calls at threshold 0.55. No change (nothing beat the current settings on fresh data).
  worst situations: close vote 50.4% (n 3874), session New York 51.6% (n 1764), session Asia 51.8% (n 1736)
- NAS100: not enough scored predictions yet (317); settings unchanged (0.55, blocked [])
- US30: not enough scored predictions yet (318); settings unchanged (0.55, blocked [])
- wrong calls in the last 7 days: 803; reasons: high volatility 560, close vote (the look-alikes were split) 531, called against the 24h move 449, shock move 378, session New York 262, session Asia 225, session London 195, unfamiliar situation (few close look-alikes) 181, session late 121, news 16
## Self-review 2026-11-22 00:31 UTC
- XAUUSD: 6201 scored (last 90 days, 440 live); right 51.5% overall, 52.0% on 1941 calls at threshold 0.55. No change (nothing beat the current settings on fresh data).
  worst situations: session New York 49.8% (n 1820), unfamiliar 50.0% (n 1241), session Asia 50.2% (n 1792)
- XAGUSD: 6201 scored (last 90 days, 440 live); right 51.8% overall, 54.4% on 2834 calls at threshold 0.53. No change (nothing beat the current settings on fresh data).
  worst situations: session Asia 50.2% (n 1792), close vote 50.8% (n 3615), session New York 51.3% (n 1820)
- BTCUSD: 6105 scored (last 90 days, 440 live); right 51.9% overall, 53.8% on 1961 calls at threshold 0.55. No change (nothing beat the current settings on fresh data).
  worst situations: close vote 50.5% (n 3915), session Asia 51.5% (n 1764), session New York 51.7% (n 1792)
- NAS100: not enough scored predictions yet (317); settings unchanged (0.55, blocked [])
- US30: not enough scored predictions yet (318); settings unchanged (0.55, blocked [])
- wrong calls in the last 7 days: 949; reasons: close vote (the look-alikes were split) 607, high volatility 594, called against the 24h move 527, shock move 417, session New York 305, session Asia 262, session London 240, unfamiliar situation (few close look-alikes) 230, session late 142, news 16
## Self-review 2026-11-23 00:31 UTC
- XAUUSD: 6297 scored (last 90 days, 536 live); right 51.4% overall, 51.7% on 1975 calls at threshold 0.55. No change (nothing beat the current settings on fresh data).
  worst situations: unfamiliar 49.5% (n 1260), session New York 49.6% (n 1848), session Asia 50.4% (n 1820)
- XAGUSD: 6297 scored (last 90 days, 536 live); right 52.0% overall, 54.5% on 2869 calls at threshold 0.53. No change (nothing beat the current settings on fresh data).
  worst situations: session Asia 50.6% (n 1820), close vote 51.1% (n 3665), session New York 51.4% (n 1848)
- BTCUSD: 6201 scored (last 90 days, 536 live); right 51.9% overall, 53.7% on 2003 calls at threshold 0.55. No change (nothing beat the current settings on fresh data).
  worst situations: close vote 50.4% (n 3984), session Asia 51.4% (n 1792), session London 51.7% (n 1550)
- NAS100: not enough scored predictions yet (322); settings unchanged (0.55, blocked [])
- US30: not enough scored predictions yet (323); settings unchanged (0.55, blocked [])
- wrong calls in the last 7 days: 1089; reasons: close vote (the look-alikes were split) 683, high volatility 622, called against the 24h move 612, shock move 451, session New York 349, session Asia 294, unfamiliar situation (few close look-alikes) 293, session London 281, session late 165, news 16

## Questions for the research session

- S1 with: +0.172R over 33 moments live this week; backtest -0.064/-0.147. Worth a registered re-test on fresh data?
- S7 with: +0.12R over 15 moments live this week; backtest 0.076/-0.104. Worth a registered re-test on fresh data?
- Recorder effects are descriptive until 4+ weeks exist; then register a test (liquidation bursts, imbalance).
- Candle memory: are its CALLS above 54% with 500+ scored per market? Then register a test of it as a filter on lab signals.
