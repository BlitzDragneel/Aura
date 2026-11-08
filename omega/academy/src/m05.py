MODULE = {
"id": "m05", "title": "Risk management first", "free": False,
"summary": "Survival maths, position sizing, R-multiples and expectancy, stop placement, drawdowns and losing streaks, the measured liquidation tables for 20× and 40×, and daily limits with OMEGA's Risk Guard.",
"lessons": [
{
"id": "m05-l01", "title": "Why risk comes first: the maths of survival",
"body_md": r"""
# Why risk comes first

You can have a real edge and still lose everything if your size is wrong. You can have no edge and survive a long time if your size is small. Risk management decides whether you are still trading next year.

## Your first job is to stay in the game

Think of trading as a long series of bets. Even a good strategy has losing streaks. If one streak can wipe you out, it eventually will — because over enough trades, the bad streak always comes.

### The ruin example

Two traders use the *same* strategy: 50% win rate, wins pay +1.2R, losses −1R (a small positive edge of +0.1R a trade).

```
Trader A risks 1% a trade.
Trader B risks 20% a trade.

A run of 8 losses in a row:
  A: 0.99^8 = 0.923 → account down 7.7%
  B: 0.80^8 = 0.168 → account down 83.2%
```

Trader B needs about +495% to get back to even. Trader A shrugs and continues. Same strategy, same luck, different survival.

## Bet size and long-run growth

There is a counter-intuitive fact about compounding: **beyond a certain point, risking more makes you poorer, even with a positive edge**, because losses hurt more than equal gains help.

```
+50% then −50%: 100 → 150 → 75   (down 25%)
+10% then −10%: 100 → 110 → 99   (down 1%)
```

The bigger the swings, the more this "volatility drag" eats your growth. Small, steady risk lets the edge — if you have one — compound.

## What OMEGA's Monte Carlo showed

OMEGA simulated **100,000 accounts** using real weekly history:

- **CREED at 1% risk a trade lost half the account in 76% of the simulated accounts within a year.** (CREED measured about −0.10R to −0.12R a trade after costs, so this is what a small negative edge does at 1% risk.)
- **No strategy reached 1,000,000 from 100 in 5 years** — a direct answer to "can I turn 100 into a million?"
- **The panic bounce H1's 2022–26 account path was slightly worse than just holding BTC.**

And the H1 test as a real-sized account (E26: 100 USDT, 5–10 USDT per trade, −10% stop) had **drawdowns of 56% and 59%**, was profitable in only 4 of 6 years, and made most of its money in 2021.

These are the *better* ideas. Risk control matters even more for untested ones.

## The three numbers that decide survival

1. **Risk per trade** — how much of the account you lose if the stop is hit. Common professional range: 0.25%–1%. OMEGA's Risk Guard default: **0.5%**.
2. **Total open risk** — how much you'd lose if every open trade stopped out at once. Risk Guard: **2 open trades at most** (so about 1% total).
3. **Loss limits** — when to stop for the day, week, or for a review. Risk Guard: **−2% a day, −5% a week, review at −20%**.

## Why beginners resist this

"0.5% of 100 USDT is only 50 cents. What's the point?"

The point is that **you are not yet trading for income; you are buying information**. Your first hundred trades tell you whether you can follow a plan and whether your method has any edge. Losing small while you learn is the cheapest tuition there is. Once you have a tested method and a record, you can think about account size — not leverage.

## A simple rule set to start with

```
Risk per trade:   0.5% of account (max 1%)
Max open trades:  2
Daily stop:       −2%  → no new trades today
Weekly stop:      −5%  → no new trades until next week
Review trigger:   −20% from peak → stop, review everything, paper trade only
Leverage:         1× (perps) or the smallest lot that fits the risk (CFDs)
```

You'll build these into your own plan in Module 10.

## Exercise

1. Open the **Risk Guard** page in OMEGA and read its rules and explanations.
2. Using your real (or planned) account size, write down in currency: 0.5% per trade, the daily stop (2%), the weekly stop (5%) and the review level (20%).
3. Calculate what 10 losses in a row would do to your account at 0.5%, 2% and 10% risk. (0.995^10 ≈ −4.9%; 0.98^10 ≈ −18.3%; 0.90^10 ≈ −65.1%.)
""",
"key_points": [
 "Even a winning strategy fails if one losing streak can wipe you out; size decides survival.",
 "Big swings create volatility drag: +50% then −50% leaves you down 25%.",
 "OMEGA's Monte Carlo: CREED at 1% risk lost half the account in 76% of 100,000 simulated accounts within a year.",
 "No strategy turned 100 into 1,000,000 in 5 years; H1 as a 100 USDT account had 56–59% drawdowns.",
 "Start with 0.5% risk a trade, 2 open trades, −2% daily and −5% weekly stops, review at −20%."
],
"quiz": [
 {"q": "Risking 20% a trade, what does a run of 8 losses do (approximately)?", "options": ["−20%", "−50%", "−83%", "−8%"], "answer": 2, "why": "0.8^8 ≈ 0.168, so the account falls about 83%."},
 {"q": "What does +50% followed by −50% do to 100?", "options": ["Back to 100", "75", "125", "50"], "answer": 1, "why": "100 → 150 → 75: losses on a larger base hurt more."},
 {"q": "In OMEGA's Monte Carlo, CREED at 1% risk lost half the account within a year in what share of accounts?", "options": ["7.6%", "25%", "50%", "76%"], "answer": 3, "why": "76% of 100,000 simulated accounts."},
 {"q": "What are the Risk Guard's default daily and weekly stops?", "options": ["−5% and −20%", "−2% and −5%", "−10% and −50%", "None"], "answer": 1, "why": "−2% a day stops trading; −5% a week stops trading; review at −20%."}
]
},
{
"id": "m05-l02", "title": "Position sizing step by step",
"body_md": r"""
# Position sizing step by step

Position sizing turns "I'll risk 0.5%" into an exact order size. It is the single most important calculation in trading, and it takes 30 seconds.

## The formula

```
Risk amount   = account × risk %
Stop distance = |entry − stop|   (in price, or as a %)
Position size = risk amount / stop distance
```

The stop comes **first** — from the chart (where your idea is wrong) and volatility (beyond noise). Then the size follows. Never choose the size first and squeeze the stop to fit.

## Crypto perp example (Binance)

Account 100 USDT, risk 0.5% → **0.50 USDT**. ETH at 3,000, stop at 2,940 (−2%).

```
Stop distance = 60 / 3,000 = 2%
Notional = 0.50 / 0.02 = 25 USDT
Quantity = 25 / 3,000 = 0.00833 ETH
```

Check the exchange's minimum order and step size; if 0.00833 isn't allowed, **round down** to the nearest allowed size (or skip if the minimum is larger than your risk allows).

Margin needed at 1×: 25 USDT. At 2×: 12.5 USDT. Leverage changes margin, **not** the 0.50 USDT risk.

Add costs: round trip ~0.1–0.16% of 25 USDT ≈ 0.03–0.04 USDT. Your real loss at the stop is about 0.54 USDT. Some traders include costs in the risk amount; that's more accurate.

## Spot example

Account 100 USDT. Buy SOL at 150, stop 141 (−6%), risk 0.5% = 0.50.

```
Position = 0.50 / 0.06 = 8.33 USDT of SOL
```

Wider stop, smaller position. That is correct.

## Gold example (Exness)

Account 1,000 USD, risk 0.5% → **5 USD**. Entry 2,650, stop 2,642 (8 dollars). 0.01 lot = 1 oz (check your spec).

```
Risk per 0.01 lot = 8 × 1 = 8 USD
Allowed lots = 5 / 8 × 0.01 = 0.00625 → below minimum 0.01 → skip, or accept 0.8% knowingly
```

At 2,000 USD the same trade fits: 10 / 8 × 0.01 = 0.0125 → **0.01 lot**.

## Forex example

Account 1,000 USD, risk 1% → 10 USD. GBPUSD stop 25 pips. 1 pip per 0.01 lot = 0.10 USD.

```
Lots = 10 / (25 × 0.10) × 0.01 = 0.04 lot
```

## Fixed-fractional sizing and compounding

Risking a fixed **percentage** of the current balance means size grows after wins and shrinks after losses. This is "fixed-fractional" sizing, and it's what the app's Growth page projects.

```
Start 1,000, risk 1%:
After a loss: 990 → next risk 9.90
After a win of +2R: 1,000 + 20 = 1,020 → next risk 10.20
```

It automatically slows you down in drawdowns — a built-in brake.

## Sizing mistakes to avoid

| Mistake | Why it's dangerous |
|---|---|
| Sizing by "how much margin I have" | You end up with a huge notional and an unknown risk |
| Moving the stop closer to fit a bigger size | The stop is now inside normal noise |
| Same lot size on every market | Gold, EURUSD and a small coin have very different volatility |
| Rounding up | Small overshoots add up across many trades |
| Forgetting correlated positions | Long BTC, ETH and SOL at once is close to one big trade |

## A sizing table to keep by your screen

```
Account: ______   Risk %: ____   Risk amount: ______
Market | Entry | Stop | Stop dist | Size = risk / dist | Rounded down | Margin at 1×
```

## Exercise

1. Use the **Futures** page (paper) to size three trades at 0.5% of a 100 USDT account: BTC with a 1.5% stop, a mid-cap coin with a 4% stop, and a small coin with an 8% stop. Record notional for each (answers: 33.3, 12.5, 6.25 USDT).
2. Size one gold trade and one forex trade for your account. If the minimum lot breaks your rule, write "skip".
3. Log one of these as a paper trade in the **Journal** with the planned risk amount.
""",
"key_points": [
 "Position size = risk amount ÷ stop distance; choose the stop first, then the size.",
 "Leverage changes the margin required, not the dollar risk set by size and stop.",
 "Always round down and check the minimum order; if the minimum breaks your rule, skip.",
 "Fixed-fractional sizing grows after wins and shrinks in drawdowns — a built-in brake.",
 "Correlated positions (BTC, ETH, SOL longs) behave like one bigger trade."
],
"quiz": [
 {"q": "Account 200 USDT, risk 0.5%, stop 4%. What notional?", "options": ["8 USDT", "25 USDT", "50 USDT", "1 USDT"], "answer": 1, "why": "Risk = 1 USDT; 1 / 0.04 = 25 USDT."},
 {"q": "Which comes first in sizing?", "options": ["The leverage", "The size", "The stop, from the chart and volatility", "The take-profit"], "answer": 2, "why": "The stop defines where you're wrong; size follows from it."},
 {"q": "Account 1,000, risk 1%, EURUSD stop 20 pips (0.10 USD per pip per 0.01 lot). How many lots?", "options": ["0.01", "0.05", "0.10", "0.50"], "answer": 1, "why": "10 / (20 × 0.10) × 0.01 = 0.05 lot."},
 {"q": "Why is being long BTC, ETH and SOL at the same time risky?", "options": ["Exchanges forbid it", "They're highly correlated, so it acts like one larger position", "Fees triple", "It isn't risky"], "answer": 1, "why": "Correlated positions tend to win and lose together, multiplying your real risk."}
]
},
{
"id": "m05-l03", "title": "R-multiples, expectancy and win rate",
"body_md": r"""
# R-multiples, expectancy and win rate

Talking in dollars makes trades hard to compare. Talking in **R** makes everything clear.

## What R is

**1R = the amount you risk on a trade** (entry to stop, times size). Every result is measured in multiples of it.

```
Risk 5 USD. Trade closes +12 USD → +2.4R
Risk 5 USD. Stopped out −5 USD   → −1R
Risk 5 USD. Slipped stop −6.5    → −1.3R
```

R lets you compare a gold trade with a crypto trade, or a 100 USDT account with a 10,000 one.

## Expectancy

**Expectancy** is the average R per trade:

```
Expectancy = (win rate × average win R) − (loss rate × average loss R)
```

### Worked examples

| Win rate | Avg win | Avg loss | Expectancy |
|---|---|---|---|
| 40% | +2.0R | −1R | 0.4×2 − 0.6×1 = **+0.20R** |
| 60% | +0.8R | −1R | 0.6×0.8 − 0.4×1 = **+0.08R** |
| 50% | +1.0R | −1R | **0R** (then costs make it negative) |
| 33% | +2.0R | −1R | 0.33×2 − 0.67×1 = **−0.01R** |

A strategy with 40% winners can beat one with 60% winners. **Win rate alone is meaningless.**

## Break-even win rate

For a given reward-to-risk (R:R), the win rate you need just to break even (before costs) is:

```
Break-even win rate = 1 / (1 + R:R)
```

| R:R | Break-even win rate |
|---|---|
| 1:1 | 50% |
| 1.5:1 | 40% |
| 2:1 | 33.3% |
| 3:1 | 25% |

Costs push these up a little. The OMEGA Research Lab's test rule (stop 1 ATR, target 1.5 ATR) needs a bit more than 40% winners after costs.

## CREED in R

CREED is the strategy on the app's CREED desk. OMEGA measured it on about 11,000 setups:

- After a setup, price reached **+1R before the stop 49% of the time** — versus **50%** for a fair coin.
- After costs: **−0.118R, −0.100R and −0.118R a trade** on three different coin sets.

So CREED's setups had essentially no directional information, and costs turned that into a small loss. At 1% risk, −0.11R per trade is about −0.11% per trade; over 200 trades that is about −20% before any bad luck. This is why the Monte Carlo found it lost half the account in most simulated years.

## Your real expectancy: the Growth page

The OMEGA **Growth** page computes your **real expectancy** from your logged trades: *"the average amount you win or lose per trade, measured from your own logged history. This is the single most important number in trading."* It needs at least 5 trades to start; it becomes meaningful only after many more (dozens at least, ideally 100+).

## How many trades until you know?

Expectancy from a small sample is very noisy. A rough guide for how uncertain your average R is:

```
Standard error ≈ (standard deviation of R) / √(number of trades)
If your trades' R has a standard deviation of 1.3:
  20 trades:  1.3 / 4.5  ≈ ±0.29R
  100 trades: 1.3 / 10   ≈ ±0.13R
  400 trades: 1.3 / 20   ≈ ±0.065R
```

After 20 trades, an average of +0.2R could easily be −0.1R in reality. Don't draw conclusions — or raise size — from a hot streak.

## Recording R in your journal

For every trade, record:

- Planned entry, stop, target and **planned R:R**
- **Actual R** at exit (including slippage and fees)
- Whether you followed the plan

Then compute expectancy weekly. Separate trades where you followed the plan from those where you didn't — you will often find the rule-breaking trades are where the losses are.

## Exercise

1. Open the **Growth** page. If you have fewer than 5 logged trades, log five paper trades with planned risk and actual R.
2. Compute expectancy by hand for these 10 trades: +2, −1, −1, +1.5, −1, −1, +3, −1, −0.5, −1. (Sum = 0; expectancy 0R. Win rate 30% with big winners — and still nothing after costs.)
3. Calculate the break-even win rate for a 2.5:1 R:R. (Answer: 1 / 3.5 ≈ 28.6%.)
""",
"key_points": [
 "1R is the amount risked; measuring results in R makes trades comparable.",
 "Expectancy = win rate × average win − loss rate × average loss; win rate alone is meaningless.",
 "Break-even win rate = 1 / (1 + R:R), before costs.",
 "CREED reached +1R before its stop 49% of the time (vs 50% chance) and lost −0.10R to −0.12R after costs.",
 "Small samples are noisy; after 20 trades your expectancy could be off by about ±0.3R."
],
"quiz": [
 {"q": "Win rate 40%, average win +2R, average loss −1R. Expectancy?", "options": ["+0.4R", "+0.2R", "−0.2R", "0R"], "answer": 1, "why": "0.4 × 2 − 0.6 × 1 = 0.8 − 0.6 = +0.2R."},
 {"q": "What is the break-even win rate for a 3:1 R:R before costs?", "options": ["33%", "25%", "50%", "75%"], "answer": 1, "why": "1 / (1 + 3) = 25%."},
 {"q": "How often did CREED setups reach +1R before the stop?", "options": ["70%", "49%, versus 50% for a coin flip", "30%", "90%"], "answer": 1, "why": "49% versus 50%: essentially no directional information."},
 {"q": "After 20 trades your average is +0.25R. What's the honest conclusion?", "options": ["Proven edge; double the size", "Too few trades — the true expectancy could easily be zero or negative", "The strategy is broken", "Switch to 20×"], "answer": 1, "why": "The standard error after 20 trades is large; keep collecting data at small size."}
]
},
{
"id": "m05-l04", "title": "Stop placement: structure, volatility and liquidation",
"body_md": r"""
# Stop placement

A stop-loss answers one question: **"At what price is my trade idea clearly wrong?"** Put it there — plus a sensible buffer — and let the position size follow.

## Three ways to place a stop

### 1. Structure stops
Beyond the swing low (for a long) or swing high (for a short) that must hold for your idea to be right.

```
Long from 1.112; last higher low 1.095; buffer 0.004
Stop = 1.091   (distance 0.021 = 1.9%)
```

### 2. Volatility stops
A multiple of ATR from entry, so normal noise doesn't hit you.

```
Gold 1h ATR = 5.0; stop = 1.5 × ATR = 7.5 below entry
```

### 3. Time stops
Exit after a fixed time if nothing has happened. The two setups that passed OMEGA's tests use **time exits**: the climax reversal holds 12 hours; the panic bounce H1 exits 24 hours after the fill.

Many traders combine structure and volatility: stop beyond the swing, and at least ~1 ATR away.

## Common stop mistakes

- **Too tight** (inside normal noise): you're stopped out by random wiggles, then watch price go your way.
- **On the obvious line**: where everybody's stop sits, and where sweeps happen (Module 3).
- **Moved further away** when price approaches it: turns a planned −1R into −3R.
- **No stop at all** "because it will come back": the path to a blown account.

## A surprising finding: stops hurt the passed setups

OMEGA's **E80 exit lab** tried 480 exit variants on the two passed rules — take-profits, stops and trailing stops. For the panic bounce H1:

> *"Every take-profit, stop or trailing stop lowered t; stops hurt most (the edge lives in the deep rebounds)."*

The best exit was the original: sell 24 hours after the fill, no stop, no target.

Does this mean "don't use stops"? **No.** It means something more subtle:

1. For a setup that buys panics, a tight stop gets triggered exactly at the worst moment — before the rebound.
2. Without a stop, single trades **lost 77–93%**. The edge only works as **many tiny positions**, where one −90% trade costs a small slice of the account.
3. So the bots use a **5%-of-equity position** (or a fixed small seat) with a **wide "disaster stop"** (the bots' default is 50%, described as *"a disaster stop, not part of the tested rules"*).

In other words, for these setups the risk is controlled by **position size**, not by a tight stop. Risk per trade = position × worst-case loss.

```
Account 100 USDT, position 5 USDT, disaster stop 50%:
Worst planned loss = 2.5 USDT = 2.5% of the account
(Real risk can be larger if price gaps through the stop.)
```

## The liquidation rule

On a leveraged position, your stop must trigger **before** liquidation. OMEGA's protocol rule:

```
Stop distance < 1 / leverage − 0.5%
```

| Leverage | Max stop distance |
|---|---|
| 2× | < 49.5% |
| 5× | < 19.5% |
| 10× | < 9.5% |
| 20× | < 4.5% |
| 40× | < 2.0% |

The bots add an extra 2% buffer live. A 50% disaster stop therefore only works at **1×** — one reason the bots cap passed rules at 1×.

## Stops are not guarantees

A stop-market order becomes a market order when triggered. In a crash or a weekend gap, it fills at the next available price. OMEGA recorded a worst intrabar move of **−83%** (an October 2025 wick). Plan for slippage: size so that even a stop that slips badly doesn't break your daily limit.

## Choosing mark price or last price (Binance)

Stops triggered by **mark price** ignore brief spikes on one exchange; stops by **last price** react to every trade. Mark price reduces "wick-outs" but can trigger a little later in real moves.

## Exercise

1. On a 1h chart in **Analysis**, plan a long: mark the swing low, add a buffer, and also compute 1.5 × ATR. Which stop is wider? Use the wider one.
2. Size the trade at 0.5% risk with that stop.
3. On the **Futures** page, check that your stop is inside the liquidation distance at 1×, 5× and 20×. At which leverage would it fail?
""",
"key_points": [
 "Put the stop where the idea is clearly wrong, plus a buffer; then size the position.",
 "Combine structure (beyond the swing) and volatility (at least ~1 ATR); time stops are also valid.",
 "In the E80 exit lab, stops reduced the panic bounce's edge; its risk is controlled by small position size.",
 "A stop must sit inside the liquidation distance: stop < 1/leverage − 0.5%.",
 "Stops can slip in gaps and wicks (worst intrabar move seen: −83%); size for that."
],
"quiz": [
 {"q": "At 10× leverage, what is the maximum stop distance under the protocol rule?", "options": ["10%", "9.5%", "19.5%", "0.5%"], "answer": 1, "why": "1/10 − 0.5% = 9.5%."},
 {"q": "What did the E80 exit lab find about stops on the panic bounce H1?", "options": ["Tight stops doubled the edge", "Every stop lowered t; stops hurt most because the edge lives in deep rebounds", "Stops made no difference", "Trailing stops were best"], "answer": 1, "why": "The original exit (24 h, no stop, no target) was best."},
 {"q": "If a setup has no tight stop, how is its risk controlled?", "options": ["By hoping", "By very small position size, plus a wide disaster stop", "By high leverage", "By adding to losers"], "answer": 1, "why": "Small positions mean even a −90% trade is a small slice of the account."},
 {"q": "Why is a stop-market order not a guarantee?", "options": ["Exchanges ignore it", "Once triggered it fills at the next available price, which can be far away in a gap", "It expires every hour", "It only works on spot"], "answer": 1, "why": "Gaps and wicks can fill it well past the stop price."}
]
},
{
"id": "m05-l05", "title": "Drawdowns and losing streaks: what to expect",
"body_md": r"""
# Drawdowns and losing streaks

A **drawdown** is the fall from your account's highest point to a later low. Every strategy has them. Knowing how big and how long they can be — before they happen — is what stops you from abandoning a sound plan or doubling down on a broken one.

## Measuring drawdown

```
Drawdown = (peak − current) / peak
Peak 1,200, now 1,020 → drawdown = 180 / 1,200 = 15%
```

**Maximum drawdown** is the largest such fall over a period.

## The recovery table (again)

| Drawdown | Gain needed to recover |
|---|---|
| 10% | 11.1% |
| 20% | 25% |
| 30% | 42.9% |
| 50% | 100% |
| 60% | 150% |

## Losing streaks are longer than you think

With a 50% win rate, how long is the longest losing run you should expect? A useful rule of thumb: over N trades the longest streak is roughly **log₂(N)**.

| Trades | Typical longest losing streak at 50% wins |
|---|---|
| 50 | about 5–6 |
| 100 | about 6–7 |
| 500 | about 9 |
| 1,000 | about 10 |

With a 40% win rate (common for 2:1 setups), streaks are longer still — 10+ losses in a row within a few hundred trades is normal, not a sign that anything is broken.

### Streaks at different risk levels

```
12 losses in a row:
  0.5% risk: 0.995^12 → −5.8%
  1% risk:   0.99^12  → −11.4%
  2% risk:   0.98^12  → −21.5%
  5% risk:   0.95^12  → −46.0%
```

At 0.5% a normal bad streak is an annoyance. At 5% it is close to the end.

## Real drawdowns from OMEGA's research

| Strategy | Drawdown |
|---|---|
| Panic bounce H1 as a 100 USDT account (E26) | **56% and 59%**; profitable in 4 of 6 years; 2021 made most of it |
| Panic tests E37/E38/E40 at 1×, 5% margin per trade | 10–15% |
| Trend book E50 (2025–26) | −28% (while BTC fell −54%) |
| Funding contrarian E54 (final) | −73% |
| Funding harvest E34 | −64.6% in one month |
| Holding BTC 2025–26 | −54% |

Even the best ideas in the research had long, deep drawdowns. The bots' risk text says it plainly: *"Expect long flat or losing stretches."*

## Drawdown in time, not just depth

Drawdowns also last. A strategy that "makes most of its money in one year" (like H1 in 2021) means **years of flat or losing results** around that year. Can you keep following a plan for 12 months with no new high? Most people can't — which is one reason the plan must be tested and written down before you start.

## Telling a normal drawdown from a broken strategy

Before you start, write down:

1. **The expected maximum drawdown** (from your test, plus a safety margin — real life is usually worse than backtests).
2. **The longest expected losing streak.**
3. **The point at which you stop and review** — OMEGA's Risk Guard uses **−20%**.

Then, during a drawdown, ask:

- Am I following the plan exactly? (If not, the problem is execution.)
- Are results within the range I wrote down? (If yes, it's probably normal variance.)
- Has the market changed in a way the plan didn't cover? (E.g. the edge fading, as the research shows for both passed setups.)

## The two classic drawdown mistakes

1. **Raising size to "win it back".** This is how a 20% drawdown becomes a 60% one.
2. **Abandoning a tested plan after a normal streak** and jumping to a new untested idea — which resets your learning to zero.

The fix for both is the same: decide the rules in advance.

## Exercise

1. Open the **Growth** page and look at your equity curve (if you have logged trades). Compute your current drawdown from the peak.
2. Write in your notes: "My expected max drawdown is ___%. My review point is −20%. I expect losing streaks of up to ___ trades." Use 10 if you don't know.
3. Calculate what your expected worst streak does to your account at your chosen risk %.
""",
"key_points": [
 "Drawdown = (peak − current) / peak; a 30% drawdown needs a 42.9% gain to recover.",
 "Losing streaks of about log₂(N) trades are normal; 10+ in a row happens with 40% win rates.",
 "At 0.5% risk, 12 straight losses cost about 5.8%; at 5% risk, about 46%.",
 "Even the passed setups had deep drawdowns (H1 as a 100 USDT account: 56–59%).",
 "Write expected drawdown, streak length and a review point (−20%) before you start."
],
"quiz": [
 {"q": "Account peaked at 500 and is now 400. What is the drawdown?", "options": ["25%", "20%", "100%", "80%"], "answer": 1, "why": "(500 − 400) / 500 = 20%."},
 {"q": "Roughly how long a losing streak should you expect over 500 trades at a 50% win rate?", "options": ["2", "About 9", "50", "250"], "answer": 1, "why": "log₂(500) ≈ 9."},
 {"q": "What was the drawdown of panic bounce H1 run as a 100 USDT account (E26)?", "options": ["5%", "15%", "56–59%", "90%"], "answer": 2, "why": "E26 found drawdowns of 56% and 59%."},
 {"q": "During a drawdown, which response is most dangerous?", "options": ["Checking you followed the plan", "Raising size to win it back", "Comparing with the expected range", "Pausing at the review point"], "answer": 1, "why": "Increasing size in a drawdown turns moderate losses into ruinous ones."}
]
},
{
"id": "m05-l06", "title": "Leverage honestly: the measured liquidation tables",
"body_md": r"""
# Leverage honestly

Exchanges and brokers advertise 20×, 50×, 100× or more. This lesson shows what OMEGA's research measured when the setups that *passed* fair tests were run at different leverage levels. If leverage destroys the best ideas, imagine what it does to untested ones.

## How the tables were made

The protocol required a leverage table for every passing rule, at **1, 2, 3, 5, 10, 20 and 40×**, with:

- **5% of equity as margin per trade**,
- liquidation judged on each trade's **worst intrabar move (MAE)** — not just the close,
- real costs and funding.

The question: what is the **highest leverage with zero liquidations and a maximum drawdown under 35%**?

## The results

### Panic tests at 5m, 15m and market-wide (E37, E38, E40 final trades)

| Leverage | Result |
|---|---|
| 1× | No liquidations; drawdown 10–15% |
| 2× | Already liquidates |
| 20× | **29–31% of trades hit the liquidation distance; the account goes to about 1 USDT** |
| 40× | **About 60% of trades liquidated** |

Worst intrabar move in the data: **−83%** (October 2025 wick).

### The passed rules in the bots' backtest

| Rule | Liquidations |
|---|---|
| Panic bounce H1 | **37 times at 2×, 107 at 3×**, wiped out at 20× and 40× |
| Climax reversal | Liquidates from 2× |
| Panic bounce H3 | Liquidates from 2× |

**Highest leverage with zero liquidations and drawdown < 35%: 1× for all three.** That is why `approved.json` sets `max_leverage: 1` and the bot guard has a hard cap.

### The slower strategies (E50–E54)

Even "calm" books had bad days at 1×: worst single days of −16.6% (trend book), −16.8% (funding book), and −4.5% for the low-risk ALT/BTC ratio book — **which is exactly 20×'s liquidation line (5% − 0.5%)**. At 40× (2.0%), the research notes, these books *"die on ordinary days"*.

## Why leverage destroys these setups

The setups buy during crashes. By design, they enter when price is falling hard, and the deepest dips come *after* entry. At 1×, a −20% dip before a rebound is painful but survivable. At 20×, a −4.5% dip ends the trade with a total loss of the margin — before the rebound that made the setup worthwhile.

```
Entry 1.00, intrabar low 0.93 (−7%), 24 h later 1.04 (+4%)
1× : survives the dip, exits +4% (minus costs)
5× : liquidation distance 19.5% → survives, +20% on margin
20×: liquidation distance 4.5% → LIQUIDATED at −4.5%, margin gone
```

The trade was a winner. At 20× it was a total loss.

## "But I use a stop"

At 20× your stop must be under 4.5% away. For volatile coins, that is inside normal hourly noise (Module 4). You'll be stopped out constantly, paying costs each time, and your fees are charged on 20× the notional (Module 2). Either way, the edge disappears.

## The core principle

> **Leverage never creates an edge; it scales the edge and the tail.**

If a strategy makes +0.2% a trade at 1×, it makes +4% at 20× *on average* — but the losses, slippage, fees and funding are also 20×, and the tail events that cost −30% at 1× now cost everything. Survival is not an average.

## When is any leverage reasonable?

- **To reduce margin locked**, not to increase size. For example, holding a 25 USDT notional at 2× uses 12.5 USDT margin. The risk (set by size and stop) is unchanged. Isolated margin limits the damage if something goes wrong.
- **Never** to turn a small account into a big position.
- **Never above what a fair test showed survives** — for everything tested here, that was 1×.

## On CFDs

Exness and other brokers may offer very high leverage on forex and gold. The same logic applies: use the leverage setting only to free margin, keep your **position size** set by your risk rule (Module 2, Lesson 6), and never let available leverage tempt you into a bigger lot.

## Exercise

1. Open the **Futures** page and read *"Leverage — what the tests say"*. Compare its statements with the tables above.
2. Using the worked example, compute what happens at 10× (liquidation distance 9.5%): does the trade survive the −7% dip? (Yes — but a −10% dip would liquidate.)
3. Write a personal leverage rule in your notes. Recommended: "1× on perps; margin is never more than what I'd lose anyway."
""",
"key_points": [
 "OMEGA measured leverage on the passed setups using each trade's worst intrabar move, 5% margin per trade.",
 "1× had no liquidations; 2× already liquidated; at 20× 29–31% of trades hit liquidation; at 40× about 60%.",
 "Panic bounce H1 was liquidated 37 times at 2× and 107 at 3×; the highest safe leverage was 1× for all rules.",
 "Setups that buy crashes suffer most: the dip after entry liquidates high leverage before the rebound.",
 "Leverage never creates an edge; it scales the edge and the tail."
],
"quiz": [
 {"q": "At 20×, what share of trades in the E37/E38/E40 tests hit the liquidation distance?", "options": ["About 3%", "29–31%", "About 60%", "None"], "answer": 1, "why": "29–31% at 20×; about 60% at 40×."},
 {"q": "What was the highest leverage with zero liquidations and drawdown under 35% for the passed rules?", "options": ["1×", "2×", "5×", "20×"], "answer": 0, "why": "1× for H1, H3 and the climax; approved.json keeps max_leverage 1."},
 {"q": "A trade dips −7% then closes +4%. What happens at 20× (liquidation ~4.5%)?", "options": ["+80% on margin", "Liquidated; the margin is lost", "Break even", "+4%"], "answer": 1, "why": "The −7% dip passes the 4.5% liquidation distance before the rebound."},
 {"q": "Which statement is the course's core principle about leverage?", "options": ["Leverage creates edges", "Leverage never creates an edge; it scales the edge and the tail", "Higher leverage reduces risk", "Leverage only matters on spot"], "answer": 1, "why": "Leverage multiplies both results and tail losses; it adds no edge."}
]
},
{
"id": "m05-l07", "title": "Daily limits, correlation and the Risk Guard",
"body_md": r"""
# Daily limits and the Risk Guard

Per-trade risk protects you from a single bad trade. **Limits** protect you from a bad day, a bad week and — most importantly — from yourself on a bad day.

## Why limits matter

Losses are not independent in real life. After two or three losses, many traders:

- take lower-quality setups to "get it back",
- raise size,
- ignore their stop "just this once".

A daily limit stops the spiral at a point decided in advance, when you were calm.

## OMEGA's Risk Guard rules

The **Risk Guard** page summarises them in one line:

> **0.5% a trade → 2 open at most → −2% a day stops → −5% a week stops → review at −20%**

| Rule | What it prevents |
|---|---|
| 0.5% a trade | One trade doing real damage |
| 2 open at most | Hidden concentration (total open risk ≈ 1%) |
| −2% a day stops | A bad day becoming a disaster (4 full losses at 0.5%) |
| −5% a week stops | A bad week becoming a bad month |
| Review at −20% | Continuing a broken plan; forces a full review and paper-only trading |

## Worked example: a bad day under the rules

Account 1,000 USD, 0.5% risk = 5 USD a trade, daily stop −2% = −20 USD.

```
09:10 Trade 1: −5   (day −5)
10:05 Trade 2: −5   (day −10)
10:40 Trade 3: +7   (day −3)
11:20 Trade 4: −6.5 (slipped stop; day −9.5)
11:55 Trade 5: −5   (day −14.5)
12:30 Trade 6: −5.5 (day −20)  → DAILY STOP HIT. No more trades today.
```

The worst case for the day is about −2%. Without the rule, trades 7, 8 and 9 — taken angry — are where accounts are usually lost.

## Correlation: the hidden extra risk

"2 open at most" exists partly because crypto coins move together. Being long BTC, ETH and SOL at once is close to one large long. When the market drops, all three stop out together.

Practical rules:

- Count positions in the **same direction on correlated markets** as one combined risk.
- Gold and the US dollar are linked; EURUSD and GBPUSD are often similar.
- A **market-wide panic** (like the H3 trigger, when many coins are in their bottom-10% hour at once) means almost everything is moving together.

## Limits for bots

The OMEGA bots' guard uses hard limits too (in USDT, for a small test account): **hard leverage cap 3× (and each rule's max_leverage, now 1×), at most 10 USDT margin per order, at most 3 open positions or resting entries (counted from the exchange), one position per coin, risk per trade at most 3 USDT, daily loss limit 5 USDT**, and a stop on every position inside the liquidation distance. If a stop can't be placed, the entry is undone. More in Module 9.

## Setting your own limits

Start with the Risk Guard defaults, then adjust *down*, not up:

```
Risk per trade:    0.5%   (0.25% while learning is also fine)
Max open trades:   2 (correlated counts as one)
Daily stop:        −2%  or 3 losses in a row, whichever first
Weekly stop:       −5%
Review:            −20% from peak → paper only until reviewed
Also stop when:    tired, ill, upset, or just after a big win
```

## What to do when a limit is hit

1. **Close the platform.** Not "just watching".
2. **Journal** the day: trades, emotions, rule breaks.
3. **Next session**, start with the review, not a trade.
4. At the **−20% review**: go back to paper, re-read your plan, check whether you followed it, and check whether the method's evidence still holds (both passed setups are fading).

## Exercise

1. Open the **Risk Guard** page and set (or note) its rules for your account size. Write the currency values of each limit.
2. Replay your last five trading days (real or paper): would any day have hit the −2% daily stop? What happened after that point?
3. Add a "stop when" line to your notes listing personal conditions (tired, angry, after a big win...) when you won't trade.
""",
"key_points": [
 "Daily and weekly limits stop a bad day from becoming a disaster, at a point decided while calm.",
 "Risk Guard: 0.5% a trade, 2 open at most, −2% a day, −5% a week, review at −20%.",
 "Correlated positions in the same direction count as one combined risk.",
 "The bots' guard also enforces hard limits: 1× rule leverage, ≤10 USDT margin, ≤3 open, 5 USDT daily loss.",
 "When a limit is hit: close the platform, journal, and start the next session with a review."
],
"quiz": [
 {"q": "With 0.5% risk a trade, about how many full losses hit a −2% daily stop?", "options": ["1", "2", "4", "10"], "answer": 2, "why": "4 × 0.5% = 2%."},
 {"q": "Why does the Risk Guard allow only 2 open trades?", "options": ["Exchanges limit it", "To limit total open risk and hidden concentration from correlated positions", "Because fees double", "It is arbitrary"], "answer": 1, "why": "Two trades at 0.5% keep total open risk near 1%; correlated trades magnify risk."},
 {"q": "What should happen at the −20% review level?", "options": ["Double size to recover", "Stop, review everything and paper trade only", "Switch to higher leverage", "Ignore it"], "answer": 1, "why": "The review point forces a full check of plan, execution and evidence."},
 {"q": "Which is the bots' daily loss limit in the guard config?", "options": ["5 USDT", "50 USDT", "No limit", "50%"], "answer": 0, "why": "The guard's daily loss limit is 5 USDT, with ≤3 USDT risk per trade."}
]
}
]}
