# OMEGA v6.5.93 — the Market Cockpit on the Analysis page (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.93 · build 2026-10-22 09:59 UTC. Made with `python3 patch93.py <v6.5.92 build> <new build>` (uses `cockpit.js`).

## New: Market Cockpit (Analysis page, under Market now and Today's plan; module `OMEGA_COCKPIT`)
One clean chart per coin: the eleven Market Read markets, 1 hour (3 days) or 15 minutes (18 hours), Binance USD-M public data.
- **Candles,** with US hours shaded (the busiest, most volatile session).
- **Volume** under the candles, each bar split into aggressive buying (green) and selling (red) from the candle's taker-buy share.
- **Market Read's liquidity levels:** dashed red above (buy stops), dashed green below (sell stops). Labels on the price axis are kept at least 9.5 units apart, with leader lines where moved.
- **The order book** in its own column at the right: resting bids and asks by price band, so it never covers the candles.
- **The Daily Plan's setup** as a position box over the last 14 candles: gold entry line, red stop zone, green target zone, labelled on the axis.
- **A strip of ten figures:** price, 24 h change, range against a typical day, hourly range, funding, open-interest change, long/short, crowding, aggressive buying over 24 h, and the book within 1%.
- **One setup card:** side, reward-to-risk, grade C, entry, stop and target with the levels they come from, and a pointer to size it on the Risk Guard (0.5%).
- **Autopilot job `cockpit`** refreshes the selected coin hourly.

## Fixed during the build
- **The cockpit didn't draw on the Analysis page.** The navigation hook only runs for extra pages, and Analysis is a core page. The cockpit now watches for the page itself, and also loads an unread Daily Plan.
- **The setup card lagged behind the Daily Plan.** The cockpit now redraws whenever the Daily Plan updates.
- **The plan zones were too thin to see;** they now span the last 14 candles.

## Verification
- **s93 (6 checks):**
  - labels apart and inside the chart;
  - book bands summed correctly;
  - volume split by the taker-buy share;
  - 72 candles and volume bars, 4 levels, the plan's 3 zones (none without a plan), the book, no NaN;
  - the cockpit's zones and setup card match the Daily Plan for the coin;
  - a browser run on the Analysis page: strip, chart, labels apart, the 15-minute view, the Autopilot refresh; no NaN, no overflow, no page errors.
- **All 27 suites pass** (s49…s93).
- **Other checks:** 113 script blocks pass the syntax check; no duplicate ids; phone guard clean; 28-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.**
