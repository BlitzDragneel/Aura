# E165 Follow or fade: let the market phase decide (fakeout detection)
Owner (17 Nov): "if we had called it in the opposite direction we would have made the pips; we call the fakeouts".
Live: the 9 signals sent lost -0.77R as called, +0.44R flipped; all 105: -0.23R vs -0.18R flipped. History says
fading every breakout (E150) and reversing after stop-outs (E151) do not pay on their own. Untested: CHOOSING the side
from the market phase, and LEARNING the side online from recent results.
Data: the Signal Lab's seven setups replayed bar by bar (E148/E149 code) on gold perp, silver perp (P1: discovery
Jan-May 2026, validation Jun-Aug, final Sep-Nov), BTC (discovery 2024, validation 2025-01..06, final 2025-07..2026-11),
ETH and SOL (P2: discovery 2025-06..12, validation 2026-01..05, final 2026-06..11). Every signal is scored twice with
the live scorer: as called, and mirrored (opposite side, stop and targets mirrored around the entry), costs included.
Phase at signal time (past only): 5-day efficiency (|5-day move| / sum of hourly moves), its tercile per market from
discovery; whether the signal is with or against the 20-day trend; the 1-week move direction.
Rules:
- R1 phase switch: on DISCOVERY (pooled markets) each cell setup x with/against x efficiency tercile gets FOLLOW if
  its follow average > +0.05R and beats fade, FADE if the fade average > +0.05R and beats follow, else SKIP. Fixed.
- R2 online flip: for each market x setup take the side whose last 20 closed signals (closed before this one) averaged
  better; needs 10+ closed, else skip.
- R3 online flip with skip: like R2 but skip when both sides averaged below 0.
- Controls: follow all, fade all, R2 with shuffled history.
Pass: pooled FINAL > 0 with t >= 2, VALIDATION > 0, positive FINAL on 3+ of 5 markets.
