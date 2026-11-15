# E144 Replication of E143's gold lead "OI-confirmed move" (P4): silver perp + neighbouring settings on gold
E143 found (grade C, not passed): on the gold perp, when 4h open-interest change has z >= 2 (7-day window) and price has
moved >= 2 ATR14 (15m) over 4h, following the move earned +10.4 bp/trade on FINAL (n 41), validation +4.8 (t 0.8).
A real effect should (a) appear on silver, the sister market, with NOTHING re-tuned, and (b) not depend on the exact
thresholds.
A. Silver XAGUSDT perp 1m + metrics (7 Jan 2026 ->): the identical rule, identical periods (TRAIN -> May, VALIDATION
   Jun-Aug, FINAL Sep -> 13 Nov 2026), 4h and 24h holds, cost 0.04%/side (also 0.01% tight). Random-entry control.
B. Gold neighbourhood (all counted): z threshold in {1.5, 2, 2.5} x move threshold in {1.5, 2, 3} ATR, 4h hold, on
   VALIDATION and FINAL. A plateau = at least 7 of 9 cells positive on FINAL and at least 6 of 9 on VALIDATION.
C. Pooled gold + silver, the original rule: FINAL and VALIDATION mean and week-clustered t.
Promotion to grade B (paper rule on the Gold/Silver desks) needs: silver FINAL > 0 and pooled FINAL t >= 2 and pooled
VALIDATION > 0 and the plateau in B. Otherwise it stays grade C or is dropped (if silver FINAL < 0).
