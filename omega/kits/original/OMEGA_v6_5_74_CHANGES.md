# OMEGA v6.5.74: round 14's final tests recorded

Built from v6.5.73 by patch74.py. Delivered as omega-v6_5-47.html.

## What changed
- **Capitulation watch (Edge Lab): FAILED.** The rule failed its final test (run once, 19 Oct 2026) on 324 coins
  nothing had touched: the 125 untouched coins with a perpetual and 199 perpetuals listed since April 2025.

  | Measure | Result |
  | --- | --- |
  | Return over the market | −1.5% a year |
  | z | −0.27 (needed 1.645) |
  | With costs doubled | −4.5% a year |
  | 2025 | −27% |
  | Worst fall | −47% |

  - The card shows this.
  - The watch is **off by default**. Switched on, it only records what fires: no BUY NOW and no alerts.
- **Research record and built-in knowledge.** Round 14's final result is recorded, so OMEGA never tests these again:
  - the capitulation rule's final test;
  - another assistant's Asian-session dip, which failed (z 0.56 week by week; −17.7% a year with costs doubled);
  - CREED re-run with its own code on 15-minute data (3,268 on-time setups). Every entry version (longs only,
    capitulation sweeps, perpetual at a discount, shorts only) and every exit (no breakeven, breakeven at 2R, targets
    at 2R and 1.5R) lost after costs.
- **Unchanged:**
  - the model across coins in the shadow book;
  - the harvest and the two round-12 blends;
  - CREED itself (its 1R breakeven stays, since removing it was not a proven improvement: +0.044R, t 1.15).

## Checks
- **s72 (11/11):** now checks the FAILED status, the watch off by default, and no alerts.
- **Earlier suites:** s73 7/7, s71 16/16, s70 21/21, s69 21/21, s67 15/15, s62 7/7, s60 9/9, s58 9/9, s50 5/5,
  s49 11/11.
- All 107 scripts pass a syntax check. Phone guard clean.
- **Real Chromium:**
  - with the watch off, nothing was fetched in 50 seconds;
  - a forced check still recorded a planted crash and showed "FIRED (recorded only)".
- Not run on a real phone.
