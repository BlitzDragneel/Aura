MODULE = {
"id": "m02", "title": "Markets and mechanics", "free": True,
"summary": "Spot, perpetual futures and CFDs; order types; spreads, fees, slippage and funding; margin and liquidation; lots and pips — all with real maths at a 100 USDT account size.",
"lessons": [
{
"id": "m02-l01", "title": "Spot, perpetual futures and CFDs: what you actually own",
"body_md": r"""
# Spot, perpetual futures and CFDs

Three very different products can all show you the "same" price chart. Knowing which one you are trading changes your costs, your risks and what can go wrong.

## Spot

On a **spot** market (for example Binance Spot) you buy the actual coin. If you buy 0.001 BTC at 60,000 USDT, you pay 60 USDT and you own 0.001 BTC.

- **Maximum loss:** what you paid (the coin can go towards zero, but you cannot lose more than you put in).
- **No liquidation**, no funding payments.
- **You can only profit from a rise** (unless you use margin or sell coins you already own).
- **Costs:** a trading fee each side, plus the spread.

Spot is the simplest and safest place for a beginner to learn execution.

## Perpetual futures (perps)

A **perpetual future** is a contract that tracks the price of a coin but never expires. On Binance USDT-M futures you post USDT as **margin** and open a position that can be **long** (profit if price rises) or **short** (profit if price falls).

- **Leverage:** your position can be larger than your margin. 10 USDT margin at 5× controls a 50 USDT position.
- **Liquidation:** if losses eat your margin down to the maintenance level, the exchange closes the position.
- **Funding:** every 8 hours on most Binance perps (00:00, 08:00 and 16:00 UTC), longs pay shorts or shorts pay longs. This keeps the perp price near the spot price. (Lesson 4.)
- **Mark price:** liquidation uses a "mark price" based on an index of several spot exchanges, not just the last trade, to reduce manipulation.

You do not own any coin. You own a contract with the exchange as counterparty and clearing house.

## CFDs (forex and gold on Exness)

A **CFD** (contract for difference) is an agreement with your broker to exchange the difference in price between opening and closing. When you trade XAUUSD (gold) or EURUSD on Exness, you own no gold and no euros.

- **Leverage** is usually available, and can be very high. High available leverage does not mean you should use it.
- **Costs:** mainly the **spread**, plus a commission on some account types, plus **swap** (overnight financing) if you hold past the daily rollover — unless your account/instrument is swap-free. Check your account's contract specification.
- **Stop-out:** instead of "liquidation", brokers use a **margin call** level and a **stop-out** level (a margin level percentage at which they start closing your positions).
- **Counterparty:** your broker. Regulation, segregation of client funds and negative-balance protection vary by broker entity and by country. Check which entity serves you in Trinidad and Tobago and what protections apply.
- **Market hours:** forex and gold trade roughly from Sunday evening to Friday evening (New York time), with a daily break. Crypto trades 24/7.

## Side by side

| | Spot crypto | Perpetual futures | CFDs (forex/gold) |
|---|---|---|---|
| You own the asset | Yes | No | No |
| Can go short | Not easily | Yes | Yes |
| Leverage | No (on plain spot) | Yes | Yes |
| Liquidation / stop-out | No | Yes | Yes |
| Holding cost | None | Funding every 8 h | Swap at rollover (unless swap-free) |
| Main trading cost | Fee + spread | Fee + spread + slippage | Spread (+ commission on some accounts) |
| Hours | 24/7 | 24/7 | Weekdays |

## Worked example: same move, three products

Bitcoin goes from 60,000 to 57,000 (−5%). You have 100 USDT.

```
Spot, 100 USDT of BTC:              −5 USDT  (account 95)
Perp long, 100 USDT margin at 1×:   −5 USDT  (plus fees)
Perp long, 100 USDT margin at 10×:  1,000 USDT position, −50 USDT (account 50)
Perp long, 100 USDT margin at 20×:  2,000 USDT position, −100 USDT → liquidated before that
```

The market did the same thing in every row. Only the product and the leverage changed the outcome.

## Which should a beginner use?

- Learn on **paper** first (the OMEGA Futures page is paper only).
- Then **spot**, or a perp at **1×** with a tiny size, so liquidation is not a realistic risk.
- For forex and gold, start with the **smallest lot size** your account allows and calculate the dollar value of every move before entering (Lesson 6).

## Exercise

1. Open the **Futures** page in OMEGA (paper only). Find where it shows liquidation, fees and funding. Read its section *"Leverage — what the tests say"*.
2. On paper, repeat the worked example for a 3% *rise* at 1×, 5× and 10× with 100 USDT margin. (Answers: +3, +15, +30 USDT before fees.)
3. If you have an Exness account, open the contract specification for XAUUSD and write down: contract size, minimum lot, and whether swaps apply to your account.
""",
"key_points": [
 "Spot means you own the coin; your loss is limited to what you paid and there is no liquidation.",
 "Perpetual futures are leveraged contracts with liquidation and funding every 8 hours on most Binance perps.",
 "CFDs on forex and gold are contracts with your broker: spread, possible commission, swap and stop-out.",
 "The same market move gives very different results depending on product and leverage.",
 "Beginners should practise on paper, then spot or 1× with tiny size."
],
"quiz": [
 {"q": "Which product has no liquidation and no funding?", "options": ["Perpetual futures", "CFDs", "Spot", "All of them"], "answer": 2, "why": "On spot you own the coin outright; there is no margin to liquidate and no funding."},
 {"q": "What is funding on a perpetual future?", "options": ["A deposit bonus", "A periodic payment between longs and shorts that keeps the perp near spot", "The exchange's withdrawal fee", "Interest paid by the exchange to everyone"], "answer": 1, "why": "Funding is exchanged between longs and shorts, typically every 8 hours on Binance perps."},
 {"q": "With 100 USDT margin at 10×, Bitcoin falls 5%. What happens?", "options": ["You lose 5 USDT", "You lose about 50 USDT", "You gain 50 USDT", "Nothing until you close"], "answer": 1, "why": "A 1,000 USDT position × 5% = 50 USDT loss, half the account."},
 {"q": "On a CFD broker, what is the 'stop-out' level?", "options": ["Your take-profit", "The margin level at which the broker starts closing your positions", "The daily market close", "The spread"], "answer": 1, "why": "Brokers close positions automatically when your margin level drops to the stop-out percentage."}
]
},
{
"id": "m02-l02", "title": "Order types: market, limit, stop and the rest",
"body_md": r"""
# Order types

An order type is an instruction about *how* you want to buy or sell. Choosing the right one saves money and prevents disasters.

## The order book in one picture

```
SELLERS (asks)
  60,030  0.8 BTC
  60,020  1.2 BTC
  60,010  0.5 BTC   <- best ask
------------- spread = 10 -------------
  60,000  0.7 BTC   <- best bid
  59,990  2.0 BTC
  59,980  1.1 BTC
BUYERS (bids)
```

The **best bid** is the highest price someone will pay. The **best ask** is the lowest price someone will sell at. The gap is the **spread**.

## Market order

"Buy (or sell) now, at whatever price is available."

- **Pros:** fills immediately.
- **Cons:** you pay the spread and you are a **taker** (higher fee). In a thin market a large market order "walks the book" and fills at several worse prices — **slippage**.
- Example: a market buy of 1.5 BTC in the book above fills 0.5 at 60,010, 1.0 at 60,020 — average about 60,017.

## Limit order

"Buy at this price or lower" (or sell at this price or higher).

- **Pros:** you control the price; if it rests in the book you are a **maker** (lower fee on Binance futures: 0.02% versus 0.05% taker).
- **Cons:** it may never fill. And the trades that *do* fill are often the ones where price kept going against you — this is called **adverse selection**.
- In OMEGA's tests, a resting limit was only counted as filled if price traded **through** it (below a buy limit), not just touched it. That is a realistic, conservative assumption you should use too.

The panic bounce setup (Module 6) is a limit-order setup: it places a buy far below the current price and only fills during a sharp drop.

## Stop (stop-market) order

"When price reaches X, send a market order."

- Used to **exit a losing trade** (stop-loss) or to enter on a break.
- Once triggered it is a market order, so in a fast move it can fill well past your stop price. A stop limits loss *in normal conditions*; it is not a guarantee. Gaps (forex and gold over a weekend) and crypto wicks can blow straight through it.
- On Binance futures you can choose whether the stop triggers on **last price** or **mark price**. Mark price is less prone to brief wicks.

## Stop-limit order

"When price reaches X, place a limit order at Y."

- Controls the fill price, but in a fast move it may **not fill at all**, leaving you in a losing trade with no exit. For protective stops, most traders prefer stop-market.

## Take-profit order

A limit or stop order placed to close a winning trade at a target. Note: in OMEGA's exit lab (E80), adding take-profits to the two passed setups *reduced* their edge — the profits came from the big rebounds a tight target would cut off. A take-profit is a choice to test, not a must.

## Useful flags

| Flag | Meaning | Why it matters |
|---|---|---|
| **Reduce-only** | Can only shrink a position, never open or flip one | Stops a stop-loss from accidentally opening a new position |
| **Post-only** | Cancelled if it would fill immediately as a taker | Guarantees maker fee |
| **Time in force** (GTC / IOC / FOK) | Good-till-cancelled / immediate-or-cancel / fill-or-kill | Controls how long an order lives |
| **OCO** (one-cancels-other) | A take-profit and a stop: when one fills, the other cancels | Common on spot |

On MetaTrader (Exness), the equivalents are **Buy/Sell** (market), **Buy Limit / Sell Limit**, **Buy Stop / Sell Stop**, with **SL** and **TP** fields on each position.

## Worked example: cost of a market versus limit entry

You buy 50 USDT of a coin on Binance futures.

```
Market (taker 0.05%):  fee 0.025 USDT, plus half the spread, say 0.02%: 0.01 USDT
Limit  (maker 0.02%):  fee 0.010 USDT, no spread paid
Saving per entry:      about 0.025 USDT
```

Small? Over 200 trades it is 5 USDT — 5% of a 100 USDT account. But remember the trade-off: some limit orders won't fill, and the ones that do may be worse trades.

## Exercise

1. In the **Futures** page (paper) or on Binance's demo, place a limit buy well below price and a stop-market sell below that. Mark the stop as reduce-only.
2. Write down: if price gaps 3% below your stop, roughly where would your stop-market fill? (Answer: near the first available price after the gap — about 3% below the stop, not at the stop.)
3. Look at an order book on any coin and calculate the spread as a percentage: (ask − bid) / bid × 100.
""",
"key_points": [
 "Market orders fill immediately but pay the spread, taker fees and possible slippage.",
 "Limit orders control price and can earn maker fees but may not fill; fills suffer adverse selection.",
 "A stop-market order becomes a market order when triggered; gaps and wicks can fill it far past the stop.",
 "Use reduce-only on exits so a stop can never open a new position.",
 "Count a limit as filled only if price trades through it — that is how OMEGA tested limits."
],
"quiz": [
 {"q": "Which order guarantees a fill but not the price?", "options": ["Limit", "Market", "Stop-limit", "Post-only"], "answer": 1, "why": "A market order fills at the best available prices, whatever they are."},
 {"q": "Why can a stop-limit order be dangerous as a protective stop?", "options": ["It costs more fees", "In a fast move the limit may never fill, leaving you in the trade", "It always fills at a worse price", "It cannot be cancelled"], "answer": 1, "why": "If price jumps past the limit, the order sits unfilled while losses grow."},
 {"q": "What does the 'reduce-only' flag do?", "options": ["Lowers the fee", "Ensures the order can only shrink an existing position", "Reduces leverage automatically", "Cancels after one minute"], "answer": 1, "why": "Reduce-only prevents an exit order from opening or flipping a position."},
 {"q": "In OMEGA's research, when was a resting limit buy counted as filled?", "options": ["When price touched it", "When price traded through (below) it", "Always", "At the next candle's open"], "answer": 1, "why": "A conservative fill rule: price must trade through the limit, as real queues mean a touch often doesn't fill."}
]
},
{
"id": "m02-l03", "title": "Spreads, fees and slippage at a 100 USDT account",
"body_md": r"""
# Spreads, fees and slippage

Costs are the one part of trading you can measure precisely before you trade. They are also the reason most strategies fail: OMEGA's research found that many ideas had a small edge *before* costs and none after.

## The three costs

1. **Fee** — charged by the exchange or broker per trade.
2. **Spread** — you buy at the ask and sell at the bid; crossing the spread costs about half the spread on each side.
3. **Slippage** — the difference between the price you expected and the price you got, from market impact or fast markets.

## Binance USDT-M futures fees

The research used Binance's standard rates: **taker 0.05%** and **maker 0.02%** per side. (Your rate may be lower with BNB discounts or VIP tiers — check your account.) Fees are charged on the **position value (notional)**, not on your margin. That is the key point beginners miss.

```
Fee = notional × fee rate
Notional = margin × leverage
```

## Worked example at 100 USDT

You have 100 USDT. Compare three ways to trade the same idea, entering and exiting with market orders (taker both sides), with an extra 0.03% slippage-and-spread per side on a mid-sized coin.

| Setup | Notional | Cost per side (0.05% + 0.03%) | Round trip | % of account |
|---|---|---|---|---|
| 10 USDT margin, 1× | 10 | 0.008 | 0.016 | 0.016% |
| 10 USDT margin, 5× | 50 | 0.04 | 0.08 | 0.08% |
| 100 USDT margin, 20× | 2,000 | 1.60 | 3.20 | 3.2% |

At 20× on the whole account, **every round trip costs 3.2% of your money**. Ten trades costs a third of the account in costs alone, win or lose.

## Costs in "basis points"

Traders often measure costs in **basis points (bp)**: 1 bp = 0.01%. A round trip of 0.05% + 0.05% taker = **10 bp**, plus slippage. Many research results in this course are quoted in bp per trade after costs, for example "panic bounce H1: +19 bp in 2025–26".

Ask yourself: *if my idea makes 15 bp a trade before costs and costs 16 bp, what do I have?* A losing strategy.

## Slippage is bigger where you least want it

- **Small coins** have thinner order books: wider spreads and more slippage. OMEGA's cost model added slippage that depended on each coin's liquidity.
- **Fast markets** (news, liquidation cascades, crashes) have the worst slippage — and that is exactly when stops trigger.
- **Your size matters** relative to the book. At 100 USDT, you rarely move the market on large coins, but on tiny coins you can.

## Forex and gold costs on Exness

On a CFD account the main cost is the spread, plus a commission on some account types (check yours). A useful habit: convert the spread into dollars for your lot size.

```
Gold (XAUUSD), contract 100 oz per lot (check your spec):
  Spread of 0.20 (20 cents) × 100 oz × 0.01 lot = 0.20 USD per trade
EURUSD, 100,000 units per lot:
  Spread of 1.0 pip (0.0001) × 100,000 × 0.01 lot = 1.00 USD per trade
```

Spreads widen at the daily rollover, around big news and on Monday opens. A "typical" spread can be several times wider at those moments.

## A quick cost-versus-target check

Before any trade, compare your expected move to your costs:

```
Target move: 0.6%   Round-trip cost: 0.16%
Costs as a share of the target: 0.16 / 0.6 = 27%
```

If costs eat a quarter of your target, you need to be right much more often just to break even. This is why the research found that very short-term trading (the 15-minute "fast scouts", E82) failed: they could see big moves coming, but **4-hour moves were too small to pay costs**.

## Ways to cut costs honestly

1. **Trade less.** The cheapest trade is the one you don't take.
2. **Use lower leverage.** Same margin, smaller notional, smaller fees.
3. **Prefer liquid markets** (BTC, ETH, majors; gold and EURUSD at active hours).
4. **Use limit orders where it makes sense** — and test with realistic fills.
5. **Avoid trading at the rollover and during big news** unless your plan is built for it.

## Exercise

1. Pick a coin in **Analysis**. Look up its spread on the exchange and compute a round trip in bp: fees (10 bp taker both sides) + spread.
2. For the trade plan shown on that coin's in-depth view, divide your round-trip cost by the distance to the target. What share of the target do costs take?
3. Write a personal rule: "I will not take a trade where costs are more than ___% of the target." (Many traders choose 10–20%.)
""",
"key_points": [
 "Fees are charged on notional (margin × leverage), not on margin.",
 "Binance futures standard fees used in the research: taker 0.05%, maker 0.02% per side.",
 "At 20× on a 100 USDT account, one round trip can cost about 3% of the account.",
 "Slippage is worst in small coins and fast markets — exactly when stops trigger.",
 "Compare costs to your target before each trade; very short-term moves often can't pay costs."
],
"quiz": [
 {"q": "A position has 10 USDT margin at 5× leverage. On what amount is the fee charged?", "options": ["10 USDT", "50 USDT", "5 USDT", "100 USDT"], "answer": 1, "why": "Fees apply to notional: 10 × 5 = 50 USDT."},
 {"q": "How many basis points is a round trip of 0.05% taker on each side (before slippage)?", "options": ["5 bp", "10 bp", "50 bp", "1 bp"], "answer": 1, "why": "0.05% + 0.05% = 0.10% = 10 bp."},
 {"q": "On EURUSD with a 1.0 pip spread, what does 0.01 lot cost in spread?", "options": ["0.10 USD", "1.00 USD", "10 USD", "100 USD"], "answer": 1, "why": "0.0001 × 100,000 × 0.01 = 1 USD."},
 {"q": "Why did the 15-minute fast scouts (E82) fail as a trading rule?", "options": ["They could not predict big moves", "The 4-hour moves were too small to pay costs", "Binance banned them", "They had no data"], "answer": 1, "why": "They forecast big moves about as well as the hourly scouts, but the moves were too small relative to costs."}
]
},
{
"id": "m02-l04", "title": "Funding on perpetuals and swaps on CFDs",
"body_md": r"""
# Funding and swaps: the cost of holding

Fees and spreads are paid when you trade. **Funding** (perps) and **swap** (CFDs) are paid for *holding* a leveraged position over time.

## Why perps have funding

A perpetual future never expires, so nothing forces its price to meet the spot price. Funding solves that:

- If the perp trades **above** spot (traders are keen to be long), the funding rate is **positive**: **longs pay shorts**.
- If the perp trades **below** spot (keen to be short), funding is **negative**: **shorts pay longs**.

On most Binance USDT-M perps funding is exchanged every 8 hours, at **00:00, 08:00 and 16:00 UTC**. You pay or receive it only if you hold a position *at that moment*. (Some contracts settle more often; check the contract details.) In Trinidad and Tobago time (UTC−4 all year) those are **20:00, 04:00 and 12:00**.

## Funding maths

```
Funding payment = position notional × funding rate
```

In calm markets the rate on many coins sits near **0.01% per 8 hours**. That sounds small:

```
1,000 USDT notional × 0.01% = 0.10 USDT per 8 hours
Per day (3 payments):        0.30 USDT
Per 30 days:                 9 USDT
```

On a 100 USDT account using 10× (1,000 notional), that is **9% of the account per month** just to hold a long. In hot markets funding can be many times higher — on small coins it can reach 1% or more per period, either direction.

## Funding as a signal or a strategy? The evidence

Funding looks like it should contain information about crowded traders. OMEGA tested this several ways:

- **E34 funding harvest** (buy spot, short the perp, collect funding — "delta-neutral"): **+8.8% a year in 2021–24, then −17% a year in 2025–26, with one flip costing −64.6% in a month.** A classic "small win every day, rare blow-up" strategy.
- **E54 funding as a contrarian signal**: three variants promoted, all failed validation in 2024; the best final version lost about −8.6 bp a day.
- **E43 funding-settlement windows** (trading around the funding times): no variant had a positive mean.
- **E28**: funding-carry effects were a 2021–22 phenomenon.

The OMEGA app's Simulation page shows a funding-rate carry monitor for information, and says plainly that OMEGA does not execute it and that carry *"can flip negative in selloffs"*.

**Lesson:** treat funding as a **cost to manage**, not a free income.

## Swaps on CFDs (forex and gold)

On a CFD you usually pay or receive a **swap** for each night a position is held past the broker's daily rollover. Swap comes from the interest-rate difference between the two currencies plus the broker's markup. Gold usually carries a swap charge on both sides at many brokers, but rates change.

- Many brokers charge **triple swap** on one day of the week (often Wednesday) to cover the weekend.
- Some Exness accounts or instruments may be **swap-free** depending on your account type and location. Check the contract specification and your account settings; do not assume.

```
Swap example (illustrative): swap long −5.0 USD per lot per night
0.10 lot held 5 nights (including one triple): 0.10 × 5.0 × 7 = 3.50 USD
```

## Practical rules

1. **Know when funding or rollover happens** and whether your plan holds across it. The research charged funding on every position held across 00/08/16 UTC when holding more than 8 hours.
2. **Check the current funding rate** before opening a perp position you plan to hold for days.
3. **Low leverage = small funding.** Funding is on notional, just like fees.
4. **Be suspicious of "yield" from funding.** It is paid by the other side because they expect price to move in their favour.

## Exercise

1. Open the **Positioning Desk** in OMEGA. Find the funding section and the "carry at your size" panel. Note the current funding rate on BTC.
2. Calculate: with 200 USDT notional at that rate, what would you pay or receive in one day (3 payments)?
3. Convert the three funding times to your local time and write them in your trading plan notes.
""",
"key_points": [
 "Funding keeps perps near spot: positive funding means longs pay shorts, negative means shorts pay longs.",
 "On most Binance perps funding is every 8 hours at 00:00, 08:00 and 16:00 UTC (20:00, 04:00, 12:00 in T&T).",
 "Funding is charged on notional, so leverage multiplies it.",
 "Funding harvest earned +8.8%/yr in 2021–24 then lost −17%/yr in 2025–26, with a −64.6% month.",
 "CFDs charge swap at the daily rollover, often triple on one weekday; check if your account is swap-free."
],
"quiz": [
 {"q": "If the funding rate is positive, who pays?", "options": ["Shorts pay longs", "Longs pay shorts", "The exchange pays everyone", "Nobody"], "answer": 1, "why": "Positive funding means the perp is above spot, so longs pay shorts."},
 {"q": "At 0.01% per 8 hours on 1,000 USDT notional, roughly what is the daily funding?", "options": ["0.10 USDT", "0.30 USDT", "3 USDT", "10 USDT"], "answer": 1, "why": "0.10 USDT per period × 3 periods = 0.30 USDT per day."},
 {"q": "What happened to the delta-neutral funding harvest (E34) in 2025–26?", "options": ["It made +8.8% a year", "It lost about −17% a year, with one month at −64.6%", "It was not tested", "It doubled"], "answer": 1, "why": "The funding harvest worked in 2021–24, then a funding flip produced large losses."},
 {"q": "When do you pay funding on a Binance perp?", "options": ["Every trade", "Only if you hold the position at the funding time", "Once a month", "Only on profitable trades"], "answer": 1, "why": "Funding is exchanged only by positions open at the settlement moment."}
]
},
{
"id": "m02-l05", "title": "Margin, leverage and liquidation: the exact maths",
"body_md": r"""
# Margin, leverage and liquidation

This is the most important mechanics lesson in the course. Many accounts are lost not to bad analysis but to a misunderstanding of margin.

## Definitions

- **Margin**: the money you lock up to open a position.
- **Notional (position size)**: the full value of the position.
- **Leverage** = notional ÷ margin.
- **Maintenance margin**: the minimum margin the exchange requires to keep the position open. On Binance it depends on the coin and position size; for small positions it is often around 0.4–1% of notional. The OMEGA research used **0.5%** as a round figure.
- **Liquidation**: when your margin minus losses falls to the maintenance margin, the exchange closes the position. You lose (roughly) all the margin on it.

## The liquidation distance

For an isolated position, a good approximation is:

```
Liquidation distance ≈ 1 / leverage − maintenance margin rate
```

| Leverage | 1 / leverage | Minus 0.5% | Liquidation distance |
|---|---|---|---|
| 1× | 100% | — | No practical liquidation for a long |
| 2× | 50% | | 49.5% |
| 3× | 33.3% | | 32.8% |
| 5× | 20% | | 19.5% |
| 10× | 10% | | 9.5% |
| 20× | 5% | | **4.5%** |
| 40× | 2.5% | | **2.0%** |

(Fees and funding move the real liquidation price a little closer.)

## Isolated versus cross margin

- **Isolated:** only the margin assigned to that position can be lost. Liquidation ends that position; the rest of your account is untouched.
- **Cross:** the whole futures wallet backs every position. A losing position can drain the entire balance before it is liquidated.

For beginners, **isolated** margin makes the worst case clear. Under cross margin, "low leverage" on one position is meaningless if your wallet is small.

## Worked example: a 100 USDT account

You open a BTC long with **20 USDT isolated margin at 10×** (200 USDT notional) at 60,000.

```
Liquidation distance ≈ 10% − 0.5% = 9.5%
Liquidation price ≈ 60,000 × (1 − 0.095) = 54,300
Loss at liquidation ≈ 20 USDT (20% of the account)
```

Now the same idea with a **stop-loss at 58,800 (−2%)**:

```
Loss at stop ≈ 200 × 2% = 4 USDT + fees ≈ 4.2 USDT (about 4% of the account)
```

The stop is well inside the liquidation distance, so you control the loss, not the exchange. **Rule from the OMEGA protocol: a stop must always sit inside the liquidation distance (stop distance < 1/leverage − 0.5%).**

## Leverage does not change your risk — your size and stop do

This surprises people. Compare:

```
A: 50 USDT margin, 1×, stop 4% → notional 50,  loss at stop 2 USDT
B: 5 USDT margin, 10×, stop 4% → notional 50,  loss at stop 2 USDT
```

Same notional, same stop, same 2 USDT risk. Leverage only decided how much margin was locked. The danger of leverage is that it **lets** you open a huge notional with a small account — and it brings the liquidation price close, so ordinary wicks can close you out before your stop is even reached. In crypto, stops can also slip.

## What the research measured

OMEGA's protocol reported leverage tables for the tested setups, using the worst intrabar move (MAE) of each trade, with 5% of equity as margin per trade:

- November 2026 panic tests (E37/E38/E40): **1× had no liquidations** (drawdown 10–15%); **2× already liquidated**; at **20×, 29–31% of trades hit the liquidation distance** and the account fell to about 1 USDT; at **40× about 60% of trades** were liquidated.
- The worst single intrabar move seen was **−83%** (an October 2025 wick).
- For the passed rules in the bots' backtest: panic bounce H1 was liquidated **37 times at 2×, 107 times at 3×**, and wiped out at 20× and 40×. **The highest leverage with zero liquidations and drawdown under 35% was 1× for all three rules.**

You'll study these tables in Module 5. For now, remember: **leverage never creates an edge; it scales the edge and the tail.**

## CFD margin: margin level and stop-out

Brokers track **margin level = equity ÷ used margin × 100%**. If it drops to the broker's margin-call level you get a warning; at the **stop-out** level, positions start closing (largest loser first, typically). Check your Exness account for its exact levels. The same lesson applies: high available leverage only means a small adverse move can stop you out.

## Exercise

1. On the **Futures** page (paper), set a 100 USDT account and open a position at 5×, then at 20×. Note the liquidation price the page shows for each.
2. For each, place a stop at 3% from entry. Which one has the stop *outside* the liquidation distance? (At 20× the liquidation distance is about 4.5%, so a 3% stop is inside; at 40× (2.0%) it would not be.)
3. Calculate the loss at stop for: 15 USDT margin, 4×, 2.5% stop. (Answer: 60 × 2.5% = 1.5 USDT plus fees.)
""",
"key_points": [
 "Leverage = notional ÷ margin; fees, funding and P&L are all on notional.",
 "Liquidation distance ≈ 1/leverage − maintenance margin: about 4.5% at 20× and 2.0% at 40×.",
 "Risk is set by notional and stop distance, not by leverage alone; a stop must sit inside the liquidation distance.",
 "Isolated margin limits the loss to that position; cross margin puts the whole wallet at risk.",
 "Research: 1× had no liquidations; 2× already liquidated; 20× and 40× wiped out the tested setups."
],
"quiz": [
 {"q": "What is the approximate liquidation distance at 40× with 0.5% maintenance margin?", "options": ["40%", "4.5%", "2.0%", "0.4%"], "answer": 2, "why": "2.5% − 0.5% = 2.0%."},
 {"q": "Position A: 50 USDT margin at 1×, 4% stop. Position B: 5 USDT margin at 10×, 4% stop. Which risks more at the stop?", "options": ["A", "B", "They risk the same", "Cannot tell"], "answer": 2, "why": "Both have 50 USDT notional and a 4% stop, so both lose about 2 USDT at the stop."},
 {"q": "Why is cross margin riskier for beginners?", "options": ["It has higher fees", "The whole futures wallet can be lost backing one position", "It cannot use stops", "It is only for shorts"], "answer": 1, "why": "Under cross margin, losses draw on the entire balance before liquidation."},
 {"q": "In the bots' backtest, what was the highest leverage with zero liquidations for the passed rules?", "options": ["1×", "3×", "10×", "20×"], "answer": 0, "why": "1× for all three rules; H1 was liquidated 37 times at 2× and 107 times at 3×."}
]
},
{
"id": "m02-l06", "title": "Lots, pips and contract sizes: forex and gold on Exness",
"body_md": r"""
# Lots, pips and contract sizes

On Binance futures you size positions in USDT or coins. On Exness and other MetaTrader brokers you size in **lots**. If you don't convert lots into dollars per move, you don't know your risk.

## The standard sizes (check your contract specification)

| Instrument | 1 standard lot | Smallest common lot | Price step people talk about |
|---|---|---|---|
| EURUSD, GBPUSD (forex majors) | 100,000 units of the base currency | 0.01 (1,000 units) | 1 pip = 0.0001 |
| USDJPY | 100,000 USD | 0.01 | 1 pip = 0.01 |
| XAUUSD (gold) | 100 troy ounces | 0.01 (1 oz) | 1.00 USD per ounce |

Brokers offer different account types (some with tiny "cent" units). Always open the **contract specification** for your exact symbol and account; that is the number that counts.

## Value per pip / per dollar move

```
Value of a move = price change × units
```

**EURUSD**, 0.10 lot = 10,000 EUR:
```
1 pip = 0.0001 × 10,000 = 1.00 USD
A 25-pip stop = 25 USD
```

**Gold (XAUUSD)**, 0.01 lot = 1 oz:
```
A 1.00 USD move in gold = 1.00 USD for you
A 10.00 USD move (e.g. 2,650 → 2,640) = 10 USD
```

**Gold**, 0.10 lot = 10 oz: the same 10-dollar move = **100 USD**.

Gold regularly moves 20–40 dollars or more in a day. At 0.10 lot that can be 200–400 USD — far more than a small account can take.

## Sizing a gold trade for a small account

You have **200 USD** and follow the Risk Guard's **0.5% per trade** rule: maximum risk = 1.00 USD.

```
Planned stop distance: 6.00 USD (below a recent swing low)
Risk per 0.01 lot at that stop: 6.00 × 1 oz = 6.00 USD
Allowed risk: 1.00 USD
Allowed lots = 1.00 / 6.00 × 0.01 = 0.0017 lot  → below the minimum 0.01
```

The honest conclusion: **this trade is too big for this account at this risk level**. Your choices are: skip it, find a setup with a tighter (but still sensible) stop, accept a larger percentage risk knowingly, or use an account type with smaller units. What you must *not* do is ignore the maths.

With 1,000 USD at 1% risk (10 USD), the same 6-dollar stop allows 10 / 6 × 0.01 ≈ 0.016 → **0.01 lot** (round down).

## Sizing a forex trade

Account 500 USD, risk 1% = 5 USD, EURUSD stop 20 pips.

```
Value per pip needed = 5 / 20 = 0.25 USD per pip
1 pip per 0.01 lot = 0.10 USD
Lots = 0.25 / 0.10 × 0.01 = 0.025 → round down to 0.02 lot
Actual risk = 20 pips × 0.20 USD = 4 USD (0.8%)
```

Always **round down**.

## Margin on a CFD

```
Required margin = notional / leverage
Gold 0.01 lot at 2,650 = 2,650 USD notional
At 1:100 leverage → 26.50 USD margin
At 1:500 → 5.30 USD margin
```

Leverage changed the margin, not the risk: the 6-dollar stop still costs 6 USD per 0.01 lot. High broker leverage simply lets you open positions far larger than your account can survive.

## What the evidence says about forex and gold methods

OMEGA's research is mostly crypto, but some forex and gold work was done:

- **E15**: forex majors tested hour by hour — **all five failed**.
- Gold hourly methods, session splits per market and a gold weekend-gap fade are on the protocol's **failed** list.
- The app's **Breakout Desk** says both of its setups *failed a clean test* and are kept as a record only.

That doesn't mean you can't trade gold or forex. It means you should **treat any gold or forex method as untested until you test it** (Module 7), and size it small.

## Exercise

1. Open **Market Profiles** in OMEGA and read the gold profile, especially *"How to size it"*.
2. Calculate the lot size for: account 300 USD, risk 0.5%, gold stop 4.50 USD. (Answer: risk 1.50 USD → 1.50 / 4.50 × 0.01 = 0.0033 → below minimum: the trade is too big at this risk.)
3. Calculate for: account 2,000 USD, risk 1%, EURUSD stop 15 pips. (Answer: 20 USD / 15 = 1.33 USD per pip → 0.13 lot.)
""",
"key_points": [
 "Convert lots to dollars per move: 1 lot EURUSD is 100,000 units (10 USD per pip); 1 lot gold is typically 100 oz.",
 "At 0.01 lot, a 1-dollar move in gold is about 1 USD; at 0.10 lot it is 10 USD.",
 "Size = allowed risk ÷ (stop distance × value per unit); always round down.",
 "If the minimum lot risks too much, the trade is too big for the account — skip it.",
 "Forex hour-by-hour (E15) and gold hourly methods failed OMEGA's tests; treat such methods as untested."
],
"quiz": [
 {"q": "What is 1 pip worth on 0.10 lot of EURUSD?", "options": ["0.10 USD", "1.00 USD", "10 USD", "100 USD"], "answer": 1, "why": "0.10 lot = 10,000 units; 0.0001 × 10,000 = 1 USD."},
 {"q": "Gold moves from 2,650 to 2,630. What is the P&L on 0.05 lot (5 oz) long?", "options": ["−20 USD", "−100 USD", "−5 USD", "−1,000 USD"], "answer": 1, "why": "20 USD × 5 oz = 100 USD loss."},
 {"q": "Your allowed risk needs 0.004 lot but the minimum is 0.01. What should you do?", "options": ["Trade 0.01 anyway", "Trade 0.10 to make it worthwhile", "Skip it or find a tighter, sensible stop", "Remove the stop"], "answer": 2, "why": "If the minimum size breaks your risk rule, the trade does not fit your account."},
 {"q": "Raising broker leverage from 1:100 to 1:500 does what to the dollar risk of a 6 USD stop on 0.01 lot gold?", "options": ["Multiplies it by 5", "Nothing; it only lowers the required margin", "Divides it by 5", "Removes it"], "answer": 1, "why": "Risk depends on size and stop; leverage only changes margin required."}
]
}
]}
