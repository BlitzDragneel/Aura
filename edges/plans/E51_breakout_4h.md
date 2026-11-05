# E51 — Donchian breakout with ATR trailing stop on majors, 4h, both directions
Conventions: `E50_common_bot2.md`. Written before the data.

## Hypothesis
A 4h close beyond the N-bar channel starts a move that runs further than an ATR trailing stop gives back (classic turtle).
Different from E21 (breakouts with fixed 24h holds, gross, failed): here exits ride the trend with a trailing stop.

## Coins (fixed before data, ones listed on Binance futures by Sep 2020): BTC ETH BNB XRP ADA LINK LTC DOT BCH SOL.

## Rule
4h bars. Long entry when close > max(high of previous N bars); short when close < min(low of previous N bars). Enter at the
next bar's open (taker). One position per coin; ignore same-direction signals while in a trade; an opposite signal closes
and reverses (direction 'both').
Exit (grid): ATR trailing stop k × ATR(20 bars) from the highest close since entry (long; mirror for short), checked on each
bar's low/high, filled at the worse of stop and open; or channel exit: close below min(low of N/2 bars) (long; mirror).
Stop distance is always within liquidation distance in the leverage test (see common rules).

## Grid
N ∈ {20, 55, 100, 200}; exit ∈ {ATR k=2, 3, 5, channel N/2}; direction ∈ {long, short, both} = 48 variants.
Costs: taker + slippage both sides; funding for every 8h settlement held.

## Luck check
Null: per coin the same number of entries at random 4h bars (direction drawn like the real signals' long/short mix) with the
SAME exit rule; best of the 48-grid on 200 null runs vs the real best weakest-year.

## Selection / pass: common rules (trade units). Leverage via bt.leverage_table on the trades (mae = intrabar adverse).
