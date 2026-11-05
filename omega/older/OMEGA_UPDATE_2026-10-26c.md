# OMEGA — update, 26 Oct 2026 (afternoon UTC). Read after OMEGA_UPDATE_2026-10-26b.md.

## The daily-trading search (E28): 9,240 rules, none survived
Log with every round, count and reason: plans-new/E28_LOG.md. Plan: PLAN_E28_daily_search.md (83cbb274…).
Promoted to 2024 validation (0948b04b…): five, all failed. Final period (2025-01 → 2026-09) untouched by any daily rule.
Main findings: small-coin and funding-carry effects were 2021–22 phenomena; next-day direction never pays costs; dip-buying
limit orders work only in rare deep dips (28% of days) and random coins did as well; hour-of-day moves < costs.
The structural conflict: the edges found live in rare moments; forcing daily trading dilutes them to nothing.
Next ideas (not run): BTC/ETH timing from aggregate funding, breadth and dispersion (multi-day holds); H1/H3 on ALL perpetuals
(more coins, more panic days); pairs of related coins.

## Apps
- Original v6.5.100: "Why signals are rare" card (Signals, Edge Lab). Change notes OMEGA_v6_5_100_CHANGES.md.
- Prime: Evidence lists E28 (five rows); the "Stand aside" verdict now says why it appears on most days.
  Test fixes: s_prime_test's page check read only the first 4,000 characters (the ledger outgrew it, now 20,000);
  s_prime_panic_test's scan check made the same over-strict "only planted coins" assertion as s98, now fixed the same way.
  Suites: 16/16 and 10/10.

## E28 scripts (e25kit/e28/): engine28.py (panel, universe, costs, funding, diagnostics), features28.py (33 features),
## search28.py (round 1), search28_r2.py, search28_r3.py, search28_r4.py, validate28.py; results round*_real/luck.jsonl,
## E28_validation.json. Data built by build_daily.py and build_funding.py from the archive (not shipped: ~1 GB).
