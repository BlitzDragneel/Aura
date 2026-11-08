# Edge Hunter backlog (top = next). Tick with the verdict when done; add new ideas below.
Working branch: claude/trading-edge-research-bots-gpkvi1
Owner's priority (8 Nov): a DAY strategy, anything that is genuinely positive after costs, even small.

## Done
- [x] Volatility-managed holding — E84 FAIL (benefit = holding less, not timing)
- [x] US index overnight drift — E83 FAIL after CFD costs (real gross +5 bp/night; ETF at a zero-commission broker +7.7%/yr, t 1.45)

## Next (day-trading ideas, untested)
- [ ] **Maker-only versions of the fast near-misses**: the 15m scouts and 5m/15m panic bounce lost mainly to costs. Re-test
      with limit entries AND limit exits (maker 0.02% both sides, fill only when price trades through). New plan, new periods
      rule: discovery 2022–23, validation 2024, final 2025–26 — the final was seen before for the taker versions, so say so
      and require t ≥ 2.5.
- [ ] **Deribit options expiry (Fridays 08:00 UTC)**: does BTC/ETH drift toward max-pain / pin around weekly and monthly
      expiries? Deribit public trades/instruments give open interest by strike.
- [ ] **CME-hours weekend gap (BTC)**: Friday 21:00 → Sunday 22:00 UTC gap on Binance as a CME proxy; does the gap fill on
      Monday? (Gold's weekend gap fade failed in E3; crypto trades all weekend, so this is different.)
- [ ] **Asian-session range → London breakout** on ETH/SOL 15m (both directions, ATR stop), costs at maker entry.
- [ ] **Panic bounce + scout filter**: take H1 fills only when UpScout's probability is in its top 20%.
- [ ] **Volatility breakout both ways** when the scouts' big-move probability is high (straddle-like with perps).
- [ ] **Cross-exchange funding divergence** Binance vs OKX on the same coin.
- [ ] **Gold and forex day ranges** with Twelve Data history (needs the owner's key as a secret; skip if absent).
- [ ] **Forward verdicts**: paper bot after 50 closed tickets per rule (incl. the watch-list rules added 8 Nov); scouts after
      500 scored calls (bot-state branch). These outrank new ideas once due.
