# E124 — Gold/silver ratio swing: mean reversion and trend, relative value and silver-only (common methods E120)

Daily closes, R_t = log(GC_t / SI_t). Positions decided at close t, earn close t → t+1. CFD costs: silver 0.04%/side,
gold 0.02%/side, financing 6.5%/yr ÷ 360 per night on each leg's |notional|; stress double.
Legs: PAIR = dollar-neutral (+1 silver, −1 gold when silver is "cheap", the opposite when "rich"), notional 1 per leg;
SILVER = silver only, long when silver is cheap, short when rich (notional 1).
A. Mean reversion (12 variants): z = (R − mean_L(R)) / std_L(R), L ∈ {60, 120, 250}. Enter when |z| > e, e ∈ {1.5, 2.0}
   (z > e: silver cheap → long silver [/ short gold]); exit when z crosses 0 or after 20 trading days. × legs {PAIR, SILVER}.
B. Trend (6 variants): ratio momentum m = R_t − R_{t−L}, L ∈ {20, 60, 120}; m < 0 (silver outperforming) → long silver
   [/ short gold], m > 0 → the opposite; always in the market, re-decided daily. × legs {PAIR, SILVER}.
Evaluation: daily P&L of the book; Newey–West t (lag 10); trades = position runs. Selection: highest discovery t
(≥ 30 trades for A). Luck: whole grid rerun on the ratio signal circularly shifted against returns (200 shifts, best-t
null), and a random-entry control (same number of trades, same holding lengths and sides, random start days).
Counted variants: 18.
