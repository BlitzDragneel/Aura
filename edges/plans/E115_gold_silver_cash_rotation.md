# E115 — Monthly rotation gold / silver / cash (holding, from the brief's "ratio rotation")
Common rules E100. GC_1d and SI_1d settlement closes (Yahoo continuous futures; closes only), ^IRX cash.
At each month-end settle: momentum M_a = L-month return of gold and of silver, cash = L-month T-bill accrual (from
^IRX). Hold the asset with the higher M_a if it beats cash, else cash, for the next month. L ∈ {3, 6, 12} → 3 variants.
Variant "GOLD_OR_CASH_L" (gold only vs cash, same L) is NOT included (that is E111's V3/V8). Unfunded, 0.05% of turnover
(a switch gold → silver = 2 × turnover). Comparators: buy-and-hold gold; 50/50 gold–silver rebalanced monthly.
Pass (E100 hold): validation AND final Sharpe above buy-and-hold gold and above 50/50, max drawdown ≥ 25% smaller than
gold B&H; luck = discovery Sharpe gain over gold B&H vs 300 circular shifts of the monthly choice series (≥ 95th pct).
Note: the silver bot (E120–E139) may test gold–silver relative value as a SWING trade; this is a holding rotation.
