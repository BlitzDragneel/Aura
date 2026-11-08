MODULE = {
"id": "m03", "title": "Reading charts", "free": False,
"summary": "Candles, timeframes, sessions, volume, support and resistance, market structure, trend versus range — and how to mark up a chart in OMEGA's Analysis and Market Read pages.",
"lessons": [
{
"id": "m03-l01", "title": "Candles and timeframes",
"body_md": r"""
# Candles and timeframes

A chart is a record of what traders actually did. Reading it well means describing what happened accurately — not predicting the future from shapes.

## Anatomy of a candle

Each candle covers one period (1 minute, 15 minutes, 1 hour, 1 day...) and shows four prices: **open, high, low, close (OHLC)**.

```
        |   <- high (upper wick)
      +---+
      |   |  <- body: open to close
      |   |     green/hollow = close above open
      +---+     red/filled  = close below open
        |   <- low (lower wick)
```

- **Body**: the distance from open to close. A big body means one side controlled the period.
- **Wicks (shadows)**: prices traded but rejected by the close. A long lower wick means price fell and then buyers pushed it back up.
- **Range**: high minus low — a measure of how volatile the period was.

## Where the close sits in the range

A simple and useful measure is **close location**:

```
Close location = (close − low) / (high − low)
0 = closed on the low, 1 = closed on the high
```

This is not a decoration — it is part of one of the two setups that passed OMEGA's tests. The **climax reversal** requires a large hourly drop on heavy volume with the close in the **top 40% of the candle's range** (close location ≥ 0.6): heavy selling that got bought back before the hour ended.

### Worked example

An hourly candle on a coin: open 2.00, high 2.02, low 1.80, close 1.95.

```
Range = 2.02 − 1.80 = 0.22
Close location = (1.95 − 1.80) / 0.22 = 0.68  → top 40% of the range
Body = 2.00 − 1.95 = 0.05 (small red body), long lower wick (0.15)
```

Description: "Sold off hard during the hour, then most of the drop was bought back."

## Timeframes

The same market looks different on different timeframes:

| Timeframe | Typical use | Noise |
|---|---|---|
| 1m – 5m | Execution, scalping | Very high |
| 15m | Intraday entries | High |
| 1h | Intraday structure, the main OMEGA research bar | Medium |
| 4h | Swing structure, "battlefield" in CREED | Lower |
| 1d | Overall trend and key levels | Low |

A one-hour candle is made of four 15-minute candles, twelve 5-minute candles and so on. A long-wicked 1h candle might be a sharp crash and a full recovery on the 5-minute chart.

## Top-down reading

A common routine is to read from higher to lower timeframes:

1. **Daily / 4h:** what is the big picture? Trending up, down or ranging? Where are the major levels?
2. **1h:** where is price inside that picture? Near a level, mid-range, after a big move?
3. **15m / 5m:** only if you have a reason to act — how is price behaving right now?

CREED, the method on the app's CREED desk, is built exactly like this: *4H battlefield → 1H pullback zone → 15M sweep → acceptance*. Note for later (Module 6): top-down reading is a good way to **organise** your view, but the research measured CREED's setups at about a coin flip after costs. Structure is description, not edge.

## The trap of shorter timeframes

Lower timeframes give more "setups", which feels productive. But:

- More trades = more costs.
- Moves are smaller, so costs are a bigger share of each move.
- The research found that 5m and 15m reversal ideas (E37–E46) and the 15-minute machine-learning scouts (E82) did not pay costs in the final test.

Beginners usually do better on **1h and above**.

## Candle "patterns"

You will meet names like hammer, doji, engulfing and shooting star. They are useful **vocabulary** for describing what happened. As stand-alone trading signals, candle patterns generally have weak or no evidence once costs are included; OMEGA's own tests of short-term wick rules (E46, 5-minute wick/cascade) failed. Use the names to describe, not to predict.

## Exercise

1. Open **Analysis** and choose a market in depth. Switch between the 5-minute, 15-minute and 1-hour views.
2. Find the largest 1-hour candle of the last day. Write down its open, high, low and close, and compute its range and close location.
3. Describe it in one plain sentence (e.g. "fell 3% then recovered half before the close"). Then look at the same hour on 5-minute candles and describe what happened inside it.
""",
"key_points": [
 "A candle records open, high, low and close; wicks show rejected prices.",
 "Close location = (close − low) / (high − low); the climax reversal needs a close in the top 40%.",
 "Read top-down: daily/4h for context, 1h for structure, 15m/5m only for execution.",
 "Shorter timeframes mean more trades, more costs and smaller moves; 5m/15m ideas failed in the research.",
 "Candle-pattern names are vocabulary for description, not proven signals."
],
"quiz": [
 {"q": "A candle has low 100, high 110 and close 108. What is its close location?", "options": ["0.2", "0.8", "0.08", "1.08"], "answer": 1, "why": "(108 − 100) / (110 − 100) = 0.8, near the top of the range."},
 {"q": "What does a long lower wick show?", "options": ["Price never went lower", "Price traded lower but was pushed back up before the close", "The market was closed", "Volume was zero"], "answer": 1, "why": "The wick marks prices that traded during the period but were rejected by the close."},
 {"q": "Why do beginners often do better on 1h and higher timeframes?", "options": ["Fees are lower there", "Fewer trades and larger moves mean costs take a smaller share", "Lower timeframes are illegal", "Higher timeframes always trend"], "answer": 1, "why": "Fewer, larger moves are less eaten by costs; short-timeframe ideas failed in the research."},
 {"q": "How should candle-pattern names like 'hammer' be used?", "options": ["As guaranteed reversal signals", "As vocabulary to describe what happened", "Only on weekends", "To set leverage"], "answer": 1, "why": "Patterns describe price action; as stand-alone signals the evidence after costs is weak."}
]
},
{
"id": "m03-l02", "title": "Sessions: when markets move (in Trinidad and Tobago time)",
"body_md": r"""
# Sessions: when markets move

Markets are not equally active all day. Volume, volatility and spreads change with the time of day. Knowing the clock helps you choose *when* to pay attention and when to step away.

## Converting time

Trinidad and Tobago uses **AST, UTC−4, all year** (no daylight saving). The UK and US do change their clocks, so some session times shift by an hour during the year.

## Forex and gold sessions

| Session | Local open | T&T time (US/UK summer) | T&T time (US/UK winter) |
|---|---|---|---|
| Week opens (Sydney/Wellington) | Sunday 17:00 New York | Sun 17:00 | Sun 18:00 |
| Tokyo | 09:00 Tokyo | 20:00 (previous day) | 20:00 (previous day) |
| London | 08:00 London | 03:00 | 04:00 |
| New York (forex) | 08:00 New York | 08:00 | 09:00 |
| US stock market (cash open) | 09:30 New York | 09:30 | 10:30 |
| Daily rollover | 17:00 New York | 17:00 | 18:00 |

Tokyo does not use daylight saving, so its time stays the same for you. The UK and US switch on different dates in March and October/November, so for a week or two the gaps are unusual — check a world clock.

### Typical behaviour

- **Asian session:** often quieter for EURUSD and gold, with narrower ranges.
- **London open:** volume jumps; many big daily moves in forex start here.
- **London–New York overlap** (roughly 08:00–12:00 T&T in summer): usually the most liquid and volatile period for forex and gold. US economic data is typically released at 08:30 New York time.
- **After the New York afternoon:** activity fades, and spreads widen around the **daily rollover**. Avoid entering just before rollover.

## Crypto sessions

Crypto trades 24/7, but activity still follows people:

- Volume tends to rise when Europe and the US are awake and is lower in the late US evening and weekend.
- **Funding times** on Binance perps: 00:00, 08:00, 16:00 UTC = **20:00, 04:00, 12:00 T&T**.
- Weekends are often thinner, so large orders and liquidation cascades can move price further.

## What the research says about timing

Timing seems like an obvious edge. OMEGA tested it carefully:

| Test | Result |
|---|---|
| E15 forex majors, hour by hour | All five failed |
| Session splits per market | Failed (protocol's failed list) |
| E43 trading around funding settlement windows | No variant had a positive mean |
| E44 US cash open, DST-correct | Best variant t 1.73 in discovery — not promoted (needed t ≥ 2) |
| E45 turn of month | Strong in 2020–23, then negative: −292 bp a trade in 2025–26 |

So **"time of day" is not a strategy by itself**. What time of day *does* reliably tell you is **how much the market is likely to move** and **what your costs will be**. That is valuable for risk: wider expected ranges need smaller positions, and wide spreads mean higher costs.

## Building your trading window

Choose a window you can actually keep, given your life:

```
Example (gold trader in T&T, US summer):
  07:30  preparation: calendar, levels, Market Read
  08:00–11:30  active window (London–NY overlap, 08:30 US data)
  11:30  stop looking for new trades; manage open ones
  No new trades within 30 minutes of 17:00 rollover
```

```
Example (crypto trader with a day job):
  19:30  review Market Read and OMEGA Signals
  20:00  funding time — avoid opening a perp right before it if funding is high
  One check before bed; alerts instead of screen-watching
```

## Exercise

1. Open **Market Profiles** and read *"When it moves"* for gold and one coin. Write down the hours it says are most active.
2. Convert the London open, the New York cash open and the daily rollover into T&T time for today's date.
3. Write your personal trading window (start, end, and "no new trades" times) into your notes. You will reuse it in Module 8 and in your trading plan.
""",
"key_points": [
 "T&T is UTC−4 all year; UK and US session times shift by an hour with their daylight saving.",
 "The London–New York overlap is usually the most active period for forex and gold; spreads widen at rollover.",
 "Crypto is 24/7 but follows human activity; Binance funding is at 20:00, 04:00 and 12:00 T&T.",
 "Timing rules (hour-by-hour forex, US open, funding windows, turn of month) failed OMEGA's tests.",
 "Time of day mainly tells you expected volatility and costs — use it for risk and scheduling."
],
"quiz": [
 {"q": "What time is the 09:30 New York cash open in T&T during US winter (EST)?", "options": ["08:30", "09:30", "10:30", "11:30"], "answer": 2, "why": "EST is UTC−5 and T&T is UTC−4, so 09:30 EST is 10:30 in T&T."},
 {"q": "When are spreads typically widest in forex and gold?", "options": ["London–New York overlap", "Around the daily rollover and big news", "Tuesday mornings", "Never"], "answer": 1, "why": "Liquidity thins at rollover and spreads widen around major news."},
 {"q": "What did OMEGA's E15 test of forex majors hour by hour find?", "options": ["Two pairs worked", "All five failed", "London open was a strong edge", "It was not run"], "answer": 1, "why": "All five majors failed the hour-by-hour test."},
 {"q": "What is time of day most reliably useful for?", "options": ["Predicting direction", "Estimating volatility and costs, and scheduling your attention", "Choosing leverage above 20×", "Avoiding taxes"], "answer": 1, "why": "Timing alone was not a directional edge, but it does tell you about expected movement and spreads."}
]
},
{
"id": "m03-l03", "title": "Volume: what it tells you and what it doesn't",
"body_md": r"""
# Volume

Volume is how much traded during a candle. Price tells you *where* trading happened; volume tells you *how much* conviction or forced activity was behind it.

## Kinds of volume

- **Exchange volume (crypto):** real traded amounts on that exchange, in coins (`v`) or quote currency such as USDT (`qv`). Binance futures volume is genuine for that venue, but it is one venue among many.
- **Tick volume (forex and gold CFDs):** the number of price changes, not contracts traded. Forex is decentralised, so your broker cannot show total market volume. Tick volume tends to rise and fall with real activity, but treat it as a rough guide.

## Relative volume

Raw volume is hard to compare across coins. A better measure is **relative volume**:

```
Relative volume = this candle's volume / average volume of recent candles (e.g. last 24 or 48)
```

A reading of 3 means three times the usual activity.

### Worked example

A coin's last 24 hourly candles averaged 1.2 million USDT of volume. The latest hour traded 4.8 million.

```
Relative volume = 4.8 / 1.2 = 4.0
```

Combined with a large drop and a close near the top of the range, that hour would match the **climax reversal** pattern: a 3σ drop, at least **3× volume**, close in the top 40%. In the 15-minute version tested later (E41), the researchers noticed every such bar had more than 5× volume — climaxes are extreme by nature.

## What volume can tell you

1. **Participation.** A breakout on tiny volume has fewer people behind it than one on heavy volume.
2. **Climax and exhaustion.** Very high volume on a sharp drop often means forced selling (stops, liquidations, panic). Once sellers are exhausted, price can rebound. This is the logic behind the two setups that passed.
3. **Volatility ahead.** Volume and volatility cluster: busy periods tend to be followed by busy periods.
4. **Liquidity.** Higher volume usually means tighter spreads and less slippage.

## What volume cannot tell you (by itself)

OMEGA tested several volume-based and order-flow ideas. Most failed:

| Test | Idea | Result |
|---|---|---|
| E30 | Order-book depth (13,690 coin-days) | Predicted neither direction nor useful size |
| E67 | Taker buy/sell imbalance, top-100 coins | Failed; momentum versions strongly negative |
| E33 | Forced deleveraging (open-interest drop + 5% fall) | −0.03% a trade (t −0.10) |
| E42 | Climax on 4h candles | Failed (t 0.29) |
| E46 | 5-minute cascade spikes | Failed (not promoted) |

The pattern: volume helps **describe** a market and **filter** for extreme events, but "more buyers than sellers" does not predict the next move after costs.

## Volume in OMEGA

- The **Market Watch** panel (Edge Lab area) records aggressive orders, large orders, the order book and liquidations — it is labelled *recording only*.
- **Market Read** shows where stops and resting orders may sit, and who is crowded.

Use them to understand what is happening, not as a buy button.

## Reading volume on a chart: a checklist

- Is this candle's volume unusual (relative volume above 2–3)?
- Did the high volume come with a big move, or with no movement (absorption)?
- Where did the candle close in its range?
- Is this at a level that matters (prior low, range edge)?
- Is it a weekend or quiet hour where one large order looks huge?

## Exercise

1. In **Analysis**, open a coin and find the three highest-volume hours of the last week. For each, note the move, the close location and what happened over the next 12 hours.
2. Compute relative volume for one of them (its volume ÷ the average of the previous 24 hours).
3. Write one sentence: did the highest-volume candles come at turning points, in the middle of moves, or both? (Usually both — which is why volume alone is not a signal.)
""",
"key_points": [
 "Crypto exchange volume is real for that venue; forex/gold CFD volume is tick volume, a rough guide.",
 "Relative volume (this candle ÷ recent average) makes volume comparable; the climax setup needs at least 3×.",
 "Very high volume on a sharp drop can signal forced selling and exhaustion — the logic of the passed setups.",
 "Order-book depth, taker imbalance and forced-deleveraging rules failed OMEGA's tests.",
 "Use volume to describe and filter extreme events, not as a stand-alone signal."
],
"quiz": [
 {"q": "A candle trades 6 million when the 24-hour average is 2 million. What is its relative volume?", "options": ["0.33", "3", "4", "12"], "answer": 1, "why": "6 / 2 = 3, three times normal."},
 {"q": "What is tick volume on a forex CFD?", "options": ["Total contracts traded worldwide", "The number of price changes on the broker's feed", "The broker's profit", "The spread"], "answer": 1, "why": "Forex is decentralised; brokers show the count of price updates as a proxy."},
 {"q": "What did E30's test of order-book depth find?", "options": ["It predicted direction well", "It predicted neither direction nor useful size", "It worked only on gold", "It was never run"], "answer": 1, "why": "13,690 coin-days of depth data predicted neither direction nor useful size."},
 {"q": "Why is very high volume on a sharp drop interesting?", "options": ["It always means the price will keep falling", "It can signal forced selling and exhaustion, after which rebounds happen", "It means the exchange is broken", "It guarantees a profit"], "answer": 1, "why": "Overdone panic selling was the only durable edge found; extreme volume is part of identifying it."}
]
},
{
"id": "m03-l04", "title": "Support, resistance and liquidity",
"body_md": r"""
# Support, resistance and liquidity

Support and resistance are the most widely used ideas in chart reading. Used carefully, they help you choose **where to put stops and targets**. Used carelessly, they become lines that "explain" everything after the fact.

## Definitions

- **Support:** a price area where falling price has repeatedly stopped and turned up.
- **Resistance:** a price area where rising price has repeatedly stopped and turned down.
- **Flip:** broken resistance often acts as support later, and the other way round.

They are **zones**, not exact prices. Draw a band around the wicks and bodies, not a single pixel-thin line.

## Why levels can matter

Levels matter because traders behave around them:

1. **Memory:** people who bought at a level and saw a loss may sell when price returns to break even.
2. **Orders cluster there:** limit orders rest at obvious levels, and **stop-losses** cluster just beyond them.
3. **Round numbers:** 60,000 on BTC, 2,600 on gold, 1.1000 on EURUSD attract orders.

## Liquidity: where the stops are

"Liquidity" in chart-trading language often means **clusters of resting orders, especially stops**:

```
          ---- stops of shorts (buy stops) above the high ----
   high ->  ^^^^^^^^^^^^^^^^^^^^
            price range
   low  ->  vvvvvvvvvvvvvvvvvvvv
          ---- stops of longs (sell stops) below the low ----
```

When price pokes below an obvious low, it triggers those sell stops. Then, if no more sellers appear, price can snap back. This is called a **sweep** (or stop run). OMEGA's **Market Read** page maps this: *"Stops above → Stops below → Resting orders → Who is crowded."*

CREED's "15M sweep" step looks for exactly this: a quick poke beyond a level and a return ("acceptance"). Remember the evidence though: CREED's setups behaved like a coin flip after the sweep (+1R before the stop 49% of the time versus 50% expected by chance).

## How to draw levels without fooling yourself

1. **Start on a higher timeframe** (daily or 4h). Mark only the most obvious swing highs and lows — places where price clearly turned.
2. **Limit yourself to 2–4 levels** above and below. If your chart has twenty lines, price is always "at a level".
3. **Use zones** sized roughly to the market's normal noise (for example a fraction of the hourly ATR, Module 4).
4. **Mark them before you trade**, and don't move them after.
5. **Check honestly:** how many times did price go straight through a level you marked? Count those too.

## The real use: placing stops and targets

Levels are most useful for **risk placement**:

- Put a stop **beyond** the level that would prove your idea wrong, plus a buffer for noise and sweeps — not exactly on the obvious line where everyone else's stop sits.
- Put a target **before** the next opposing level, where profit-taking is likely.
- Calculate the **reward-to-risk** that results.

### Worked example

Gold is at 2,652. Support zone 2,640–2,643. Next resistance 2,675–2,678.

```
Long idea near support:
  Entry   2,646
  Stop    2,636 (below the zone, with a buffer) → risk 10.00
  Target  2,672 (before resistance)             → reward 26.00
  Reward-to-risk = 26 / 10 = 2.6
```

That looks attractive on paper. But a reward-to-risk number only tells you the payoff *if* you win. It says nothing about *how often* you win. A 2.6R target that is hit 25% of the time loses money:

```
Expectancy = 0.25 × 2.6 − 0.75 × 1 = 0.65 − 0.75 = −0.10R
```

Interestingly, −0.10R a trade is about what CREED measured after costs.

## Exercise

1. Open **Market Read** for a market you follow. Note where it shows stops above and below price.
2. On the daily chart in **Analysis**, mark no more than three support and three resistance zones. Screenshot or write them down with today's date.
3. Over the next week, record each time price reaches one of your zones: did it turn, pause, or pass straight through? Keep the count — it is your first small, honest test.
""",
"key_points": [
 "Support and resistance are zones where price has turned before, not exact lines.",
 "Stops cluster beyond obvious highs and lows; a sweep triggers them and may reverse.",
 "Mark only a few levels from higher timeframes, before trading, and count the failures too.",
 "The best use of levels is placing stops (beyond the level, with a buffer) and targets (before the next level).",
 "Reward-to-risk alone says nothing about win rate; a 2.6R target hit 25% of the time loses money."
],
"quiz": [
 {"q": "Where should a protective stop usually go relative to a support zone for a long?", "options": ["Exactly on the line", "Beyond the zone, with a buffer for noise and sweeps", "Above the entry", "No stop is needed at support"], "answer": 1, "why": "Stops exactly on obvious lines are easily swept; place them where the idea is clearly wrong, plus a buffer."},
 {"q": "What is a 'sweep'?", "options": ["A cleaning of the order book by the exchange", "Price poking beyond an obvious level to trigger stops, then possibly returning", "A long-term trend", "A funding payment"], "answer": 1, "why": "Sweeps trigger clustered stops; Market Read maps where those stops may sit."},
 {"q": "A setup offers 3R but wins only 20% of the time. What is the expectancy?", "options": ["+0.6R", "−0.2R", "0R", "+0.4R"], "answer": 1, "why": "0.2 × 3 − 0.8 × 1 = 0.6 − 0.8 = −0.2R."},
 {"q": "Why limit yourself to a few levels?", "options": ["Charts can't show more", "With many lines price is always 'at a level', so the levels explain nothing", "Exchanges charge per line", "Levels expire"], "answer": 1, "why": "Too many levels make any outcome look predicted after the fact."}
]
},
{
"id": "m03-l05", "title": "Market structure: trend versus range",
"body_md": r"""
# Market structure: trend versus range

Market structure is the sequence of swing highs and swing lows. It is a simple, objective way to describe what a market is doing.

## Swings

A **swing high** is a high with lower highs on both sides (for example, the highest high of the 2 candles before and after). A **swing low** is the opposite. Using a fixed rule (such as "2 candles each side") keeps you objective.

## The three states

```
Uptrend:   higher highs (HH) and higher lows (HL)
             HH
        HH  /  \
   HH  /  \/    HL
  /  \/    HL
 /    HL

Downtrend: lower highs (LH) and lower lows (LL)

Range:     highs and lows roughly level; price bounces between two zones
```

- **Uptrend:** each pullback stops above the previous low.
- **Downtrend:** each bounce stops below the previous high.
- **Range:** neither side makes progress.

## Break of structure

- In an uptrend, a close **below the last higher low** is a break of structure: the uptrend description no longer holds.
- In a downtrend, a close **above the last lower high** breaks it.

It is a change in the *description*, not a guarantee that a new trend has started. Many breaks fail and price returns to the range.

## Worked example

Hourly closes on a coin (simplified swings):

```
Swing low 1.00 → swing high 1.10 → swing low 1.04 → swing high 1.16 → swing low 1.09
```

Highs: 1.10 → 1.16 (higher). Lows: 1.00 → 1.04 → 1.09 (higher). **Uptrend.**
The last higher low is 1.09. A close below 1.09 would break the structure.

A long-side plan might be: wait for a pullback towards 1.09–1.11, stop below 1.09 with a buffer, target near the 1.16 high or above. Then compute reward-to-risk and costs (Module 2) and size it (Module 5).

## Trend versus range: why it matters for risk

- In trends, pullback entries and wider targets are common.
- In ranges, trades near the edges with targets at the opposite edge are common.
- In **volatile chop**, both approaches suffer, and many traders do best by trading less.

## What the evidence says about trend trading

This is an area where beliefs are strong and evidence is weak. OMEGA's November research (E50–E55) found:

- **Own-trend (time-series momentum) on BTC, ETH and the top 10:** the best variant was only at the 70th percentile of the luck check (the bar is the 95th). Crypto trend following earns the market's drift, but **no more than a shifted signal with the same long bias**.
- **Donchian breakouts with an ATR trailing stop:** **random entries with the same stop beat it.**
- **Cross-sectional momentum and reversal:** none eligible; in April 2026 one short leg held a coin that rose about 50× in a week, and the book lost more than 100% in a day.
- **BTC → alt lead-lag:** the catch-up is gone by the next bar's open.

So: describing trend is useful context; **"buy because it is trending" was not an edge after costs** in these tests. The OMEGA Research Lab also tests trend and structure conditions on your own history — you can check them yourself (Module 7).

## Using structure honestly

- Use it to **define where you are wrong** (the swing that must hold).
- Use it to **avoid** fighting a strong move with a large position.
- Don't treat a label ("uptrend") as a reason to trade on its own.

## Exercise

1. In **Analysis**, open the in-depth view for a market. Note how OMEGA describes its structure on 5m, 15m and 1h.
2. On the 1-hour chart, mark the last four swing highs and lows using the "2 candles either side" rule. Label them HH/HL/LH/LL. Is it trending or ranging?
3. Write down the exact price that would break the current structure. Check back in 24 hours: did it break? Did the break continue or fail?
""",
"key_points": [
 "Market structure is the sequence of swing highs and lows; use a fixed rule to define swings.",
 "Uptrend = higher highs and higher lows; downtrend = lower highs and lower lows; range = neither.",
 "A break of structure changes the description; it does not guarantee a new trend.",
 "Trend and breakout rules failed OMEGA's tests: random entries with the same stop beat Donchian breakouts.",
 "Use structure to define where your idea is wrong, not as a reason to trade on its own."
],
"quiz": [
 {"q": "Swing lows of 50, 52 and 55 with swing highs of 54 and 58 describe:", "options": ["A downtrend", "An uptrend", "A range", "A liquidation"], "answer": 1, "why": "Higher highs and higher lows define an uptrend."},
 {"q": "In an uptrend, what is a break of structure?", "options": ["A new higher high", "A close below the last higher low", "Any red candle", "A funding payment"], "answer": 1, "why": "Closing below the last higher low means the higher-lows pattern no longer holds."},
 {"q": "What did E51 find about Donchian breakouts with an ATR trailing stop?", "options": ["They were the best strategy", "Random entries with the same stop beat them", "They worked only in 2025", "They were not tested"], "answer": 1, "why": "Breakouts added nothing over random entries with the same stop."},
 {"q": "What is the most reliable use of market structure in this course?", "options": ["Predicting the next candle", "Defining where your idea is wrong and placing stops", "Choosing leverage", "Timing funding"], "answer": 1, "why": "Structure gives an objective invalidation point; as a directional signal it was not an edge."}
]
},
{
"id": "m03-l06", "title": "A guided mark-up with OMEGA Analysis and Market Read",
"body_md": r"""
# A guided mark-up in OMEGA

This lesson puts the whole module together into a repeatable routine you can do in 10–15 minutes per market, using the OMEGA app.

## Step 1 — Choose the market and timeframe

Open **Analysis**. Press *Scan now* (or let it scan every 10 minutes while open). Filter by *Crypto* or *Forex & gold*, and sort by *Setups first* or *Score*.

Remember what the score is: the page says it is *"the classic analysis engine, not a tested OMEGA idea"*. A score of 60+ with at least 2:1 reward-to-risk "meets the bar" for the engine — it is a filter for attention, not evidence of an edge. Each card also says how old its reading is; forex and gold take turns within the Twelve Data allowance.

## Step 2 — Higher-timeframe context

Press *In depth* on one market. On the higher timeframe:

- Write the structure: uptrend / downtrend / range.
- Mark 2–3 key zones above and below.
- Note the recent daily range (how far it typically moves).

## Step 3 — Market Read

Open **Market Read** for the same market. It shows:

1. **Stops above / stops below** — where a sweep could trigger orders.
2. **Resting orders** — where limit orders cluster.
3. **Who is crowded** — positioning and funding.
4. **What the research supports** — a reminder of what has and hasn't been tested.

Compare with your own zones. Where they agree, you have a clearer map. Where they differ, write down both.

## Step 4 — Market Profile

Open **Market Profiles** if the market is one of those profiled (gold and five coins). Read *When it moves*, *How it behaves*, *How to size it* and *What was tested*.

## Step 5 — Write the scenario, not a prediction

Write two scenarios with prices:

```
Market: XAUUSD      Date/time: 2026-11-09 07:45 T&T
Context: 4h range 2,630–2,680; price 2,655 mid-range
Zones: support 2,630–2,634; resistance 2,676–2,680
Market Read: stops below 2,628; crowded long (mild)
Scenario A: sweep below 2,630 and close back above → long idea,
            stop 2,621, target 2,665 (R:R ≈ 2.1)
Scenario B: clean 1h close below 2,626 → no long; range broken
Not trading: mid-range at 2,655 — no edge in the middle
Size check: 0.5% risk on 1,000 USD = 5 USD; stop 9-ish → 0.01 lot = ~9 USD → too big, skip unless tighter
```

Notice the last line. The mark-up ends with a **size check**, and in this case the honest answer is "too big for my account at my risk level". That is a correct outcome, not a failure.

## Step 6 — Compare with tested signals

Open **OMEGA Signals**. Is there an open signal on this market? Signals appear *only when a condition the Research Lab rated held out-of-sample fires on the last closed hourly bar*, and each shows a **Signal score** (how strong now) and **Evidence** (how much tested history backs it). Most of the time there won't be one. That is normal: tested edges are rare.

## Step 7 — Record it

Whether you trade or not, record the scenario. The Journal can hold *trades and setups not taken*. Over weeks, your recorded mark-ups become a small, honest dataset: how often did Scenario A actually happen, and what followed?

## A common mistake: the story fits everything

After a move, it is easy to draw lines that "predicted" it. This is **hindsight bias**. The only mark-ups that count are the ones written down **before** price moved, with prices and times. This is the same principle as OMEGA's research: plan before data.

## A checklist you can copy

```
[ ] Market and time recorded
[ ] Higher-timeframe structure written
[ ] 2–3 zones each side
[ ] Market Read: stops, resting orders, crowding noted
[ ] Two scenarios with entry, stop, target, R:R
[ ] Costs as % of target checked
[ ] Size calculated at my risk % (and rounded down)
[ ] OMEGA Signals checked
[ ] Recorded in Journal (taken or not taken)
```

## Exercise

Do a full mark-up for **two markets** (one crypto, one forex or gold) using the checklist. Save them with the time. Tomorrow, look back: what happened, and did your scenarios cover it? Do not change the original notes — add a separate "result" line.
""",
"key_points": [
 "The Analysis score is a filter for attention, not a tested edge.",
 "Combine higher-timeframe structure, your zones, Market Read and Market Profiles into one map.",
 "Write scenarios with prices and a size check, not predictions; 'too big for my account' is a valid result.",
 "Check OMEGA Signals for tested conditions — most of the time there won't be one.",
 "Record mark-ups before price moves; only pre-written notes count."
],
"quiz": [
 {"q": "What does a high Analysis score with 2:1 reward-to-risk mean?", "options": ["A tested edge with proven profit", "It meets the classic engine's bar for attention; it is not a tested OMEGA idea", "A guaranteed winner", "You must take the trade"], "answer": 1, "why": "The page explicitly says the engine is not a tested OMEGA idea."},
 {"q": "When does an OMEGA Signal appear?", "options": ["Every hour on every market", "When a condition rated as holding out-of-sample fires on the last closed hourly bar", "When the Analysis score hits 60", "When funding is positive"], "answer": 1, "why": "Signals only fire for conditions that held out-of-sample in the Research Lab."},
 {"q": "Your mark-up shows the minimum lot would risk more than your rule allows. What is the right outcome?", "options": ["Take it with a bigger account later", "Skip the trade or find a sensible tighter setup", "Remove the stop", "Double the size to make it worthwhile"], "answer": 1, "why": "If the size check fails, the trade doesn't fit your account."},
 {"q": "Why must mark-ups be recorded before price moves?", "options": ["The app requires it", "To avoid hindsight bias; only pre-written scenarios can be judged honestly", "To save battery", "So the exchange can see them"], "answer": 1, "why": "Lines drawn afterwards always seem to fit. It's the 'plan before data' principle."}
]
}
]}
