# PLAN E29 — an improved CREED, judged on 30 coins CREED has never seen (written 2026-10-27 before any of their data)
DIAGNOSIS (design data: the app's own CREED engine replayed on 20 majors, creed15, Jan 2020 → Oct 2026, 5,053 on-time setups):
- As taught: +0.003R before costs, −0.118R after (costs 0.121R a trade; winners 10.9%).
- After a CREED setup price behaves like a driftless random walk: +1R before the stop 49% (random 50%), +2R 32% (33%),
  +3R 24% (25%), target ~5R 17.5% (~17%). The sweep + acceptance carries no directional information; changing stop, target or
  breakeven cannot create an edge from that (consistent with every earlier exit variant failing).
- 99% of setups are sweeps of the 1-hour pullback zone, not the 4-hour liquidity objectives (52 such, −0.49R gross).
- The only lever: market context. Against BTC's last 24 hours: +0.10R gross; longs only +0.19R; longs after BTC fell ≥ 2%
  +0.32R gross, +0.24R net, but weekly t only 0.66–1.30 and losing years. 6 variants were scored on design data.
CANDIDATES (m = 2), CREED's engine and exits unchanged (app v6.5.101 code, as taught: stop first, breakeven at 1R):
- C2: CREED long setups only, taken only when BTC's 24-hour log return at the decision bar is ≤ −1%.
- C5: CREED long setups only, taken only when BTC's 24-hour log return is ≤ −2%.
- C0 (as taught) is reported, not tested.
DATA: the 30 coins in E29_untouched_coins.json (md5 62de5a7f…), Binance USDT perpetual 15-minute klines from the archive,
2023-10-01 → 2026-09-30 (CREED's own design window, other coins). BTC context from BTCUSDT 15-minute (creed15, as in design).
Volume-0 candles missing. Costs 0.06% a side (as all CREED replays), results in R.
PASS per candidate: weekly t ≥ 1.96 (one-sided α 0.05/2), net mean > 0, positive in 2024, 2025 and 2026 (each with ≥ 20
trades). ALSO REPORTED: a benchmark at the same moments — the same coin bought at the decision close and held for the same
number of bars as the CREED trade — to say whether CREED's pattern adds anything over "buy after BTC fell".
Run once. If both fail, CREED's method stays as taught (byte-identical) and the app says why it does not win.
