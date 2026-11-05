# PLAN E8 — market states (depressed, booming, correcting, consolidating) and one rule with a cause for each
Written 2026-10-20, before computing anything below. Universe: the 20 major coins of the 15-minute files (creed15_2–5:
ADA, DOGE, AVAX, LINK, LTC, TRX, DOT, BCH, NEAR, ATOM, UNI, APT, ARB, OP, SUI, FIL, ICP, ETC, XLM, INJ), daily closes
(UTC), Jan 2020 – Oct 2026. Data status: already used for other rules; none of the state rules below has been computed.
Market index = equal-weight average of the coins' daily log returns (coins with data that day).
State each day, from data up to that day's close only (first match wins):
  DEPRESSED     index below its 200-day average AND index 30-day return ≤ −15%
  BOOMING       index above its 200-day average AND index 30-day return ≥ +25%
  CORRECTING    index above its 200-day average AND index 7-day return ≤ −8%
  CONSOLIDATING 30-day volatility of the index below its median of the previous 365 days AND |30-day return| < 10%
  NORMAL        anything else
Part 1 (descriptive): days in each state; the index's next-7-day return in each state (mean, median, share positive), split
2020–2023 / 2024–2026.
Part 2, one rule per state (costs 0.10% a side; decided at a day's close, held from the next day; no overlapping positions
within a rule; equal weight across the coins held):
  D1 capitulation bounce: DEPRESSED and index 3-day return ≤ −10% → buy the 5 coins with the biggest 3-day drop, 3 days.
  D2 relief-rally fade:   DEPRESSED and index 3-day return ≥ +10% → short the 5 coins with the biggest 3-day rise, 3 days.
  B1 ride the boom:       BOOMING → long the 5 best 7-day performers, 7 days.
  B2 blow-off fade:       BOOMING and index 7-day return ≥ +20% → short the 5 best 7-day performers, 3 days.
  C1 buy the correction:  CORRECTING → buy all coins equally, 7 days.
  K1 range reversion:     CONSOLIDATING → long the 5 coins nearest their 20-day low, short the 5 nearest their 20-day
                          high, 3 days.
Judged ONCE on 2024-01-01 → 2026-10-18 by weekly P&L: a rule passes if t ≥ 2.40 (one-sided 5% over 6 rules), its
2024–2026 result is positive, AND its 2020–2023 result is also positive. Reported whatever happens.
