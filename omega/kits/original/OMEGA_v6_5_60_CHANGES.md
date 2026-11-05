# OMEGA v6.5.59–60: the funding harvest and the BTC trend benchmark

Delivered as **omega-v6_5-47.html** (v6.5.60), the same file name as before, so it opens on your existing data.

## The untouched test (51 fresh coins, Jan 2020 – Oct 2026, each rule run once)

| Rule | A year | z (bar) | Costs doubled | Worst fall | Verdict |
|---|---|---|---|---|---|
| **Funding harvest** (hold the coin + short its perpetual) | **+12.0%** | **4.14 (2.13)** | **+6.5%** | **−2.3%** | **PASS** |
| Carry (frozen rule) | +49.7% | 1.70 (2.13) | +42.6% | −83.2% | fail |
| Carry over 8 coins a side | +33.4% | 1.39 (2.13) | +26.9% | −76.3% | fail |
| 14-day trend on every coin (added after) | +39.3% | 1.58 (2.24) | +34.0% | −65.1% | fail |
| BTC 14-day + 18% volatility target, on every coin (added after) | +14.2% | 1.60 (2.33) | +12.3% | −28.2% | fail |

Every test was written down before it was run (PLAN7.md and its two addenda). Each rule added later raised the bar for itself.

## v6.5.59
- **Funding harvest card** at the top of OMEGA Strategy: frozen rule `harvest-30d`, paper only.
  - Each Sunday close it holds the coin and shorts its perpetual in the 5 coins (out of the 25) whose buyers paid the most funding over 30 days, if that is above 0.1% a week.
  - The card shows this week's pairs, the coins paying the most now, the forward record and the untouched-test result by year.
  - Plainly stated: it pays mostly in boom years (+49% in 2021) and about 0% in 2025–26, and it holds nothing when funding is low.
  - Forward judgement, fixed now:
    - nothing is judged before 26 weeks with positions;
    - retired if those weeks average zero or less, or after a 10% fall;
    - confirmed at z ≥ 1.96.
  - It matches the Python test code on 153 weeks. The one exception is a week with an exact tie at 5th place, where the Python code's choice was arbitrary. The app keeps a coin it already holds, then goes by name.
- **Carry is relabelled "not an edge (failed both untouched tests); record only"**, with its fresh-coin result (−83% worst fall).
- **Positioning Desk:**
  - The untouched-test table.
  - Finding 7: only being paid for supplying leverage passed.
  - A **BTC and ETH first** card:
    - their live funding;
    - funding a short perpetual collected in every year since 2019 (BTC 2.3–30.6%, ETH 0.8–37.5%);
    - BTC/ETH trend with funding counted (in-sample, falls of −62% and −75%).

## v6.5.60
- **BTC trend benchmark card** on OMEGA Strategy: another assistant's frozen "BTC 14-day momentum + 18% volatility target".
  - It runs exactly as written, plus the funding the original left out.
  - The card shows today's position, the forward record from the close of 18 Oct (8 pm in Trinidad) and why it is a benchmark, not an edge:
    - In-sample on BTC with funding: +23.9% a year, worst fall −27.5%.
    - No single period is clear of chance on its own.
    - 14 days was among the luckiest lookbacks (7–10 days lost in 2025).
    - The same rule failed on the 51 fresh coins.
  - Forward judgement:
    - nothing before 26 weeks;
    - retired at an average of zero or less, or after a 35% fall;
    - confirmed at z ≥ 1.96.
  - It matches the Python test code day by day over 1,113 days.
- The desk's BTC/ETH card shows the benchmark's position.

## Corrections to the other assistant's live reading
- There was no "18 Oct close" yet. Their 81,542.73 is the first hour of 18 Oct.
- On proper daily closes (17 Oct vs 3 Oct), BTC's 14-day change is −3.85% (not −5.76%), and its 20-day volatility is 25.3%.
- The rule wants short 0.71×. Because it trades only when the size moves more than 0.15, it is still holding **short 0.80×** from earlier.

## Checks
- `s60_test.js` 9/9, `s59_test.js` 13/13, `s58_test.js` 9/9, `s49` 11/11, `s50` 5/5.
- Chromium crawl: no errors.
- Phone-number guard: clean.
- `s56_test.js` has one wording check ("not proven") that is replaced by `s59`'s "not an edge" check.
