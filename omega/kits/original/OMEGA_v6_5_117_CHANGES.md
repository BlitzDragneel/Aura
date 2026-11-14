# OMEGA v6.5.117 — no positive size for a negative edge
- The Brain's betSize (signal "Suggested size") floored a negative ¼-Kelly at 0.25× base risk. Now a negative edge sizes **0×** and the signal says "Suggested size: none — the math says this cell has no edge, so do not trade it". Positive edges keep the [0.25×, 2×] clamps and the volatility scale.
- Checked at the same time (external audit, OMEGA-HANDOFF 12–14 Nov): the app's paper accounts, bots and Growth Bot already book cash P&L or compound correctly; no summed-percentage equity was found.
- Tests: s117 5/5; s102 (CREED byte-identical) 4/4; s58, s78, s89, s91–s99, s108–s113, s115, s116 all pass.
