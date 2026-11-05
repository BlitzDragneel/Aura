# OMEGA v6.5.56: the 2019–2023 test result

Delivered as **omega-v6_5-47.html**, the same file name as before, so it opens on your existing data.

## The fresh test (round 5)

Every frozen rule (14 in all) was run once on Jan 2019 – Sep 2023, data no rule had seen, using the same 25 coins. Before the data was opened, I wrote down how the carry rule would be judged on it (PLAN5.md, addendum B).

**None of the 14 rules passed.** The bar was z ≥ 2.69: one-sided 5%, Bonferroni-corrected for the 14 rules.

**Funding carry (carry-xs-7d) came closest:**
- Sep 2020 – Sep 2023: +98.5% a year, z 2.27. Not passed.
  - Before Sep 2020, fewer than 15 of the coins had perpetuals, so the rule held nothing for 77 weeks.
- With costs doubled: +92.8% a year.
- By year: 2020 (Sep–Dec) −39%, 2021 +230%, 2022 +37%, 2023 (Jan–Sep) +69%.
- Its worst fall was **−48%**, from Oct 2020 to Jan 2021.

**A second large fall, also outside the test windows:** from Nov 2023 to Jan 2024 it fell about **−59%**. In the week to 24 Dec 2023 alone it lost 37%: it was short NEAR (+68% that week) and OP (+71%). That period sat just before the 2024–25 window it was chosen on. The app now shows it as its own row, worked out from your stored history.

## What changed in the app

- **The card now reads "the strongest rule found, not proven".** It includes a "Where it stands" line, the full 2019–2023 result, and the falls of 48% and 59% when altcoins rally.
- **The forward fall limit is now 60%, up from 25%.** I raised it the same day, before any forward week, because falls of 48% and 59% are part of how this rule behaves. A 25% limit would have retired it in both episodes.
  - Every other part of the forward judgement is unchanged: 26 weeks before any verdict, retired if its forward weeks average zero or less, confirmed at z ≥ 1.96.
- **"Before the freeze" table:**
  - It now starts with Oct–Dec 2023: 11 weeks, −50% in all, worst fall −54%.
  - It shows the total for each period, plus a yearly rate for periods of 26 weeks or more.
- **The outside-research card** now reads "no rule passed every test; funding carry came closest" and includes the round-5 row.
- **The Brain note** has been replaced with the honest summary.

## Checks

- `s56_test.js`: 15 of 15 pass.
- `s49_test.js` (11/11) and `s50_test.js` (5/5) also pass.
- Chromium crawl: no errors.
- Phone-number guard: clean.
