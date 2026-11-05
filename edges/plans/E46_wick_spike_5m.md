# E46 — Extreme 5m wick / volume-spike reversals (liquidation-cascade proxy, 30 coins)
Research bot 1, written 2026-11-05 before any data was examined for this purpose.

## Question
Liquidation cascades print long lower wicks on huge volume within minutes. Does buying right after such a 5m candle (or a
3-bar 15-minute cascade) earn more than costs?

## Rule (per coin, 5m bars)
- σ = std (ddof 1) of 1-bar log returns over the previous 168 bars; medv = median volume over the previous 288 bars (24 h).
- WICK signal: lower wick (min(o,c) − l)/c ≥ K·σ, v ≥ V·medv, close location ≥ 0.6.
- CASCADE signal: ln(c_t/c_{t−3}) ≤ −K·σ·√3, volume of the 3 bars ≥ V·3·medv, close location of bar t ≥ 0.4.
- Buy at the next bar's open (taker), exit at the close H bars after the signal bar. One open trade per coin per variant.
- Grid (16 variants): {WICK, CASCADE} × K ∈ {4, 6} × V ∈ {5, 10} × H ∈ {12 bars (1 h), 48 bars (4 h)}.

## Luck check
100 repeats, random signal bars (same count per coin).

## Common methods (research bot 1, plans E37–E46; identical text in every plan of this family)
- **Data:** `/home/user/data/5m` (30 liquid coins, 2022-01 →) and `/home/user/data/1h` (all USDT-M perps incl. delisted,
  2020-01 →), loaded with `edges/lib/bt.py` (volume-0 candles = missing). 15m bars are built from 5m (open first, high max,
  low min, close last, volume and quote volume summed; a 15m bar is valid only if all three 5m bars exist). 4h bars are built
  from 1h the same way (all four 1h bars needed). Bars are labelled by their open time; a signal on a bar is known at its close.
- **Universes:** 5m/15m plans: the 30 coins in `/home/user/data/5m`. 4h plans: every symbol in `/home/user/data/1h` except
  the equity/commodity/index/stable perps listed in `edges/research1/tradfi_exclusions.json` (written before any data was
  looked at; these instruments only exist from 2025 and are not crypto).
- **Periods (PROTOCOL.md):** DISCOVERY = data start → 2023-12-31 (5m-based: 2022-01-01 → 2023-12-31; 1h-based: 2020-01-01 →
  2023-12-31); VALIDATION 2024; FINAL 2025-01-01 → latest. A trade belongs to the period of its signal time.
- **Execution and costs:** `bt.round_trip_cost(qv24, entry, exit)` with qv24 = the coin's quote volume over the 24 h before the
  signal. Taker entries fill at the next bar's open. Limit buys are maker (0.02%, no slippage) and fill only if a later bar's
  low is **strictly below** the limit (trades through), at the limit price. Exits are taker at the close of the exit bar.
  Funding: for holds longer than 8 h, longs pay (shorts receive) the sum of funding rates with settlement time in
  (fill, exit]; holds ≤ 8 h are not charged. One open trade per coin per variant (a new signal is ignored while a trade or a
  resting limit is live).
- **Excursion:** `mae` = lowest low (longs; highest high for shorts) from the fill bar through the exit bar relative to the
  fill price; used for liquidation in `bt.leverage_table`.
- **Statistics:** `bt.summarize` (mean bp after costs, week-clustered t, years, without best 5%, trades/day). Every variant on
  every period is logged with `bt.log_attempt`.
- **Selection (fixed now):** DISCOVERY winner = highest week-clustered t among variants with n ≥ 100 and mean > 0. Promoted to
  VALIDATION: up to the 2 variants with highest discovery t that have mean > 0 and t ≥ 2.0 (none → the plan FAILS at
  discovery). FINAL: the promoted variant with the best VALIDATION t, provided VALIDATION mean > 0 and t ≥ 1.5. If no promoted
  variant passes validation the plan FAILS; the top promoted variant's FINAL is still computed once and reported for
  information only (it cannot change the verdict). Nothing is re-tuned after FINAL.
- **Luck check:** the whole discovery grid is re-run with the signal times replaced by random bars (per coin, same number of
  signals as the real rule, drawn from that coin's valid discovery bars; for calendar/timing plans the anchor is moved to a
  random time of day/month as stated in the plan). The best t of each repeat (same n ≥ 100, mean > 0 filter) forms the luck
  distribution; the real discovery best t must be ≥ its 95th percentile. Repeats: 100 (50 where a plan says so for runtime).
- **Pass mark:** PROTOCOL.md items 1–5 (FINAL mean > 0 with t ≥ 2.0; VALIDATION > 0 with t ≥ 1.5; luck ≥ 95th pct;
  ≥ 60% of calendar years positive over all periods; FINAL without the best 5% reported; ≥ 100 FINAL trades or ≥ 50 with t ≥ 3).
- **Leverage:** for a pass, `bt.leverage_table` (1–40×, 5% of equity margin per trade) on the FINAL trades and on all trades;
  max_leverage = highest leverage with zero liquidations and max drawdown < 35%.
