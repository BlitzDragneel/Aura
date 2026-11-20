# What I know about Gold (XAU)

Built automatically from the research findings, the approved rules and my own forward record. No language model; no invented directions.

## What the research found

- Source of truth: the matching section of edges/RESULTS.md; result files in edges/results/.

## Day trades

- Common rules plans/E100_common_xau.md (md5 78d284f7…). Code edges/assets/XAU/code/. Numbers
- edges/results/E101…E115_result.json plus E101_perp_description.json; md5s in assets/XAU/code/plan_md5.json.
- 304 gold variants are logged in attempts.jsonl; 24 are empty rows from a first E114 run with a timestamp bug, rerun.
- Costs: CFD 0.02%/side plus 6.5%/yr financing per NY rollover (stress 2×); daily rules 0.05% of turnover. Periods per the
- brief. Day rules were searched on PAXG 2020–23 (hourly correlation with GC 0.984) and checked on GC 1h 2026.
- Not available: Dukascopy (not attempted); BLS calendars answer 403, so CPI/NFP/PPI were skipped. FOMC dates come from
- No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.
- My own record: 105 readings scored; big moves followed 17% of them, 28% after a WATCH (29 WATCH readings) - too few to judge yet.

## Swing trades (1-20 days)

- No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.
- My own record: 85 readings scored; big moves followed 40% of them, 30% after a WATCH (20 WATCH readings) - too few to judge yet.

## Holding (weeks-months)

- No rule has passed for this horizon, so I do not call trades here; I WAIT or WATCH.
- My own record: no readings scored yet (each is scored once its horizon has passed).

## Habits I measure myself

- Over the last 20 days the busiest session was New York (average hourly move 0.21%) and the quietest London (0.13%).
- At weekends, while spot is closed, the perpetual moves 34% as much per hour as on weekdays: weekend prices are thin and less reliable.
- A typical day ranges 1.4% from low to high (last 60 days); 35% of those days closed higher.
- Over the last 30 days the price moved -12.3% (a fact, not a forecast).

## Right now

- Price 3558.7; volatility regime extreme (hourly ATR 0.851% of price, 99.6th percentile).
- Spot XAUUSD 3558.60; the perpetual trades +0.00% from spot.

## My calls so far

- no calls yet: no tested rule for this asset has fired
