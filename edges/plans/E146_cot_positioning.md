# E146 Weekly direction for gold and silver from CFTC positioning (Commitments of Traders, disaggregated, futures only)
New information for this repo: who holds the futures. Source: publicreporting.cftc.gov (dataset 72hh-3qpy), gold
contract 088691, silver 084691, weekly since June 2006. A report is dated Tuesday and published Friday 15:30 New York:
it is treated as known only from the following Monday; trades are made at Monday's close (GC/SI daily, Yahoo).
Periods: DISCOVERY 2006-2015, VALIDATION 2016-2020, FINAL 2021 -> Nov 2026 (judged once).
Definitions: mm = (managed-money long - short) / open interest; pm = (producer long - short) / open interest;
z3(x) = z-score over the last 156 reports; d4 = 4-report change, zd = z-score of d4 over 52 reports.
Rules (weekly positions, each held from Monday close to the next Monday close; 4-week rules hold 4 weeks, overlapping
quarter-size tranches):
 C1 fade crowded funds: z3(mm) >= +1.5 short, <= -1.5 long, 4 weeks.
 C2 follow fund flows: zd(mm) >= +1 long, <= -1 short, 1 week.
 C3 follow producers: z3(pm) >= +1.5 long, <= -1.5 short, 4 weeks.
 C4 long unless crowded: long 1x except flat while z3(mm) >= +1.5; compared with buy-and-hold on Sharpe and drawdown.
 C5 gold vs silver: s = z3(mm gold) - z3(mm silver); s >= +1 long silver / short gold, s <= -1 the reverse, 4 weeks.
Costs: 0.02% (gold) / 0.04% (silver) per side on each position change; CFD financing 6.5%/yr on held notional shown as a
second line. Statistics on weekly returns with Newey-West t (lag 4).
Pass: FINAL mean > 0 after costs with t >= 2 and VALIDATION > 0 with t >= 1.5 (C4: Sharpe above buy-and-hold in both and
drawdown no worse). 9 variants, all logged.
