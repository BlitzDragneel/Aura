# OMEGA v6.5.79 — round 17: what moves the market (19 Oct 2026)

Built from v6.5.78 by `patch79.py`. Delivered as `omega-v6_5-47.html`. Research: `research/PLAN17.md`, `round17.py`,
`round17b.py`, `macro_dates.py`.

## What research found
This is description, not rules. It covers 165 coins, hourly, from 2020 to Oct 2026; final4 was left untouched.

- **The market explains about 60% of a coin's hourly move** (BTC and ETH: 68%). The coin's own aggressive buying and
  selling adds about 6 points. In 2026 the market explained less (45%).
- **The hour's biggest movers, and the most aggressively bought coins, give a little back the next hour.** The effect
  is real but smaller than trading fees, and has faded since 2024.
- **Busiest hours:** 13:00–16:00 UTC (US open). At 14:00 UTC, 2.9% of hours have a 3σ move, against about 1% at
  04:00–11:00. 00:00 UTC (the daily close) and 08:00 are also busy. Weekends are about 20% calmer.
- **CPI hour** (79 releases, dates from the BLS):
  - a median 1.3× a normal hour, and 5× in 2022;
  - rose in 75% of releases, against 51% for the same hours on other weekdays;
  - 2022 averaged −1.6%.
- **FOMC statement hour** (53 statements, Federal Reserve calendar):
  - a median 1.9× a normal hour;
  - rose in 70% (52% otherwise), mostly 2021–24;
  - flat on average in 2025–26.
- **Options expiry:** no distinct effect.
- **CME weekend "gap fill":** not supported. Over 353 weekends, big weekend moves reversed only half the time.
- **After a 3σ market-wide fall** the market rebounded +0.8% over the next day, against +0.13% for an ordinary day.
- **The climax reversal rides that rebound.** 95% of its signals come in market-wide flushes. The coins rose +1.7% in
  12h, slightly less than the market did. Coins collapsing alone by 8σ or more did worst.
- **Hypotheses for forward testing only:**
  - the CPI hour rising;
  - rejected 3σ spikes (an up-hour sold back to its bottom 40%) lagging the market for 3 days (−1.9%, 309 cases);
  - the climax without the deepest collapses.

## What changed in the app
- **Market Watch: new card, "When the market moves"**:
  - the hour now, and how busy it usually is;
  - a 24-hour map of when sudden moves happen;
  - the next scheduled events, each with what research found:
    - US CPI and FOMC (official dates, with daylight saving);
    - monthly options expiry;
    - funding settlements;
    - the CME weekend close and reopen;
  - and "What moves a coin's chart".
- **Flight recordings** are now tagged when they happen in a CPI hour, an FOMC hour or a monthly options expiry.
- **The climax reversal card** explains what the rule really catches.
- **Research record and built-in knowledge** now include round 17 (2,236 rules and studies in all).

## Checks
- **s79 (9/9):**
  - the hour map equals round 17's pooled figures;
  - CPI and FOMC times are converted from New York time with daylight saving;
  - last-Friday expiry;
  - the upcoming list, including the weekend the clocks change;
  - flight-recording tags;
  - climax note, record and knowledge.
- **All earlier suites:**
  - s49 11/11, s50 5/5, s58 9/9, s60 9/9, s62 7/7, s67 15/15, s69 21/21, s70 21/21;
  - s71 16/16, s72 11/11, s73 7/7, s77 27/27, s78 13/13.
- 111 script blocks pass `node --check`. Phone guard clean.
- **Chromium at 412 px:** the card renders above the recorder, with no errors and no sideways scroll.
- Not run on a real phone.
