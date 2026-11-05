# PLAN E3 — three structural hypotheses on gold hourly, then confirmation on silver
Written 2026-10-20, before computing anything for these hypotheses. Data: the gold file used once by plan E2
(sha256 743289eb44a674bba4611da47116731e103d6e336e339e3d03a568d21f877d2f, XAU/USD, 40,000 hours, 2020-07-15 → 2026-10-20).
E2 used it only for a 72-hour breakout; none of the rules below has been computed on it. Silver hourly (XAG/USD) has never
been downloaded: it is the confirmation set and is touched only for rules that pass on gold.
Hours are bar OPEN hours in UTC. Bar return = ln(close / previous bar's close). Costs per side: 0.02% (main: between
Binance gold-perp maker fees and an MT5 raw account), 0.05% also reported.

H1 — overnight drift. Cause: physical buying in Asian and London hours; futures selling in US hours.
  Rule: long from the close of the bar opening 20:00 to the close of the bar opening 12:00 (i.e. hold the bars opening
  21:00–12:00, including weekend gaps); flat for the bars opening 13:00–20:00. One round trip per trading day.
  Also reported (not tested): the US-hours-only long and plain holding.
H2 — forced-selling rebound. Cause: stop and margin cascades overshoot; price rebounds when forced sellers are done.
  Rule: at the close of hour i, z = bar return / standard deviation of the 168 bar returns before it; if z ≤ −3 and the
  bar closed in the top 40% of its range, buy at the next open, sell at the close 12 bars later. One position at a time.
H3 — weekend gap fade. Cause: thin liquidity at the Sunday reopen overshoots.
  Rule: the first bar after a break of 40+ hours; gap = ln(that bar's open / last close before the break). If |gap| ≥ 0.25%,
  trade against the gap from that first bar's close, exit at the close 12 bars later.
Measure: each strategy's P&L summed by calendar week (weeks with no position count as zero); t = mean / (sd / √weeks).
Pass on gold, for each hypothesis: t ≥ 2.13 at 0.02% a side (one-sided 5% split over 3 tests), average positive, and at
least 4 of the 7 calendar years positive. A hypothesis that passes on gold goes to silver ONCE with the same rule:
confirmed if t ≥ 1.65 and positive at 0.02%. Reported whatever the result; no rule changes after seeing data.
