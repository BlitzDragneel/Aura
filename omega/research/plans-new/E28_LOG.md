# E28 — the daily-trading search: log (every round, every count, every reason)
Plan: PLAN_E28_daily_search.md (md5 83cbb274…). Data: Binance archive, 903 USDT perpetuals incl. 163 delisted, daily 2020-11 →
2026-09, top 100 by dollar volume each day, costs 0.10%/side, real funding, 5% delisting penalty.
Baseline (hold the top-100 equally, long): 2021–2023 +21 bp/day but a −87% crash; 2021 +73, 2022 −37, 2023 +26 bp/day.

## Round 1 — 1,782 variants (31 features × ± × long-short/long/short × 5/10/20 coins × hold 1/3/7 days), discovery
Luck-best (same grid, shuffled signals): weekly t 1.67. 55 beat it, all from two ideas:
- small-over-big (size−): +12.6 bp/day, t 2.97, but fading (2021 +25, 2022 +11, 2023 +2).
- funding carry (fund−): +7 to +13 bp/day, t 2.6–2.8, mostly from funding collected.
Failed, and why: next-day direction (returns 1–3 days, intraday, close-location, sigma moves): up to 15 configs per idea were
positive before costs and negative after → daily direction ≈ random, costs win. Long-only winners: the 2021 bull (crashes
80–97%). Volatility, volume surges, beta, age: no ranking power.

## Round 2 — 6,822 variants: composites of the survivors with every feature, holds 7/14/30, beta-neutral option
Luck-best still 1.67 (3,294+ shuffled tries). Combining size and funding raised t in 97–100% of configurations (two sources);
best 0.75 funding + 0.25 size, k10, H14: +11.9 bp/day, t 4.14, dd −10%. Beta-neutral: no help. H14 best. Warning: 2023 weak
(+1 to +5 bp/day) in every top variant. Problem: overlapping 14-day cohorts are not executable at 100 USDT (orders < 5 USDT).

## Round 3 — 56 variants: executable single portfolios (rebuild every 1/3/7/14 days, or daily band ×2/3/4), k 5/10
Daily band trades on 93–99% of days and keeps most of it: funding 0.5 + size 0.5, band ×3, k10: +14.9 bp/day, t 3.26, dd −17%.

## Validation 2024 — five promoted (E28_promoted_to_validation.md, md5 0948b04b…): ALL FAIL
V1 +0.4 bp/day t 0.15 | V2 +1.6 t 0.29 | V3 −3.2 t −0.35 | V4 +2.7 t 0.37 | V5 −10.2 t −1.44; drawdowns −27% to −45%.
WHY: both ideas were mostly a 2021–2022 phenomenon. In 2024 funding was still collected (+3 to +5 bp/day) but price moves
cancelled it (coins with negative funding kept falling); the small-coin tilt lost as the large coins rallied (short leg −11.6).
The decay was visible in 2023 inside discovery: a ranking by overall t picked effects carried by 2021.

## Lessons carried forward (they change the method)
1. Rank discovery results by CONSISTENCY, not overall t: require every discovery year positive, judge by the weakest year.
2. Costs decide daily rules. The only rules that held 2024–2026 (E22/E25 H1) enter with LIMIT orders below the price; market
   entries lost. Next: maker-style limit entries (0.02% fee instead of 0.05% + slippage) for daily rules.
3. Crypto cross-sections change regime: anything that worked 2021–2022 must show it still works in 2023 before promotion.
Tries so far: 8,660 real (+ ~5,000 shuffled). Validation uses: 5.

## Round 4 — 580 variants: daily LIMIT-entry rules (discovery), ranked by the weakest year
At each close: the k most-fallen coins (7 measures) or the k most-risen (mirror), a limit m×σ30 beyond the close valid all next
day, exit at that day's close or the next; 0.12% round trip; funding. Luck check: the same orders on randomly picked coins.
- Luck reached weekly t 3.43 and a weakest year of +22 bp/day: random coins with limit orders did as well as any selection.
  0 real variants beat luck on both. Choosing which coin fell most adds nothing.
- Long dip limits k20 at 2σ, held 2 days: positive in all three years (+16/+4/+4 bp/day), t 2.1–2.2, dd −18 to −22%, BUT fills on
  only 28% of days (deep dips are rare: this is the panic bounce again). At 0.5–1σ it fills daily and 2022 turns negative (beta).
- Short limits above the day's risers: fill 75–97% of days, positive each year, t ≈ 1.1, drawdowns −94% and worse (squeezes).
## Hour-of-day (funding-settlement timing), BTC/ETH/SOL 2021–2023: the largest mean hourly moves are 3–9 bp, mostly inside
## their own noise; a round trip costs 12–20 bp. No timing rule can pay its costs. Killed by arithmetic, not by a search.

## Where the search stands (9,240 real variants; 5 validation uses; final period untouched)
- No daily rule has survived. The two cross-sectional effects (small coins, funding carry) were real in 2021–2022 and gone by
  2024. Daily direction is not predictable enough to pay costs. Limit-order dip buying works only in rare deep dips.
- The structural conflict: the edges found live in RARE moments (panics). Forcing them to trade daily dilutes them to nothing.
- Next ideas, not yet run: market-level timing of BTC/ETH (aggregate funding, breadth, dispersion), hold several days; a
  "daily watch" of H1/H3 across ALL perpetuals (more coins = more frequent panics, same rules); pairs of related coins.

## Round 5 — 3,240 variants: timing BTC, ETH and a top-10 basket from 15 market-wide gauges (discovery)
Gauges: median/BTC funding, breadth (share up, share above 30-day average), dispersion, market returns 1/3/7/30 days, BTC
7-day volatility and return, BTC vs alts, ranges, volume surge — each ranked against its own previous 365 days (causal).
Long-short / long / short, ±, top/bottom 10–50%, held 1/3/7 days, costs and funding. Luck: each gauge circularly shifted.
- Luck reached weekly t 2.53 and a weakest year of +10.9 bp/day. Real: best t 2.55 (in the market 8% of days), 0 beat luck on
  both. Rules in the market most days: t ≤ 1.37, drawdowns 46–82%. No daily timing edge.
## Tries: 12,480 real variants (+ the same number of luck runs). Validation uses: 5. Final period untouched.

## Descriptive, not tests (data already used)
- How often H1 fires (2024-01 → 2026-10-18, E25 rules): across all perpetuals a filled order on 95% of days (median 15 a day);
  across the top 100 by volume 82% of days (median 3); the 40-coin watch in the apps far less. → apps get a 40/100 switch.
- E26's −10% stop: the same 2024–26 fills average −0.04% with E26's stop and exits, +0.32% without (E25). The stop cuts the
  coins that dip further and then rebound.
- E26's account WITHOUT the stop, 2021 → Oct 2026 (E26_nostop_DESCRIPTIVE.json, md5 d68175f2…): 20 × 5 USDT seats 100 → 1,588
  (2021 +846%, 2022 −27%, 2023 +63%, 2024 +59%, 2025 −25%, 2026 +18%), max drawdown −55%, worst trade −99%; 10 × 10 USDT
  seats 100 → 649, drawdown −85%, 2025 −54%, 2026 −42%. More seats = smoother; 100 USDT cannot spread wider (5 USDT minimum).
  Not money-safe. A forward paper record WITHOUT a stop is what the apps keep.
