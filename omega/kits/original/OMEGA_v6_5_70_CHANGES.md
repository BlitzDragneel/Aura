# OMEGA v6.5.70: Edge Lab, OMEGA looks for untested edges by itself

Built from v6.5.69 by patch70.py. Delivered as omega-v6_5-47.html. Plan: PLAN13.md, including addendum A (your
direction: build in what is known, search only what is not).

## What it does
- **New page: Edge Lab** (sidebar, under Positioning Desk).
- **Built-in knowledge.** The app holds every rule research has tested, with its results at each stage and its verdict,
  plus the lessons. It never tests any of them again. It covers:
  - 630 round-12 rules and regime variants;
  - 105 combinations;
  - rounds 1–11, the outside study and the other assistants' tests.

  You can search it, for example "RSI" or "carry", to see what was tried and what happened.
- **Coin data.** Daily bars and funding for 291 coins: the 25 studied, 51 fresh, 90 new, and 125 untouched coins with a
  perpetual.
  - Downloaded on your phone from Binance and kept in its own store.
  - The Autopilot fills it once (about 15–25 minutes with the app open) and tops it up every few hours.
- **Explorer, on untested ground only.**
  - **Tier 1, 2,910 candidates:** 38 representative rules × 18 market and coin conditions × 5 exits.
  - **New families from the lessons:**
    - harvest guards: close a pair on negative daily funding, coins over a year old only, liquid coins only, skip coins
      paying over 1% a week;
    - coin age across coins;
    - funding against price.
  - **Tier 2, about 2,100 more:** two conditions at once. It opens after tier 1.
- **Discipline, unchanged from research.**
  - **Screen:** on half the coins (A).
  - **Check:** once, on the other half (B). The pass mark rises with every survivor, so luck doesn't get through.
  - **Shadow book:** survivors are tracked forward week by week on all coins.
  - **EDGE:** only after at least 8 forward weeks clear the bar over the whole book. An EDGE shows its positions as
    orders for you to place; OMEGA places none.
  - **Retirement:** after 26 flat weeks or a 15% fall.
- **The research winners are in the book from day one,** tracked forward on all 291 coins: the 10-pair harvest and
  the two round-12 blends. That gives about 10 times more forward evidence per week than the 25 coins alone.
- **Coin by coin.** Each coin's best rule over the last 365 days, with the app's own measure of whether such picks
  persist. It's shown as information, not as an edge, because research found they don't persist.

## Checks
- **s70 (19/19).**
  - The app's engine reproduces the research code on the 25 studied coins for all 40 rules. Funding uses exact sums,
    because rates have 8 decimals, and coins that tie are ordered by name. In research, float noise and arbitrary tie
    order moved 5 of them slightly; a research rerun with exact sums matches the app exactly.
  - **No look-ahead:** for 52 rules, conditions and exits, changing every price and funding payment after a day leaves
    all positions up to that day identical.
  - Conditions and exits behave as specified.
  - The explorer proposes nothing already in the knowledge, and no duplicates.
  - **Protocol, on synthetic coins:** a planted real edge passes both halves and enters the book, and noise doesn't.
    Promotion needs 8+ weeks, a 15% fall retires, and retirement is permanent.
  - The data store merges updates without double-counting funding.
- **Speed:** a full tier-1 pass takes about 1–2 minutes on a computer, so roughly 5–10 minutes of a phone's time,
  spread over Autopilot runs.
- **Regression tests:** s69 21/21, s67 15/15, s62 7/7, s60 9/9, s58 9/9, s50 5/5, s49 11/11. s58's page-list check
  now includes "edgelab", on purpose.
- **Phone-number guard:** clean. No keys in the file.
- **s70 store checks (21/21 in all):**
  - A bug found by the first browser test is fixed and now covered. Reading a coin not yet stored returned the request
    object instead of nothing, so every save failed silently.
  - The store is tested end to end on an IndexedDB stand-in.
- **Null test:** the whole tier-1 pass on 290 coins of realistic random noise, 8 different datasets. 1–6% passed the
  screen on half A, as chance allows, and **none passed the check on half B in any run**. Luck does not reach the
  shadow book.
- **Browser test with a fake Binance:**
  - 291 coins downloaded and saved in about 3 minutes;
  - tier 1 explored (2,910 candidates screened and checked) in about 2 minutes;
  - the page renders at phone width with no sideways scroll;
  - the store and the lab's state survive a reload;
  - no page errors.

  The fake prices are smooth waves, which really are predictable, so many rules entered the book there. That was used
  to check the page: Edges and research winners are always listed, then the 25 strongest shadow entries, and the rest
  sit under "show all".
- **Memory:** per-coin conditions are kept as bytes, and the store's raw records are released once the lab has built
  its own arrays.

## Not changed
CREED, the three desk markets, the existing strategies and their forward records, and the Brain's method. Everything
stays paper only.
