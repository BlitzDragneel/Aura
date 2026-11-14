# E141 Gold pyramiding, reflected: trade only where E140's DISCOVERY losses did not cluster
Follows E140 (FAIL: pyramiding pays only in trending stretches; random entries did as well). Learn-from-losses cycle:
1. Take E140's momentum PYR k0.5 N6 trades (best E140 variant) on DISCOVERY only (XAU 2025-12 -> 2026-05; PAXG 2021-2023).
2. edges/lib/reflect.py over these features at entry (all known at entry time): hour (UTC), weekday, trend efficiency
   over the last 24 h (|net move| / sum of |5m moves|), volatility percentile (ATR/price vs trailing 30 days),
   daily trend agreement (direction agrees with close vs 20-day average: 1/0).
3. The single best bucket (highest mean R with n >= 30, both assets pooled by rank) becomes the filter. Every bucket
   examined is counted.
4. Judge the filtered rule on VALIDATION and FINAL exactly as E140 (same costs, stress, random-entry control WITH the
   same filter, account at the trader's size). Pass mark as E140. Contamination note: E140's validation/final were
   seen, so a pass here is at most grade B and goes to paper only.
