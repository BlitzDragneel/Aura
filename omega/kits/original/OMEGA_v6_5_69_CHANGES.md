# OMEGA v6.5.69: round 12 winners on paper

Built from v6.5.68 by patch69.py. Delivered as omega-v6_5-47.html.

## Round 12 in one line
600 known strategies, then 100 combinations and 5 own ideas. The final test ran once on 125 coins no round had touched
(bar z ≥ 3.29). **2 passed, both the funding harvest plus RSI(5) dip-buying.** Plan and results: PLAN12.md in the
research archive.

## What changed
- **New card at the top of OMEGA Strategy, under the harvest: "Round 12 winners — harvest + dip-buying".** It runs
  two frozen paper strategies, computed exactly as in the research code:
  - **C028:** half the 10-pair harvest, half RSI(5) dip-buying (long only, sized to volatility). Untouched coins:
    +3.95% a year over the market, z 3.31, worst fall −3.6%.
  - **C016:** harvest 15 pairs 53.6%, dip-buying 23.4%, long when 3-day funding is negative 12.7%, Supertrend 7/2
    5.2%, SMA 10/50 5.1%. Untouched coins: +4.12% a year, z 3.90, worst fall −2.6%.
- **For each strategy the card shows:**
  - the harvest pairs (open / close / keep);
  - the perpetual positions after the latest close, in USDT for your account size, with what changed today;
  - the forward record and verdict;
  - its history on your stored data.

  You place any orders; OMEGA places none. A note appears when amounts are below an exchange's minimum order.
- **Warning on both harvest cards** when a held coin's funding over the last 24 hours is below −0.3%. That means the
  short side is paying. On the untouched coins a squeeze like this cost the harvest 7.7% in one week.
- **Data loader:** now also passes daily highs and lows (used by the Supertrend part). Nothing else reads them.
- **Positioning Desk:** a Round 12 card.
- **Research record:** round 12 added.
- **Brain observation and research report:** both carry round 12.
- **Autopilot:** a job "Round 12 winners" runs twice a day.

## Judgement (fixed 18 Oct 2026, before any forward week)
- Nothing is judged before 26 weeks.
- After that, a rule is retired if its weeks average zero or less, and confirmed at z ≥ 1.96.
- It is retired at any time on a 10% fall from its forward peak. A retired rule never returns.

## Not changed
CREED, the three desk markets, the existing harvest rules (identical to the Python test code on 153 weeks), the Brain's
method and the trading rules. Everything stays paper only.

## Checks
- **s69 (21/21): every part reproduces the research code day by day on the 25 coins (2,476 days).**
  - Dip-buying, funding-negative and Supertrend match to about 10⁻¹⁵.
  - Both harvests match exactly.
  - SMA 10/50 differs on 36 days. These are exact ties of the two averages, where float rounding decides the sign;
    the yearly result is identical, 17.31% in both.
  - The blends match within 0.04% a year.
  - Positions, flags and the forward judgement are tested.
  - The app's final-test figures equal round12_final.json.
- **Regression tests:** s67 15/15, s62 7/7, s60 9/9, s58 9/9, s50 5/5, s49 11/11. The headline-wording checks in
  s62 and s67 now accept the round-12 headline, on purpose.
- **Browser test with the 25-coin data:** the card renders under the harvest and the desk card renders, with no
  sideways scroll at phone width and no page errors.
- **Phone-number guard:** clean.
