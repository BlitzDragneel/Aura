# E112 — Gold seasonality, tested properly (hold)
Common rules E100. GC_1d closes, unfunded, cash earns T-bill. Rules (each = long gold on the selected days, cash else):
  S1 best-6 months: the 6 calendar months with the highest mean return in DISCOVERY; S2 best-3 months;
  S3 fixed prior (published "gold is strong Aug–Feb"): long Aug → Feb, cash Mar → Jul (no fitting);
  S4 turn of month: last 2 + first 3 trading days; S5 day of week: the weekday with the best discovery mean (one).
5 variants (+ the per-month and per-weekday tables as description). Luck: S1/S2 vs 500 permutations of the month labels
within each year (best-6 picked the same way); S4/S5 vs random day sets of equal size. Pass = E100 hold criteria (vs
buy-and-hold Sharpe) plus the ON-minus-OFF difference (mean daily return on vs off) with NW t ≥ 2 in FINAL.
