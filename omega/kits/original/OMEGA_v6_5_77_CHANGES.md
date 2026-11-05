# OMEGA v6.5.77 — Market Watch, the recorder (19 Oct 2026)

Built from v6.5.76 by `patch77.py`. Delivered as `omega-v6_5-47.html`. Plan: `research/PLAN16_DRAFT.md`.

## New page: Market Watch (sidebar, under Edge Lab)
Press **Start recording**. From then on it records whenever OMEGA is open, and it resumes by itself after a reload.

**What it records for each watched coin** (default: the 25 studied coins; up to 60):
- **Aggressive buying and selling,** in USDT per minute, on spot and on the perpetual. These are orders that cross
  the spread, so they show who is in a hurry.
- **Large orders:** one taker order of at least 0.02% of the coin's 24-hour volume (minimum 10,000 USDT). An order
  filled at several prices counts once. The largest buy and sell each minute are also kept.
- **Visible spot order book,** every second: bids against asks in the top 20 levels, and the spread.
- **Perpetual:** mark and index price, premium and funding rate, every second.
- **Liquidations** on every Binance perpetual. This is Binance's live sample: at most one per coin per second.
- **Coinbase BTC, ETH and USDT prices,** which give the Coinbase premium (US buyers).
- **Every 15 minutes:** 5-minute open interest, long/short account ratio, top-trader position ratio and taker
  buy/sell ratio. Binance keeps 30 days of this, so gaps while the app was closed fill in.
- **Liquidity map** (every 15 minutes by default, 500 levels):
  - USDT within 0.5%, 1%, 2% and 5% of the price on each side;
  - the three largest walls on each side;
  - how far the book reaches.

**Flight recordings.** A coin moving 4 or more of its own 1-minute standard deviations in 60 seconds, or 10M USDT
liquidated across the market in 60 seconds, opens a recording:
- the 30 minutes before and the 60 minutes after, second by second;
- what was happening (15-minute flows, large orders, liquidations, open interest, BTC at the same moment, session,
  funding hour, weekend);
- what came next (5, 15 and 60 minutes, and the range).

Up to 150 recordings are kept.

**What's moving it now:**
- a table of the last 15 minutes per coin;
- a factual read of the top three movers, for example "futures led; longs liquidated $1.1M; open interest −3% in
  the hour (positions closing); bids 28% heavier than asks";
- the market's liquidations and the Coinbase premium.

**Export for research** covers 1, 3 or 7 days. The file is `omega-watch-….json.gz`, read by `research/watch16.py`.
It contains no keys.

**Modes:**
- Full: every trade. It can use a few GB a day on busy days, so Wi-Fi is best.
- Light: 1-minute totals, much less data, but no large-order detail.

The page keeps the screen on while recording (setting), and minutes are stored for 14 days.

## Fixed: liquidations had stopped arriving
Binance moved its futures streams in 2026. Trades, mark price and liquidations are now on `/market`, and the old
`/ws` and `/stream` addresses ended on 23 Apr 2026.
- The Positioning collector's liquidation feed now uses the new address (`wss://fstream.binance.com/market/ws/!forceOrder@arr`).
- It says "live" only once data actually arrives. Until now it most likely recorded nothing after April.

## Honest limits
- **It records only while the app is open and on screen.** Phones pause background pages, and those minutes stay
  empty (never filled in). For 24/7, leave it open on a computer that doesn't sleep.
- **No order-book history exists for free,** so that record starts now.
- **Liquidations are a sample.**
- **This is description, not a signal.** Nothing here trades or votes.
- **The new Binance address has not been verified against the live exchange.** It follows Binance's published change
  notice. The page shows "connected but no data" if the address is wrong.

## Checks
- **s77 (27/27):**
  - minute totals;
  - one order filled at two prices counted once;
  - the large-order rule;
  - premium averaged;
  - the book;
  - liquidations (coin and market);
  - Coinbase;
  - per-second rows;
  - a sudden fall opens a recording, but not on a throttled tab;
  - outcomes at 5, 15 and 60 minutes;
  - compact storage;
  - light mode;
  - liquidity map;
  - time tags;
  - the plain read;
  - export decoded by `watch16.py` exactly;
  - stream addresses;
  - Coinbase subscribe;
  - the "no data" warning;
  - the page;
  - the liquidation fix.
- **Earlier suites:**
  - s49 11/11, s50 5/5, s58 9/9 (now allows the new page), s60 9/9, s62 7/7, s67 15/15;
  - s69 21/21, s70 21/21, s71 16/16, s72 11/11, s73 7/7.
- **Static checks:** 109 script blocks pass `node --check`; phone guard clean.
- **Chromium at 412 px with Binance and Coinbase mocked** (WebSocket and REST). Everything below worked:
  - all three feeds went live;
  - the table and the read filled after a minute;
  - positioning history filled (297 five-minute rows a day);
  - the liquidity map found the planted walls;
  - the export decoded in Python;
  - after a reload it resumed by itself;
  - no page errors and no sideways scroll.
- Not run on a real phone or against the live exchanges.
