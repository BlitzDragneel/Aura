# OMEGA v6.5.83 — the Breakout Desk (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.83 · build 2026-10-20 03:02 UTC. Made with `python3 patch83.py <v6.5.82 build> <new build>`.
Nothing existing was changed apart from one test's heading pattern (s82 now accepts "rounds 1–18" or "1–19").

## What was added
**A new page, Breakout Desk** (menu: under OMEGA Signals). Two candidates from the outside study of 19–20 Oct 2026 run as
paper accounts. **They are not an edge**: they are judged only on weeks after 20 Oct 2026 03:00 UTC.

| | Setup A: 72-hour breakout | Setup B: momentum burst |
|---|---|---|
| When | hours opening 13:00–20:00 UTC (09:00–16:00 Tobago) | same |
| Signal | close above the 72-hour high (below the low: short) on ≥ 2× the 168-hour median volume | hourly move ≥ 3σ (σ of the 168 hours before) on ≥ 3× volume, closing in the top 40% of the hour (down 3σ, bottom 40%: short) |
| Entry | next hour's open | next hour's open |
| Stop | 2 × ATR(14, hourly) | 2 × ATR |
| Management | 5 units. At +1R close 3, stop to entry, add 1. Add 1 at +2R and +3R (stop to the last add − 1R). Trail 3 ATR from the best price. Out after 168 h | 1 unit. Add 1 at each +1R (up to 3; stop to the last add − 1R). Trail 3 ATR. Out after 168 h |
| Which coin | the strongest signal (highest volume ratio), one market at a time | the strongest (largest move in σ) |
| Universe | Binance USDT coin perpetuals listed ≥ 820 h, average daily volume (480 h) ≥ $5M | same |

- **Paper account per setup:** 100 USDT, 1% risk, one market at a time. Binance's rules apply: 5 USDT minimum order, a 20× cap, liquidation only on a gap past both stop and margin. Costs are 0.10% a side, and funding is read from Binance for every hour held.
- **On the page:**
  - a "Start here" panel saying what to do now;
  - an hourly candle chart of the signal coin with the plan drawn on it: entry, stop, +1R (bank 3, add 1), +2R and +3R adds, the 72-hour line, the live stop, and shaded risk and reward zones;
  - an order table for any account size and risk, which warns when the 5 USDT minimum forces more risk than chosen;
  - the paper account's balance, trades and equity line;
  - what the research found, and why it is not an edge.
- **Elsewhere in the app:** a line on OMEGA Signals, a command-palette entry, and a menu badge when a signal is waiting.
- **Data:** it reads the hourly bars the climax watch already stores (`omega_climax`), so there is no second download. When those bars are stale it asks the climax watch to update. Its own state lives in IndexedDB `omega_bdesk`.
- **Judging (fixed now):**
  - nothing is judged before 26 weeks;
  - confirmed at weekly z ≥ 1.96;
  - retired if the weeks average ≤ 0, or on a fall of 46% (A) or 56% (B) from the peak.
  - Those limits are 1.5× the worst research falls (31%, 37%). The Edge Lab's 15% rule would have retired both during the research, so it is not used.
- **Research record:** round 19 (the outside study, including the CREED result below).

## Evidence carried on the page
- **Unseen half (Jul 2025 – Oct 2026), 100 USDT, 1% risk:**
  - A ends at 180.5 (623 trades, worst fall 31%);
  - B ends at 144.3 (403 trades, worst fall 37%).
- **Coin-flip direction test:** A beat 96% of 100 accounts; B beat 91%.
- **Not proven:** each was the best of 10 setup-and-method pairs, so luck explains a result that good about 1 time in 3.
- **Risk:** more risk lost money (A: 1% → 180, 2% → 142, 5% → 75, 10% → 15).
- **From 10 USDT:** the 5 USDT minimum forces about 10% risk, and half the 6-month starts went to zero.

## CREED (studied, not changed)
CREED's own engine was replayed on 20 coins (4,696 on-time setups). Same-setup results:

| Exit | 2020-01 → 2023-09 | 2023-10 → 2026-10 |
|---|---|---|
| As taught | −0.006R (t −0.08) | −0.106R (t −2.08) |
| 5-unit method | −0.049R, 47% winners | −0.120R, 44% winners (t −3.57) |
| Pyramid | +0.004R | −0.110R |
| Trailing 3 ATR | −0.007R | −0.123R |

None is positive in both periods, so CREED is unchanged.

## Verification
- **Parity with the research:** on 40 perpetuals (Jul–Sep 2025), the app's code takes the same 99 (A) and 60 (B) trades as the research simulator `edge/live.py`. Coin, hour, exit and R match within 1e-9, and the final balance to the cent. This holds for a one-pass replay and for hour-by-hour checks at random 1–30 hour gaps, with funding requested from the (stubbed) exchange.
- **No look-ahead:** changing every bar after an hour leaves every earlier trade unchanged.
- **Browser test:** a fake exchange serves a coin that breaks out at 17:00 UTC. Both paper accounts enter at the 18:00 open, and the chart shows all levels. There is no NaN, no sideways overflow and no page error.
- **All 17 suites pass:** s49, s50, s58, s60, s62, s67, s69, s70, s71, s73, s77, s78, s79, s80, s81, s82, s83.
- **Other checks:** `node --check` passes on all 105 script blocks; there are no duplicate ids; the phone guard is clean; the 25-page crawl, offline and with the fake exchange, shows 0 page errors and 0 console errors.
- **Not run on a real phone.**

## Files (build kit)
- **New:** `bdesk.js`, `patch83.py`, `s83_test.js`, `fixtures/bdesk40.json`, `creed83.js` (CREED replay with the extra exits).
- **Updated:** `tools/crawl.js` (25 pages), `s82_test.js`.
- **Note:** `s70_test.js` loads `/home/claude/fake_idb.js`, so copy `tools/fake_idb.js` there before running it.
