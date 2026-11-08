MODULE = {
"id": "m10", "title": "Building your trading plan", "free": False,
"summary": "Write your own trading plan from a template, see a filled-in example, follow a 30-day practice schedule, and complete the capstone: test, paper-trade and review one idea end to end.",
"lessons": [
{
"id": "m10-l01", "title": "Why a written plan, and what goes in it",
"body_md": r"""
# Why a written trading plan

A trading plan is a short document that answers, in advance, every question you would otherwise answer emotionally in the middle of a trade. Professionals have one. Most losing retail traders don't.

## What a plan does for you

1. **Makes decisions before emotions.** The plan was written calmly; the market won't be calm.
2. **Defines your edge — or admits you don't have one yet.** "I'm practising and building a forward record" is an honest, valid plan.
3. **Sets your risk** so one bad day can't end your trading.
4. **Makes review possible.** You can only measure "did I follow the plan?" if there is a plan.
5. **Protects you from shiny new ideas.** Any new idea must go through testing (Module 7) before it enters the plan.

## The sections of a plan

| Section | Questions it answers | Module |
|---|---|---|
| 1. Purpose and goals | Why am I trading? What does success look like this year (in process, not money)? | 1 |
| 2. Capital and products | How much money (that I can afford to lose)? Spot, perps, CFDs? Which exchange/broker? | 2 |
| 3. Markets and schedule | Which 2–3 markets? Which hours (T&T time)? News rules? | 3, 8 |
| 4. Setups | Exactly which setups, with what evidence? Entry, stop, exit rules | 4, 6, 7 |
| 5. Risk rules | Risk per trade, max open, daily/weekly stops, leverage, review level | 5 |
| 6. Execution | Order types, alerts, when orders are placed, stops at entry | 2 |
| 7. Routine | Pre-market checklist, trading window, end-of-day | 8 |
| 8. Records and review | Journal fields, weekly and monthly reviews | 8 |
| 9. Testing and retirement | How new ideas are tested; when a setup is retired | 6, 7 |
| 10. Automation (optional) | Which bots, which rung of the ladder, guards, kill switch | 9 |
| 11. Personal rules | Stop-trading list, tilt signs, what I do after a limit is hit | 8 |

## Principles for writing it

- **Short.** Two pages is better than twenty. You must be able to read it before every session.
- **Specific.** Numbers, times and exact rules — not "be disciplined".
- **Honest about evidence.** For each setup, write what evidence it has (tested by me? by OMEGA? untested?) and what its expected result is.
- **Conservative.** Start with the Risk Guard defaults or smaller.
- **Versioned.** Date it. Change it only at reviews, never during a trading session.

## Goals: process, not profit

Profit goals ("make 10% a month") push you to over-trade and over-size. The research shows how unpredictable results are — even the passed setups had long losing stretches and years with most of the profit in one year. Set **process goals** instead:

- "Follow my pre-market checklist on 90% of trading days."
- "Log 100% of trades with all fields."
- "Zero trades above my risk limit this month."
- "Complete 100 paper trades of my setup and a full review."

## Evidence labels for setups

Use a simple label for each setup in your plan:

| Label | Meaning | Allowed size |
|---|---|---|
| **Tested-pass** | Passed your own fair test or OMEGA's, forward record building | Minimum live size (after paper/testnet) |
| **Watch** | Promising (grade C, or partial test) | Paper only |
| **Untested** | No fair test yet | Paper only |
| **Failed / retired** | Failed a test or its retirement rule | None |

By these labels, CREED is "Failed" as an edge (but may be used as a discipline checklist), the climax and panic bounce are "Tested-pass, fading", E66 and E68-F6 are "Watch", and most indicator rules are "Untested" until you test them.

## Exercise

1. Write section 1 of your plan now: why you trade (look back at your sentence from Module 1), and three process goals for the next month.
2. List every setup you currently use or want to use, and give each an evidence label.
3. Open the **Risk Guard** page and copy its rules into a draft section 5.
""",
"key_points": [
 "A written plan answers in advance the questions you'd otherwise answer emotionally.",
 "Sections: goals, capital, markets/schedule, setups, risk, execution, routine, records, testing/retirement, automation, personal rules.",
 "Keep it short, specific, honest about evidence, conservative and dated.",
 "Set process goals, not profit goals.",
 "Label each setup: tested-pass, watch, untested or failed — and size accordingly."
],
"quiz": [
 {"q": "Why is a profit goal like '10% a month' discouraged?", "options": ["It's too low", "It pushes over-trading and over-sizing, while results are unpredictable", "Brokers forbid it", "Taxes"], "answer": 1, "why": "Process goals are controllable; profit targets encourage risk-taking."},
 {"q": "What label fits an idea you haven't fairly tested yet?", "options": ["Tested-pass", "Untested — paper only", "Watch — trade large", "Retired"], "answer": 1, "why": "Untested ideas stay on paper."},
 {"q": "When should you change your trading plan?", "options": ["During a losing trade", "At scheduled reviews, with a new date", "Whenever you feel like it", "Never"], "answer": 1, "why": "Changes made mid-session are emotional; reviews are calm."},
 {"q": "How should CREED be labelled given the evidence?", "options": ["Tested-pass edge", "Failed as an edge; usable as a discipline checklist", "Watch list grade C", "Untested"], "answer": 1, "why": "CREED measured a coin flip minus costs; its value is process."}
]
},
{
"id": "m10-l02", "title": "Your trading plan template, with a worked example",
"body_md": r"""
# Your trading plan template

Below is a complete template, followed by a filled-in example for a beginner in Trinidad and Tobago with a small account. Copy the template and fill it in for yourself.

## The template

```
TRADING PLAN — version __   Date __________

1. PURPOSE AND GOALS
   Why I trade:
   Process goals this month (3):

2. CAPITAL AND PRODUCTS
   Trading capital (money I can afford to lose completely):
   Exchange / broker and account type:
   Products: spot / perps / CFDs   Margin mode: isolated / cross

3. MARKETS AND SCHEDULE (T&T time)
   Markets (max 3):
   Trading window:                No new trades after:
   News rule:
   Days I don't trade:

4. SETUPS (for each)
   Name:            Evidence label:
   Entry rule:
   Stop rule:       Exit rule:
   Expected result (and source):
   Retirement rule:

5. RISK RULES
   Risk per trade:        Max open trades:
   Daily stop:            Weekly stop:
   Review level:          Max leverage:
   Correlation rule:

6. EXECUTION
   Order types:   Stops placed:   Alerts:

7. ROUTINE
   Pre-market checklist: yes   Duration:
   End of day:

8. RECORDS AND REVIEW
   Journal: every trade + setups not taken
   Weekly review day/time:      Monthly review:

9. TESTING NEW IDEAS
   Process: plan → discovery → validation → final → paper → small live
   Pass mark:

10. AUTOMATION
   Bots used / rung (paper, testnet, live):
   Guards:        Kill switch location:

11. PERSONAL RULES
   Stop-trading list:
   Tilt signs and responses:
   After a limit is hit:
```

## A worked example

```
TRADING PLAN — version 1   Date 2026-11-15

1. PURPOSE AND GOALS
   Why: build a skill and a second income over years, not weeks.
   Goals: (a) checklist on 90% of trading days; (b) journal 100% of trades
          incl. emotion; (c) 0 trades above 0.5% risk.

2. CAPITAL AND PRODUCTS
   Capital: 300 USDT on Binance (sub-account) + 200 USD on Exness. Money I can lose.
   Products: Binance USDT-M perps, ISOLATED margin, 1×. Exness CFDs, smallest lots.

3. MARKETS AND SCHEDULE
   Markets: BTCUSDT, ETHUSDT, XAUUSD.
   Window: 19:30–21:30 T&T weekdays (after work). Gold only if a setup
           is still valid from my morning check. No new trades after 21:30.
   News: flat or no new entries 30 min before/after US CPI, jobs, FOMC.
   Not trading: Fridays after a losing week; any day I'm tired or upset.

4. SETUPS
   A) Climax reversal (OMEGA, grade A, fading)
      Label: Tested-pass, fading → PAPER via OMEGA Signals/bots until 50 forward trades.
      Rules exactly as tested: 3σ hourly drop, 3× volume, close top 40%;
      buy next open, exit 12 h. Expected: ~+1% a trade 2025–26 but t < 1.
      Retire: if 100 forward trades average below 0.
   B) Structured pullback (CREED checklist)
      Label: Failed as an edge (−0.10 to −0.12R). Used only as a discipline
      exercise at 0.25% risk, max 2 a week. Stop if 50 trades average below −0.1R.
   C) My idea: gold London-open fade
      Label: Untested → test plan written 2026-11-10; paper only.

5. RISK RULES
   Risk/trade 0.5% (0.25% for B). Max open 2 (BTC+ETH same side = 1).
   Daily stop −2% or 3 losses. Weekly stop −5%. Review at −20% from peak.
   Max leverage 1× on perps. Stop inside liquidation distance always.

6. EXECUTION
   Limit entries where tested; stop-market, reduce-only, placed with the entry.
   Alerts at levels; no screen-watching.

7. ROUTINE
   19:00–19:25 checklist (Market Read, Signals, CREED, Risk Guard, calendar).
   End: journal + 5-minute note.

8. RECORDS AND REVIEW
   OMEGA Journal; real and simulated separate. Weekly: Saturday 09:00.
   Monthly: first Sunday — expectancy, drawdown, retirement rules.

9. TESTING NEW IDEAS
   Plan first; discovery/validation/final; luck check vs random entries;
   pass = final > 0 after costs, t ≥ 2, ≥ 100 trades. Then paper 50.

10. AUTOMATION
   OMEGA paper bot for setup A. Testnet only after 50 paper trades.
   Guard: 1×, ≤10 USDT margin, ≤3 open, daily loss 5 USDT. Kill switch on desktop.

11. PERSONAL RULES
   Stop-trading list: tired, angry, after 3 losses, after a big win, during news.
   Tilt signs: checking P&L constantly, switching to 5m. Response: close app 30 min.
   After a limit: journal, no trading until next session, first trade half size.
```

## Sanity checks for your plan

```
[ ] Could a stranger follow my setup rules exactly?
[ ] Is every setup labelled with its evidence?
[ ] Is my maximum daily loss a number in currency?
[ ] Is leverage limited to what tests showed survives (1× for everything tested here)?
[ ] Does the schedule fit my real life?
[ ] Is there a retirement rule for each setup?
[ ] Is there a kill switch / stop-trading rule?
```

## Exercise

1. Fill in the full template for yourself. Keep it to two pages.
2. Run it through the sanity checks.
3. Save it with a version number and date. Print it or keep it open next to OMEGA.
""",
"key_points": [
 "Use the 11-section template: goals, capital, markets, setups, risk, execution, routine, records, testing, automation, personal rules.",
 "The example plan labels every setup with its evidence and sizes it accordingly.",
 "Risk rules are numbers in currency: 0.5% a trade, 2 open, −2% day, −5% week, −20% review, 1× leverage.",
 "Each setup needs exact rules, an expected result with its source, and a retirement rule.",
 "Run the plan through the sanity checks, version it, and keep it beside you."
],
"quiz": [
 {"q": "In the example plan, how is the climax reversal handled?", "options": ["Traded at 20× immediately", "Paper via OMEGA Signals/bots until 50 forward trades, with a retirement rule", "Ignored", "Traded with a quick take-profit"], "answer": 1, "why": "It's tested-pass but fading, so it builds a forward record on paper first."},
 {"q": "Why does the example plan count BTC and ETH longs as one position?", "options": ["Fees", "They're highly correlated", "Binance requires it", "No reason"], "answer": 1, "why": "Correlated positions act like one bigger trade."},
 {"q": "Which sanity check helps ensure your rules are exact?", "options": ["Is my logo nice?", "Could a stranger follow my setup rules exactly?", "Did I make money last week?", "Is my leverage high enough?"], "answer": 1, "why": "If a stranger couldn't apply them, they involve judgement and can't be tested."},
 {"q": "What maximum perp leverage does the example plan use, and why?", "options": ["20×, to grow faster", "1×, because that's the highest level tested setups survived", "5×, a compromise", "No limit"], "answer": 1, "why": "Every tested rule liquidated from 2×; 1× was the highest safe level."}
]
},
{
"id": "m10-l03", "title": "A 30-day practice schedule",
"body_md": r"""
# A 30-day practice schedule

Knowledge becomes skill through repetition. This schedule turns the course into 30 days of practice — about 30–60 minutes a day — using the OMEGA app and paper trading. No real money is required.

## Week 1 — Mechanics and mark-ups (days 1–7)

| Day | Task | OMEGA page |
|---|---|---|
| 1 | Write version 1 of your plan (sections 1–3, 5) | Risk Guard |
| 2 | Fee, funding and liquidation calculations for 3 positions at 100 USDT | Futures calculator, Position desk |
| 3 | Lot and pip sizing for gold and one forex pair at your account size | Analysis, Futures calculator |
| 4 | Full mark-up for 2 markets using the checklist | Analysis, Market Read |
| 5 | Mark-up again; compare yesterday's scenarios with what happened | Analysis, Journal |
| 6 | Sessions and calendar: convert this week's events to T&T time | — |
| 7 | **Weekly review #1** (process only — you've made no trades yet) | Journal |

## Week 2 — Paper trading with full risk rules (days 8–14)

| Day | Task | OMEGA page |
|---|---|---|
| 8 | Pre-market checklist + up to 2 paper trades, sized at 0.5% | Futures (paper), Journal |
| 9 | Same; record "setups not taken" too | Journal |
| 10 | Same; practise placing stop and exit orders at entry | Futures |
| 11 | Same; note emotion at entry for every trade | Journal |
| 12 | Same; compute R for each trade so far | Growth |
| 13 | Observe OMEGA Signals and CREED; log observed setups and outcomes | Signals, CREED |
| 14 | **Weekly review #2**: process score, rule breaks, one change | Journal, Growth |

Rules for week 2: maximum 2 trades a day, 0.5% risk, Risk Guard limits apply even on paper. If you hit the daily stop on paper, stop — you're practising the habit.

## Week 3 — Testing an idea (days 15–21)

| Day | Task | OMEGA page |
|---|---|---|
| 15 | Write a full test plan for one idea (Module 7 template); fingerprint it | — |
| 16 | Discovery: record every occurrence in the discovery period | Analysis |
| 17 | Luck check: same number of random entries | — |
| 18 | Validation: run once, record | — |
| 19 | Final: run once, record; write verdict with caveats | — |
| 20 | Compare two tests' discovery vs final results on the progress board | omega-board.onrender.com |
| 21 | **Weekly review #3** + continue daily paper trades (max 1 a day this week) | Journal |

## Week 4 — Routine, automation and the plan (days 22–30)

| Day | Task | OMEGA page |
|---|---|---|
| 22 | Full routine: checklist → window → journal → 10-minute review | Command |
| 23 | Same, plus news rule practice around a scheduled event | — |
| 24 | Start (or review) a paper bot on a tested rule; find the kill switch | Bots, Autopilot |
| 25 | Routine + paper trades | — |
| 26 | Write your tilt plan and stop-trading list | — |
| 27 | Routine + paper trades | — |
| 28 | Monthly check: expectancy (with how many trades), drawdown, process score | Growth, Journal |
| 29 | Rewrite your plan as version 2 using everything you learned | — |
| 30 | **Capstone** (next lesson) | — |

## What "done" looks like after 30 days

- A written, dated trading plan (version 2).
- 20–40 paper trades logged with full fields, plus observed setups.
- One complete test of an idea, with an honest verdict.
- Four weekly reviews and one monthly check.
- A process score — for example "checklist used 26 of 30 days; 2 rule breaks".

You will **not** know whether you have an edge after 30 days. Nobody can, from 20–40 trades (Module 5: the uncertainty is too large). That's not the goal. The goal is a **process you can repeat** for the next 100–300 trades, at minimum risk, while the evidence builds.

## After the 30 days

- **Continue paper** until you have at least 50–100 trades of a setup with a positive label.
- **Move up the ladder** (paper → testnet → tiny live) only for setups with evidence.
- **Keep risk at the Risk Guard defaults or lower** for at least your first 100 live trades.
- **Re-read Modules 5 and 8** monthly. They're the ones people forget first.

## Exercise

1. Put the 30 days in your calendar with times.
2. Decide what you'll do on days you miss (catch up next day — don't double up).
3. Start Day 1 today.
""",
"key_points": [
 "Week 1: mechanics and mark-ups; Week 2: paper trading with full risk rules; Week 3: test an idea; Week 4: routine, automation, plan v2.",
 "Apply Risk Guard limits even on paper — you're practising the habit.",
 "After 30 days you'll have a plan, 20–40 logged paper trades, one full test and four reviews.",
 "You won't know if you have an edge after 30 days; the goal is a repeatable process.",
 "Move up the ladder only for setups with evidence, at minimum risk."
],
"quiz": [
 {"q": "What is the main focus of week 3?", "options": ["Live trading with leverage", "Testing one idea from plan to final verdict", "Buying a bot", "Skipping reviews"], "answer": 1, "why": "Week 3 applies Module 7 end to end."},
 {"q": "Why apply the daily stop even on paper?", "options": ["Paper accounts can be liquidated", "You're practising the habit you'll need with real money", "The app forces it", "No reason"], "answer": 1, "why": "Habits built on paper carry over to live trading."},
 {"q": "After 30 days and 30 paper trades, what can you conclude about your edge?", "options": ["It's proven", "Not much — the sample is far too small", "It's definitely negative", "Use 20× now"], "answer": 1, "why": "With 20–40 trades, uncertainty is too large to judge an edge."},
 {"q": "What should you do after the 30 days?", "options": ["Go live at full size", "Continue paper to 50–100 trades, then climb the ladder only for setups with evidence", "Stop journaling", "Switch strategies weekly"], "answer": 1, "why": "Evidence builds slowly; risk stays minimal while it does."}
]
},
{
"id": "m10-l04", "title": "Capstone: test, practise, review — and what comes next",
"body_md": r"""
# Capstone

The capstone brings the whole course together in one project. When you finish it, you'll have done everything a careful trader does — on one idea, end to end, without risking money.

## The capstone brief

Choose **one** idea. It can be:

- an indicator rule you believed in before the course,
- a structure-based setup (for example a CREED-style pullback on one market),
- a session or volatility idea,
- or one of the passed setups observed through OMEGA Signals.

Then complete the six parts below and write a short report (1–2 pages).

### Part 1 — The plan (before any data)
Use the Module 7 template: hypothesis with a reason, exact entry and exit, costs, variants (and their number), periods, pass mark, luck check. Date it and save it before you look at results.

### Part 2 — The test
Run discovery, the luck check, validation (once) and final (once). Use a manual chart test or a spreadsheet. Log every variant. Report results after costs, in R or %, with trade counts. Include results **without the best 5%** if you have enough trades, and the **worst single trade**.

### Part 3 — The verdict
PASS, FAIL or NOT ENOUGH TRADES — with at least two caveats. Label the setup (tested-pass, watch, untested, failed).

### Part 4 — Risk design
For your account size, write: risk per trade, position size for a typical stop (with the calculation), maximum leverage (and why — check the liquidation distance), daily/weekly stops, and what a normal losing streak would cost.

### Part 5 — Practice
Paper trade or observe the setup for at least **20 occurrences** (more if it's frequent), following your plan exactly. Log everything in the Journal: trades and setups not taken, emotion at entry, followed plan Y/N.

### Part 6 — Review
Compare your practice results with the test. Classify every loss (good loss / execution error / rule break / bad plan). Compute your process score. Decide: continue paper, move up the ladder, change one thing and re-test, or retire the idea.

## Report template

```
CAPSTONE REPORT                       Name ____  Date ____
Idea:
Plan written on:          Variants tried:
Discovery:   n __  mean __  t __    Random entries: mean __
Validation:  n __  mean __  t __
Final:       n __  mean __  t __    Without best 5%: __   Worst trade: __
Verdict + label:
Caveats (2+):
Risk design (size calc, leverage, limits):
Practice: n __  average R __  followed plan __/__  rule breaks __
Loss classification:
Decision and next step:
What I learned (3 lines):
```

## How to judge your own capstone

A **good** capstone is not one where the idea passed. Most ideas fail — in OMEGA's research, almost all did. A good capstone is one where:

- the plan was written before the data,
- every attempt was counted,
- costs were included,
- the verdict follows from the numbers,
- the risk design would survive a bad streak,
- the practice followed the plan, and
- the decision is honest.

A clean FAIL with good process is an excellent result. It just saved you real money.

## What you now know

Look back at where you started. You can now:

- explain spot, perps and CFDs, and calculate fees, funding, margin and liquidation at small account sizes;
- read a chart's structure, levels, volume and sessions without fooling yourself;
- use indicators as measuring tools, and explain why most indicator rules don't pay costs while volatility is predictable;
- size any trade, measure results in R, and design daily, weekly and review limits;
- explain exactly why 20× and 40× liquidated even the setups that passed;
- describe the climax reversal and panic bounce precisely — and why they're fading;
- use CREED as a discipline framework while knowing its measured coin-flip result;
- write and run a fair test with a luck check, and avoid the classic traps;
- run a daily routine, a journal and weekly reviews, and handle tilt and FOMO;
- climb the paper → testnet → live ladder with guards and a kill switch, and read a forward record.

## What comes next

1. **Keep the process going** for your next 100–300 trades, at minimum risk.
2. **Review monthly** against your plan and your retirement rules.
3. **Re-test** when markets change; edges fade.
4. **Stay sceptical** — of courses, signals, bots and your own best ideas. Including this course: check its claims against your own records.
5. **Course updates** will add new research results as OMEGA's forward records grow, including the forward-scored scouts and signals.

## A final word on risk

Trading can lose money quickly, and nothing in this course promises profit. If you trade, trade small, unleveraged, with money you can afford to lose, and only with methods that survived a fair test. The traders who last are not the ones with the best predictions; they are the ones who manage risk, test before they trust, and keep showing up with a plan.

## Exercise

Complete the capstone and fill in the report template. Save it with your trading plan. In three months, read both again — and write version 3 of your plan.
""",
"key_points": [
 "The capstone takes one idea through plan, test, verdict, risk design, practice and review.",
 "A clean FAIL with good process is an excellent result — it saved you real money.",
 "Judge the capstone by process: plan first, every attempt counted, costs included, honest decision.",
 "Keep going for 100–300 trades at minimum risk, review monthly, and re-test as markets change.",
 "Stay sceptical of everything — courses, signals, bots and your own best ideas."
],
"quiz": [
 {"q": "What makes a capstone 'good'?", "options": ["The idea passed", "The process was honest: plan first, attempts counted, costs included, verdict follows the numbers", "It used high leverage", "It had a high win rate"], "answer": 1, "why": "Most ideas fail; the quality of the process is what you control."},
 {"q": "What is the minimum practice requirement in Part 5?", "options": ["1 trade", "At least 20 occurrences, following the plan exactly", "1,000 live trades", "None"], "answer": 1, "why": "Twenty occurrences give a first look at execution and behaviour."},
 {"q": "Your idea fails the final test with good process. What does that mean?", "options": ["The capstone failed", "An excellent result: you avoided losing real money", "Retest until it passes", "Add leverage"], "answer": 1, "why": "Avoiding a bad strategy is a real gain."},
 {"q": "Which statement reflects the course's final word on risk?", "options": ["Profits are guaranteed if you follow the course", "Trade small, unleveraged, with money you can afford to lose, using methods that survived a fair test", "Use the maximum leverage your broker offers", "Risk doesn't matter with a good plan"], "answer": 1, "why": "No profit is promised; risk management and testing come first."}
]
}
]}
