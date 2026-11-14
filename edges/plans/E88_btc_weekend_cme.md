# E88 — BTC weekend / CME-gap / session-range day rules (BTC bot, 14 Nov 2026)
Common rules: `E86_common_btc.md`. Data: BTCUSDT 1h, DISCOVERY 2020–23, VALIDATION 2024, FINAL 2025 → end.
Clock: CME BTC futures weekend close = Friday 16:00 America/Chicago, reopen = Sunday 17:00 America/Chicago (DST-correct
conversion to UTC). "Friday close price" = close of the 1h bar ending at the CME close; reopen price = open of the 1h bar
starting at the reopen. No new idea from E43 (funding windows) / E44 (US open) / E45 (turn of month) is repeated.

## Grid (14 variants, all logged)
1. CME gap fill (6): gap = reopen price / Friday close − 1; if |gap| ≥ g, g ∈ {0.5%, 1%, 2%}: trade TOWARD the Friday
   close at the reopen bar's open (taker); take-profit = resting maker limit at the Friday close price (fills only when a
   later bar trades through it); else exit at the close H hours after entry, H ∈ {24, 72} (taker). No stop.
2. Weekend hold (2): long / short from the Friday close to the reopen open (taker both sides, funding charged).
3. Monday follow / fade (4): weekend move = BTC close at Monday 00:00 UTC / Friday CME-close price − 1; entry at the
   Monday 00:00 UTC open in (follow) or against (fade) its sign; exit after H ∈ {8, 24} h, taker.
4. Asia-range breakout (2): range = high/low of 00:00–08:00 UTC bars; first 1h close outside the range between 08:00 and
   20:00 UTC → FOLLOW (enter next open, stop at range mid, exit 20:00 UTC close) or FADE (enter next open against it,
   stop at range edge ± 1 × range width beyond the break, exit 20:00 UTC). Stop-first engine as E86 (gap-through exits at
   the open). Weekdays only.

## Selection, luck check, judgement
Selection by common rules (best discovery t, mean > 0, n ≥ 100 for the event rules; the weekend/Monday rules trade once a
week (≈ 200 in discovery) so n ≥ 100 applies). Luck check: the WHOLE grid re-run with the weekly clock shifted by a random
whole number of hours (12 … 156) — i.e. treating a random other hour of the week as "Friday close / Sunday reopen /
Monday 00 / Asia session" — 150 shifts; the real best t must be ≥ the 95th percentile of shifted best t's. This tests
whether the CME weekend clock is special. Control (day rules) = the same shifted-clock version of the chosen variant.
Chosen variant → VALIDATION; if VALIDATION > 0 with t ≥ 1.5 → FINAL, judged once.
