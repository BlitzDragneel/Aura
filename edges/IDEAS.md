# Edge Hunter backlog (top = next). Tick with the verdict when done; add new ideas below.
Working branch: claude/trading-edge-research-bots-gpkvi1

- [ ] **Volatility-managed holding** (BTC, ETH, top-10 basket): exposure ∝ 1 / predicted volatility (UpScout/DownScout
      show volatility IS predictable, AUC ≈ 0.6). Judge vs buy-and-hold on Sharpe, CAGR and max drawdown, not per-trade t.
- [ ] **Panic bounce + scout filter**: take H1 fills only when UpScout's probability is in its top 20%.
- [ ] **Volatility breakout both ways**: when the scouts' combined big-move probability is high, enter on the first
      hourly close beyond a ±1σ band in either direction (straddle-like), 24 h hold.
- [ ] **Cross-exchange funding divergence**: Binance vs OKX funding on the same coin (OKX history API) — does the gap close?
- [ ] **Weekend volatility** in crypto: are weekend ranges predictably smaller, and does a range rule pay costs there?
- [ ] **Options skew / put-call (Deribit)** as a panic gauge for the panic bounce (history from Deribit trades).
- [ ] **US stocks overnight vs intraday drift** (SPY/QQQ, via a keyless or connector source) — a documented anomaly;
      check whether it pays costs for a small account (Exness CFDs).
- [ ] **Gold and forex day ranges** with Twelve Data history (needs the owner's key as a secret; skip if absent).
- [ ] **Forward verdicts**: paper bot after 50 closed tickets; scouts after 500 scored calls (bot-state branch).
