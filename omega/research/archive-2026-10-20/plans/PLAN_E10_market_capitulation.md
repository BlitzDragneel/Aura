# PLAN E10 — market-level capitulation bounce on the biggest coins (BTC, ETH, SOL, BNB, XRP)
Written 2026-10-20 after plans E8 and E9 and before the data exists here. E8's rule D1 (buy the 5 hardest-hit coins after a
depressed market falls 10%+ in 3 days) was positive in both halves on the 20 majors but failed on the 324 perpetuals:
in May 2022 the hardest-hit coins were the ones dying (the Terra collapse), not ones forced sellers had pushed too far.
Cause-based change, decided now: buy the MARKET's biggest coins, not the hardest-hit ones.
Data: the 15-minute file omega_history_creed15_1 (BTC, ETH, SOL, BNB, XRP; Binance spot; 2020 – Oct 2026) when it arrives,
daily closes (UTC). Never used for any state rule.
State: exactly E8's definition, computed from these five coins' own equal-weight index.
Rule: when DEPRESSED and the five-coin index's 3-day return ≤ −10%, buy all five equally at the next day, hold 3 days;
costs 0.10% a side; no overlapping positions.
Pass: weekly t ≥ 1.65, positive overall and positive in each half with trades (before 2024 / from 2024). Run once; reported
whatever happens. A pass makes it a forward candidate on the app's paper record, not a proven edge.
