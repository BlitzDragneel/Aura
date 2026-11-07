# E80 — Exit lab: take-profit, stop, trailing stop and hold time on the two passed rules (lead, 7 Nov 2026)

**Why:** every test so far kept each rule's original exit (climax: sell 12 h after entry; H1: sell 24 h after fill).
The owner asks for different take-profits, stops and exits. If the edge is real but badly harvested, a better exit
could lift it; if better exits only appear in discovery, that is curve-fitting and must fail validation/final.

**Entries (unchanged, from edges/bots/strategies):** `climax_a` (market, next open) and `panic_h1` (limit at
C·exp(−2σ), fills only when a later bar trades through it within 3 h). All 923 perps incl. delisted, 1h bars.

**Exit grid (counted, every combination is an attempt):**
- max hold H ∈ {6, 12, 24, 48, 72} hours (exit at that bar's close, taker)
- take-profit TP ∈ {none, +2%, +4%, +8%} (resting limit; fills when a later bar's high ≥ TP; maker; the entry bar
  itself cannot hit TP for limit entries — conservative)
- stop SL ∈ {none, −5%, −10%, −20%} (from intrabar lows, taker + slippage; if a bar opens below the stop, fill at the open;
  if TP and SL are both inside one bar, assume the stop hit first — conservative)
- trailing stop TR ∈ {none, arm at +3% trail 3%, arm at +6% trail 4%} (checked on closes, exit next open, taker)
= 5×4×4×3 = 240 variants per rule, 480 in total.
Costs: bt.round_trip_cost legs (entry maker for H1 fills, taker for climax; exit maker for TP, else taker); funding
charged from the funding files for the time actually held.

**Periods:** DISCOVERY 2020-01→2023-12 picks the best variant per rule by week-clustered t (n ≥ 300).
**Luck check:** the same 240-variant search on random-entry trades (same coins, same count, random hours, market entry)
repeated 30 times; the real discovery best t must exceed the 95th percentile of the random bests.
**VALIDATION** 2024: the chosen variant per rule must be > 0 with t ≥ 1.5 and beat the rule's original exit.
**FINAL** 2025-01→latest: judged once, PROTOCOL.md pass mark (t ≥ 2, ≥ 100 trades, ≥ 60% years positive, report
without the best 5%). Leverage table for anything that passes.
**Decision rule:** an exit is adopted only if it passes FINAL; otherwise the original exits stay.
