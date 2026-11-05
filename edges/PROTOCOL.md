# Edge research protocol (Nov 2026 round, E37+)

This continues OMEGA's research (E1–E36, see `omega/OMEGA_HANDOVER_2026-11-02.md` and
`omega/research/plans-new/E29_E32_RESULTS.md`). The same standing rules apply: **never fabricate data, plan before data,
count every try, report true results after costs, paper/testnet first.**

## What already passed (do not re-discover, do build on)
- **Climax reversal (grade A):** 3σ hourly drop, 3× volume, close in top 40% of the candle's range → buy next open, hold 12 h.
- **Panic bounce H1 (grade B):** buy limit at C·exp(−2σ_hourly), fills only if a candle in the next 3 h trades below it, exit
  24 h after fill. H3: market-wide panic (q5 and ≥20% of coins in their bottom-10% hour), taker. Lives on big rebounds;
  single trades lost 77–93%; as a 100 USDT account drawdowns were 56–59%.

## What already failed (do not retest the same thing; a genuinely different variant must say why it is different)
Daily direction rules (12,480 in E28), CREED, gold hourly methods, forex majors hour-by-hour, session splits per market,
short-only rules, market-state rules, absorption, BTC-as-father-coin (daily), order-book depth, crowd positioning ratios,
forced deleveraging (OI drop + 5% fall), neural net on 33 daily features, delta-neutral funding harvest, new-listing fade,
pairs mean reversion, weekend gap fade (gold).

## Data
`edges/data/fetch.py` → `$OMEGA_DATA` (default `/home/user/data`): `1h/` all 923 USDT-M perps incl. delisted (2020→Nov 2026),
`5m/` 30 liquid coins (2022→), `funding/` all. `/home/user/data/symbols.json`. Other public data on data.binance.vision
(metrics, premiumIndexKlines, markPriceKlines, indexPriceKlines, aggTrades, spot klines) can be fetched by a bot into
`/home/user/data/<name>/`. Check `/home/user/data/fetch.log` for progress; a `.parquet.empty` file = no data for that coin.
Load with `edges/lib/bt.py` (`load`, `panel`, `funding`). Volume-0 candles are NaN (missing).

## Periods (fixed for every E37+ plan)
- **DISCOVERY** 2020-01-01 → 2023-12-31: search freely here; count every variant.
- **VALIDATION** 2024-01-01 → 2024-12-31: only the variants promoted by the plan; judged once.
- **FINAL** 2025-01-01 → latest: the single chosen variant per plan; judged once. Nothing gets re-tuned after FINAL.
- Coin universes: when a plan uses "untouched coins", use coins listed in `/home/user/data/symbols.json` but **not** in
  `omega/research/plans-new/E29_untouched_coins.json`, `E31_untouched_coins.json`, `E33_coins.json` if the plan says so.

## Pass mark (all must hold)
1. FINAL mean after costs > 0 with week-clustered **t ≥ 2.0**; VALIDATION also > 0 with t ≥ 1.5.
2. Beats the luck check: real DISCOVERY best vs the best of the same search on shuffled/random-time data (≥ 95th pct).
3. Positive in ≥ 60% of calendar years overall; FINAL not carried by a single month (report without the best 5% of trades).
4. Costs: `bt.round_trip_cost` (taker 0.05% + liquidity slippage per side; maker 0.02% for resting limits that fill only when
   price trades **through** the limit). Funding charged for positions held across 00/08/16 UTC when holding > 8 h.
5. Enough trades: ≥ 100 in FINAL, or ≥ 50 with t ≥ 3.

Grades: **A** passes everything; **B** passes 1–3 with fewer trades or one weak year; **C** discovery+validation only (watch list).

## Leverage (the owner asks about 20× and 40×)
Leverage never creates an edge; it scales the edge **and** the tail. For every passing rule report `bt.leverage_table`
(1, 2, 3, 5, 10, 20, 40×) using intrabar worst adverse excursion (`mae`) for liquidation, and the **highest leverage with
zero liquidations and max drawdown < 35%** at 5% of equity margin per trade. State plainly when 20× or 40× liquidates.
A stop must always sit inside the liquidation distance (stop distance < 1/leverage − 0.5%).

## Bookkeeping
- Write `edges/plans/E<nn>_<name>.md` before running anything on validation/final; `bt.register_plan()` fingerprints it.
- `bt.log_attempt()` for every variant evaluated (any period).
- Results: `edges/results/E<nn>_result.json` + a short section in `edges/RESULTS.md` (PASS/FAIL, numbers, why).
- Plan numbers: Research bot 1 uses E37–E49, bot 2 E50–E62, bot 3 E63–E75.
- A passing rule is added to `edges/approved.json` (spec the trading bots read) — schema in `edges/bots/README.md`.
- Machine: 4 CPUs, 15 GB RAM shared by 3 research bots. Keep each job under ~4 GB, ≤ 2 processes.
