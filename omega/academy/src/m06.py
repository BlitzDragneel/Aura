MODULE = {
"id": "m06", "title": "Setups that have evidence", "free": False,
"summary": "Exactly how the climax reversal and the panic bounce work, what passed and by how much, how their edge is fading, how to approach them small and slowly, and how to use CREED as a discipline framework despite its coin-flip results.",
"lessons": [
{
"id": "m06-l01", "title": "What 'passed' means: grades, evidence and limits",
"body_md": r"""
# What "passed" means

Before studying the two setups that passed OMEGA's tests, you need to understand exactly what "passed" does and does not mean. Otherwise it is easy to hear "grade A" and think "safe" or "profitable". Neither is true.

## The grades

From OMEGA's protocol:

| Grade | Meaning |
|---|---|
| **A** | Passes everything: final period significant after costs, beats the luck check, consistent across years, enough trades |
| **B** | Passes the core tests with fewer trades or one weak year |
| **C** | Passed discovery and validation only — **watch list**, not tradeable |

- **Climax reversal: grade A.**
- **Panic bounce H1/H3: grade B.** The bots' risk text explains: *"Grade B means 'passed a fair test, not yet confirmed'."*

## What a pass tells you

1. On data the rule had never seen, it made more than its costs on average.
2. The result was unlikely to be luck from searching many variants.
3. It wasn't carried by a single month.

## What a pass does NOT tell you

1. **That it will keep working.** Both setups have weakened since they passed (Lesson 4).
2. **That it's smooth.** Single panic trades lost 77–93%. As a 100 USDT account, H1 had drawdowns of 56–59%.
3. **That it works with leverage.** All three rules liquidate from 2×; the highest safe level was 1×.
4. **That it works for you.** Your fills, costs, timing and discipline will differ from a backtest.
5. **That it is better than doing nothing.** The Monte Carlo found H1's 2022–26 account path was slightly worse than simply holding BTC.

## Why these two and nothing else?

Both setups share one idea: **panic selling gets overdone**. When a coin drops violently — often from stop-losses and liquidations firing in a cascade — the selling can overshoot what "willing" sellers wanted, and the price partly rebounds once the forced selling ends. OMEGA's research summary calls this *"the only durable edge found"*.

This is a reasonable mechanism, which matters: an edge with a plausible reason behind it is more believable than a pattern with none. But a mechanism is not a guarantee. As more traders and bots buy crashes, the rebounds get competed away — which is one explanation for the fading.

## The forward record is the real test

The research's own conclusion about both setups in 2025–26 data: *"both still have a positive mean but neither is significant out of sample — the forward-ticket record is needed before trusting them with money."*

A **forward record** means: the rule's signals are published and recorded *as they happen*, with no chance to adjust afterwards, and judged later. OMEGA does this through its signals and the bots in paper and testnet modes. You will learn to read a forward record in Module 9.

## How to approach this module

- Learn the setups **precisely**, so you can recognise them and test them yourself.
- Treat them as **case studies in what an edge looks like** — rare, violent, fat-tailed and fragile.
- If you ever trade them, do it **at 1×, with tiny fixed positions, after paper and testnet**, and expect long losing stretches.

## Exercise

1. Open **OMEGA Signals** and read the explanation of *Signal score* versus *Evidence*. Write down why they are two separate numbers.
2. Open the **Scoreboard** and find the no-skill baseline. Write in one sentence why a strategy must beat that baseline, not just make money.
3. List three things a "grade A" result does *not* promise.
""",
"key_points": [
 "Grade A passes everything; B passes the core tests with weaker support; C is watch list only.",
 "The climax reversal is grade A; the panic bounce H1/H3 is grade B ('passed a fair test, not yet confirmed').",
 "A pass doesn't promise future profit, smoothness, leverage tolerance, or beating buy-and-hold.",
 "Both setups rely on one mechanism: panic selling gets overdone — the only durable edge found.",
 "In 2025–26 neither is significant; a forward record is needed before trusting them with money."
],
"quiz": [
 {"q": "What does grade C mean in OMEGA's protocol?", "options": ["Tradeable with caution", "Passed discovery and validation only — watch list", "Failed everything", "Passed at 20×"], "answer": 1, "why": "Grade C ideas go on the watch list; they are not tradeable."},
 {"q": "Which statement about the passed setups is true?", "options": ["They are smooth and low-risk", "Single panic trades lost 77–93%", "They work best at 10×", "They beat BTC every year"], "answer": 1, "why": "They are fat-tailed: big individual losses, deep drawdowns."},
 {"q": "What mechanism do both passed setups share?", "options": ["Trend continuation", "Overdone panic selling followed by partial rebound", "Funding carry", "News trading"], "answer": 1, "why": "Both buy violent, forced selling; it was the only durable edge found."},
 {"q": "What does the research say is needed before trusting either setup with money?", "options": ["A higher leverage test", "A forward record", "A new indicator", "Nothing; they're proven"], "answer": 1, "why": "Neither is significant in 2025–26; the forward record must show it still works."}
]
},
{
"id": "m06-l02", "title": "The climax reversal, step by step",
"body_md": r"""
# The climax reversal

The climax reversal is the only grade-A rule in OMEGA's research. Here are its exact rules, the reasoning behind each, and the numbers.

## The rules

On **hourly** candles, a coin has a climax when **all three** happen in the same closed hour:

1. **A 3σ drop:** the hour's fall is at least 3 standard deviations of that coin's normal hourly moves.
2. **3× volume:** the hour's volume is at least 3 times its recent normal.
3. **Close in the top 40% of the candle's range:** close location ≥ 0.6 — much of the drop was bought back before the hour closed.

**Entry:** buy at the **next hour's open** (a market order).
**Exit:** sell **12 hours later**. No target, no tight stop in the tested rule.

## Why each condition matters

- **3σ drop:** a genuinely extreme move for *that* coin, not just "red candle". Using σ (standard deviation) adjusts for each coin's normal volatility — a 3% hour is huge for BTC and ordinary for a tiny coin.
- **3× volume:** confirms heavy, probably forced, activity — stops and liquidations.
- **Close near the high:** buyers already absorbed the selling within the hour. It's the "climax" — selling exhausted.

## Worked example: checking a candle

A coin's hourly returns have a standard deviation (σ) of 1.2%. Average hourly volume over the last day: 2.0 million USDT.

The last closed hour: open 10.00, low 9.40, high 10.02, close 9.62. Volume 7.5 million.

```
Return for the hour (close vs previous close, say 10.00): −3.8%
In σ: −3.8 / 1.2 = −3.2σ           ✓ (≥ 3σ drop)
Relative volume: 7.5 / 2.0 = 3.75  ✓ (≥ 3×)
Close location: (9.62 − 9.40) / (10.02 − 9.40) = 0.22 / 0.62 = 0.35  ✗ (needs ≥ 0.6)
```

**Not a climax**: the close was still near the low. Selling had not been absorbed. If instead the close had been 9.80, the close location would be 0.65 and all three conditions would hold.

## The evidence

- **Passed on 324 untouched coins** — coins not used in designing the rule. Grade A.
- **E68 side finding** (all ~880 perps, the researcher's own implementation): 2020–23 **+126 bp a trade** (t 1.65), 2024 **+120 bp** (t 1.41), 2025–26 **+109 bp** (t 0.78).
- **Bots' backtest:** climax **+109 bp a trade (t 0.77) in 2025–26.**
- **E80 exit lab:** a quick take-profit (+2% within 6 hours) looked best in discovery (t 3.46), but then **lost** in 2024 (−10 bp) and 2025–26 (−23 bp), while the original 12-hour exit made +126 and +109 bp. *"A quick TP cut the winners."*

The average trade has stayed positive at about +1.1% after costs — but the t-statistics have fallen below 2, so the result is **no longer statistically significant** out of sample. It's also rare: in the 15-minute test the conditions fired only about 0.3 times a day across all coins.

## Versions that failed

- **Climax on 15-minute candles (E41):** t 1.38 in discovery, barely above luck — failed.
- **Climax on 4-hour candles (E42):** t 0.29 — failed.

The hourly version is the one with evidence. Changing the timeframe produces a different rule that must be tested from scratch.

## Leverage

**Climax liquidates from 2×.** Its highest safe leverage in the bots' backtest was **1×**.

## How to recognise one in OMEGA

- OMEGA's signals and bot strategies implement the rule exactly; signals fire on a **closed** hour.
- You can practise recognition in **Analysis**: find large red hourly candles with long lower wicks on high volume and check the three conditions by hand. Most "big red candles" will fail at least one.

## Exercise

1. In **Analysis**, look through the last week of hourly candles on three coins. Find the biggest down-hour on each.
2. For each, estimate σ (average absolute hourly move × about 1.25 is a rough proxy), the move in σ, the relative volume, and the close location. Did any qualify?
3. If one qualified, note the price at the next open and 12 hours later. Record it in the **Journal** as an observed (not taken) setup.
""",
"key_points": [
 "Climax: hourly drop ≥ 3σ, volume ≥ 3× normal, close in the top 40% of the range; buy next open, hold 12 h.",
 "Each condition matters: extreme for that coin, forced activity, and selling already absorbed.",
 "Grade A on 324 untouched coins; about +109 bp a trade in 2025–26 but t 0.77–0.78, no longer significant.",
 "A quick take-profit looked best in discovery and lost out of sample; the 12 h exit was kept.",
 "15m and 4h versions failed; the climax liquidates from 2×, so 1× only."
],
"quiz": [
 {"q": "Which is NOT one of the climax conditions?", "options": ["Drop of at least 3σ", "Volume at least 3× normal", "Close in the top 40% of the range", "RSI under 30"], "answer": 3, "why": "RSI is not part of the rule; the three conditions are σ drop, volume and close location."},
 {"q": "A candle has low 50, high 54, close 52.6. Does it meet the close-location condition (≥ 0.6)?", "options": ["Yes, 0.65", "No, 0.35", "Yes, 0.9", "No, 0.1"], "answer": 0, "why": "(52.6 − 50) / (54 − 50) = 0.65 ≥ 0.6."},
 {"q": "What happened when a quick +2% take-profit was added (E80)?", "options": ["It improved results in every period", "It looked best in discovery but lost in 2024 and 2025–26", "It was not tested", "It removed all losses"], "answer": 1, "why": "It cut the big winners; the original 12-hour exit stayed best out of sample."},
 {"q": "What is the climax's highest leverage with no liquidations in the bots' backtest?", "options": ["1×", "2×", "5×", "20×"], "answer": 0, "why": "It liquidates from 2×."}
]
},
{
"id": "m06-l03", "title": "The panic bounce (H1 and H3)",
"body_md": r"""
# The panic bounce

The panic bounce is a **limit-order** setup: it places a buy order far below the current price and only fills if the coin crashes into it. It comes in two versions, H1 (single-coin) and H3 (market-wide).

## H1 — single-coin panic

At each hourly close (price C), for each coin:

1. Compute σ, the coin's normal hourly volatility.
2. Place a **limit buy at C × exp(−2σ)** — roughly 2σ below the close.
3. The order is valid for **3 hours**. It fills only if a candle **trades below** the limit price in that window.
4. **Exit 24 hours after the fill.** No target, no tight stop in the tested rule.

### Worked example

```
Coin closes at 4.000. Hourly σ = 1.5% (0.015)
Limit = 4.000 × exp(−0.030) = 4.000 × 0.9704 = 3.882
Next 3 hours: lows 3.95, 3.90, 3.86  → third candle trades below 3.882 → filled at 3.882
Exit: 24 hours after the fill, at market
```

Because it's a resting limit, you pay the **maker** fee (0.02%) on entry — but only fills that genuinely trade *through* the price were counted in the tests.

## H3 — market-wide panic

H3 triggers when the **whole market** panics: the coin is in its own extreme bottom move (q5) **and at least 20% of all coins are in their bottom-10% hour at the same time**. It enters as a **taker** (market order).

## The evidence

| Test | H1 | H3 |
|---|---|---|
| E22 | **+0.36% a trade, t 4.34** | +0.22%, t 3.63 |
| E25 survivorship test (883 coins incl. **143 delisted**) | **+0.32%, t 4.54** | +0.30%, t 4.08 |

E25 matters: many tests accidentally use only coins that still exist today (survivorship bias), which flatters crash-buying strategies because the coins that crashed to zero are missing. E25 put the delisted coins back in, and the edge held. Its data check against the reference set was exact.

## The caveats — read these twice

1. **It lives on the big rebounds.** Without the best 5% of trades, each version **loses about 0.7% a trade**.
2. **Single trades lost 77–93%.** Some crashes don't bounce.
3. **As a real 100 USDT account (E26:** 5–10 USDT per trade, −10% stop): **drawdowns of 56% and 59%**, profitable in 4 of 6 years, with **2021 making most of the money**.
4. **It's fading** (next lesson): H1 roughly +127 bp in 2020–23 → +33 bp in 2024 → +19 bp in 2025–26 in the bots' backtest; H3 just +6 bp (t 0.20) in 2025–26.
5. **Leverage:** H1 liquidated 37 times at 2× and 107 at 3×; wiped out at 20× and 40×.
6. **Exits:** every stop, take-profit or trailing stop tested in E80 made it worse. Risk must be controlled by position size.

## Why the limit order matters

The limit captures the deepest part of the panic — the forced selling — at a price no human would want to pay at that moment. It also means:

- Most orders **never fill**. You need many coins and patience.
- The ones that fill are, by definition, during a crash. It feels terrible every time.
- When it fills, the next few hours can go much lower.

## Shorter timeframes: interesting, not tradeable

The November research looked for the panic bounce on 5-minute and 15-minute candles (E37, E38) and as a market-wide 15-minute breadth version (E40). It **does show up**, passed the luck check in 2022–23, was positive in every calendar year 2022–2026 and traded about 5 times a day. But its 2025–26 edge (+3 to +32 bp) was too small to be significant, and **without the best 5% of trades it lost**. These are **watch-list ideas, not tradable rules**. At 4 hours (E39), the panic trigger did no better than buying limit dips at random times.

## Exercise

1. Pick a coin in **Analysis**. Estimate its hourly σ. Compute today's H1 limit price from the last close using C × exp(−2σ) (for small σ, roughly C × (1 − 2σ)).
2. Check over the next 3 hours whether a candle traded below it. Repeat on 5 coins for a few days and count how rarely it fills.
3. If OMEGA Signals or the paper bots show a panic-bounce fill, follow it for 24 hours and log the result as observed.
""",
"key_points": [
 "H1: limit buy at C × exp(−2σ), valid 3 hours, fills only if price trades through it; exit 24 h after the fill.",
 "H3: market-wide panic (coin in bottom move and ≥20% of coins in their bottom-10% hour), taker entry.",
 "E22/E25: H1 about +0.32–0.36% a trade (t 4.3–4.5), including 143 delisted coins.",
 "Caveats: without the best 5% of trades it loses ~0.7% a trade; single trades lost 77–93%; account drawdowns 56–59%.",
 "5m/15m versions are watch-list only; at 4h it was no better than random limit dips."
],
"quiz": [
 {"q": "Close 10.00, hourly σ 1%. Where is the H1 limit (approximately)?", "options": ["9.80", "9.90", "9.98", "9.50"], "answer": 0, "why": "10 × exp(−0.02) ≈ 9.802."},
 {"q": "Why did E25 include 143 delisted coins?", "options": ["To increase fees", "To remove survivorship bias, which flatters crash-buying", "Because they were cheaper", "By mistake"], "answer": 1, "why": "Leaving out coins that died would hide the worst crash trades."},
 {"q": "What happens to H1 without its best 5% of trades?", "options": ["It doubles", "It loses about 0.7% a trade", "Nothing changes", "It becomes risk-free"], "answer": 1, "why": "The edge lives in the big rebounds."},
 {"q": "What was the verdict on the 5m/15m panic versions (E37, E38, E40)?", "options": ["Approved for trading", "Watch-list ideas, not tradable rules", "Best edge found", "Never tested"], "answer": 1, "why": "Their 2025–26 edge was too small to be significant and lost without the best 5%."}
]
},
{
"id": "m06-l04", "title": "How the edges are fading — and what that teaches",
"body_md": r"""
# How the edges are fading

An honest course has to show you this: the two setups that passed are getting weaker. Here are the numbers, possible reasons, and what it means for how you trade any edge.

## The numbers, period by period

| Rule | 2020–23 (discovery) | 2024 (validation) | 2025–26 (final) |
|---|---|---|---|
| Panic bounce H1 (bots' backtest) | +127 bp, t 3.38 | +33 bp, t 0.53 | +19 bp, t 0.63 |
| Panic bounce H1 (E80, 923 perps) | +109 bp, t 3.02 | +31 bp, t 0.50 | +21 bp, t 0.69 (n 39,383) |
| Panic bounce H3 | — | — | +6 bp, t 0.20 |
| Climax reversal (E68 side finding) | +126 bp, t 1.65 | +120 bp, t 1.41 | +109 bp, t 0.78 |

(bp = basis points; 100 bp = 1%. All after costs.)

The panic bounce H1 has fallen from about 1.1–1.3% a trade to about 0.2%. That is close to the size of a single slippage mistake. The climax has held its average better but on few trades, with t-statistics now below 1.

## Why edges fade

Nobody can be sure, but common reasons are:

1. **Competition.** More traders and bots now buy crashes, so rebounds are bought earlier and smaller.
2. **Market structure changes.** Exchange liquidation engines, insurance funds, market makers and coin listings change over time.
3. **Regime.** 2021 had extreme crashes and rebounds; later years were different. H1 made most of its account profits in 2021.
4. **The original result was partly luck.** Even passing tests, some of the discovery result is usually noise — so the "true" edge was smaller than it first looked.

## The watch list: same idea, new data

Research bot 3 tested new data sources and found two grade-C ideas — both turned out to be **the same crash-rebound effect seen through different data**:

- **E66 perp premium:** buy coins whose perp trades at least 0.3% under the index, hold 12 h. Final +49.2 bp (t 1.47); 2025 +102 bp, 2026 +20 bp.
- **E68-F6:** take H1 only when BTC's implied volatility (DVOL) is in the top 30% of its year. Final +106 bp versus +18 bp base (t 1.32); 2025 +323 bp, 2026 +15 bp.

Both *"lived in 2025 and faded in 2026"*. Watch list only — no approved trading entry.

## What the exit lab added

E80 tried 480 different exits to see if a better exit could rescue the fading edge. Its conclusion: *"keep the original exits; tighter stops or quick take-profits make these rules worse, and no exit design rescues their fading edge."*

## Lessons for every edge you ever use

1. **Edges are not permanent.** Plan for decay from day one.
2. **Track the edge, not just your P&L.** Compare your live average per trade with the tested average.
3. **Define a retirement rule in advance.** For example: "If after 100 forward trades the average is below zero, or below half the tested average, I stop and review."
4. **Don't increase size on old evidence.** A 2021 result says little about 2026.
5. **Don't rescue a fading edge by tuning.** Each tweak adds another hidden test (overfitting). E80 shows that even 480 honest tries didn't help.

## Worked example: is it still working?

Suppose you've paper-traded H1 for 120 forward fills with an average of +0.05% a trade and a standard deviation of 6% per trade.

```
Standard error = 6% / √120 = 6 / 10.95 = 0.55%
t = 0.05 / 0.55 ≈ 0.09
```

That is indistinguishable from zero. It doesn't prove the edge is dead — but it gives no reason to risk more money. Because single trades are so variable, it takes **hundreds** of trades to see a small edge clearly. That's one reason to keep sizes tiny.

## Exercise

1. Write a "retirement rule" for any strategy you use or plan to use: how many forward trades, what minimum average, and what you will do if it fails.
2. Compute t for: 200 trades, average +0.30%, standard deviation 5%. (SE = 5 / 14.1 = 0.35; t ≈ 0.85.)
3. Open the **Scoreboard** and note how many forward records each product has. Is it enough to judge?
""",
"key_points": [
 "Panic bounce H1 fell from about +1.1–1.3% a trade (2020–23) to about +0.2% (2025–26); H3 to +6 bp.",
 "The climax kept a ~+1.1% average but with t below 1 in 2025–26 — not significant.",
 "Watch-list ideas E66 and E68-F6 are the same crash-rebound effect; they lived in 2025 and faded in 2026.",
 "No exit design rescued the fading edges (E80, 480 variants).",
 "Plan for decay: track your forward average against the tested one and set a retirement rule in advance."
],
"quiz": [
 {"q": "What was panic bounce H1's average in 2025–26 in the bots' backtest?", "options": ["+127 bp", "+19 bp (t 0.63)", "−292 bp", "+340 bp"], "answer": 1, "why": "+19 bp a trade, not significant."},
 {"q": "What do E66 and E68-F6 have in common?", "options": ["Both are trend strategies", "Both are the crash-rebound effect seen through new data, faded in 2026", "Both passed with grade A", "Both use RSI"], "answer": 1, "why": "The research notes they look like the same crash-rebound effect."},
 {"q": "120 trades, average +0.05%, standard deviation 6%. Roughly what is t?", "options": ["0.09", "2.0", "5.0", "0.9"], "answer": 0, "why": "SE = 6/√120 ≈ 0.55; t = 0.05/0.55 ≈ 0.09."},
 {"q": "What is the right response to a fading edge?", "options": ["Tune parameters until it works again", "Increase size to make up for it", "Follow a predefined retirement rule based on forward results", "Add leverage"], "answer": 2, "why": "Tuning adds hidden tests; size and leverage add risk. A predefined rule keeps you honest."}
]
},
{
"id": "m06-l05", "title": "Trading them small: from observation to a tiny live test",
"body_md": r"""
# Trading them small

Suppose, after everything you've read, you still want to try the passed setups with real money. This lesson describes a slow, small, honest path. It is not a recommendation to trade them — the evidence in 2025–26 is not significant — but if you do, this is how to limit the damage and learn the most.

## Stage 0 — Observe (2–4 weeks)

- Watch **OMEGA Signals** and the paper bots. Every signal is followed to its outcome and recorded in the Journal.
- Log each setup you see: time, coin, entry, exit, result. Don't trade.
- Goal: understand how rare, how ugly and how variable these trades are.

## Stage 1 — Paper (at least 50 trades)

The OMEGA bots are designed for this: `run_paper` places nothing and writes every signal, order, fill and exit to a log. Compare paper results with the research numbers. Expect noise — 50 trades is not enough to prove anything, but it's enough to see whether your execution matches the rules.

## Stage 2 — Testnet (50+ trades)

Binance's futures testnet places real orders against a demo exchange. The bots' instructions: go live *"only if 50+ testnet trades look like the backtest, and only by you."* Testnet prices differ from the real market, so the bots re-base limit prices; treat testnet as a test of **mechanics** (orders, stops, cancellations), not of profit.

## Stage 3 — Tiny live

If you go live, the research and bots' settings give you the template:

```
Leverage:          1× (approved.json max_leverage = 1)
Margin per trade:  5 USDT (approved.json example), at most 10 USDT
Open positions:    at most 3, one per coin
Risk per trade:    at most 3 USDT (size × disaster stop)
Daily loss limit:  5 USDT
Disaster stop:     wide (bots' default 50%) — not part of the tested rule
API key:           futures only, no withdrawals, restricted to your IP
```

### What that means on a 100 USDT account

```
Position 5 USDT at 1×, disaster stop 50% → worst planned loss 2.5 USDT (2.5% of account)
Typical expected result at +0.2% a trade → +0.01 USDT a trade
Round-trip cost ≈ 0.1–0.2% × 5 = 0.005–0.01 USDT
```

Look at that honestly: the expected profit per trade is about one cent, while a single bad trade can cost 2.50 USDT. **You are not doing this for income; you are buying a forward record.** If that doesn't appeal, the honest choice is to observe only — which is perfectly fine.

## Why small, fixed seats

- The edge lives in rare big rebounds, so you need **many trades** — only possible if each is small.
- Single trades can lose 77–93%; at 5% of the account that is a 4–5% hit, survivable. At 50% of the account it's ruin.
- Fixed seats prevent "this one looks great, let's go bigger" — the instinct that usually picks the worst trade.

## What you must accept

1. **Long losing stretches.** The bots' risk text: *"Expect long flat or losing stretches."*
2. **Trades that feel wrong.** You'll buy during crashes, often at night (crypto is 24/7). That's why automation is natural for this setup.
3. **The edge may be gone.** Your forward record is how you'll find out, at minimal cost.

## Comparing your record with the research

Keep a simple table:

| Metric | Research (2025–26) | My forward record |
|---|---|---|
| Average per trade after costs | H1 ≈ +0.2% | |
| Number of trades | thousands | |
| Worst trade | −77% to −93% possible | |
| Without best 5% of trades | negative | |

After 100+ trades, ask: is my average close to the research, below it, or negative? Apply your retirement rule from the last lesson.

## Exercise

1. Open the **Trading Bots** page and confirm everything there is paper. Start (or simulate starting) a paper bot that follows a tested rule and note where its trades are recorded.
2. Fill in the comparison table above with the research column. Plan when you'll update the right-hand column (e.g. every 25 trades).
3. Write your decision for this course: observe only, paper, or testnet. All three are valid; live is not required to complete the course.
""",
"key_points": [
 "Path: observe → paper (50+) → testnet (50+) → tiny live, only if records match the research.",
 "Template: 1×, 5–10 USDT margin, ≤3 positions, ≤3 USDT risk a trade, 5 USDT daily loss, no-withdrawal API key.",
 "At ~+0.2% a trade on 5 USDT, expected profit is about a cent; you're buying a forward record, not income.",
 "Small fixed seats are essential because single trades can lose 77–93% and the edge needs many trades.",
 "Observing only is a perfectly valid choice."
],
"quiz": [
 {"q": "According to the bots' instructions, when should you consider going live?", "options": ["After the first winning paper trade", "Only if 50+ testnet trades look like the backtest, and only by you", "Immediately at 20×", "Never test first"], "answer": 1, "why": "Live is a manual decision after a matching testnet record."},
 {"q": "What leverage does approved.json allow for the passed rules?", "options": ["1×", "3×", "10×", "40×"], "answer": 0, "why": "max_leverage is 1 — the highest level with no liquidations in the tests."},
 {"q": "Why use small fixed seats for these setups?", "options": ["Exchanges require it", "Single trades can lose 77–93% and the edge needs many trades to show", "It increases the edge", "To pay fewer taxes"], "answer": 1, "why": "Small seats make the fat tails survivable and allow enough trades."},
 {"q": "What is the honest purpose of a tiny live test of these setups?", "options": ["Fast income", "Building a forward record at minimal cost", "Proving the edge is permanent", "Using leverage safely"], "answer": 1, "why": "Expected profit per trade is tiny; the value is the honest forward data."}
]
},
{
"id": "m06-l06", "title": "CREED as a discipline framework",
"body_md": r"""
# CREED as a discipline framework

CREED is the method on OMEGA's CREED desk. It is a structured, top-down approach of the kind taught in many trading courses:

> **4H battlefield → 1H pullback zone → 15M sweep → acceptance**

This lesson explains the method, shows what OMEGA measured, and explains how to use it honestly — as a **discipline framework**, not as an edge.

## The method in plain words

1. **4H battlefield:** on the 4-hour chart, identify the market's structure and the zones that matter.
2. **1H pullback zone:** on the hourly chart, wait for price to pull back into a zone in line with the bigger picture.
3. **15M sweep:** on the 15-minute chart, wait for price to sweep liquidity — poke beyond a nearby high or low to trigger stops.
4. **Acceptance:** wait for price to return and hold back inside the level, then enter with a stop beyond the sweep.

The CREED desk runs this on three independent markets (you choose forex, gold & silver, or crypto), and its auto-monitor checks every slot.

## What OMEGA measured

E29 and E31 tested CREED on about **11,000 setups** across three coin sets:

- After a setup, price reached **+1R before the stop 49% of the time** — against **50%** for a fair coin.
- After costs: **−0.118R, −0.100R and −0.118R a trade** on the three sets.
- Variants — **longs only, BTC context, panic-gated, volatility buffer** — **all failed** on untouched coins.
- The Monte Carlo: at 1% risk, CREED **lost half the account in 76% of simulated accounts within a year**.

The app is open about this. The Futures page states: *"CREED: −0.10R to −0.12R a trade after costs (E29, E31)"*, and the Scoreboard compares CREED's own records against a no-skill baseline.

## So why is CREED in this course?

Because a structured method has real value even without an edge:

1. **It forces patience.** Four conditions must line up; most of the time, there's no trade. That alone cuts overtrading and costs.
2. **It defines risk before entry.** The stop goes beyond the sweep; size follows.
3. **It's checkable.** Every step is a yes/no question you can journal — and see where you broke your own rules.
4. **It teaches chart reading.** Structure, zones, liquidity and acceptance are the vocabulary of Module 3.
5. **It's a fair test bed.** The Journal records CREED live trades, observed signals *and rejected setups*. You can measure your own CREED results against the research.

But: **a checklist that organises your trading is not the same as a checklist that makes money.** The research says CREED's direction is a coin flip. Treat it accordingly.

## How to use CREED honestly

- **As a filter for attention:** "I only look closely at markets where CREED's steps line up."
- **As a discipline score:** in your journal, record whether each trade followed all four steps.
- **At minimum size:** given −0.1R expectancy, risk the smallest amount, or paper only.
- **Combined with tested evidence:** check OMEGA Signals; prefer setups with tested evidence over structure alone.
- **With a stop rule:** if your CREED forward record after 100 trades is near −0.1R like the research, stop.

## Worked example: what −0.11R means

```
Risk per trade: 0.5% of 1,000 USD = 5 USD
Expectancy: −0.11R = −0.55 USD a trade
Over 200 trades: −110 USD ≈ −11% (before luck — which could make it much better or worse)
At 1% risk: about −22%; and the Monte Carlo shows the swings around that are large
```

## Exercise

1. Open the **CREED desk**. Choose a market and press *Run CREED*. Note which of the four steps are met right now.
2. In the **Journal**, filter to *CREED rejected setups* or *CREED signals (observed)*. Pick five and check whether price reached +1R before the stop. Compare with the research's 49%.
3. Write one paragraph: how will you use CREED (or any structured checklist) in your plan — as an edge, a filter, a discipline score, or not at all? Justify it with the numbers.
""",
"key_points": [
 "CREED: 4H battlefield → 1H pullback zone → 15M sweep → acceptance.",
 "On ~11,000 setups it reached +1R before the stop 49% of the time vs 50% by chance; −0.10R to −0.12R after costs.",
 "Longs-only, BTC-context, panic-gated and volatility-buffer variants all failed on untouched coins.",
 "Its value is discipline: patience, predefined risk, checkable steps and a fair test bed — not an edge.",
 "Use it as a filter or discipline score at minimum size, and stop if your forward record matches the research."
],
"quiz": [
 {"q": "What are CREED's four steps?", "options": ["Daily trend, RSI, MACD, volume", "4H battlefield, 1H pullback zone, 15M sweep, acceptance", "News, funding, breakout, target", "Buy, hold, sell, repeat"], "answer": 1, "why": "That is the method as shown on the CREED desk."},
 {"q": "How did CREED perform after costs on three coin sets?", "options": ["+0.5R a trade", "−0.118R, −0.100R and −0.118R a trade", "Break even", "+2R a trade"], "answer": 1, "why": "A small, consistent loss — a coin flip minus costs."},
 {"q": "Which is an honest use of CREED?", "options": ["Trade it at high risk because it's structured", "As a discipline and attention filter at minimum size", "Add 20× to make the small edge bigger", "Skip stops"], "answer": 1, "why": "Its value is process; the evidence shows no directional edge."},
 {"q": "At 0.5% risk on 1,000 USD, what does −0.11R a trade cost over 200 trades (before luck)?", "options": ["About −11 USD", "About −110 USD", "About −1,100 USD", "Nothing"], "answer": 1, "why": "5 USD × −0.11 = −0.55 a trade × 200 = −110 USD."}
]
}
]}
