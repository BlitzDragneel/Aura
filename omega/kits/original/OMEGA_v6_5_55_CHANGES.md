# OMEGA v6.5.55: funding carry, the rule that passed

Delivered as **omega-v6_5-47.html**, the same file name as before, so it opens on your existing data.

## What's new

**A new card at the top of OMEGA Strategy: "Funding carry, weekly".** This is the frozen rule `carry-xs-7d`. Among everything tested off the phone, it is the only rule that passed its test.

**The rule:**
- At each Sunday's daily close (00:00 UTC Monday), rank 25 crypto markets by the funding paid over the last 7 days.
- Short the 5 highest and buy the 5 lowest.
- Each position is 1/5 of the account, so the total held is 2× the account.
- Hold for the week.
- If fewer than 15 markets can be ranked, hold nothing.
- Tied markets share their average rank, as in the research.

**Costs:** 0.06% a side on every change, plus funding paid and received.

**This week's basket.** The card shows the markets, the 7-day funding of each and its size at your Autopilot equity. The basket decided on 11 Oct is pre-freeze and does not count:
- Short: ICP, NEAR, APT, ETC, FIL
- Long: TRX, ARB, XLM, ETH, BTC

**Forward record.**
- It starts with the basket decided at the close of Sunday 18 Oct 2026. Each forward basket is recorded when it is decided and kept as recorded.
- The judgement was fixed before any forward week:
  - nothing is judged before 26 weeks;
  - after that, the rule is retired if its forward weeks average zero or less;
  - it is confirmed at z ≥ 1.96 (weekly, Newey-West), a bar that allows for looking at both 26 and 52 weeks;
  - it is retired at any time after a 25% fall from its forward peak.
- A retired rule never returns.

**Before the freeze, worked out by the app from your stored history.** These figures match the research code week by week:
- 2024–25: +62% a year, z 2.93, worst fall −17%.
- 2026: +117% a year, z 2.77, worst fall −6%.

**Also shown on the card:**
- The research record, with the official test result: 2026 +105.8% a year, z 2.88 against a bar of 2.58 (10 looks at 2026), and +99% with costs doubled.
- The one-change-at-a-time checks.
- Plain caveats: 2× gross exposure, mostly price rather than funding, a −17 to −20% fall in 2024–25, survivorship, and Sunday being a luckier rebalance day.

## How it runs

- It is an Autopilot research job (`carryxs`). It runs twice a day, and within about 30 minutes of each Sunday close once the data is stored.
- It needs every traded market's Sunday funding to be stored before it decides a basket.
- The **Update now** button runs it at once.

## Other changes

- The research report has a new field, `carryRule`: the rule, the research record, the verdict, the weekly results and the recorded baskets.
- The Brain gets one pinned note, which changes only when the verdict changes.
- The outside-research card now covers all six rounds instead of saying "no edge survived". Round 5 (2019–2023) is still waiting for the older-history file.

## What doesn't change

- Paper only: nothing places orders.
- CREED, the Autopilot's trading and every other strategy are unchanged.
- No keys are stored or exported.

## Checks

- `s55_test.js`: 12 of 12 pass.
  - Identical to the Python research code on 146 weeks (largest difference 1e-16).
  - Live-edge timing.
  - A missing Sunday funding holds the basket back.
  - Recorded baskets are kept.
  - Tie handling; holds nothing under 15 markets.
  - Every verdict path.
  - No credential-like field in the report.
  - The wiring.
- `s49_test.js`: 11 of 11 pass. `s50_test.js`: 5 of 5 pass.
- Chromium crawl at phone width: the card renders from real data, the report export includes `carryRule`, the Brain note is written, and there are no runtime errors.
- Phone-number guard: clean.
