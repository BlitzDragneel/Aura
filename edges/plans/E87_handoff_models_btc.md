# E87 — External-handoff learned models and macro events re-run on BTC (BTC bot, 14 Nov 2026)

Common rules: `E86_common_btc.md`; trade engine identical to E86 (15m, entry at open of i+2, stop 2 ATR, target 6 ATR,
4 h max hold, stop-first, no overlap, taker + funding). One configuration per item, fixed here.

## A. Learned price-only direction model (3 classes)
Label at bar i: fwd = close(i+16)/close(i) − 1; boundary b = max(0.0012, 0.5 × ATR14/close); class up if fwd > b, down
if fwd < −b, else flat. Features (price only, known at close i): log returns over 1, 2, 4, 8, 16, 32, 96 bars; ATR14/c;
ATR14/ATR96; range(i)/ATR; close location; distance to 16/96-bar high and low in ATR; RSI14; hour-of-day, day-of-week.
LightGBM multiclass, 200 trees, lr 0.05, 31 leaves, min_child_samples 200, subsample 0.8 (seed 0). Train on 2022-01 →
2023-12 (the last 16 bars dropped), score 2024; threshold = 98th percentile of 2024 max(P_up, P_down). Then retrain on
2022-01 → 2024-12 and score FINAL with the 2024-chosen threshold. Trade the side of the larger probability when it
exceeds the threshold. Judged as a trading rule (common pass mark, VALIDATION = 2024 out of sample from the first model).

## B. Movement-timing ("watch") model
Label: |close(i+16)/close(i) − 1| > max(0.0040, 2 × ATR14/close). Same features + LightGBM binary (same settings) vs a
volatility-and-clock control: logistic regression on [log ATR14/c, log ATR96/c, log ATR14/ATR96, hour-of-day one-hot,
weekend flag]. Same train/score splits as A. Watch windows = model probability above the 75th percentile of its 2024
predictions. Report: base rate vs rate inside watch windows, log loss of model vs control, per period (and Sep–Oct
2026, Nov 2026 to the end of data). The handoff found control log loss better; this is information, not a trade rule.

## C. FOMC follow / fade (CPI, NFP skipped: bls.gov answers 403 and FRED resets the connection from this sandbox;
no dates typed from memory)
FOMC statement dates from federalreserve.gov (fomccalendars.htm + fomc_historical_year pages), statement time 14:00
US Eastern (18:00/19:00 UTC by DST). Initial reaction = return from the 15m bar that opens at the statement time to the
close of the bar 30 minutes later; "delayed 4-hour continuation" = trade in the direction of that reaction (FOLLOW) or
against it (FADE), market entry at the open 30 min after the statement, exit 4 h later (time exit only, as the handoff's
delayed-continuation numbers were gross time-based). Report gross and net, per year. ~8 events a year → this cannot meet
the trade-count bar; reported as information against the handoff's BTC FOMC +0.643% (2024–25) → −0.126% (2026).

## D. Trend/volatility controller
Already re-run on BTC exactly as the handoff stated in E85 (FAIL as an edge, drawdown limiter). Not repeated; cited.

Attempts logged: A (1), B (2: model, control), C (2: follow, fade).
