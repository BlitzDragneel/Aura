# Signal Auditor — scoring rules (fixed before any signal is scored)

Honesty rules, fixed before any signal is scored (edges/auditor/RULES.md explains them in plain words):
1. A signal counts from the moment it was LOGGED (the time OMEGA received it), never from a time someone claims later.
2. Every logged signal is scored: losses, breakevens and never-filled orders included. Nothing can be deleted from
   the score once its outcome is known (the app only allows deleting before the signal is filled).
3. Entry: "now"/market signals fill at the open of the first 1-minute bar after logging; a price away from the market
   fills only when price trades to it (a zone fills at its nearer edge); unfilled after `fill_hours` = NOT FILLED.
4. After the fill each 1-minute bar is checked stop-first: if the stop and a target are both inside one bar, it is a
   stop (we cannot see the order inside the bar, so we assume the worse case).
5. Two management styles are scored for every signal: "TP1" (everything closed at the first target) and
   "ladder" (equal parts closed at each target, stop moved to entry once TP1 is hit). Max hold `max_hold_h`, then
   closed at market.
6. Costs: a typical retail spread (SPREAD table) is charged once per trade.
7. A signal with no stop cannot be measured in R (risk units); it is still scored in pips and flagged NO STOP.

Why: a recap posted after the week cannot be checked; a signal logged before the move can. About 30 closed
signals with stops are needed before the numbers mean anything, 50+ to trust them.
