MODULE = {
"id": "m04", "title": "Technical analysis, honestly", "free": False,
"summary": "Moving averages, RSI, Bollinger Bands, ATR and volume: how they are calculated, what they can and cannot do, and the evidence that most indicator rules don't pay their costs — while volatility is genuinely predictable.",
"lessons": [
{
"id": "m04-l01", "title": "What indicators really are",
"body_md": r"""
# What indicators really are

Every technical indicator is a **formula applied to past prices and volume**. That is all. An indicator cannot know anything the price chart does not already contain. It can only summarise it in a different way.

## Three families

| Family | Examples | What it summarises |
|---|---|---|
| Trend / average | Moving averages (SMA, EMA), MACD | Where price has been on average, and its slope |
| Oscillators | RSI, Stochastic | How far and fast price moved recently, scaled 0–100 |
| Volatility | ATR, Bollinger Bands, standard deviation | How much price is moving, regardless of direction |
| Volume | Relative volume, OBV, VWAP | How much is trading, and at what average price |

## The lag problem

Most indicators are built from averages, so they **lag**: they confirm what has already happened.

```
Prices:    10  11  12  13  14  15  14  13  12
5-period SMA at the last bar = (15+14+13+12+... )
SMA turns down only several bars after the top at 15.
```

A faster indicator lags less but gives more false signals. A slower one gives fewer false signals but reacts later. There is no setting that removes this trade-off — it is built into the maths.

## Why indicators seem to work

Indicators look convincing on charts for three reasons:

1. **Hindsight.** You remember the textbook examples where RSI under 30 marked a bottom, and forget the times price kept falling.
2. **Choice of settings.** With enough settings (RSI 7, 9, 14, 21; thresholds 20, 25, 30...), one combination will look great on any past chart. This is **overfitting** (Module 7).
3. **Trend in the market.** Crypto rose a lot over 2020–2026. Almost any rule that is often long looks good, because it caught the drift. The test is whether it beats a simple shifted or random version with the same long bias. In OMEGA's trend research (E50), it did not.

## What the research says, in one table

| Indicator idea | Where tested | Result |
|---|---|---|
| Daily direction rules of many kinds | E28, 12,480 rules | Never paid costs; 2024 validation failed |
| Neural network on 33 daily measures | E32 | −0.10% a day, within luck's range |
| Trend (TSMOM), Donchian + ATR trail | E50, E51 | No better than luck / random entries |
| ~40 technical features in a machine-learning model | E81, E82 | Good at predicting *big moves*, weak at *direction* |
| Volatility (ATR, range) as a forecast of future volatility | E81 and general | **Predictable** |

That last row is the important one, and we spend a whole lesson on it.

## So why learn indicators at all?

Because they are useful for things other than predicting direction:

- **ATR** tells you how far a market normally moves, so you can set stops beyond normal noise and size positions correctly.
- **Moving averages** give a quick, objective description of trend for context.
- **Relative volume** helps identify extreme, forced events — like the climax reversal.
- **Bands** show when a market is unusually quiet or unusually stretched.

In short: use indicators as **measuring tools**, not as **oracles**.

## A note on the OMEGA Research Lab

The **Research Lab** page tests OMEGA's own conditions — trend, structure, RSI, volatility squeezes, range extremes, momentum, each also with the 4H trend required to agree — on your stored history. Its fixed trade rules are: entry at the hourly close, stop 1 ATR away, target 1.5 ATR, closed after 24 hours if neither is hit. A condition only reaches OMEGA Signals if it **held on a held-out test**. Most don't. You will use the Lab in Module 7.

## Exercise

1. Open **Analysis**, pick a market, and add or view any indicator it shows (e.g. a moving average or RSI).
2. Scroll back over the last month and count *every* time the indicator gave its classic signal (e.g. RSI under 30). For each, note whether price was higher or lower 24 hours later. Don't skip the bad ones.
3. Compare your count with your impression before counting. Most people find the "obvious" signals were far less reliable than they remembered.
""",
"key_points": [
 "Indicators are formulas on past price and volume; they contain no information the chart doesn't.",
 "Averages lag; faster settings lag less but give more false signals — the trade-off can't be removed.",
 "Indicators look good because of hindsight, settings chosen after the fact, and crypto's long-run drift.",
 "OMEGA's research found indicator-based direction rules generally did not pay costs; volatility is predictable.",
 "Use indicators as measuring tools (noise, trend description, extremes), not oracles."
],
"quiz": [
 {"q": "What is a technical indicator?", "options": ["A secret data feed", "A formula applied to past price and volume", "A forecast from the exchange", "News sentiment"], "answer": 1, "why": "Indicators transform past data; they cannot add information that isn't in it."},
 {"q": "Why do faster moving averages give more false signals?", "options": ["They use future data", "They react to more noise", "Exchanges penalise them", "They don't"], "answer": 1, "why": "Shorter averages follow price closely, including random wiggles."},
 {"q": "Why can almost any frequently-long rule look good on 2020–2026 crypto data?", "options": ["Crypto drifted upward over the period", "Fees were zero", "Data was fake", "Indicators were banned"], "answer": 0, "why": "A long bias catches the market's drift; the fair test is to beat a shifted or random rule with the same bias."},
 {"q": "Which of these did the research find genuinely predictable?", "options": ["Direction of the next day", "Volatility (how big moves will be)", "RSI reversals", "Breakout direction"], "answer": 1, "why": "Size of moves is predictable; direction mostly is not."}
]
},
{
"id": "m04-l02", "title": "Moving averages and trend tools",
"body_md": r"""
# Moving averages and trend tools

Moving averages are the most common indicator on any chart. Let's see how they're built, how traders use them, and what the evidence says.

## Simple and exponential averages

**SMA (simple moving average):** the plain average of the last N closes.

```
Closes: 100, 102, 101, 105, 107
5-period SMA = (100 + 102 + 101 + 105 + 107) / 5 = 103.0
```

**EMA (exponential moving average):** weights recent closes more heavily.

```
k = 2 / (N + 1)        for N = 5, k = 0.333
EMA_today = close × k + EMA_yesterday × (1 − k)
If EMA_yesterday = 102.0 and close = 107:
EMA = 107 × 0.333 + 102.0 × 0.667 = 35.6 + 68.0 = 103.7
```

The EMA reacts faster to the latest price, so it lags less — and is noisier.

## Common uses

1. **Trend description:** price above a rising 50-period average = uptrend context; below a falling one = downtrend context.
2. **Crossovers:** a fast average crossing above a slow one ("golden cross") as a buy signal; the opposite ("death cross") as a sell.
3. **Dynamic support/resistance:** buying pullbacks to an average in an uptrend.
4. **Filters:** "only take longs when the 4H trend agrees" — a filter the Research Lab also tests.

## Worked example: the cost of whipsaws

A 20/50 crossover on a ranging hourly chart crosses back and forth 8 times in two weeks. Each trade: 0.05% taker each side plus 0.03% slippage each side = 0.16% round trip. Suppose the average gross result per crossover trade in a range is 0%.

```
8 trades × −0.16% = −1.28% of the position's value in two weeks, from costs alone
```

In trends crossovers catch big moves; in ranges they bleed. The question is whether the trend profits beat the range losses **after costs** — on data you didn't use to choose the settings.

## The evidence: trend following in crypto (E50–E53)

OMEGA's research bot 2 tested this properly on a survivorship-free universe with real funding and liquidity costs:

| Test | Result |
|---|---|
| E50 own-trend (TSMOM), BTC/ETH/top-10, 1d and 4h, volatility-targeted | Best +8.5 bp/day was only the **70th percentile** of the luck check (needed 95th). 10 eligible, none promoted |
| E50 final (BTC, 60-period, long/short, 4h) | +4.2 bp/day, t 0.54, CAGR +6.4%, drawdown −28% — while holding BTC lost −14.6% with a −54% drawdown |
| E51 Donchian breakout + ATR trailing stop, 10 majors | **Random entries with the same stop beat it**; final −42.5 bp a trade |
| E53 ALT/BTC ratio trend | 37th percentile of the luck check; 2024 negative |

The research summary: *"crypto trend following earns the market's drift, but no more than a shifted signal with the same long bias."* In other words, trend rules looked good mainly because crypto went up.

There is a fair point hidden in the numbers: in 2025–26, the trend book lost much less than holding BTC (−28% drawdown versus −54%). That is a **risk view** — a way to be out of the market in some bad stretches — not a proven edge. And OMEGA's E70 test of "hold BTC or cash by regime" also failed its luck check.

## How to use moving averages honestly

- As **context**: "Is the bigger picture up, down or flat?"
- As a **filter** you have tested, not assumed.
- Not as a stand-alone buy/sell trigger, unless your own fair test (Module 7) says otherwise.
- Remember the **lag**: by the time a 50-period average turns, much of the move has happened.

## Exercise

1. In **Analysis**, look at a coin's 1h chart with a short and long moving average (or estimate them visually). Count the crossovers in the last two weeks.
2. For each crossover, note whether a trade from cross to the next opposite cross would have won or lost, then subtract 0.16% per trade for costs.
3. Total it. Then ask: would I have chosen these settings *before* seeing this chart? If not, the result is in-sample only.
""",
"key_points": [
 "SMA is the plain average; EMA weights recent prices more and lags less, with more noise.",
 "Crossovers catch trends but whipsaw in ranges; costs on every whipsaw add up.",
 "E50: crypto trend following earned the drift but no more than a shifted signal with the same long bias.",
 "E51: random entries with the same stop beat Donchian breakouts.",
 "Use moving averages for context and tested filters, not as stand-alone triggers."
],
"quiz": [
 {"q": "Closes 10, 12, 14: what is the 3-period SMA?", "options": ["12", "14", "36", "13"], "answer": 0, "why": "(10 + 12 + 14) / 3 = 12."},
 {"q": "Why does an EMA react faster than an SMA of the same length?", "options": ["It uses future prices", "It weights the most recent prices more heavily", "It ignores volume", "It is calculated less often"], "answer": 1, "why": "The EMA's weighting gives the newest closes more influence."},
 {"q": "In E50, how did the best trend-following result rank against the luck check?", "options": ["Above the 99th percentile", "About the 70th percentile, below the 95th needed", "Exactly the 95th", "It wasn't checked"], "answer": 1, "why": "+8.5 bp/day ranked at the 70th percentile of random grids, so it failed."},
 {"q": "What is the honest takeaway from the trend book losing less than BTC in 2025–26?", "options": ["It's a proven edge", "It's a risk view, not a significant edge", "BTC is broken", "Trend always wins in bear markets"], "answer": 1, "why": "The result was not significant (t 0.54); the research calls it a risk view, not an edge."}
]
},
{
"id": "m04-l03", "title": "RSI, Bollinger Bands and mean reversion",
"body_md": r"""
# RSI, Bollinger Bands and mean reversion

These are the classic "overbought / oversold" tools. They try to measure when price has moved too far, too fast.

## RSI (Relative Strength Index)

RSI compares recent gains with recent losses over N periods (usually 14):

```
RS  = average gain / average loss   (over 14 periods)
RSI = 100 − 100 / (1 + RS)
```

### Worked example

Over 14 hours, the average gain on up hours is 0.6% and the average loss on down hours is 0.3%.

```
RS  = 0.6 / 0.3 = 2.0
RSI = 100 − 100 / (1 + 2) = 100 − 33.3 = 66.7
```

- RSI above 70 is called "overbought", below 30 "oversold".
- But in a strong trend RSI can stay above 70 (or below 30) for a long time while price keeps going.

## Bollinger Bands

A moving average (usually 20 periods) with bands at ±2 standard deviations:

```
Middle = 20-period SMA
Upper  = Middle + 2 × standard deviation of the last 20 closes
Lower  = Middle − 2 × standard deviation
```

Example: SMA 100, standard deviation 1.5 → bands at 97 and 103.

- **Touching the lower band** is often read as "stretched to the downside".
- **Band width** measures volatility. Very narrow bands ("squeeze") mean the market has been unusually quiet — and quiet periods tend to be followed by bigger moves. That is a *volatility* statement, not a direction one.

## Mean reversion: the idea

Mean reversion says that after a big move away from the average, price tends to come back. Sometimes true, sometimes not:

- In ranges, stretched moves often revert.
- In trends, "oversold" keeps getting more oversold.
- In crashes, you are buying while others are forced to sell — sometimes brilliant, sometimes catastrophic.

## What the evidence says

Here OMEGA's research gives a nuanced answer.

**Ordinary oversold signals did not hold up.** Short-timeframe reversal ideas — 5-minute and 15-minute panic limits, 4-hour versions, wick and cascade rules (E37–E46) — did not pass the final test. At 4 hours, the panic trigger did *no better than buying limit dips at random times* (E39 was below the luck check).

**Extreme, panic-driven reversals did pass.** The only durable edge in the whole research was the **panic bounce** and the **climax reversal**: buying *extreme* hourly drops (2σ or 3σ moves, with heavy volume or market-wide panic). Those are much rarer and more violent than "RSI under 30". And even they:

- live on the big rebounds — without the best 5% of trades each loses about 0.7% a trade (E22/E25 caveat),
- had single trades lose 77–93%,
- are fading in 2024–2026.

So the honest summary: **mild "oversold" is not an edge; extreme, forced selling has been — with fat tails and shrinking returns.**

## Using RSI and Bands sensibly

1. Use **band width** or ATR as a volatility gauge for position sizing.
2. Use RSI to **describe** momentum ("strong selling over the last 14 hours"), not as a buy signal.
3. If you want to test a mean-reversion idea, define the extreme precisely (how many standard deviations? which timeframe? which volume?), write it down, and test it on unseen data with costs (Module 7).
4. Never average down into a falling market without a predefined maximum loss.

## Exercise

1. Open the **Research Lab** in OMEGA and look at the conditions it tests (RSI, volatility squeezes, range extremes). Note which, if any, it rates as having held on the held-out test for your markets.
2. On a 1h chart, find the last three times price closed below the lower Bollinger Band (or RSI under 30). Record the result 24 hours later, including the losing cases.
3. Compute RSI by hand for: average gain 0.4%, average loss 0.8%. (Answer: RS 0.5 → RSI = 100 − 100/1.5 = 33.3.)
""",
"key_points": [
 "RSI = 100 − 100/(1 + average gain / average loss); it can stay 'overbought' or 'oversold' for long periods.",
 "Bollinger Bands are a 20-period average ± 2 standard deviations; band width is a volatility measure.",
 "Mild oversold and short-timeframe reversal rules failed OMEGA's tests; at 4h they were no better than random dips.",
 "Only extreme, panic-driven reversals passed — with fat tails (single trades −77% to −93%) and fading returns.",
 "Use RSI and bands to describe and size; test any mean-reversion rule before trusting it."
],
"quiz": [
 {"q": "Average gain 0.9%, average loss 0.3%. What is RSI?", "options": ["25", "50", "75", "90"], "answer": 2, "why": "RS = 3; RSI = 100 − 100/4 = 75."},
 {"q": "Bollinger SMA is 50 and standard deviation is 2. Where is the upper band (2 SD)?", "options": ["52", "54", "100", "48"], "answer": 1, "why": "50 + 2 × 2 = 54."},
 {"q": "What does a Bollinger 'squeeze' most reliably tell you?", "options": ["Price will rise", "Price will fall", "Volatility has been low and a bigger move may follow, direction unknown", "The exchange is closing"], "answer": 2, "why": "Narrow bands are a volatility observation; volatility is predictable, direction isn't."},
 {"q": "What kind of reversal passed OMEGA's fair tests?", "options": ["RSI under 30 on 15m", "Extreme panic-driven drops (climax, panic bounce)", "Any touch of the lower band", "Turn of month"], "answer": 1, "why": "Only extreme, forced selling events showed a durable edge — and it's fading."}
]
},
{
"id": "m04-l04", "title": "ATR and volatility: the part you can predict",
"body_md": r"""
# ATR and volatility: the part you can predict

If there is one indicator every trader should use, it is a volatility measure. Not because it tells you where price is going — it doesn't — but because it tells you **how far price is likely to move**, and that is what risk management needs.

## True range and ATR

The **true range** of a candle is the largest of:

```
high − low
|high − previous close|
|low − previous close|
```

(The last two account for gaps.) **ATR (Average True Range)** is the average of the true range over N candles (often 14).

### Worked example

Five hourly candles on gold have true ranges of 4.0, 5.5, 3.5, 6.0 and 6.0 dollars.

```
5-period ATR = (4.0 + 5.5 + 3.5 + 6.0 + 6.0) / 5 = 5.0
```

Gold typically moves about 5 dollars an hour right now. A stop 2 dollars away is inside ordinary noise; it will be hit by random wiggles.

## Volatility clusters

Volatility has a well-known property: **calm periods tend to follow calm periods, and wild periods follow wild periods**. Today's volatility is a good forecast of tomorrow's. This is one of the most reliable regularities in financial markets.

OMEGA's research confirmed it directly. The machine-learning scouts (E81) were designed to predict a big up move (≥ +1σ in 24 hours) or a big down move. Their AUC (a score where 0.5 = no skill and 1.0 = perfect) was about 0.61 for UpScout. But the researchers noted:

> *"Much of the AUC is a volatility forecast (when a big move comes, either way)."*

The models were good at knowing **when** a big move was likely, and weak at knowing **which way**. That's the theme of this whole module: **size is predictable, direction is not.**

## Using ATR in practice

### 1. Stops beyond noise

```
Stop distance = k × ATR   (k often 1 to 2 on the entry timeframe)
Gold 1h ATR 5.0, k = 1.5 → stop 7.5 dollars from entry
```

The OMEGA Research Lab uses **stop 1 ATR, target 1.5 ATR** as its fixed test rule.

### 2. Volatility-adjusted position size

Because size = risk ÷ stop distance, a wider ATR automatically means a smaller position:

```
Account 1,000 USD, risk 0.5% = 5 USD
Calm day:   stop 1.5 × ATR(4) = 6  → 5 / 6 × 0.01 lot ≈ 0.008 → too small for 0.01 min; skip
Wild day:   stop 1.5 × ATR(10) = 15 → even smaller
```

On a crypto perp:

```
Account 100 USDT, risk 0.5% = 0.50 USDT
Coin price 2.00, 1h ATR 0.03 (1.5%), stop 1.5 ATR = 2.25%
Notional = 0.50 / 0.0225 = 22.2 USDT  (at 1× that's 22.2 USDT margin)
```

### 3. Leverage sanity check

Compare your stop distance to the liquidation distance. If a 1.5-ATR stop is 3% and you use 40× (liquidation ≈ 2%), you will be liquidated before your stop. The protocol rule: *stop distance < 1/leverage − 0.5%*.

### 4. Expected daily range

Daily ATR tells you how far a market typically travels in a day. If gold's daily ATR is 35 dollars and it has already moved 40 today, a further 30-dollar target is asking a lot.

### 5. When to stand aside

Extremely high ATR often comes with wide spreads and slippage. Many traders halve their size or stop trading when ATR is far above normal.

## Volatility versus "risk"

High volatility is not automatically bad. The two setups that passed OMEGA's tests *only* exist in high-volatility moments (3σ or 2σ drops). What matters is that your **size matches** the volatility.

## Exercise

1. In **Analysis**, find the ATR (or estimate it from the last 14 hourly ranges) for one crypto and one forex/gold market.
2. For each, compute a 1.5-ATR stop and the position size that risks 0.5% of your account. Round down. Is the size above the minimum order?
3. Open the **Futures** page and check that your stop is inside the liquidation distance at the leverage you'd use.
""",
"key_points": [
 "True range includes gaps; ATR averages it and shows how far a market typically moves.",
 "Volatility clusters, so it is genuinely forecastable — the scouts' skill was mostly a volatility forecast.",
 "Set stops beyond noise (e.g. 1–2 × ATR) and size = risk ÷ stop distance, so higher ATR means smaller size.",
 "Check the ATR-based stop is inside the liquidation distance (stop < 1/leverage − 0.5%).",
 "Size is predictable, direction is not."
],
"quiz": [
 {"q": "Candle: high 105, low 101, previous close 108. What is the true range?", "options": ["4", "3", "7", "8"], "answer": 2, "why": "Max of 105−101=4, |105−108|=3, |101−108|=7 → 7."},
 {"q": "What were the E81 scouts mostly good at forecasting?", "options": ["Direction of the next move", "When a big move was likely, in either direction", "Funding rates", "News"], "answer": 1, "why": "The research noted much of their AUC was a volatility forecast."},
 {"q": "Account 100 USDT, risk 0.5 USDT, stop 2.5% away. What notional should you use?", "options": ["2 USDT", "20 USDT", "50 USDT", "200 USDT"], "answer": 1, "why": "0.5 / 0.025 = 20 USDT notional."},
 {"q": "If ATR doubles and your risk per trade stays the same, what happens to your position size?", "options": ["Doubles", "Roughly halves", "Stays the same", "Goes to zero"], "answer": 1, "why": "A stop twice as wide needs half the size to keep the same dollar risk."}
]
},
{
"id": "m04-l05", "title": "The evidence: why most rules don't pay their costs",
"body_md": r"""
# The evidence: why most rules don't pay their costs

This lesson collects OMEGA's research results in one place. It is the part of the course most traders never get to see: a large, honest record of what happened when popular ideas were tested properly.

## How large was the search?

| Round | What | Variants counted |
|---|---|---|
| E28 | Daily trading rules in 5 rounds (cross-sectional, composites, executable portfolios, limit entries, BTC/ETH timing) | 12,480 |
| E29, E31 | CREED setups on three coin sets | ~11,000 setups |
| E37–E46 | Short-timeframe reversals and intraday timing | 156 |
| E50–E55 | Trend, momentum, cross-section, positioning | 512 |
| E63–E70 | New data sources (Fear & Greed, implied volatility, premiums, flows) | about 160 |
| E80 | Exit lab on the two passed rules | 480 |
| E81–E82 | Machine-learning scouts | one configuration each |

## The results

| Idea | Best-looking result | What happened on unseen data |
|---|---|---|
| Daily direction (E28) | Some rules looked good 2020–22 | "Daily direction never pays costs"; 2024 validation failed; small-coin and funding-carry effects were 2021–22 phenomena |
| CREED (E29, E31) | — | Coin flip: +1R before stop 49% vs 50% chance; −0.118R, −0.100R, −0.118R a trade |
| Panic limit 5m (E37) | +72.6 bp, t 2.56 | Final +31.8 bp, t 1.05; without best 5% −32.7 bp |
| Turn of month (E45) | +358 bp, t 4.84 | 2024 −36.5 bp; 2025–26 −292 bp, t −2.65 |
| Coinbase premium (E65) | +27.0 bp, t 2.42, all 4 years positive | Final +6.7 bp, t 0.34 |
| Perp premium (E66) | +340 bp, t 6.21 | Final +49.2 bp, t 1.47; 2026 faded |
| Fear & Greed (E63) | +794 bp on 28 trades | Failed the luck check |
| Trend (E50) | +8.5 bp/day | Only 70th percentile of the luck check |
| Funding as a signal (E54) | Passed the luck check | Failed 2024; final −8.6 bp/day, CAGR −43% |
| Neural network (E32) | — | −0.10%/day, within luck's range |
| Funding harvest (E34) | +8.8%/yr 2021–24 | −17%/yr 2025–26; −64.6% in one month |

Notice how many ideas had **impressive discovery numbers** — t-statistics of 4.84 or 6.21 — and then shrank or reversed on new data.

## Why so many rules fail

### 1. Costs are bigger than most edges
A round trip on Binance futures is about 10 bp in fees alone, plus slippage. Many short-term effects are a few basis points. The BTC→alt lead-lag test (E55) found gross profit of about **0 bp** and net results of **−19 to −32 bp a trade**: the effect, if it ever existed, is gone by the next bar's open.

### 2. Searching finds luck
If you test 500 variants, the best one will look good by chance. That's why OMEGA ran a **luck check** on every search: rerun the whole search on shuffled or shifted data and see what the best "fake" result looks like. Several ideas (E39, E51, E53, E55, E63, E64, E69, E70) were beaten by their own random versions.

### 3. Markets change
Effects that existed in 2020–22 — small-coin effects, funding carry, cross-sectional momentum — faded as markets matured and more people traded them.

### 4. Fat tails
Some strategies look smooth until a single event: a short leg on a coin that rose about 50× in a week (E52) or a funding flip (E34).

## What it means for you

- **Assume any rule you hear about is untested** until proven otherwise.
- **Discovery results mean little.** Only out-of-sample results after costs count.
- **A small number of real edges exist**, they are rare and fragile, and they shrink.
- **Your most reliable advantage** is not a signal. It is cost control, small size, discipline and the ability to test.

## Exercise

1. Open the **Scoreboard** page. Read how CREED and OMEGA compare against a no-skill system at the same reward:risk on their own records.
2. Pick one indicator rule you believed in before this course. Write it down exactly (entry, exit, timeframe, market). In Module 7 you will write a test plan for it.
3. From the table above, choose the result that surprised you most and write two sentences on why.
""",
"key_points": [
 "OMEGA counted every attempt: 12,480 daily rules, ~11,000 CREED setups and more than 1,300 variants in November.",
 "Many ideas had impressive discovery t-statistics (4.84, 6.21) and shrank or reversed on unseen data.",
 "Rules fail because costs exceed small edges, searching finds luck, markets change and tails are fat.",
 "Several ideas were beaten by their own random or shifted versions in the luck check.",
 "Your most reliable advantages are cost control, small size, discipline and the ability to test."
],
"quiz": [
 {"q": "What happened to the Coinbase premium idea (E65) in the final period?", "options": ["Stayed at t 2.42", "Fell to +6.7 bp, t 0.34", "Became the best edge", "Was not tested"], "answer": 1, "why": "Discovery looked strong, but the final result was small and insignificant."},
 {"q": "What does a luck check do?", "options": ["Checks your account balance", "Reruns the same search on shuffled or shifted data to see how good a fake best result looks", "Removes losing trades", "Adds leverage"], "answer": 1, "why": "If random data produces results as good as yours, your result may be luck."},
 {"q": "Why did the BTC→alt lead-lag idea (E55) fail?", "options": ["It had huge gross profits wiped out by tax", "Gross profit was about 0 bp and net was −19 to −32 bp a trade", "It only worked on gold", "It was liquidated"], "answer": 1, "why": "The catch-up was gone by the next bar's open; costs made it negative."},
 {"q": "Which is the course's view of your most reliable advantage?", "options": ["A secret indicator", "Cost control, small size, discipline and testing", "High leverage", "Following influencers"], "answer": 1, "why": "Given how rare real edges are, process and risk control are what you can rely on."}
]
},
{
"id": "m04-l06", "title": "The scouts: volatility is predictable, direction mostly isn't",
"body_md": r"""
# The scouts: a case study in prediction

OMEGA built two families of machine-learning "scouts" to see how far modern methods could predict short-term moves. Their results are a perfect lesson in what prediction can and cannot do for a trader.

## What the scouts are

- **E81 hourly scouts:** a LightGBM model (a common, strong machine-learning method) on about 40 technical features, 30 liquid coins, predicting the next **24 hours**. One configuration, trained on 2020–23 and tested on 2024, then trained on 2020–24 and tested on 2025–26.
- **E82 fast scouts:** the same model on **15-minute** candles, predicting the next **4 hours**.

They predict four things: a big up move (UpScout, ≥ +1σ in 24 h), a big down move (DownScout, ≤ −1σ), and turns in trend (up and down).

## Reading AUC

**AUC** measures how well a model ranks cases: 0.5 = coin flip, 1.0 = perfect. 0.6 is modest but real skill. **Brier skill** compares the model's probabilities with a naive forecast: 0 = no better, positive = better.

## The results

| Scout | AUC 2024 | AUC 2025–26 | Top-2% trades after costs 2024 | 2025–26 |
|---|---|---|---|---|
| UpScout (≥ +1σ) | 0.618 | 0.612 | +121 bp, t 2.20 | +118 bp, t 1.29 |
| DownScout (≤ −1σ) | 0.607 | 0.567 | −112 bp, t −1.75 | +28 bp, t 0.43 |
| Trend turn up | 0.816 | 0.797 | +137 bp, t 1.46 | +47 bp, t 0.43 |
| Trend turn down | 0.807 | 0.808 | −93 bp, t −1.74 | −6 bp, t −0.13 |

And for the 15-minute fast scouts in 2025–26: FastUp AUC 0.623 but top-2% calls **−24.7 bp** after costs; turn-down −19.3 bp.

## Why good AUC didn't mean profit

### 1. Much of the skill was volatility
The researchers' note: *much of the AUC is a volatility forecast (when a big move comes, either way)*. If you predict "a big move is coming", you will score well on *both* "big up" and "big down". But a trade needs a direction.

### 2. The turn scouts had a built-in head start
For turns, the label needs the trend to be down (or up) *now*, which the model can see. A high AUC (0.8) partly reflects that, not foresight.

### 3. Costs
The fast scouts saw big moves coming as well as the hourly ones, but **4-hour moves were too small to pay costs**.

### 4. Significance
UpScout was the closest to useful — positive in both years — but **missed t ≥ 2 in 2025–26**, so it is not tradeable under the pass mark.

## What OMEGA did with them

The scouts were not thrown away. They run live as **public, forward-scored predictions** — every 15 minutes for the fast scouts, available on demand at the Live API's `/scouts` endpoint — and they **feed no bot** until their forward record shows skill. That is exactly the right way to treat a promising-but-unproven tool: watch it, score it honestly, risk nothing.

## How you can use this lesson

1. **Use volatility forecasts for risk.** When scouts, ATR or band width say a big move is likely, reduce size and widen stops; don't assume direction.
2. **Be sceptical of "AI predicts the market" claims.** A model with real skill on *something* (volatility) can still have no tradeable skill on *direction after costs*.
3. **Separate "interesting" from "tradeable".** A tool can be informative and still not be a strategy.
4. **Watch forward records.** The fairest test of any predictor is its live, forward-scored record, judged against a no-skill baseline.

## A worked example of the volatility idea

Suppose a scout says a coin has a high chance of a ±1σ move in 24 hours. Its daily σ is about 4%.

```
Normal size: risk 0.5% of 100 USDT = 0.50 USDT, stop 3% → notional 16.7 USDT
Volatility warning: widen stop to 5%, keep risk 0.50 → notional 10 USDT
```

You haven't predicted direction. You've adjusted risk to the forecast you *can* trust.

## Exercise

1. If your OMEGA app shows scout readings (via the Live API), note today's readings for two coins and check them 24 hours later. Did a big move happen? In which direction?
2. Keep a 2-week log: scout said "big move likely" (yes/no), big move happened (yes/no), direction. Compute how often "big move likely" was followed by a big move, and how often the direction matched.
3. Write one sentence on what your log says about volatility versus direction.
""",
"key_points": [
 "The E81/E82 scouts were LightGBM models on ~40 technical features, tested on unseen 2024 and 2025–26 data.",
 "AUC around 0.6 (0.8 for turns) looked like skill, but much of it was a volatility forecast.",
 "Direction skill was small; UpScout missed t ≥ 2 in 2025–26 and fast scouts lost after costs.",
 "The scouts run live as forward-scored information and feed no bot until they prove skill.",
 "Use volatility forecasts to adjust size and stops, not to pick direction."
],
"quiz": [
 {"q": "What does an AUC of 0.5 mean?", "options": ["Perfect prediction", "No better than a coin flip", "50% profit", "Half the trades are liquidated"], "answer": 1, "why": "0.5 is random ranking; 1.0 is perfect."},
 {"q": "Why didn't the scouts' AUC translate into trading profit?", "options": ["The data was fake", "Much of the skill was predicting when big moves come, not which way, plus costs", "AUC was below 0.5", "They were never tested"], "answer": 1, "why": "Volatility skill helps both up and down labels but doesn't pick a direction."},
 {"q": "Why did the 15-minute fast scouts fail as a trading rule?", "options": ["They couldn't see big moves", "4-hour moves were too small to pay costs", "Binance blocked them", "They used future data"], "answer": 1, "why": "They forecast big moves well, but those moves were too small relative to costs."},
 {"q": "How does OMEGA treat the scouts now?", "options": ["Trades them at 20×", "Runs them live as forward-scored information that feeds no bot", "Deleted them", "Sells them as signals"], "answer": 1, "why": "They're watched and scored forward; nothing trades on them until they show skill."}
]
}
]}
