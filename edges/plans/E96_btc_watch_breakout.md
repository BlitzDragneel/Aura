# E96 — Movement-timing watch windows + stop-entry breakout, BTC 15m (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. Builds on E87-B (big 4 h moves are 52% likely in the model's top-quarter windows vs
34% base). Direction is unknown, so enter only once price commits: at a flagged bar i place a buy-stop at c + m·ATR14
and a sell-stop at c − m·ATR14, valid for the next 4 bars (first one triggered wins, the other is cancelled; if both in
one bar, take the adverse case = the trade is stopped at its stop in that bar). Fill at the stop price, or at the open if
the bar gaps through it (taker 0.07%). Exits: BRACKET (stop 2 ATR, target 6 ATR from the fill, 16 bars max, stop-first,
as E86) or TIME (stop 2 ATR, otherwise exit at the close 16 bars after the fill). No overlap.
Gate (flag): MODEL = E87-B LightGBM movement model (same features/settings) probability above the 75th percentile of its
own predictions over the trailing 30 days (causal); CONTROL = the E87-B vol+clock logistic, same percentile rule.
Model fitting: discovery scores are out-of-fold (train 2022 → score 2023, train 2023 → score 2022); validation from the
model trained on 2022–23; FINAL from the model trained on 2022–24 (as E87).
## Grid (8): m ∈ {0.5, 1.0} × exit {BRACKET, TIME} × gate {MODEL, CONTROL}.
Luck: gate replaced by random bars with the same count (200 runs, whole grid). Control comparison: the chosen MODEL row
must also beat the matching CONTROL row in discovery and validation (else the model adds nothing over volatility).
