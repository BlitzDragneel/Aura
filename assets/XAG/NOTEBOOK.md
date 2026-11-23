# What I know about Silver (XAG)

Built automatically from the research findings, the approved rules and my own forward record. No language model; no invented directions.

## What the research found

- Source of truth: the matching section of edges/RESULTS.md; result files in edges/results/.

## Day trades

- Common methods plans/E120_common_xag.md (8cb3848d). Code edges/research_xag/, numbers results/E121–E128_result.json.
- 197 logged attempts, about 170 distinct variants (E121 was run twice after a bug fix: FOMC window and in-sample model
- selection; both runs are logged). Costs: CFD 0.04%/side for silver and 0.02% for gold + 6.5%/yr financing per night;
- maker variants use perp costs. Hourly data is 1h only (no 15m) and is short, and the bar was not lowered for it.
- BLS calendars returned 403, so CPI/NFP were skipped. FOMC dates are from federalreserve.gov.
- | Plan | md5 | Var. | Discovery best | Luck (95th pct) | Validation | Final | Verdict |
- No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.
- My own record: 190 readings scored; big moves followed 14% of them, 11% after a WATCH (57 WATCH readings) - too few to judge yet.

## Swing trades (1-20 days)

- No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.
- My own record: 170 readings scored; big moves followed 39% of them, 17% after a WATCH (63 WATCH readings) - too few to judge yet.

## Holding (weeks-months)

- No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.
- My own record: 19 readings scored; big moves followed 68% of them - too few to judge yet.

## Habits I measure myself

- Over the last 20 days the busiest session was Asia (average hourly move 0.45%) and the quietest London (0.25%).
- At weekends, while spot is closed, the perpetual moves 45% as much per hour as on weekdays: weekend prices are thin and less reliable.
- A typical day ranges 2.8% from low to high (last 60 days); 40% of those days closed higher.
- Over the last 30 days the price moved -21.2% (a fact, not a forecast).

## Right now

- Price 43.11; volatility regime active (hourly ATR 1.191% of price, 93.0th percentile).
- Spot XAGUSD 43.01; the perpetual trades +0.23% from spot.

## My calls so far

- no calls yet: no tested rule for this asset has fired
