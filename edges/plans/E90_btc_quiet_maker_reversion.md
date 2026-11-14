# E90 — BTC 15m quiet-window maker mean reversion (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. Idea: E87-B shows big 4 h moves are partly forecastable from volatility and the
clock; in the QUIET windows (low recent volatility) price may oscillate, so resting maker orders both sides of the price
could earn small reversions while paying only maker fees.
Rule at each 15m close with no open position and the gate true: place a buy limit at c − k·ATR14 and a sell limit at
c + k·ATR14, valid for the next bar only (one-cancels-other; if both would fill in the same bar, treat as the ADVERSE
case: the side that then loses more is taken — conservative). Fill only on trade-through (maker 0.02%). Exit: maker limit
back at c (the signal close) when a later bar trades through it; else taker exit at the close H bars after the fill.
Gate: ATR14/close in the lowest q of its trailing 960 bars (10 days), q ∈ {0.2, 0.4}, AND hour-of-day not in 13–16 UTC
(US data/cash-open hours, the most volatile clock hours; fixed here, not searched).
## Grid (8): k ∈ {0.5, 1.0} × q ∈ {0.2, 0.4} × H ∈ {4, 16}. Plus 2 information rows with no gate (k 0.5/1.0, H 16).
Luck check: gate replaced by random bars with the same count (200 runs, whole grid); real best t ≥ 95th pct.
Note stated in advance: if the ungated rows are as good as the gated ones, the gate adds nothing and the luck check is
expected to fail even if reversion exists; that will be reported as such, not rescued.
