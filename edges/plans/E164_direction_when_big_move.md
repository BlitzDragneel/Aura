# E164 Direction call only when a big move is expected
Why: E163's approved calls are right 55-56% but a 1-hour move is too small to beat costs. The memory predicts big moves
much better (AUC 0.70-0.75). If the direction call is taken only when a big move is expected, the same accuracy is
applied to larger moves.
Inputs: E163's walk-forward predictions (same markets, periods, costs; no new fitting).
Rule: trade when the mistake model approves (P(right) >= 0.55) AND P(big move in 4h) >= its 80th percentile in the
warm-up period before VALIDATION (fixed number, not refit). Direction = model D. Entry next open; two exits, both
reported and both counted: (a) 1 hour later, (b) 4 hours later. One trade at a time per market (no overlaps).
Control: same rule with the direction sign-flipped by a coin (luck baseline), and the big-move filter alone with D's
direction but no mistake-model approval.
Pass: FINAL net > 0 with t >= 2 and VALIDATION net > 0 (either exit), on any market; Bonferroni note: 2 exits x 4 markets.
