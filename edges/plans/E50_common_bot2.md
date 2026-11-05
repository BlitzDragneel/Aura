# Bot-2 common conventions (apply to E50–E55; referenced by each plan, fingerprinted with them)

Written 2026-11-05 before any 1h/funding data was loaded (5m set existed; not looked at for returns).

## Data and universe
- 1h klines from `/home/user/data/1h` (all 923 USDT perps incl. delisted). 4h and 1d bars are resampled from 1h
  (UTC boundaries, o=first, h=max, l=min, c=last, qv=sum). Volume-0 candles = missing (bt.load).
- **Crypto-only universe**: excluded are stablecoins/FX (USDC, USDE*, FDUSD, TUSD, BUSD, USDP, USDBRL, USTC is kept as a coin),
  index perps (BTCDOM, DEFI, FOOTBALL, BLUEBIRD), metals/commodities (XAU, XAUT, PAXG, XAG, XPT, XPD, COPPER, NATGAS, OIL-type),
  and tokenized stocks/ETFs. Stocks are detected without return information: a symbol is TradFi if its median weekend hourly
  |range| is < 35% of its median weekday hourly |range| (stocks barely move when their home market is closed), plus a manual
  list of obvious tickers. The list is written to `edges/research2/excluded.json` before any test and frozen.
- **Liquid top-N** at each rebalance: rank by trailing 30-day quote volume (sum of qv over the 30 days before the rebalance
  time), require ≥ 60 days of history and a non-missing close at the rebalance bar. This is survivorship-free (delisted coins
  are in the data until their last bar).
- **Delisting**: if a held coin has no bars after time t (dies while held), the position is closed at its last close with an
  extra 5% loss against the holder whatever the side (conservative).

## Costs and funding
- Every change of position pays `bt.TAKER + bt.slippage(qv24)` per side on the traded notional (qv24 = trailing 24h quote
  volume of that coin). Stops are market orders (same cost), filled at the worse of the stop price and the bar open.
- Funding: a position held across a funding timestamp pays `weight × rate` (long pays positive rate, short receives it), from
  `/home/user/data/funding`. Missing funding = 0.01%/8h for longs (charged), 0 for shorts (not credited) — conservative.
  Plans whose funding data is still missing when discovery runs say so; validation/final always include funding.

## Evaluation units
- **Portfolio rules** (E50, E52, E53, E54): the unit is the daily net portfolio return (UTC day, marked to market at
  00:00 UTC, costs and funding included) on 1× gross exposure (weights sum of |w| ≤ 1). t = `bt.tstat_weekly` on these
  daily rows (clustered by ISO week). Also reported: CAGR, max drawdown, years positive, mean without the best 5% of days,
  number of orders (position changes per coin) per day, and the same numbers for buy-and-hold of the relevant benchmark.
  "Trades ≥ 100 in FINAL" is read as ≥ 100 daily observations AND ≥ 100 orders.
- **Trade rules** (E51, E55): unit = one trade (net after costs), bt.summarize.

## Selection discipline (E28 lessons)
- DISCOVERY = 2020-01-01..2023-12-31 (E55: 2022-01-01..2023-12-31, the 5m data start). Every variant is logged with
  `bt.log_attempt`. Ranking metric = the **weakest discovery calendar year** (mean daily net return for portfolio rules, mean
  trade net for trade rules); eligibility needs discovery overall t ≥ 2.0 and every discovery year > 0.
- **Luck check**: the same full grid re-run on null data (plan-specific: circularly shifted signals or random entries),
  ≥ 100 null grids; the real best ranking metric must be ≥ the 95th percentile of the null-best distribution.
- **Promotion**: at most 3 eligible variants (best by weakest year) go to VALIDATION 2024 (pass: mean > 0, t ≥ 1.5).
  The FINAL variant = the promoted variant with the highest validation t among those passing validation.
- If nothing is eligible or the luck check fails, the plan FAILS. For the owner's question (does it work in 2025–26?) the FINAL
  period is still run **once** on the single best discovery variant and reported as information only, clearly marked.
- PASS requires all PROTOCOL.md pass marks. Leverage: `bt.leverage_table` on position-level trades (entry, exit, net, mae
  from intrabar extremes) plus a portfolio-level simulation at L× gross where a day's intrabar worst move of the book
  ≥ 1/L − 0.5% = liquidation.
