# PLAN E10 — addendum A (data source), written 2026-10-21 before any of the data exists here
The 15-minute file omega_history_creed15_1 could not be found on the owner's devices, and its export was removed from the
app in an earlier build. E10 uses daily closes only, so the data source changes to the app's own wide data store: Binance
spot daily bars (closes at 00:00 UTC, the same closes the 15-minute file would give), from Jan 2020, exported by OMEGA
v6.5.88's "Save daily history" button as omega-history-daily25-*.json.gz. Only BTC, ETH, SOL, BNB and XRP are used for E10.
Everything else in PLAN_E10_market_capitulation.md is unchanged: state, rule, costs, pass mark, run once.
