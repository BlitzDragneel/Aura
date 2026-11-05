# OMEGA v6.5.81 — round 18: checking another assistant's report (19 Oct 2026)

Built from v6.5.80 by `patch81.py`. Delivered as `omega-v6_5-47.html`. Plan and results: `research/PLAN18.md`. The
report and its files are kept in `research/outside/`.

## What was checked
**1. The order-flow rule** (`flow_tracker.py`): rank liquid perpetuals by their 7-day share of aggressive buying; long
the top fifth, short the bottom fifth, weekly.
- **Reproduced** on the coins where it was found (final4): +46.8% a year, t 2.95.
- **Independent test, written down before running** (PLAN18), on the 165 coins it never used, from 2020: +5.3% a
  year, t 0.72, negative with costs doubled. 2021 was −23% and 2026 −10%. **FAILED.**
- Round 12 had already tested a close relative and it failed too. **Not tracked.**

**2. New listings.**
- **Shorts pay funding in a coin's first weeks.** Our measure: −116% a year in days 0–7, easing to −30% by days
  30–90. Confirmed.
- **The +27% harvest income in 2026** that round 15 described came entirely from the 118 new listings with no Binance
  spot market, which cannot be hedged on Binance.
- **On the 81 new listings with spot,** the harvest made −2% (2025) and −3% (2026). The report was right: nothing to
  track.

## App changes
- The harvest card now gives this answer instead of "a question for the next round".
- The research record and knowledge gain round 18 (2,240 rules and studies) and a lesson.

## Checks
- s81 3/3.
- All earlier suites: s49 11/11, s50 5/5, s58 9/9, s60 9/9, s62 7/7, s67 15/15, s69 21/21, s70 21/21, s71 16/16,
  s72 11/11, s73 7/7, s77 27/27, s78 13/13, s79 9/9 (now allows later round numbers), s80 4/4.
- 111 script blocks pass `node --check`. Phone guard clean.
- Chromium shows the card with no errors.
