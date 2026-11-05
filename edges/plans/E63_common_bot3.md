# Bot-3 common conventions (apply to E63–E69; fingerprinted with each plan)

Written 2026-11-05 before any external series was compared with prices. Sources and their reachability:
`edges/research3/SOURCES.md`. Code: `edges/research3/`.

## Trades
- Traded instrument: the Binance USDT-M perp (`/home/user/data/1h`), entry at the **open of the first 1h bar that starts
  after the signal is publicly known** (publication lag below), exit at the open of the bar `H` hours later (time exit, no
  stop unless the plan says so). One open position per (rule, coin): signals while in a position are ignored.
- Publication lags (conservative): hourly Binance/Coinbase/Deribit bars are known at bar close (ts + 1h) → enter at ts+1h.
  alternative.me Fear & Greed value stamped day D 00:00 → enter D 02:00. DefiLlama stablecoin supply stamped D → enter
  D+1 02:00. CoinMetrics daily metrics for day D (complete after D ends, published ~02:30 D+1) → enter D+1 04:00.
- Return: side × (exit/entry − 1); `mae` = worst intrabar adverse move vs entry over the held bars (lows for longs, highs
  for shorts), used for leverage/liquidation only.
- Costs: `bt.round_trip_cost(qv24)` taker/taker (qv24 = trailing 24h quote volume at entry). Funding from
  `/home/user/data/funding` for every 00/08/16 UTC stamp strictly inside the holding window when H > 8 h (long pays rate,
  short receives); missing funding rows = 0.01%/8h charged to longs, 0 to shorts.

## Periods
Protocol periods (DISCOVERY 2020-01-01→2023-12-31, VALIDATION 2024, FINAL 2025-01-01→latest). Where a source starts
later (Deribit DVOL 2021-03-24), discovery is simply that source's start → 2023-12-31; the plan says so. The protocol's
periods are binding, so they are kept fixed rather than moved to a "first 60%" split (DVOL discovery = 2.8 of 5.6 years ≈
50%; noted as a deviation from the lead's 60% suggestion in favour of PROTOCOL.md).

## Selection and luck check
- Every variant evaluated on discovery is logged with `bt.log_attempt`. Selection metric = discovery week-clustered t
  (`bt.tstat_weekly`), require n ≥ 30 in discovery.
- Luck check: the **external series is circularly shifted** against prices by a random offset (≥ 60 days, ≤ len − 60
  days) and the *whole grid* is re-run; the best discovery t of each shifted run forms the null (200 shifts, or 100 for
  the heavy panel plans). The real best must be ≥ 95th percentile. Shifting keeps the signal's own clustering and
  frequency, so it tests "does *this* data line up with *these* prices", not just "is buying dips good".
- Promotion: at most 3 variants per plan go to VALIDATION (the best by discovery t that beat the luck check, also positive
  in ≥ 60% of discovery years). Of those, the one with best VALIDATION t that has VALIDATION mean > 0 and t ≥ 1.5 goes to
  FINAL. If none qualifies, the plan stops (FAIL) and FINAL is not looked at.
- Filters on already-passed rules (E68): the base rule is fixed exactly as PROTOCOL.md describes; a filter counts as an
  improvement only if the filtered rule passes the full pass mark AND its mean beats the unfiltered rule's mean in both
  VALIDATION and FINAL.
