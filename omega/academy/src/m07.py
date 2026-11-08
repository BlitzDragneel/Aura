MODULE = {
"id": "m07", "title": "Testing your own ideas", "free": False,
"summary": "How to turn a trading idea into a fair test: a written hypothesis, plan before data, in-sample versus out-of-sample, luck checks and t-statistics, realistic costs, the classic traps, and a walk-through of real tests from the OMEGA research.",
"lessons": [
{
"id": "m07-l01", "title": "Why test: the graveyard of untested ideas",
"body_md": r"""
# Why test?

Every trader has ideas. "Gold always reverses at the London open." "Buy BTC when funding goes negative." "Fade the first move after news." The question is never *whether* an idea sounds good. It is **whether it makes money after costs on data it has never seen**.

## The graveyard

OMEGA's research is, among other things, a graveyard of reasonable-sounding ideas. A sample:

| Idea | Why it sounded good | What happened |
|---|---|---|
| Turn of month (E45) | Money flows at month-end | +358 bp, t 4.84 in 2020–23 → −292 bp, t −2.65 in 2025–26 |
| Fear & Greed extremes (E63) | "Be greedy when others are fearful" | +794 bp on 28 trades, failed the luck check |
| Coinbase premium (E65) | US demand leads price | t 2.42 in discovery → t 0.34 final |
| Funding contrarian (E54) | Crowded traders get squeezed | Failed 2024; final CAGR −43% |
| Donchian breakouts (E51) | Classic trend-following rule | Random entries with the same stop did better |
| BTC → alt lead-lag (E55) | Alts follow Bitcoin | Gross ≈ 0 bp; net −19 to −32 bp a trade |
| Neural network, 33 features (E32) | Machines find hidden patterns | −0.10%/day, within luck's range |
| CREED (E29, E31) | Structured top-down method | Coin flip; −0.10R to −0.12R after costs |

Many of these would have convinced you on a chart. Several produced numbers that look highly significant in the first test. Only a **fair, pre-planned test on unseen data** separated them from the two that held up.

## What a test protects you from

1. **Losing money on something that never worked.** Most ideas.
2. **Losing money on something that used to work.** Like turn of month.
3. **Over-sizing something that works a little.** A real but small edge, traded large, still blows up on its tails.
4. **Fooling yourself with your own examples.** The trades you remember are not a sample.

## You can test without being a programmer

There are three levels:

| Level | How | Good for |
|---|---|---|
| 1. Manual chart test | Scroll back, record every occurrence of your rule in a spreadsheet | Simple rules, a first look |
| 2. OMEGA Research Lab / Edge Lab | The app tests conditions on your stored history with fixed rules, then on held-out data / forward weeks | Checking conditions the Lab supports |
| 3. Code (Python) | A backtest with costs, multiple periods and a luck check | Serious testing |

All three follow the same principles, which the rest of this module teaches:

1. Write the hypothesis and exact rules **first**.
2. Decide the **pass mark** first.
3. Split the data: **discovery**, **validation**, **final**.
4. **Count every variant** you try.
5. Include **realistic costs**.
6. Run a **luck check**.
7. Judge the final data **once**.

## The mindset

The goal of a test is not to prove your idea right. It is to **try hard to prove it wrong**. If it survives an honest attempt to kill it, it's worth a small forward test. If it doesn't, you've just saved money.

A good scientist is happy when a test fails cleanly: they learned something for the price of an afternoon instead of a year of losses.

## Exercise

1. Write down the indicator rule you chose in Module 4 (or a new idea) as one sentence.
2. Open the **Research Lab** page. Read its pipeline: *1-min history → Hypothesis → In-sample → Held-out test → Knowledge*. Note which of the seven principles above it already applies.
3. Open the **Edge Lab** and read its pipeline: *Built-in knowledge → Untested candidates → Half A, then half B → Forward weeks → EDGE*. Write how "half A then half B" relates to discovery and validation.
""",
"key_points": [
 "The question is whether an idea makes money after costs on data it has never seen.",
 "Many reasonable ideas (turn of month, Fear & Greed, Coinbase premium, breakouts) failed fair tests.",
 "Testing protects you from ideas that never worked, that stopped working, or that you over-size.",
 "You can test manually, with OMEGA's Research Lab and Edge Lab, or in code — the principles are the same.",
 "Aim to prove your idea wrong; if it survives, forward test it small."
],
"quiz": [
 {"q": "What is the real question about any trading idea?", "options": ["Does it sound logical?", "Does it make money after costs on data it has never seen?", "Did it work last week?", "Do influencers use it?"], "answer": 1, "why": "Only out-of-sample results after costs separate real edges from noise."},
 {"q": "What happened to the Fear & Greed extremes idea (E63)?", "options": ["Passed with grade A", "Looked big on 28 trades but failed the luck check", "Was never tested", "Became H3"], "answer": 1, "why": "A large average on few trades was not better than what random shifts produced."},
 {"q": "What should a test try to do?", "options": ["Prove the idea right", "Try hard to prove the idea wrong", "Find the best parameters", "Avoid costs"], "answer": 1, "why": "Surviving a serious attempt to kill it is what gives an idea credibility."},
 {"q": "What does the Edge Lab's 'half A, then half B' resemble?", "options": ["Discovery then validation on separate data", "Doubling position size", "Trading two markets", "Using two exchanges"], "answer": 0, "why": "Find on one half, confirm on the other — the same logic as discovery and validation."}
]
},
{
"id": "m07-l02", "title": "Hypothesis and plan-before-data",
"body_md": r"""
# Hypothesis and plan before data

The single most powerful habit in testing is to **write everything down before you look at the results**. OMEGA's research made this a hard rule: each plan was written to a file and fingerprinted (an md5 checksum) before validation or final data were touched, so the rules could not be changed after the fact.

## Why "plan first" matters

If you look at results and then adjust the rules, you are fitting the rules to the data. Every adjustment is a hidden extra test. After ten adjustments, you are no longer testing an idea — you are describing the past.

## A test plan template

```
PLAN: [short name]                   Date written: ______
1. Hypothesis (why it should work):
2. Market(s) and timeframe:
3. Exact entry rule:
4. Exact exit rule (time / target / stop):
5. Position size and costs assumed:
6. Variants I will try (and how many):
7. Data periods: discovery ____ validation ____ final ____
8. Pass mark (decided now):
9. Luck check method:
10. What I'll do if it passes / fails:
```

## Writing a good hypothesis

A good hypothesis has a **reason**:

- Weak: "RSI under 25 on BTC 1h goes up."
- Better: "After a sharp, high-volume drop, forced selling is exhausted, so price tends to rebound over the next 12 hours."

The reason helps you design the rule, guess when it might stop working, and resist rules that fit by coincidence.

## Exact rules — no judgement calls

Every rule must be checkable by someone else, or by code, with no interpretation:

| Vague | Exact |
|---|---|
| "Strong support" | "Low within 0.2% of the lowest low of the previous 48 hourly candles" |
| "Big volume" | "Volume ≥ 3 × average volume of the previous 24 candles" |
| "Exit when momentum fades" | "Exit at the close 12 hours after entry" |
| "Good trend" | "Close above the 50-period SMA and the SMA higher than 10 candles ago" |

## Decide variants in advance — and count them

It's fine to try variants (for example RSI thresholds 20, 25, 30 and hold times 6, 12, 24 hours = 9 variants). Write the list first and **log every one you run**. OMEGA did this for every plan: E37 had 24 variants, E50 had 192, E80 had 480, and the counts are reported with the results. More variants means a stricter luck check (Lesson 4).

## A worked example plan

```
PLAN: Gold London-open fade            Written: 2026-11-10
1. Hypothesis: the first hour after London open often overshoots
   as stops are triggered; price partly reverts by the US session.
2. XAUUSD, 15m and 1h candles.
3. Entry: if the 03:00–04:00 T&T (summer) hourly candle moves > 1.5 × ATR(14, 1h),
   enter opposite at the next open.
4. Exit: at 08:00 T&T, or stop at 1 × ATR beyond the extreme.
5. 0.01 lot; spread 0.25 + slippage 0.10 per side assumed.
6. Variants: threshold 1.0 / 1.5 / 2.0 × ATR = 3 variants.
7. Discovery 2021–2023, validation 2024, final 2025 → today.
8. Pass: final mean > 0 after costs, t ≥ 2, ≥ 100 trades (or 50 with t ≥ 3);
   validation > 0 with t ≥ 1.5.
9. Luck check: same rule on random hours of the day (100 runs).
10. Pass → paper 50 trades. Fail → record it and drop it.
```

Note: OMEGA's research already lists "session splits per market" and gold hourly methods as failed. A plan like this would need to say how it is genuinely different — the protocol requires that for any retest.

## The bookkeeping habit

Keep a simple **attempts log** — one line per variant run:

```
date | plan | variant | period | trades | mean after costs | t
```

If you can't show your attempts log, you can't trust your best result.

## Exercise

1. Fill in the plan template for your own idea from Lesson 1. Be exact in sections 3 and 4.
2. Decide your variants and write the total number.
3. Save the plan with today's date *before* looking at any results. (A screenshot or email to yourself works as a simple fingerprint.)
""",
"key_points": [
 "Write the hypothesis, exact rules, variants, periods and pass mark before seeing results.",
 "Each adjustment after seeing results is a hidden extra test; plan-first prevents fitting the past.",
 "A good hypothesis has a reason that explains why it should work and when it might stop.",
 "Rules must be exact enough for someone else or code to apply without judgement.",
 "Keep an attempts log of every variant; your best result is only meaningful with the full count."
],
"quiz": [
 {"q": "Why did OMEGA fingerprint each plan before using validation or final data?", "options": ["To compress the file", "So the rules couldn't be changed after seeing results", "For copyright", "To speed up backtests"], "answer": 1, "why": "The checksum proves the plan existed unchanged before the data was seen."},
 {"q": "Which rule is exact enough to test?", "options": ["Buy at strong support", "Buy when volume ≥ 3 × the 24-candle average and close ≥ 60% of the range", "Buy when it feels oversold", "Buy good trends"], "answer": 1, "why": "It can be checked without interpretation."},
 {"q": "You test 3 thresholds × 3 hold times. How many variants must you log?", "options": ["1 (the best)", "3", "6", "9"], "answer": 3, "why": "3 × 3 = 9; every one counts."},
 {"q": "What must a retest of an already-failed idea say, according to the protocol?", "options": ["Nothing", "How it is genuinely different", "That it uses more leverage", "That it's on a new exchange"], "answer": 1, "why": "Otherwise you're just retrying a failed test until luck shows up."}
]
},
{
"id": "m07-l03", "title": "In-sample, validation and out-of-sample",
"body_md": r"""
# In-sample, validation and out-of-sample

The core of fair testing is to keep some data **untouched** until the very end. Data you search on can't also be the data that proves your result.

## The three periods

| Period | Also called | What you do | OMEGA's dates (E37+) |
|---|---|---|---|
| Discovery | In-sample, training | Explore, try variants, pick the best | 2020-01-01 → 2023-12-31 |
| Validation | Hold-out 1 | Check the promoted few, **once** | 2024 |
| Final | Out-of-sample, test | Judge the single chosen variant, **once** | 2025-01-01 → latest |

**Nothing gets re-tuned after the final test.** If it fails, it fails.

## Why three, not two?

With only two periods, people tend to try idea after idea until one passes the second period — which quietly turns the second period into discovery. Validation acts as a filter; the final period is the one you can't touch more than once.

## Real examples of the drop-off

| Plan | Discovery | Validation 2024 | Final 2025–26 |
|---|---|---|---|
| E37 panic limit 5m | +72.6 bp, t 2.56 | +93.8 bp, t 1.83 | +31.8 bp, t 1.05 |
| E40 breadth panic 15m | +92.5 bp, t 2.63 | +90.8 bp, t 1.56 | +24.7 bp, t 0.74 |
| E65 Coinbase premium | +27.0 bp, t 2.42 | +62.2 bp, t 2.49 | +6.7 bp, t 0.34 |
| E66 perp premium | +340 bp, t 6.21 | +140 bp, t 2.49 | +49.2 bp, t 1.47 |
| E45 turn of month | +358 bp, t 4.84 | −36.5 bp, t −0.19 | −292 bp, t −2.65 |

Look at E65: it passed **both** discovery and validation and still faded to almost nothing in the final period. Without a final period, it would have looked like a winner.

## Choosing periods for your own test

- **Discovery** should include different conditions: up, down and sideways markets. For crypto, 2020–23 covers a boom (2021) and a bust (2022).
- **Validation** and **final** should each have enough trades to judge — the protocol asks for at least 100 trades in the final period (or 50 with t ≥ 3).
- **Use time order.** Don't randomly mix days into the periods; markets change over time, and the real question is "does it work *later*?"

## Other ways to hold data out

- **Untouched coins:** E22 passed the climax on **324 untouched coins** — coins never used in designing it. This is a "cross-sectional" hold-out, and a powerful one.
- **Half A / half B:** the Edge Lab finds on one half and checks on the other.
- **Forward testing:** the ultimate out-of-sample — data that didn't exist when you made the rule. The Edge Lab's *forward weeks* and the paper bots do this.

## Walk-forward (an advanced option)

Some tests repeatedly train on a window and test on the next. The E81 scouts did a simple version: train 2020–23 → test 2024; train 2020–24 → test 2025–26. It's fair as long as each test period is never used for choosing settings.

## Common ways people leak the final period

1. **"Just checking"** the final period early, then going back to tweak.
2. **Choosing the market or coins** after seeing which did well recently.
3. **Picking the start date** that makes results look best.
4. **Re-running the final** with a "small bug fix" that happens to improve results. (OMEGA logged reruns and fixes explicitly, e.g. a funding over-charge bug in E50 runs.)

## Doing it in the OMEGA Research Lab

The Research Lab tests a condition **in-sample**, then on a **held-out test**, and only adds it to *Knowledge* (and OMEGA Signals) if it held. Its trade rules are fixed — entry at the hourly close, stop 1 ATR, target 1.5 ATR, closed after 24 hours — so you can't tune them to the data. That fixed design is itself a protection against overfitting.

## Exercise

1. For your plan from Lesson 2, write the exact discovery, validation and final dates. Check that each period should have enough occurrences of your setup.
2. In the **Research Lab**, run (or review) a condition's in-sample and held-out results for one market. Did the held-out result shrink?
3. Make a rule for yourself: "I will look at my final period once, and record the result whatever it is."
""",
"key_points": [
 "Discovery is for searching; validation checks the promoted few once; final judges one variant once.",
 "Nothing is re-tuned after the final test.",
 "Results usually shrink out of sample; E65 passed discovery and validation and still faded in the final period.",
 "Other hold-outs: untouched coins (climax on 324), half A/half B, and forward testing.",
 "Avoid leaks: no early peeks, no choosing coins or dates after seeing results."
],
"quiz": [
 {"q": "Which period may you search freely and try many variants on?", "options": ["Discovery", "Validation", "Final", "None"], "answer": 0, "why": "Discovery is the in-sample search period; the others are judged once."},
 {"q": "Why have a final period as well as validation?", "options": ["To double the data", "Because repeated tries can turn validation into discovery; the final period is touched only once", "Exchanges require it", "It isn't needed"], "answer": 1, "why": "The final period is the untouched judge."},
 {"q": "What happened to E66 (perp premium) from discovery to final?", "options": ["t 6.21 → t 1.47", "t 1.47 → t 6.21", "Stayed at t 6.21", "Was never run"], "answer": 0, "why": "A huge discovery result shrank to an insignificant one."},
 {"q": "Which of these leaks the final period?", "options": ["Writing the plan first", "Checking the final early, then tweaking the rule", "Using time order", "Logging all variants"], "answer": 1, "why": "Any tweak after seeing final data makes it no longer out-of-sample."}
]
},
{
"id": "m07-l04", "title": "Luck checks and the t-statistic",
"body_md": r"""
# Luck checks and the t-statistic

Even random trading produces winning streaks and impressive-looking results. This lesson gives you two tools to tell skill from luck: the **t-statistic** and the **luck check**.

## The t-statistic, simply

The t-statistic asks: *how many "standard errors" is my average result away from zero?*

```
Standard error (SE) = standard deviation of trade results / √(number of trades)
t = average result / SE
```

### Worked example

200 trades, average +0.25% after costs, standard deviation 2.0%.

```
SE = 2.0 / √200 = 2.0 / 14.14 = 0.141%
t  = 0.25 / 0.141 = 1.77
```

A rough guide:

| t | Rough meaning |
|---|---|
| below 1 | Indistinguishable from zero |
| 1–2 | Suggestive, not convincing |
| 2–3 | Reasonable evidence (if you didn't try many variants) |
| above 3 | Strong (still check for luck from searching) |

OMEGA's pass mark required **t ≥ 2.0 in the final period** and **t ≥ 1.5 in validation**.

### Week-clustered t

Trades that happen at the same time — like 20 coins all bought during one crash — are not independent. If you treat them as separate, your t looks bigger than it should. OMEGA used **week-clustered** t-statistics, which group trades by week. A simple manual version: compute the result **per week**, then do the t-test on the weekly numbers.

## The problem with many tries

If you test 100 random variants, about 2–3 of them will show t above 2 by pure chance. So a t of 2.5 is impressive for **one** pre-planned test, and unimpressive as the **best of 100**. That's why you need...

## The luck check

A luck check asks: *if there were no real effect, how good would my best result look after the same search?*

Methods used in OMEGA's research:

1. **Random-time entries:** replace your signal with random entries (same number of trades, same exits and stop). Repeat many times. E51 found random entries with the same stop beat the Donchian breakout.
2. **Shuffled or shifted data:** shift the signal series against prices (for example by a few weeks), breaking any real link but keeping its pattern, and rerun the **whole** search. Research bot 3 used circular shifts of the external data.
3. **Null grids:** rerun the full grid of variants on many random versions (E50 used at least 200 null grids) and record the best each time.

Then compare: your real best must beat the **95th percentile** of the random bests.

### Examples from the research

| Plan | Real best | Random best (95th percentile) | Verdict |
|---|---|---|---|
| E37 panic limit 5m | t 2.56 | t 0.29 | Beats luck |
| E39 panic limit 4h | t 3.15 | t 3.91 | **Below luck** — random dips did as well |
| E63 Fear & Greed | t 1.53 (n ≥ 30) | t 3.46 | Fails |
| E66 perp premium | t 6.21 | t 2.63 | Beats luck |
| E50 trend | +8.5 bp/day | ranked at the 70th percentile | Fails (needs 95th) |

E39 is the striking one: a t of 3.15 looks excellent — but random limit buys produced t 3.91. The "edge" was just "buy dips with a limit order in a rising market".

## Two more checks

- **Without the best 5% of trades:** if removing the top 5% turns a profit into a loss, the result depends on a few outliers. E37 final: +31.8 bp → **−32.7 bp** without the best 5%.
- **Year by year:** the protocol needed positive results in at least 60% of calendar years, and the final period not carried by one month.

## A manual luck check you can do

For a chart-based rule you tested by hand on 60 occurrences:

1. Note the average result 12 hours later.
2. Pick 60 **random** times (use a random number generator for dates/hours) on the same market.
3. Measure the same 12-hour result from those times.
4. Repeat steps 2–3 a few times. Is your rule clearly better than the random sets?

In a rising market, random longs make money too. Beating zero is not enough; you must beat random.

## Exercise

1. Compute t for: 80 trades, average +0.6R, standard deviation 2.2R. (SE = 2.2 / 8.94 = 0.246; t ≈ 2.44.)
2. Do the manual luck check above for a simple rule on one market (even 20 occurrences and three random sets is instructive).
3. For your plan, write which luck check you'll use and what percentile your result must beat.
""",
"key_points": [
 "t = average ÷ (standard deviation ÷ √trades); OMEGA required t ≥ 2 in the final period.",
 "Trades at the same time aren't independent; use week-clustered t (or weekly results).",
 "The best of many variants looks good by chance; a luck check compares it with the best of random searches.",
 "E39 had t 3.15 but random limit dips reached t 3.91 — below luck.",
 "Also check results without the best 5% of trades and year by year; beating zero is not enough, you must beat random."
],
"quiz": [
 {"q": "100 trades, average +0.4%, standard deviation 2%. What is t?", "options": ["0.2", "2.0", "4.0", "20"], "answer": 1, "why": "SE = 2/10 = 0.2; t = 0.4/0.2 = 2.0."},
 {"q": "Why can't you trust the best t from 100 variants at face value?", "options": ["t is always wrong", "Some variants will show t above 2 by chance", "100 is too few", "Costs are ignored"], "answer": 1, "why": "Searching many variants finds lucky ones; that's what the luck check measures."},
 {"q": "What did E39's luck check show?", "options": ["Real t 3.15 beat random easily", "Random limit buys did as well or better (t 3.91)", "No trades", "It passed with grade A"], "answer": 1, "why": "The panic trigger at 4h added nothing beyond random limit dips."},
 {"q": "Why use week-clustered t-statistics?", "options": ["They're faster", "Trades in the same week (e.g. one crash) are not independent", "Exchanges report weekly", "To remove losing weeks"], "answer": 1, "why": "Clustering avoids overstating significance from many simultaneous trades."}
]
},
{
"id": "m07-l05", "title": "The traps: overfitting, survivorship, look-ahead and costs",
"body_md": r"""
# The traps

Most bad backtests aren't fraud. They're honest mistakes that make results look better than reality. Here are the big ones, with how OMEGA's research avoided each.

## 1. Overfitting

**What:** tuning rules until they fit the past perfectly, including its noise.

**Signs:** many parameters; very specific values (RSI 23, hold 17 hours); great discovery results that collapse later; performance that depends on one exact setting.

**Defences:**
- Few parameters, round values, decided in advance.
- Check **neighbouring** settings: if RSI 23 works but 20 and 26 don't, it's noise.
- Fixed exit rules (the Research Lab's 1 ATR stop / 1.5 ATR target / 24 h).
- Count variants and run a luck check.

E80 is a good example of resisting overfitting: 480 exit variants were tried, the discovery winner for the climax (a +2% take-profit) **lost** out of sample, and the original simple exit was kept.

## 2. Survivorship bias

**What:** testing only on coins (or stocks) that still exist today. The ones that crashed and were delisted — exactly where crash-buying strategies lose most — are missing.

**Defences:** include delisted instruments. OMEGA's data covers **all 923 USDT-M perps including delisted** (2020 → Nov 2026), and E25 specifically re-ran the panic bounce with **143 delisted coins**. Research bot 2 used a survivorship-free top-N universe and added a **5% delisting penalty**.

## 3. Look-ahead bias

**What:** using information that wasn't available at the time of the trade.

**Common forms:**
- Using the candle's close to decide to buy *at that candle's open*.
- Using data published later (e.g. on-chain or sentiment data with a delay) as if known in real time.
- Using an indicator calculated with future values (some "repainting" indicators).
- Selecting coins by *today's* top-100 list.

**Defences:** decide on a **closed** bar and enter at the **next** bar's open. Research bot 3 entered *"at the first open after the data is public"*. OMEGA Signals fire only on a **closed** hourly bar. The bots' contract: `last row = the bar that just CLOSED`.

## 4. Unrealistic fills

**What:** assuming every limit order fills when price touches it, or market orders fill at the last price.

**Defences:** fill a limit only when price trades **through** it; add slippage to market orders; use liquidity-dependent slippage for small coins. OMEGA's `round_trip_cost`: taker 0.05% + liquidity slippage per side; maker 0.02% only when price trades through the limit.

## 5. Ignoring costs and funding

**What:** testing before costs. Many short-term ideas look great gross and lose net (E55: gross ≈ 0 bp, net −19 to −32 bp).

**Defences:** fees, spread, slippage, and **funding** for perps held across 00/08/16 UTC (charged in the research when holding over 8 hours); swaps for CFDs.

## 6. Data errors

**What:** bad ticks, missing candles, zero-volume bars treated as real prices.

**Defences:** check data. OMEGA treats volume-0 candles as missing, and E25's data was cross-checked against a reference set (exact match).

## 7. Small samples and outliers

**What:** 28 trades with a huge average (E63 Fear & Greed); results driven by one coin that rose 50× (E52).

**Defences:** minimum trade counts (≥ 100 final, or 50 with t ≥ 3); report **without the best 5%**; look at the worst single trade and day.

## 8. Regime dependence

**What:** an edge that only existed in one market phase (2021's boom, small-coin and funding effects in 2021–22).

**Defences:** yearly breakdowns; require ≥ 60% of years positive; a final period after the discovery years.

## A quick trap checklist

```
[ ] Rules and variants written before results; all variants logged
[ ] Neighbouring parameter values also checked
[ ] Delisted instruments included
[ ] Decide on closed bar, enter next open; no future data
[ ] Limits fill only when price trades through
[ ] Fees, slippage, funding/swap included
[ ] Data cleaned (zero-volume bars, gaps)
[ ] ≥ 100 final trades; results without best 5%; worst trade noted
[ ] Year-by-year results; final period untouched until the end
```

## Exercise

1. Run your plan from Lesson 2 through the checklist. Which traps are you most exposed to?
2. If you're doing a manual chart test, explain exactly how you'll avoid look-ahead (e.g. "I cover the chart to the right of the signal candle before deciding").
3. Re-read one result in this course (e.g. E52 or E63) and name the trap the research's checks caught.
""",
"key_points": [
 "Overfitting: few parameters, round values, check neighbours, fixed exits, count variants.",
 "Survivorship: include delisted coins — OMEGA used all 923 perps and re-tested with 143 delisted coins.",
 "Look-ahead: decide on a closed bar, enter at the next open, use data only once it's public.",
 "Realistic fills and full costs (fees, slippage, funding, swaps) turn many gross edges into net losses.",
 "Check sample size, outliers (without best 5%) and year-by-year results."
],
"quiz": [
 {"q": "A rule works at RSI 23 but not at 20 or 26. What is the most likely explanation?", "options": ["A precise edge", "Overfitting to noise", "Survivorship", "Low fees"], "answer": 1, "why": "Real effects usually work across neighbouring settings."},
 {"q": "Why does survivorship bias especially flatter crash-buying strategies?", "options": ["Delisted coins are where crashes didn't bounce, and they're missing", "Survivors have higher fees", "It only affects shorts", "It doesn't"], "answer": 0, "why": "Coins that crashed to zero are exactly the worst trades for crash buyers."},
 {"q": "Which is look-ahead bias?", "options": ["Entering at the next open after a closed signal bar", "Using a candle's close to buy at that same candle's open", "Including delisted coins", "Adding slippage"], "answer": 1, "why": "You couldn't know the close at the open."},
 {"q": "What did E55 show about costs?", "options": ["Gross +50 bp, net +40 bp", "Gross ≈ 0 bp, net −19 to −32 bp a trade", "No costs applied", "Costs were refunded"], "answer": 1, "why": "Without costs it looked neutral; with costs it clearly lost."}
]
},
{
"id": "m07-l06", "title": "Walk-through: a real test from start to finish",
"body_md": r"""
# Walk-through: a real test, start to finish

Let's walk through how OMEGA's research tested ideas, using two real examples: one that **failed** (turn of the month, E45) and one that **passed** (the panic bounce survivorship test, E25). Then you'll do a small version yourself.

## Example 1: E45 — turn of the month (FAIL)

### The hypothesis
Money flows (salaries, fund rebalancing) cluster around month-end and month-start, which might push crypto prices up in those days.

### The plan
Written and fingerprinted before validation and final data were used (md5 763ec85e). 6 variants (different numbers of days before and after month-end). Standard costs and periods.

### Discovery (2020–23)
Best variant "N3 M1": **+358 bp a trade, t 4.84, 450 trades**. That's a huge, highly significant-looking result.

### Luck check
Real t 4.84 versus the random 95th percentile of 2.81 — **it beat luck**.

### Validation (2024)
**−36.5 bp, t −0.19.** It failed validation.

### Final (information only, 2025–26)
**−292 bp a trade, t −2.65** — every period 2024–26 was negative.

### Verdict
**FAIL.** *"Turn of month was a 2020–23 effect and went negative after that."*

### What it teaches
A discovery result can pass every check — big t, enough trades, beats the luck check — and still be an effect of one period. Only data after the discovery period could reveal it. If you had traded it in 2024 based on 2020–23, you'd have lost.

## Example 2: E25 — panic bounce with delisted coins (PASS)

### The hypothesis
Panic selling overshoots; a deep limit buy during a panic captures part of the rebound. But earlier tests might have been flattered by **survivorship** — coins that crashed and died may be missing.

### The plan
Re-run H1 and H3 on **883 coins including 143 delisted**, with the same rules and costs.

### Data check
The data was cross-checked against a reference dataset: exact (median and 99.9th percentile differences of 0).

### Result
**H1 +0.32% a trade (t 4.54); H3 +0.30% (t 4.08).** The edge survived adding back the dead coins.

### Caveats reported with it
Lives on the big rebounds (without the best 5% each loses about 0.7% a trade); single trades lost 77–93%; and later years show it fading.

### What it teaches
A good test **attacks the most likely weakness** of the idea. For crash-buying, that's survivorship. The idea survived that attack — but the researchers still reported every caveat, and later results (2024–26) are tracked rather than assumed.

## Your turn: a small manual test

Pick a simple, exact rule. For example:

> "On BTC 1h, after an hourly close down more than 2.5%, buy at the next open and sell 12 hours later."

1. **Plan (write first):** rule, exit, costs (say 0.16% round trip), periods (e.g. Jan–Jun for discovery, Jul–Sep validation, Oct–now final), pass mark (final average > 0 after costs and better than random entries).
2. **Discovery:** scroll the 1h chart in **Analysis** (or exported data). Record every occurrence: date, entry price, exit price, result minus 0.16%.
3. **Luck check:** pick the same number of random hours in the same period; record the 12-hour results.
4. **Validation and final:** repeat, once each, without changing the rule.
5. **Report honestly:**

```
Plan: BTC −2.5% hour, hold 12 h      Variants tried: 1
Discovery:   n = __, mean = __%, random mean = __%
Validation:  n = __, mean = __%
Final:       n = __, mean = __%
Without best 5%: __%
Verdict: PASS / FAIL / not enough trades
```

With small samples you'll probably get "not enough trades" — which is an honest and useful answer. It tells you a rule like this needs many coins or many years to judge.

## Or use the Research Lab

Run one of the Lab's conditions on a market and record: the in-sample result, the held-out result, and whether it was added to Knowledge. Compare the two numbers. That's the same discovery → out-of-sample drop you saw in E45.

## Exercise

1. Complete the small manual test (or a Research Lab run) and fill in the report template.
2. Log the attempt in your attempts log with the number of variants.
3. Write a two-sentence verdict, including at least one caveat — even if it "passed".
""",
"key_points": [
 "E45 turn of month: t 4.84 in discovery and beat luck, then −36.5 bp in 2024 and −292 bp in 2025–26 — FAIL.",
 "A result can pass every discovery check and still be an effect of one period.",
 "E25 attacked the panic bounce's likeliest weakness (survivorship) with 143 delisted coins — and it held.",
 "Report caveats even for passes: outlier dependence, worst trades, fading.",
 "A small manual test or Research Lab run teaches the full process; 'not enough trades' is a valid verdict."
],
"quiz": [
 {"q": "What did E45 do in discovery?", "options": ["−292 bp", "+358 bp, t 4.84, and beat the luck check", "Failed the luck check", "Had no trades"], "answer": 1, "why": "It looked excellent in discovery, then failed later."},
 {"q": "What is the lesson of E45?", "options": ["Luck checks are useless", "Only data after the discovery period can reveal a one-period effect", "Turn of month is a great edge", "t above 4 guarantees success"], "answer": 1, "why": "Discovery checks can't detect an effect that simply stops later."},
 {"q": "What weakness did E25 attack?", "options": ["High fees", "Survivorship bias, by adding 143 delisted coins", "Look-ahead", "Leverage"], "answer": 1, "why": "Crash-buying is most flattered by missing dead coins."},
 {"q": "Your manual test has only 12 trades in the final period. What's the honest verdict?", "options": ["PASS", "FAIL", "Not enough trades to judge", "Increase leverage"], "answer": 2, "why": "Too few trades can't support a conclusion either way."}
]
}
]}
