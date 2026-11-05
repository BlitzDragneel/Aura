# PLAN E2 — addendum A (written before running, after reading only the file's own checks)
The gold file (sha256 743289eb44a674bba4611da47116731e103d6e336e339e3d03a568d21f877d2f) holds XAU/USD only, 40,000 hours,
2020-07-15 06:00 to 2026-10-20 14:00 UTC, 0 candles corrected, 0 dropped, 10 gaps over 72 hours, marked "complete: false"
(the download stopped before Twelve Data's oldest hour). Silver was not downloaded (it was report-only).
Decision: plan E2 runs ONCE on this file as it is. Everything else in PLAN_E2_gold_hourly.md is unchanged (entry, methods,
costs, account, pass). Older gold hours downloaded later will not be used to re-run, extend or overturn E2; they could only
serve a new, separately written plan.
