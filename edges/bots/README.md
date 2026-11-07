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

### Contract details (extensions, backward compatible)
- `Signal` fields beyond the example: `strategy`, `ref_close` (filled by the runner/strategy; optional). Timing:
  **market** = fill at the next bar's open, exit at the close of *signal bar + hold_bars*; **limit** = fills only if a
  later bar trades **through** the price (low < limit for a long) within `valid_for_bars`, exit at the close of
  *fill bar + hold_bars*. `stop_pct`/`target_pct` are fractions of the entry (0.10 = 10%).
- `strategy.meta = {sym: {"first_ts": ..., "first_valid_ts": ...}}` is set by the runners (listing time) for
  "listed ≥ N days" rules and for daily windows anchored as in the research.
- `now` may be the last closed bar's open time (runners) or a wall-clock time (omega/live_api passes
  `Timestamp.now()`); use `edges.bots.core.is_current(df, now, tf)`.
- Optional `scan(data, start, end)`: a vectorised `signals()` for the backtester; `edges/tests_bots/test_strategies.py`
  checks scan == bar-by-bar. Set `needs_all = True` for cross-sectional rules (breadth).

---

# Running the bots (Maro, Windows)

**What they do:** at every hourly close, fetch closed candles, run every rule in `edges/approved.json` whose status
allows the mode, and (testnet/live) place the orders on Binance USDT-M futures with a protective stop, cancel unfilled
limits when the rule's window ends, and sell when the rule's hold time is over. Paper mode places nothing.

## Setup in ~15 minutes
1. Install **Python 3.11+** from python.org (tick "Add to PATH"). Copy the `Aura` folder (or at least `edges/`) to
   e.g. `C:\OMEGA\Aura`. In a terminal there: `pip install httpx pandas numpy pyarrow keyring`.
2. **Paper first** (no keys): double-click `edges\bots\run_paper.bat`. It runs forever; every signal, order, fill and
   exit is written to `%APPDATA%\OMEGA-Bots\bots_log.jsonl` and the state to `state.json` there.
   `edges\bots\status.bat` shows open positions and the last log lines.
3. **Testnet** (after a few days of paper): log in at `https://testnet.binancefuture.com` (Binance's futures demo),
   create an API key, then `python -m edges.bots setkey testnet` (goes into the Windows Credential Manager, never a
   file). Set `"status": "testnet"` for the rule(s) in `edges/approved.json`. Double-click `run_testnet.bat`.
   The REST address is `binance.testnet_url` in `%APPDATA%\OMEGA-Bots\config.json` (default
   `https://demo-fapi.binance.com`, per Binance's docs in Nov 2026). The account must be in **One-way Mode**.
   Testnet prices differ from the real market: signals come from real candles and limit prices are re-based by the
   testnet/real price ratio.
4. **Live** — only if 50+ testnet trades look like the backtest, and only by you: a real key with **Futures only, no
   withdrawals, restricted to your IP** (`setkey live`), approved.json `"status": "live"` for that rule,
   `"live": true` in config.json, and `set OMEGA_LIVE=I_UNDERSTAND_REAL_MONEY` in the terminal before
   `python -m edges.bots run --mode live`. Any one missing = refused.

**Kill switch:** `KILL_all.bat` (or `python -m edges.bots kill`) cancels every order, closes every position on the
futures account and blocks new orders. It also writes OMEGA Bridge's KILL file, and the bots obey the Bridge's kill
too: one switch for both. `kill_off.bat` lifts both.

**Guard (config.json → guard):** hard leverage cap 3× (and each rule's `max_leverage`, now 1), ≤ 10 USDT margin per
order, ≤ 3 open positions/resting entries (counted from the exchange, not only the bot's file), one position per coin,
risk per trade (size × stop) ≤ 3 USDT, daily loss limit 5 USDT, a stop on every position inside the liquidation
distance (2% buffer live), entry undone if its stop cannot be placed (if even that fails: kill switch + the position is
kept as UNPROTECTED and closed by the kill cycle). Keys only from the OS vault or environment variables; config files
containing a key/secret are refused; logs redact secrets.

## Honest risk text
- These rules are rare-event, fat-tailed bets. **H1 as a 100 USDT account (E26) had 56–59% drawdowns** and made most of
  its money in 2021; single panic trades lost 77–93%. Grade B means "passed a fair test, not yet confirmed".
- The bots' own backtest (923 coins incl. delisted, 2020 → Nov 2026, costs from bt.round_trip_cost, funding where
  data exists) shows the edge **shrinking**: H1 +127 bp/trade in 2020–23 but +33 bp (t 0.53) in 2024 and +19 bp
  (t 0.63) in 2025–26; H3 +6 bp (t 0.20) in 2025–26; climax +109 bp (t 0.77) in 2025–26. Without the best 5% of
  trades H1 and H3 lose money. Expect long flat or losing stretches.
- **Leverage never creates an edge; it scales the tail.** With 5% of equity per trade: H1 is liquidated 37 times at 2×,
  107 at 3×, and wiped out at 20× and 40×; climax liquidates from 2×; H3 from 2×. **20× and 40× liquidate every
  rule.** The highest leverage with zero liquidations and drawdown < 35% is **1× for all three**, so approved.json
  keeps `max_leverage: 1`.
- The default 50% protective stop is a disaster stop, not part of the tested rules.

## CLI
`python -m edges.bots backtest --strategy panic_h1 --from 2024-01-01 [--coins A,B] [--stop 0.5] [--save]` ·
`run --mode paper|testnet|live [--once]` · `status` · `kill [off]` · `setkey testnet|live` · `list`

## Not verified
fapi.binance.com answers 451 from Claude's sandbox and the testnet is unreachable there: every exchange call is tested
against a simulated Binance (httpx MockTransport) only. Never run on Windows, against the real testnet, or with
MetaTrader 5. The MT5 adapter is a stub routed through OMEGA Bridge's guard (disabled by default).
