# E122 — Silver day trades: CME-break gap, LBMA silver fix window, session opening-range breakouts (common methods E120)

Hourly SI, CFD costs, no overlap, stop-first. Times are converted with real time zones (Europe/London, America/New_York).
Different from the failed "session splits" (PROTOCOL): those were unconditional hour-of-day holds; here every trade is
conditional on a pre-move, a gap or a range break.

A. CME-break gap (12 variants). Gap = first bar's open after the daily break (first bar ≥ 22:00 UTC after a ≥ 1 h hole,
   Sunday reopen included) minus the last close before the break, in ATR14 units. If |gap| > k, k ∈ {0.5, 1.0}:
   FOLLOW or FADE from that bar's open (no extra delay: the gap is known at the open), hold h ∈ {1, 2, 4} bars,
   stop 2 ATR. 2 × 2 × 3 = 12.
B. Silver fix (12:00 London) window (4 variants). Pre-move = close of the 11:00 London bar vs close of the 07:00 London
   bar, in ATR. If |pre-move| > 1 ATR: FOLLOW or FADE from the 12:00 London bar's open, exit after 2 or 4 bars.
C. Opening-range breakout (8 variants). Opening range = the first hour of London (08:00 London bar) or of New York
   (08:00 NY bar, COMEX metals open 08:20). Over the next 4 bars, the first close beyond the range → trade at the next
   bar's open, stop at the other side of the range or 2 ATR (whichever is nearer), exit at the 4th bar after entry.
   Variants: session {London, NY} × trigger {close beyond, close beyond by ≥ 0.25 ATR} × vol gate {none, prior-day
   realized vol above its 250-day median}.
Selection: highest discovery t with ≥ 30 discovery trades. Luck: random-entry control (same count, hour, side mix, exits)
and the whole grid rerun with signals circularly shifted (100 shifts, best-t null).
Counted variants: 24. Cost-room table (information): mean |move| over 1/2/4 h vs the 8 bp CFD round trip, silver vs gold.
