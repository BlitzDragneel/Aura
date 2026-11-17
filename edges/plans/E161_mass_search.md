# E161 Mass search: 100,000 rule backtests + a 100,000-rule null, then 100,000 Monte Carlo runs for survivors
Owner: "do 100,000 simulations and 100k backtests, find it". Done as a data-mining study with guards.
Markets/bars: BTC perp 1h (2020-01 -> 2026-11), gold = PAXG 1h (gold-backed token, 2020-01 -> 2025-10; traded as gold
CFD: 0.04% round trip), BTC cost 0.14% round trip. Periods: DISCOVERY 2020-2022, VALIDATION 2023, FINAL 2024 -> end.
Conditions (~60, all known at the bar close; quantile cut-points fixed from DISCOVERY): past return 1/4/24/72/168h in
top/bottom fifth; RSI14 < 30 / > 70; close vs SMA20/50/200 above/below; ATR%-percentile top/bottom third; session
(Asia 0-7, London 7-13, NY 13-21, late 21-24 UTC); Monday / Friday / weekend; position in the 24h range top/bottom fifth;
volume z top/bottom fifth; Bollinger %B < 0 / > 1; 24h trend strength (|r24| / sum |r1|) top/bottom third; BTC only:
funding top/bottom fifth.
Rules: 100,000 random draws of 1-3 distinct conditions (AND) x direction (long/short) x hold (1, 4, 12, 24 h),
per asset 50,000. Score = day-clustered t of net return per entry bar (overlapping holds; survivors re-tested without
overlap). Minimum 150 entries in DISCOVERY.
Selection: top 100 per asset by DISCOVERY t. Survive VALIDATION: mean > 0 and t >= 1.5. Survive FINAL (judged once):
non-overlapping backtest, mean > 0 after costs with week-clustered t >= 2, positive in each FINAL year.
Null: the same 100,000-rule search on returns whose sign is flipped by random day blocks (destroys any real link, keeps
volatility); the number of null survivors at each stage is the luck baseline. The real search counts only if it beats
the null clearly at the FINAL stage.
Survivors: 100,000 bootstrap paths of their FINAL trades (1% risk) for drawdown and ruin odds.
