# E43 — Funding-settlement windows conditioned on the funding rate (10 majors, 5m)
Research bot 1, written 2026-11-05 before any data was examined for this purpose.

## Question / why it is new
E4/E5 tested sessions per market unconditionally at 1h. Here the clock anchor is the funding settlement (00/08/16 UTC, or
every settlement the funding file records) at 5-minute precision, and the trade is conditioned on how crowded the side is
(the last settled funding rate vs its own trailing distribution). Hypothesis: when funding is extreme, the paying side
exits just before settlement (price moves against them) and re-enters after.

## Universe
BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX, LINK, LTC (all with 5m from 2022-01).

## Rule
- At each settlement time S, F_prev = the last settled rate before S (known). Per coin, p90/p10 = 90th/10th percentile of the
  settled rates over the previous 90 days (needs ≥ 100 settlements).
- Condition HIGH: F_prev ≥ p90 and F_prev > 0.0001 (above the 0.01% base). Condition LOW: F_prev ≤ p10 and F_prev < 0.
- Trades (taker in, taker out at 5m bar opens/closes):
  - PRE, window w: enter at the open of the bar starting at S−w, exit at the close of the bar ending at S (never held through S).
    HIGH → short; LOW → long.
  - POST, window w: enter at the open of the bar starting at S, exit at the close of the bar ending at S+w. HIGH → long; LOW → short.
  - ALL (baseline, unconditional): PRE long and POST long on every settlement.
- Grid (18 variants): w ∈ {30, 60, 120 min} × {PRE-HIGH, PRE-LOW, POST-HIGH, POST-LOW, PRE-ALL, POST-ALL}.
- No funding charged (holds ≤ 2 h, never across a settlement for PRE; POST enters after it).

## Luck check
100 repeats: the anchors S are replaced by the same number of random 5m times per coin (conditions kept by attaching each
real event's condition to a random time on the same day); best t of the 18 variants vs the real best.

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
