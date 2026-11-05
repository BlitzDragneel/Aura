# OMEGA v6.5.58: the Positioning Desk (new approach)

Delivered as **omega-v6_5-47.html**, the same file name as before, so it opens on your existing data. It includes v6.5.57's fresh-coins download.

## The change of approach
Seven years of data say charts don't pay after fees, and crowding does, most years. So there is a new page in the side menu, under **Positioning — the new approach → Positioning Desk**. It reads the market by who is crowded and who pays whom, not by chart patterns.

1. **What seven years of data say.** Six findings with the year-by-year numbers:
   - 148 chart rules, none of which survived.
   - Carry by year.
   - Carry's −48% and −59% crashes, with no warning light found.
   - Funding income shrinking from 36% a year in 2021 to about 0% in 2026.
   - Momentum fading.
   - Volatility management not protecting carry.
2. **Crowding map now.** For each of the 25 coins it shows:
   - 7-day and 30-day funding as a yearly rate, and the 7-day move;
   - its "kind" (crowded, neutral or uncrowded × weak, middle or strong);
   - what that kind did the next week, Sep 2020 – Oct 2026, and in how many of the 7 years;
   - whether the carry rule holds it.

   The 3×3 map shows how many coins sit in each cell now. The steadiest cell is **crowded · weak**: it trailed the average coin in all 7 years. That is a tilt, not a sure thing.
3. **The market's state against its own history.**
   - Market funding and its decile since 2020.
   - The average coin's 14-day move, with a flag for a hard altcoin rally.
   - The funding income on offer now from the 5 best-paying coins.
4. **Carry at the size you choose: 0.5×, 1× or 2×** (2× is the frozen size). The rule never changes; only the swings do.

   | Size | A year | Worst fall |
   |---|---|---|
   | 0.5× | +19% | −18% |
   | 1× | +39% | −34% |
   | 2× | +80% | −59% |

   It shows the forward record at your size. Your choice is saved on this phone only.
5. **The next honest test.** This is the fresh-coin plan (PLAN7) and its result once the file arrives. A button takes you to the download.

Every history number on the page is a description of the past, computed in the research and embedded exactly as computed. The map and the market state are worked out from the stored daily closes and funding.

## Also
- The carry module now shares the data it has loaded, so the desk doesn't load it twice.
- The research report gains a `positioning` field: the history tables, the plan, and the current readings.
- The Brain gets one pinned note with the new approach.

## The three outside reports, checked
- Their 14-day momentum candidate is not added. Its own confidence range includes zero, and my data shows momentum reversing in 2026.
- Their volatility-persistence finding was tested as a size control for carry. It did worse than a fixed smaller size, so it is not used.
- Their shock-breadth alert gives no price direction, so it is not added as a rule.

## What doesn't change
Paper only, and nothing places orders. CREED and every other strategy are unchanged.

## Checks
- `s58_test.js` (9 of 9):
  - The desk's readings match the research code for all 25 coins.
  - The history tables are byte-identical to the research output.
  - Tie handling and stale-funding handling.
  - The wiring.
  - No credential-like fields.
- `s56_test.js` 15/15, `s49_test.js` 11/11, `s50_test.js` 5/5.
- Chromium crawl at phone width with real stored-data fixtures: no errors.
- Phone-number guard: clean.
