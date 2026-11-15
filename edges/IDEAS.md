# Edge Hunter backlog (top = next). Tick with the verdict when done; add new ideas below.
Working branch: claude/trading-edge-research-bots-gpkvi1
Owner's priority (15 Nov): DIRECTION signals on gold, silver, BTC (+ NAS100, US30, the lab's coins) that beat
Profit4Life; alerts when moves happen. Done since 13 Nov: E140–E153 (all FAIL except timing: WATCH and news size).
Before every test: read edges/RESULTS.md from E140 on. The live Signal Lab (edges/siglab) and its forward record
(bot-state/siglab/signals.json) outrank backtests: grade setups from it weekly.

## Done
- [x] Volatility-managed holding — E84 FAIL (benefit = holding less, not timing)
- [x] US index overnight drift — E83 FAIL after CFD costs (real gross +5 bp/night; ETF at a zero-commission broker +7.7%/yr, t 1.45)

## Next (queue from 15 Nov, top first)
- [ ] **Signal Lab forward review (weekly)**: read bot-state/siglab/signals.json; report per setup x market x trend side;
      if a muted cell has 30+ forward signals with avg > 0, unmute it in edges/siglab/priors.json; if a PAPER cell earns
      PROMISING/CONFIDENT, say so in RESULTS.md.
- [ ] **Higher-timeframe filter** (from the 15 Nov BTC loss): replay lab setups keeping only signals that agree with the
      4h AND daily trend (EMA50/200 of 4h and 20/50 of daily closes). Registered plan; mute/BACKTEST+ rule as E148.
- [ ] **Order-book data (free tardis.dev samples)**: tardis.dev publishes the first day of every month free (Binance
      BTCUSDT book snapshots, trades, liquidations). Test whether book imbalance predicts the next 15–60 minutes.
- [ ] **freqtrade-strategies** (github.com/freqtrade/freqtrade-strategies, 5.6k stars): port the 10 most-starred
      15m/1h strategies faithfully, run them through the lab scorer on BTC/ETH/SOL, report each, count every variant.
- [ ] **ccxt** for live data from more venues (Bybit, Kraken, Coinbase) when Binance is blocked on GitHub runners.
- [ ] **News + WATCH combination**: does the lab's breakout/pullback after a high-impact USD release behave differently
      (Forex Factory CSV in /home/user/data/ff or re-download from github.com/ehsanrs2/forexfactory-scraper)?

## Older queue (day-trading ideas, untested)
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
