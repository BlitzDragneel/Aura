# E153 Smart Money Concepts on gold, BTC, silver, ETH, SOL (causal versions; library has look-ahead)
Source idea: joshyattridge/smart-money-concepts. Its fvg() marks a gap on the middle candle using the NEXT candle and
swing_highs_lows() uses a centred window (future bars), so its signals cannot be backtested as-is. Causal rules, 15m bars,
all known at the close of the bar that completes them:
 F  Fair value gap retest: bullish FVG when low[i] > high[i-2] and bar i-1 is a displacement bar (range >= 1.5 ATR14).
    Limit buy at the gap's middle for the next 16 bars (4h); stop = gap bottom - 0.25 ATR (min 0.2% of price, 6 spreads);
    bearish mirror. Variant F-T: only in the direction of the 1h trend (EMA50 vs EMA200 of 1h closes).
 O  Order block retest: displacement bar (range >= 2 ATR, body >= 60% of range) that closes beyond the prior 16-bar
    high/low; the order block = the last opposite-colour bar before it. Limit at the block's open for 16 bars; stop beyond
    the block's far extreme + 0.25 ATR (same minimum). Variant O-T: with the 1h trend.
 L  Liquidity sweep and reclaim: bar takes the prior 16-bar low by >= 0.1 ATR and closes back above it (and mirror);
    enter at next open against the sweep; stop beyond the sweep extreme + 0.25 ATR. Variant L-T with the 1h trend.
Targets every 0.5R to 2.5R, fifths with the stop to entry after TP1, scorer = edges/auditor (fine-bar path, stop first,
spread charged, 24h limit). One open trade per rule per market. 6 rules x 5 markets = 30 cells, all counted.
Periods as E148/E149/E150. Pass per rule: pooled FINAL > 0 with week-clustered t >= 2, positive on FINAL in >= 4 of 5
markets, pooled VALIDATION > 0. A pass becomes a Signal Lab setup (paper, BACKTEST+).
