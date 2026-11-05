# PLAN E13 — addendum A, written 2026-10-21 after exploring one night (21 Oct 01:32–08:18 UTC) and before any qualifying data
1. Exclusion: minutes from 2026-10-21 01:00 to 08:59 UTC were explored and are removed from every E13 question.
2. Several exports may be combined (merged minute by minute; a minute counts once). The minimum stays: at least 5 UTC days
   in which BTC has live data in ≥ 80% of minutes (the days need not be consecutive). E13 runs ONCE, on the first merged set
   that reaches the minimum; the sha256 of every file used is recorded first.
3. New question Q4 — short-squeeze exhaustion (the mirror of Q1; cause: forced buyers run out once squeezed shorts are gone).
   Event (per coin): a minute whose short liquidations (liqS, USDT) are at least 10× that coin's median non-zero minute of
   short liquidations, while pC rose ≥ 1% over the previous 15 minutes; events on one coin at least 60 minutes apart.
   Group F: open interest fell ≥ 0.5% over the 15 minutes up to the event; group N: the rest.
   Outcome: SHORT from the next minute's close for 60 minutes, minus 0.10% costs.
   Pass: group F has ≥ 30 events, average positive with t ≥ 1.65 (clustered by hour), and it beats group N.
4. New description Q5 — thin hours (not pass/fail): Q1 and Q4 events pooled, outcome as the reversal trade; averages for
   events in 21:00–08:00 UTC versus 08:00–21:00 UTC, with counts.
