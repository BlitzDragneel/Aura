# OMEGA trading bots — strategy interface (contract between research bots and the trading bot)

One strategy = one file `edges/bots/strategies/<id>.py` exposing `STRATEGY = <Strategy subclass>()`.
The **same code** runs in backtest, paper, and live (testnet by default), so a live signal is trade-for-trade the backtest's.

```python
from edges.bots.core import Strategy, Signal

class MyRule(Strategy):
    id = "panic_h1"            # matches edges/approved.json
    tf = "1h"                  # bar size the rule is evaluated on: 5m | 15m | 1h | 4h | 1d
    universe = "all"           # or a list of symbols
    lookback = 24 * 30         # bars of history the rule needs
    def signals(self, bars, now):
        """bars: {sym: DataFrame[o,h,l,c,v,qv] indexed by UTC bar-open time, last row = the bar that just CLOSED}.
        Return a list of Signal for orders to place right now."""
        return [Signal(sym="BTCUSDT", side="long", entry="limit", price=123.4,
                       valid_for_bars=3, hold_bars=24, stop_pct=None, target_pct=None, note="why")]
```

`edges/approved.json` — the list the trading bot is allowed to trade (anything else is refused):
```json
[{"id": "panic_h1", "grade": "B", "plan": "E22", "tf": "1h", "max_leverage": 1, "margin_usdt": 5,
  "status": "testnet", "evidence": "omega/research/... or edges/results/E..json"}]
```
`status`: `paper` (signals only) · `testnet` (orders on Binance futures testnet) · `live` (only the owner sets this by hand).
`max_leverage` is the highest leverage the research showed with no liquidations (PROTOCOL.md, Leverage); the bot never exceeds it.
