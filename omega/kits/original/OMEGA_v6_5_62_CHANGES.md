# OMEGA v6.5.61–62: ten new strategies (round 8)

Delivered as **omega-v6_5-47.html** (v6.5.62), the same file name as before, so it opens on your existing data.

## The test (PLAN8.md, written before anything ran)
Ten strategies with every setting fixed in advance, each tested once per stage. A strategy had to pass a stage to go on to the next:
1. **25 studied coins.** Up in at least 4 of the 6 years 2021–2026.
2. **51 earlier fresh coins.** A light bar, because these coins had already been used: z ≥ 1.0, and still positive with costs doubled.
3. **90 coins never used.** z ≥ 2.45: one-sided 5%, Bonferroni-corrected over the 7 strategies that reached this stage.

| Strategy | 25 coins | 51 coins | 90 new coins |
|---|---|---|---|
| 1 Cash-and-carry, always on | +12.5% (BTC+ETH) | +8.9%, z 3.56 | +3.3%, z 1.28: fail |
| 2 Harvest, managed daily | +11.0% | fail (−2.5% with costs doubled) | – |
| **3 Harvest, 10 coins** | +13.4% | +12.6%, z 4.68 | **+8.8%, z 3.38, worst fall −4.4%: PASS** |
| 4 Crowded-and-weak short | +27.1% | +27.2%, z 1.89 | −30.2%, worst fall −94%: fail |
| 5 Uncrowded-and-strong long | +52.8% | +18.7%, z 1.42 | −27.4%, worst fall −88%: fail |
| 6 Squeeze long | +48.4% | +22.5%, z 1.08 | −36.2%, worst fall −92%: fail |
| 7 Quiet, against the crowd | out (−15.2%) | – | – |
| 8 Uncrowded trend | +21.7% | +44.8%, z 2.47 | −19.6%: fail |
| 9 Trend ensemble | +19.0% (BTC+ETH) | +11.2%, z 1.88 | +2.9%, z 0.52: fail |
| 10 Settlement drift | out (−15.5%) | – | – |

**Addendum.** The other assistant's BTC/ETH pair (trend-filtered 14-day momentum and trend-filtered 55-day breakout) was also tested once on the 90 new coins. It made −0.4% and −0.7% a year: fail. On BTC itself (in-sample, with funding) the first one made +19% a year. BTC may be special, or that result may be luck. Only future weeks can tell.

## What changed
- **v6.5.61: "Download new coins (2021 – now) for the final test".** This is the file you downloaded.
- **v6.5.62: the 10-coin harvest now runs on paper.** It sits inside the funding-harvest card, beside the 5-coin version, at the top of OMEGA Strategy.
  - It uses the same forward judgement: retired at an average of zero or less after 26 weeks with positions, or after a 10% fall; confirmed at z ≥ 1.96.
  - It matches the Python test code exactly on all 153 weeks.
- **The Positioning Desk now has a Round 8 card and an 8th finding.** The crowding rules that worked on the big coins reversed on newer coins, and trend made about nothing. Being paid for supplying leverage is the only thing that kept working.
- **The research record now includes round 8.**

## Checks
- `s62_test.js` 7/7, `s60` 9/9, `s58` 9/9, `s49` 11/11, `s50` 5/5.
- `s59` 12/13: its one failing check looks for the research-record heading that round 8 replaced on purpose. `s62` now checks that heading.
- Chromium crawl: no errors.
- Phone-number guard: clean.
