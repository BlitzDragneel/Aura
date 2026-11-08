MODULE = {
"id": "m09", "title": "Bots and automation", "free": False,
"summary": "What trading bots can and cannot do, why 'small win every day' bots blow up, the paper → testnet → live ladder, guards and kill switches, API-key safety, and how to read a forward record.",
"lessons": [
{
"id": "m09-l01", "title": "What bots can and can't do",
"body_md": r"""
# What bots can and can't do

Trading bots are sold with big promises. Let's be precise about what automation actually changes — and what it doesn't.

## What a bot is

A bot is a program that, on a schedule (say every hourly close), reads market data, applies fixed rules, and — if allowed — places orders through an exchange API. OMEGA's bots work exactly like this: *"at every hourly close, fetch closed candles, run every rule in approved.json whose status allows the mode, and (testnet/live) place the orders on Binance USDT-M futures with a protective stop, cancel unfilled limits when the rule's window ends, and sell when the rule's hold time is over."*

## What bots are good at

1. **Consistency.** They take every valid setup and skip every invalid one. No FOMO, no revenge, no hesitation.
2. **Speed and coverage.** They can scan hundreds of coins every hour — useful for rare setups like the panic bounce, which needs many coins to find enough fills.
3. **Unsocial hours.** Crypto panics happen at 3 a.m. Bots don't sleep.
4. **Exact rules.** The same code can run in backtest, paper and live. OMEGA's design: *"a live signal is trade-for-trade the backtest's."* That makes the forward record directly comparable with the test.
5. **Enforcing limits.** A guard can refuse oversized orders, cap leverage, and stop trading at a daily loss limit — reliably.

## What bots cannot do

1. **Create an edge.** A bot running a rule with no edge loses money faster and more consistently than a human. CREED automated is still −0.10R to −0.12R a trade.
2. **Adapt intelligently.** A bot doesn't know the market has changed. Fading edges keep being traded until *you* stop them.
3. **Avoid technical risk.** Bugs, internet outages, exchange API changes, rate limits, wrong settings, a key with too many permissions.
4. **Guarantee fills.** Real fills differ from backtests; slippage, partial fills and rejected orders happen.
5. **Protect you from the tails.** A bot following a fat-tailed rule will take the −80% trade just as faithfully as the +20% one.

## Bots and the evidence

Look at the OMEGA bot page: *"PAPER TRADING. No real orders are placed by any bot on this page. None of them is connected to a broker. Every bot trades simulated positions against real prices and records the results as simulated."* Some bots in the Journal are marked *retired*.

And the separate trading-bot system for Binance only allows rules listed in `approved.json` — the spec says *"anything else is refused"* — and each rule's `max_leverage` is the highest leverage the research showed with no liquidations (**1**).

## Typical bot marketing claims — and the reality

| Claim | Reality |
|---|---|
| "90% win rate" | Win rate says nothing about expectancy; high win rates often hide big losers |
| "1% a day" | That's over 3,600% a year compounded. OMEGA's Monte Carlo: no strategy turned 100 into 1,000,000 in 5 years |
| "AI-powered" | OMEGA's neural network (E32) and ML scouts (E81/E82) found little tradeable direction after costs |
| "Backtested returns of 500%" | Ask: out of sample? after costs? including delisted coins? how many variants tried? |
| "Set and forget" | Edges fade; bots need monitoring, kill switches and retirement rules |

## When automation makes sense

- You have a **rule tested fairly** (or you're running a paper/testnet experiment to build a forward record).
- The rule is **exact** — no judgement calls.
- Human execution would be **impractical** (many coins, odd hours).
- You have **guards, a kill switch and small size**.

## Exercise

1. Open the **Bots** page (Growth Bot / Bots) in OMEGA. Confirm that everything is paper and note where results are recorded.
2. Find one bot advert or social-media claim. Write the five questions from the table you would ask before believing it.
3. Open **Autopilot** and read what it does: researches, tests and paper-trades while the app is open, *never real orders*.
""",
"key_points": [
 "Bots apply fixed rules on a schedule; OMEGA's same code runs in backtest, paper and live.",
 "Bots are good at consistency, coverage, odd hours, exact rules and enforcing limits.",
 "Bots can't create an edge, adapt to fading markets, avoid technical risk or escape fat tails.",
 "OMEGA's app bots are paper only; the Binance bot trades only rules in approved.json, at max 1× leverage.",
 "Question every bot claim: out of sample, after costs, delisted coins, number of variants."
],
"quiz": [
 {"q": "What happens if you automate a rule with no edge?", "options": ["It becomes profitable", "It loses money consistently and quickly", "Fees disappear", "The exchange refunds losses"], "answer": 1, "why": "Automation executes the rule faithfully, including its negative expectancy."},
 {"q": "Why is OMEGA's 'same code in backtest, paper and live' design valuable?", "options": ["It runs faster", "Live signals match the backtest trade for trade, so forward records are comparable", "It hides losses", "It allows higher leverage"], "answer": 1, "why": "Comparing like with like is how you judge whether the edge still works."},
 {"q": "A bot advertises '1% a day'. What's the right reaction?", "options": ["Sign up immediately", "Sceptical: it implies extreme compounding; the research found nothing close", "Use 20× to make it 20% a day", "It's realistic"], "answer": 1, "why": "No strategy in the Monte Carlo turned 100 into 1,000,000 in 5 years."},
 {"q": "What does the Binance bot do with a rule not listed in approved.json?", "options": ["Trades it at 1×", "Refuses it", "Trades it on testnet only", "Asks the user each time"], "answer": 1, "why": "approved.json is the list the bot is allowed to trade; anything else is refused."}
]
},
{
"id": "m09-l02", "title": "'Small win every day' bots and their blow-ups",
"body_md": r"""
# "Small win every day" bots and their blow-ups

Some bot strategies produce beautiful, smooth equity curves — until they don't. Understanding why will protect you from the most common way automated accounts are wiped out.

## The shape of the problem

```
Equity
  |                         ___/‾‾‾‾‾‾‾‾\
  |               ___/‾‾‾‾‾              \
  |      ___/‾‾‾‾                          \
  | ___/                                    \____
  +------------------------------------------------ time
     months of small, steady wins       one event
```

These strategies **sell insurance**: they collect small payments most of the time and pay out a large amount occasionally. The expected value can be negative even though most days are green.

## Common examples

### Grid bots
Place buy orders below and sell orders above the price at fixed intervals. In a range, they buy low and sell high repeatedly. In a strong trend down, they keep buying all the way, ending with a large position far underwater. With leverage, that ends in liquidation.

### Martingale / averaging down
Double the size after each loss so one win recovers everything. Works until a long losing streak (which always comes, Module 5) requires a size the account can't afford.

```
Start 1 USDT, double after each loss:
Losses: 1, 2, 4, 8, 16, 32, 64, 128 → 8 losses = 255 USDT lost
The 9th trade must be 256 USDT to win back... 1 USDT
```

### Funding harvest (delta-neutral carry)
Buy spot, short the perp, collect funding. OMEGA tested this (E34): **+8.8% a year in 2021–24, then −17% a year in 2025–26, including one funding flip that lost −64.6% in a single month.**

### High-win-rate scalpers
Tight target, wide (or no) stop. Win 90% of trades, lose ten times the average win on the rest. Expectancy ≈ 0.9 × 1 − 0.1 × 10 = −0.1 per unit — before costs.

### Market-neutral books with short legs
OMEGA's cross-sectional test (E52): in April 2026 the short leg held a coin that rose about **50× in a week**, and **the book lost more than 100% in a day**. Shorting small coins carries squeeze-ruin risk.

## Why they're attractive

- They match the wish for steady daily income (Module 8, psychology).
- Short backtests or live periods rarely include the blow-up, so they look safe.
- High win rates feel like skill.

## How to spot one

Ask these questions about any bot or strategy:

1. **What's the worst single trade or day** in the full history? Not the average.
2. **What happens in a 30–50% crash** or a 50% spike in one day?
3. **Does it add to losing positions?** (grids, martingale, averaging down)
4. **Is the stop much wider than the target?**
5. **Does the history include 2021's boom, 2022's crashes and the October 2025 wick** (a −83% intrabar move was recorded)?
6. **Is there leverage?** Leverage turns a bad day into liquidation.

## The research's summary

OMEGA's main lessons include: *"'small win every day' strategies (grids, funding harvest, high-win-rate bots) carry rare blow-ups."* And for the funding book, the app's own monitor warns that carry *"can flip negative in selloffs, and holds exchange counterparty risk"*.

## The honest alternative

The setups that actually passed are the opposite shape: **many small losses or flat periods, occasional big wins** (the edge lives in the big rebounds). That shape is psychologically harder but doesn't hide a cliff — as long as positions are small and unleveraged.

## Worked example: a grid at 5×

```
Account 100 USDT. Grid buys 10 USDT notional every 2% down, 5× leverage (2 USDT margin each).
Price falls 20%: 10 buys = 100 USDT notional, average entry about 11% below the start.
  Unrealised loss ≈ 100 × (0.89 − 0.80) / 0.89 ≈ 10 USDT. Uncomfortable, survivable.
Price falls 40%: 20 buys = 200 USDT notional (40 USDT margin), average entry about −21%.
  Unrealised loss ≈ 200 × (0.79 − 0.60) / 0.79 ≈ 48 USDT.
Price falls 60% (it happens in crypto): 30 buys = 300 USDT notional, loss ≈ 126 USDT
  → more than the whole account: liquidated well before this point.
```

The grid "won" every small wiggle for months, then one crash took the account.

## Exercise

1. Open the **Position desk** and look at the current funding rates. Use the **Futures calculator** to work out what a funding flip from +0.01% to −0.10% per 8 hours would do to a 1,000 USDT short-perp position over a week.
2. Take any bot strategy you've heard of and answer the six questions above.
3. Write a rule in your plan: "I will not run strategies that add to losing positions or that have a stop more than __× the target."
""",
"key_points": [
 "'Small win every day' strategies sell insurance: steady small gains, rare huge losses.",
 "Grids, martingale, funding harvests, high-win-rate scalpers and short-leg books share this shape.",
 "Funding harvest (E34): +8.8%/yr 2021–24, then −17%/yr with a −64.6% month; E52's short leg lost >100% in a day.",
 "Judge strategies by worst trade and worst day, crash behaviour, averaging down and stop-to-target ratio.",
 "The passed setups have the opposite shape — but only small, unleveraged positions keep that safe."
],
"quiz": [
 {"q": "Martingale starting at 1 USDT loses 8 in a row. How much has been lost?", "options": ["8 USDT", "128 USDT", "255 USDT", "512 USDT"], "answer": 2, "why": "1+2+4+…+128 = 255 USDT."},
 {"q": "A scalper wins 90% at +1 and loses 10% at −10. Expectancy before costs?", "options": ["+0.9", "−0.1", "0", "+1.0"], "answer": 1, "why": "0.9 × 1 − 0.1 × 10 = −0.1."},
 {"q": "What happened in E52's cross-sectional book in April 2026?", "options": ["It doubled", "A short leg rose about 50× in a week and the book lost over 100% in a day", "Nothing", "It was never run"], "answer": 1, "why": "Short legs on small coins carry squeeze-ruin risk."},
 {"q": "Which question best reveals a hidden blow-up risk?", "options": ["What's the win rate?", "What's the worst single trade or day in the full history?", "How nice is the logo?", "How many users?"], "answer": 1, "why": "Averages and win rates hide tails; worst outcomes show them."}
]
},
{
"id": "m09-l03", "title": "Paper → testnet → live: the ladder",
"body_md": r"""
# Paper → testnet → live

Every automated strategy should climb a ladder, one rung at a time. Each rung tests something different. Skipping rungs is how bugs and bad ideas meet real money.

## Rung 1 — Backtest

**Tests:** the idea, on history, with costs. (Module 7.)
**Doesn't test:** your code in real time, fills, exchange behaviour.

OMEGA's bots have a backtest command that uses the same strategy code, for example:

```
python -m edges.bots backtest --strategy panic_h1 --from 2024-01-01
```

## Rung 2 — Paper

**Tests:** that the bot runs reliably in real time, produces the signals you expect, logs correctly, and that the forward results look like the backtest's.
**Doesn't test:** real order handling, real fills.

OMEGA: *"Paper first (no keys): double-click run_paper.bat. It runs forever; every signal, order, fill and exit is written to bots_log.jsonl and the state to state.json."* A `status` command shows open positions and the last log lines. Recommended: **a few days at least**, and ideally many trades.

## Rung 3 — Testnet

**Tests:** real order mechanics against a demo exchange — placing orders, protective stops, cancelling unfilled limits, closing at hold time, handling errors.
**Doesn't test:** real liquidity and real prices.

OMEGA's instructions for Binance's futures testnet:

- Create a **testnet API key** and store it with `setkey testnet` — it goes into the operating system's credential vault, *never a file*.
- Set the rule's status to `testnet` in `approved.json`.
- The account must be in **One-way Mode**.
- *"Testnet prices differ from the real market: signals come from real candles and limit prices are re-based by the testnet/real price ratio."*

## Rung 4 — Live (tiny)

**Tests:** everything, with real money at stake.

OMEGA's live switch is deliberately hard. **All** of these are required, and *"any one missing = refused"*:

1. **50+ testnet trades that look like the backtest.**
2. A real API key with **futures only, no withdrawals, restricted to your IP**, stored with `setkey live`.
3. `"status": "live"` for that rule in `approved.json` — *"only the owner sets this by hand"*.
4. `"live": true` in the config file.
5. An environment variable typed in the terminal: `OMEGA_LIVE=I_UNDERSTAND_REAL_MONEY`.

That friction is intentional. Going live should be a calm, deliberate decision, never a click.

## What to compare at each rung

| Check | Paper | Testnet | Live |
|---|---|---|---|
| Signals match backtest for the same period | ✓ | ✓ | ✓ |
| Orders placed / cancelled correctly | — | ✓ | ✓ |
| Stops placed on every position | — | ✓ | ✓ |
| Fill prices vs assumed | — | partly | ✓ |
| Average result per trade vs backtest | rough | rough | ✓ (after many trades) |

## How long on each rung?

- **Paper:** until you've seen the bot run through restarts, quiet periods and at least a few signals.
- **Testnet:** 50+ trades, per OMEGA's rule.
- **Live:** start with the minimum size and keep it there for at least 100 trades before considering any change.

For rare setups (the climax fires only occasionally), this takes months. That's fine. There's no deadline.

## Honest limits

OMEGA's bot README is candid: exchange calls were tested against a **simulated Binance** only, because the research environment couldn't reach the real exchange or testnet; the bots had *"never run on Windows, against the real testnet, or with MetaTrader 5"* at that time. That is exactly why the ladder exists — each rung finds problems the previous one couldn't.


## Worked example: what each rung actually caught

Here is an illustrative (made-up) example of one rule climbing the ladder; the numbers are invented to show the process, not results from OMEGA — the kind of problems each rung is designed to find.

**Backtest.** The rule shows about +0.2% a trade after costs on 2024–26 data, many trades, 1×. Fine as a starting point.

**Paper (3 weeks, 41 signals).**

```
Signals matched a backtest of the same 3 weeks: 39 of 41.
Two mismatches: the bot restarted during an hourly close and skipped one bar;
a coin's data had a missing (volume-0) candle that the backtest treated as missing too,
but the live feed filled it.
Fixes: on restart, re-evaluate the last closed bar; treat volume-0 bars the same way live.
```

Without paper, those two mismatches would have shown up as unexplained live results.

**Testnet (7 weeks, 52 trades).**

```
Orders placed: 52 entries, 52 stops, 31 limit cancellations at window end.
Problems found:
  - 3 stops rejected (price precision wrong for small-price coins) → entry undone by the guard ✔
  - 1 position briefly without a stop after a network timeout → guard hit the kill cycle ✔
Average result: noisy and not comparable (testnet prices differ from real).
```

The guard did its job: no unprotected position stayed open. The precision bug was fixed and re-tested for another 20 trades.

**Live (tiny).** 5 USDT seats, 1×, a no-withdrawal, IP-restricted key.

```
First 60 live trades: average fill on limit entries matched the assumed price
(fills only when price traded through); market exits slipped about 0.03% on average.
Average result: −0.05% a trade, t ≈ −0.1 → no conclusion yet; continue to 100+.
```

Every rung caught something the previous one couldn't. None of them proved the edge — only a long live record can — but together they made sure that when the live record is judged, it's judging the **strategy**, not bugs.

## Exercise

1. Write the ladder for one strategy you'd consider automating: what you'll check at each rung, and the minimum number of trades or days before moving up.
2. If you have the OMEGA bots, run paper mode and use `status` to view positions and the log. Note one thing that surprised you.
3. Write your personal "go live" checklist with the five OMEGA conditions plus any of your own.
""",
"key_points": [
 "Each rung tests something different: backtest (idea), paper (real-time running), testnet (order mechanics), live (everything).",
 "Paper first with no keys; every signal, order, fill and exit is logged.",
 "Testnet keys go in the OS credential vault; testnet prices differ, so it tests mechanics more than profit.",
 "Live requires 50+ matching testnet trades, a no-withdrawal IP-restricted key, and several manual switches.",
 "Rare setups take months to climb the ladder — there's no deadline."
],
"quiz": [
 {"q": "What does testnet mainly test?", "options": ["Whether the strategy is profitable", "Real order mechanics: placement, stops, cancellations, errors", "Tax reporting", "Leverage limits on the real market"], "answer": 1, "why": "Testnet prices differ from the real market, so it's a mechanics test."},
 {"q": "Which API key setting is required for OMEGA's live mode?", "options": ["Withdrawals enabled", "Futures only, no withdrawals, restricted to your IP", "Spot and margin", "Any key works"], "answer": 1, "why": "A minimal-permission key limits the damage if it's ever leaked."},
 {"q": "How many matching testnet trades does OMEGA require before live?", "options": ["5", "10", "50+", "1,000"], "answer": 2, "why": "Go live only if 50+ testnet trades look like the backtest."},
 {"q": "Why is OMEGA's live switch deliberately hard to turn on?", "options": ["Poor design", "To make going live a calm, deliberate decision, not a click", "To charge a fee", "It isn't"], "answer": 1, "why": "Multiple manual steps prevent accidental or impulsive live trading."}
]
},
{
"id": "m09-l04", "title": "Guards, kill switches and key safety",
"body_md": r"""
# Guards, kill switches and key safety

A bot will do exactly what it's told, very fast, forever. Guards limit what it *can* do when something goes wrong — a bug, a bad signal, a market crash, or a mistake in settings.

## OMEGA's guard (config.json → guard)

| Guard | Setting | What it prevents |
|---|---|---|
| Hard leverage cap | **3×**, and each rule's `max_leverage` (now **1×**) | Accidental high leverage |
| Margin per order | **≤ 10 USDT** | One oversized order |
| Open positions / resting entries | **≤ 3**, counted **from the exchange**, not only the bot's file | Runaway order loops; state-file errors |
| Positions per coin | **One** | Doubling up by accident |
| Risk per trade (size × stop) | **≤ 3 USDT** | Large single losses |
| Daily loss limit | **5 USDT** | A bad day spiralling |
| Stop on every position | Inside the liquidation distance, **2% buffer live** | Liquidation before the stop |
| Stop can't be placed | **Entry undone**; if that fails too, **kill switch** and the position is marked UNPROTECTED and closed | Naked positions |

Notice the design: limits are checked against the **exchange**, not just the bot's memory. If the bot's state file is wrong, the exchange is the source of truth.

## The kill switch

> *"KILL_all.bat (or python -m edges.bots kill) cancels every order, closes every position on the futures account and blocks new orders."*

It also writes the OMEGA Bridge's KILL file, and the bots obey the Bridge's kill too — *one switch for both*. `kill_off` lifts it.

Every automated setup you run should have:

1. **One action that stops everything** — cancels orders, closes positions, blocks new ones.
2. **Easy access** — a desktop shortcut, a phone action, or a written procedure.
3. **A test** — try it on paper/testnet so you know it works before you need it.

## When to press it

- The bot is placing orders you don't understand.
- Positions exist without stops.
- The exchange or your internet is behaving strangely.
- A major market event (exchange hack, extreme crash) and you're unsure.
- The daily loss limit is hit but orders keep coming.

Pressing the kill switch "too early" costs little. Pressing it too late can cost the account.

## API key safety

| Rule | Why |
|---|---|
| **No withdrawal permission, ever** | A leaked key can then trade badly but can't send your funds away |
| **Futures only** (or only what the bot needs) | Least privilege |
| **Restrict to your IP address** | A stolen key won't work from elsewhere |
| **Store in the OS vault or environment variables** | OMEGA refuses config files containing a key/secret and redacts secrets in logs |
| **Separate keys for testnet and live** | No mix-ups |
| **Use a sub-account with limited funds** | The bot can only lose what's in it |
| **Rotate keys** if you suspect anything | Cheap insurance |

## Account-level protections

- **Isolated margin** so one position can't drain the wallet.
- **Small balance on the bot account** — keep the rest elsewhere.
- **2FA** on the exchange account; withdrawal address whitelisting.

## Guards for manual trading too

The same ideas apply to you:

- Risk Guard limits (0.5% a trade, 2 open, −2% day, −5% week).
- Stop on every position, placed at entry.
- A "kill switch" habit: when in doubt, flatten and step away.

## Worked example: a guard saving the day

```
Bug: a strategy sends a long signal on every coin at once (a data glitch).
Without guard: 40 orders × 10 USDT = 400 USDT notional on a 100 USDT account.
With guard: ≤ 3 open positions counted from the exchange → 3 orders accepted,
            37 refused; risk per trade ≤ 3 USDT; daily loss limit 5 USDT.
Worst case: about 5 USDT, then trading stops. Owner presses KILL, investigates.
```

## Exercise

1. Write a guard config for any bot you might run: leverage cap, margin per order, max open, risk per trade, daily loss limit.
2. Find the kill switch for your setup (OMEGA's KILL_all, or your exchange's "close all") and practise it on paper or testnet.
3. Check every API key you own: remove withdrawal permission and add IP restrictions where possible.
""",
"key_points": [
 "OMEGA's guard: 3× hard cap (rules at 1×), ≤10 USDT margin per order, ≤3 open (counted from the exchange), ≤3 USDT risk, 5 USDT daily loss.",
 "Every position needs a stop inside the liquidation distance; if a stop can't be placed, the entry is undone.",
 "Have one tested kill switch that cancels orders, closes positions and blocks new ones.",
 "API keys: no withdrawals, minimal permissions, IP-restricted, stored in the OS vault, never in files.",
 "Use isolated margin and a small sub-account balance for bots."
],
"quiz": [
 {"q": "Why does OMEGA count open positions from the exchange, not only the bot's file?", "options": ["It's faster", "The exchange is the source of truth if the bot's state file is wrong", "Files are illegal", "To save fees"], "answer": 1, "why": "State files can be out of date; the exchange shows real exposure."},
 {"q": "What does OMEGA's kill switch do?", "options": ["Pauses the screen", "Cancels every order, closes every position and blocks new orders", "Withdraws funds", "Raises leverage"], "answer": 1, "why": "It's a single action to stop everything."},
 {"q": "Which API key permission should a trading bot never have?", "options": ["Read", "Futures trading", "Withdrawal", "Order cancellation"], "answer": 2, "why": "Without withdrawal permission a leaked key can't move funds out."},
 {"q": "What happens in OMEGA's bots if a protective stop can't be placed?", "options": ["The trade continues unprotected", "The entry is undone; if that fails, kill switch and close", "Leverage increases", "Nothing"], "answer": 1, "why": "No position is allowed to stay naked."}
]
},
{
"id": "m09-l05", "title": "Reading a forward record",
"body_md": r"""
# Reading a forward record

A **forward record** is a list of trades or predictions made in real time, recorded as they happened, and never edited. It's the most honest evidence there is — if you know how to read it.

## Why forward records matter

Backtests can be wrong in many ways (Module 7). A forward record can't be overfitted to data that didn't exist yet. That's why OMEGA's research says the passed setups need *"the forward-ticket record ... before trusting them with money"*, and why the scouts run live as *"public, forward-scored predictions"* that *"feed no bot until their forward record shows skill"*.

## What a trustworthy forward record looks like

1. **Timestamped before the outcome.** Signals are published or logged when made.
2. **Complete.** Every signal, including losers and ones not traded. OMEGA Signals: *"Every signal is followed to its outcome and recorded in the Journal."*
3. **Unedited.** No deleting, no "that one doesn't count".
4. **Same rules as tested.** OMEGA Signals' *"stop, target and 24-hour limit are exactly the terms that were tested"*; the bots' live code is the backtest code.
5. **After real costs.**
6. **Compared with a baseline.** OMEGA's tests judge each rule against random entries with the same exits — a system with no skill.

## Five questions to ask

### 1. How many trades?
Small records mean almost nothing. Using the standard error formula from Module 5:

```
SD of results 1.3R:
  30 trades: SE = 1.3 / 5.5 ≈ 0.24R → an average of +0.2R is within noise
  100 trades: SE = 0.13R
  300 trades: SE = 0.075R
```

For fat-tailed setups like the panic bounce (single trades from −90% to big rebounds), you need **hundreds**.

### 2. How does it compare with the backtest?
If the backtest said +0.2% a trade and the forward record after 200 trades is −0.1%, something is different: costs, fills, market change, or the edge was never real.

### 3. Without the best few trades?
Does the result depend on one or two huge winners? (H1 loses without its best 5% — so a forward record of H1 might look negative for long stretches even if the edge is still there.)

### 4. Worst trade, worst day, max drawdown?
Do they fit what the test said? A worst trade far beyond the test's range is a red flag.

### 5. Against a no-skill baseline?
For a 2:1 reward:risk system, a no-skill trader wins about a third of the time. A 35% win rate at 2:1 isn't skill; it's roughly the baseline minus costs.

## Worked example: judging a signal record

```
Signal service: 60 trades, win rate 58%, average +0.35R after costs
SD per trade: 1.2R
SE = 1.2 / √60 = 1.2 / 7.75 = 0.155R
t = 0.35 / 0.155 ≈ 2.26
```

Promising — **if** the record is complete, unedited and pre-timestamped, and **if** it isn't the best of many services or periods shown to you (survivorship again: you rarely see the services that failed). Next steps: keep watching for 100–200 more trades; check the worst trades; compare with the stated rules.

## Red flags in forward records

- Screenshots of wins, no complete list.
- Records that start "from our best month".
- Results shown only as % of account with unknown leverage.
- Signals deleted or "updated" after the fact.
- No costs, or "before fees".
- A record shorter than the strategy's typical drawdown.

## Building your own forward record

Everything in this course points here. Whether manual or automated:

1. Write the rules (Module 7).
2. Log every signal and trade in the Journal, real and simulated separate.
3. Compare monthly with the test and a baseline.
4. Apply your retirement rule.

## Exercise

1. Open **OMEGA Signals** → *Live results against the research*. Note the number of closed signals and how they compare with the research.
2. Open the public forward records linked from the progress board (https://omega-board.onrender.com). Is any rule clearly above zero after costs? With how many trades?
3. Take any public trading record you can find and score it against the six "trustworthy" criteria and the red-flag list.
""",
"key_points": [
 "A forward record is timestamped before outcomes, complete, unedited, uses the tested rules and includes costs.",
 "Judge it by number of trades, comparison with the backtest, dependence on best trades, worst outcomes and a no-skill baseline.",
 "Small records mean little; fat-tailed setups need hundreds of trades.",
 "OMEGA Signals use exactly the tested terms and are followed to outcome; OMEGA's tests compare against a no-skill baseline.",
 "Red flags: screenshots only, cherry-picked start dates, unknown leverage, edits, no costs."
],
"quiz": [
 {"q": "Which makes a forward record trustworthy?", "options": ["Screenshots of the best trades", "Complete, unedited, timestamped before outcomes, after costs", "Starting from the best month", "Showing only % gains"], "answer": 1, "why": "Completeness and pre-timestamping are what make it honest."},
 {"q": "60 trades, average +0.35R, SD 1.2R. Roughly what is t?", "options": ["0.29", "2.26", "5.0", "0.6"], "answer": 1, "why": "SE = 1.2/7.75 ≈ 0.155; t ≈ 2.26."},
 {"q": "For a 2:1 reward:risk system, what is a no-skill win rate (roughly)?", "options": ["About 33%", "50%", "66%", "90%"], "answer": 0, "why": "Break-even at 2:1 is 1/(1+2) ≈ 33%."},
 {"q": "Why might an H1 forward record look negative for long stretches even if the edge still exists?", "options": ["Because H1 loses without its best 5% of trades, which are rare", "Because it uses 20×", "Because signals are delayed", "It can't"], "answer": 0, "why": "Results depend on rare big rebounds, so long flat or losing spells are expected."}
]
}
]}
