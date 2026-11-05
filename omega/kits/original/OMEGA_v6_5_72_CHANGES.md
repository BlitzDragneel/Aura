# OMEGA v6.5.72: the capitulation watch

Built from v6.5.71 by patch72.py. Delivered as omega-v6_5-47.html. Everything in v6.5.71 is included (honest CREED
numbers, the CREED Backtest entry setting, the two research downloads).

## New: Capitulation watch (top of the Edge Lab page)
- **What it watches.** Round 14's candidate rule, live on the perpetuals of all 291 research coins.
  - **The signal:** a coin falls 5 or more of its own hourly standard deviations in one hour, while its perpetual's
    premium is at or below its 5th percentile of the last 30 days (forced selling).
  - **The trade:** buy the perpetual at the next hour's open, close it 12 hours later. 5% of the account a trade, at
    most 20 at once, deepest falls first.
- **When it checks.** About one minute after every hour closes, while the app is open, with one request per coin. The
  first check fills 950 hours per coin, which takes under a minute or two.
- **When a coin fires.** The card shows **BUY NOW** with the coin, the size and the close time. It also sends a
  notification if you turn alerts on, and your webhook if one is set in Settings.
- **Speed is shown on the card.** In research, entering 1 hour late kept about 60% of the edge, 2 hours about 40%, and
  4 hours none.
- **Every signal is recorded on paper from 19 Oct 2026.**
  - It counts signals seen late, too: they are rebuilt from the bars when the app reopens.
  - Each trade closes with funding and costs.
  - Every week is judged against the market of the watched coins: alpha and z, as in the Edge Lab's shadow book.
- **Status:** "CANDIDATE — final test pending" until the final-test files you download are run. After that it reads
  EDGE or FAILED.
- **Limit.** The app can only watch while it is open. Catching every hour would need a server.

## Checks
- **s72 (10/10).**
  - **Matches research trade for trade:** the watch takes the same 42 trades as the research engine on the 25 studied
    coins' last 3,000 hours, with the same hour, coin, depth of fall and return after funding.
  - **No look-ahead:** changing every price after an hour changes no earlier decision.
  - **Book limits:** never more than 20 trades, and never one coin twice at once.
  - **Live behaviour:** a fresh signal waits for its entry price, and open trades are marked at the latest close.
  - **Forward record:** weeks end on Sunday (UTC); only decisions after the freeze count; the hourly P&L adds up to the
    trades.
- **Real Chromium with Binance mocked:** 291 perpetuals checked in 38 s.
  - A planted crash (−8.7σ with the premium at −0.38%) fired and showed BUY NOW.
  - A second check found nothing new in under a second.
  - The record survived a reload.
  - No page errors, no sideways scroll at phone width.
- **All earlier suites:** s71 16/16, s70 21/21, s69 21/21, s67 15/15, s62 7/7, s60 9/9, s58 9/9, s50 5/5, s49 11/11.
  All 106 scripts pass a syntax check. Phone guard clean.
- Not run on a real phone.
