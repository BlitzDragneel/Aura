# OMEGA v6.5.92 — Risk Guard and Growth Bot (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.92 · build 2026-10-22 09:33 UTC. Made with `python3 patch92.py <v6.5.91 build> <new build>` (uses `rguard.js`).

## New page: Risk Guard (menu above Market Read; module `OMEGA_RGUARD`)
**The rules, the same for the bot and for real trades:**
- 0.5% of equity at risk per trade (1% after 30 trades without a rule break);
- at most 2 open;
- no new trades after −2% in a UTC day or −5% in a week;
- a pause for review at 20% below the peak.

**Growth Bot (plan E17, md5 `27f13c9a…`):** a 100 USDT paper account, forward only.
- **What it takes:** every new climax-watch trade (grade A) and every new Daily Plan paper trade (grade C) within the rules. It is not frightened: every valid signal inside the limits is taken.
- **Sizing:**
  - climax trades: notional = risk ÷ 10% (they have no stop);
  - Daily Plan trades: risk ÷ the stop distance;
  - Binance's 5 USDT minimum is respected, and skips are recorded with the reason.
- **It only reads the signals' records:** the test confirms they are byte-for-byte unchanged.
- **On the page:** the equity curve, the result split by grade A and grade C, the weekly t, open trades, the limits and skips.
- **Judged once** after 26 weeks or 50 trades.

**Before a real trade:**
- A pre-trade check on coin, side, entry, stop and size. It says whether the trade fits the rules and gives the largest allowed size.
- **Log the trade** opens it in a journal; **Close** asks for the exit price and books the result after 0.08% fees.
- Rule breaks are counted and their result shown separately.
- **Set balance** sets your real account size.

**Research exports (automatic):** after every 3 new full Market Watch days the 7-day export is saved; when the metals and forex download completes, that file is saved. A notification is sent each time, and one-tap Save buttons cover browsers that ask for a tap.

## Autopilot
- **`rguard`** (Watching lane, every 15 min): the Growth Bot.
- **`autoexp`** (Downloads & research lane, every 2 h): the automatic exports.

## Brain
- **A Mind lesson in the spirit of Sharran Srivatsaa's teaching on risk:** risk is what makes money; managing it decides whether it does.
- `KN.earlier` gains E17. Research record round 31.

## Verification
- **s92 (6 checks):**
  - every rule blocks new trades and risk steps up after 30 clean trades;
  - the bot is forward only, sizes 5 and 50 USDT correctly, refuses a third trade while 2 are open, books +0.10 and +1.00 to 101.10, and leaves the signal records unchanged;
  - the pre-trade check refuses 2% risk with the right size (25 USDT), accepts a trade inside the rule and warns under 5 USDT; the journal books +0.48 after fees;
  - each automatic export happens exactly once;
  - a browser run: the page, the form keeping its values, the curve, the Autopilot running the bot; no NaN, no overflow, no page errors.
- **Fixed during the build:** the review pause missed exactly 20% because of floating point (now with a tolerance); the check form lost its values after Check it (now kept).
- **All 26 suites pass** (s49…s92).
- **Other checks:** 112 script blocks pass the syntax check; no duplicate ids; phone guard clean; 28-page crawl offline and with a fake exchange shows 0 page errors and 0 console errors.
- **Not run on a real phone.**
