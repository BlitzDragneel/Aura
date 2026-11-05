# edges/bots: security findings (review only, the files were not edited)

Reviewed on 5 Nov 2026, while the builder was still writing (files dated 08:43–08:46): `config.py`, `keys.py`,
`guard.py`, `sizing.py`, `state.py`, `exchange_binance.py`, `exchange_mt5.py`, `live.py`, `__main__.py`. Re-check after
the builder finishes. Line numbers are approximate.

**What is already right:** keys come only from the OS vault or environment variables, and config files that contain
`key|secret|password|token` at any depth are refused. The log redacts anything secret-like. `__repr__` hides the key.
Going live needs four things: approved.json status `live`, config `live: true`, `OMEGA_LIVE=I_UNDERSTAND_REAL_MONEY`,
and a key whose restrictions show neither withdrawals nor internal transfer. If the restrictions cannot be read, live is
refused. Hedge Mode accounts are refused. Stops go through the Algo Order API (correct since Binance's Dec 2025 change).
A limit entry whose stop fails is cancelled; a market entry whose stop fails is closed. Leverage is capped at
`min(rule max_leverage, hard_max_leverage=3)`. The stop must sit inside the liquidation distance. Sizing floors to the
exchange step and refuses orders below the minimums. **I found no over-sizing error:** notional = margin × L ≤ 10 × 3 =
30 USDT per order.

## High

### B1. A failed stop that also fails to undo leaves a naked position, and the bot forgets it
In `live.py` `ExchangeBroker.entry` (around lines 137–148), if the market entry fills, `place_stop` fails, and then
`a.close()` also fails (or raises `httpx` errors, which are not `BinanceError`), the exception goes up to
`Runner.place`. That logs `order_error` and returns `None`, so the position is neither in `state.positions` nor
protected. The same applies if `place_market` itself times out (`httpx.TimeoutException`): the order may have filled,
and the bot records nothing.

Fix:
- (a) In `BinanceFutures._req`, wrap `httpx.HTTPError` into a `BinanceError` subclass (say `TransportError`).
- (b) On an entry transport error, query `GET /fapi/v1/order?origClientOrderId=cid` before deciding the order is not
  there. The `newClientOrderId` is already set.
- (c) If both the stop and the undo fail, call `G.set_kill(True)`, log `UNPROTECTED`, and still add the position to
  state, so `check_position`/`kill` will try to close it again.

OMEGA Bridge got the same fix in this review (`omega_bridge/binance.py` `send`/`_unwind`; tests in
`tests/test_security.py`).

### B2. Two separate kill switches on the same Binance account
The bots use `%APPDATA%\OMEGA-Bots\KILL`; the Bridge uses `%APPDATA%\OMEGA-Bridge\KILL`. `KILL_and_close_all.bat`
(Bridge) closes every position on the account, including the bots' positions. The bot then treats this as
`stop_or_external` (`check_position`) and **keeps trading new signals**. The reverse is also true.

Fix: make `guard.killed()` true if either file exists:
```python
BRIDGE_KILL = os.path.join(os.environ.get("OMEGA_BRIDGE_HOME") or os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "OMEGA-Bridge"), "KILL")
def killed(): return os.path.exists(path("KILL")) or os.path.exists(BRIDGE_KILL)
```
Have `python -m edges.bots kill` write the Bridge's KILL file too, or document one combined kill .bat.

## Medium

- **B3. Open-position limits count only the bot's own state file.** `State.open_count/open_symbols` ignore positions
  and resting orders already on the exchange: manual trades, Bridge orders, or anything left behind if `state.json` is
  lost. In testnet/live, merge in `api.positions()` and the open entry orders before calling `order_refusals`. The
  `one_position_per_symbol` check exists because Binance nets positions, so it needs exchange truth.
- **B4. Kill marks positions closed before the exchange confirms.** `Runner.kill` calls `self._close(pid, None, "kill")`
  for every state position, then `broker.kill_all`. If `kill_all` fails for a symbol, state already says closed. Also,
  `kill_all` catches only `BinanceError`, so one `httpx` error stops the loop over the remaining symbols. Close on the
  exchange first, remove from state only what is confirmed, and catch `Exception` per symbol.
- **B5. No per-trade risk cap.** `protective_stop_pct` defaults to 0.5. At 3x the stop is capped at about 32%, so one
  trade can lose about 97% of its 10 USDT margin plus slippage. Three can be open, and the 5 USDT daily limit is only
  checked before new entries. The Bridge's guard caps risk at 1 USD. If the bots are meant to be as strict, add
  `max_risk_usdt` (risk = notional × stop_pct) to `order_refusals`. `notional` is already passed in but not checked.
- **B6. The MT5 adapter skips the Bridge guard.** `exchange_mt5.MT5Broker.entry` calls `omega_bridge.mt5.MT5.prepare` and
  `.send` directly. The Bridge's guard (kill switch, risk cap, daily loss, max positions, live dialog) lives in
  `omega_bridge.core.Bridge`, not in `mt5.MT5`, so the docstring's claim that "the Bridge's own guard still applies
  inside Bridge" is false. Use `Bridge.preview(...)` plus `omega_bridge.guard.check`, or keep the adapter disabled
  (it is a stub and `mt5.enabled` is false by default).
- **B7. The live key is not required to be IP-restricted.** `withdrawals_enabled` reads `apiRestrictions` but ignores
  `ipRestrict`. A trading-only key that is not IP-bound can still be used to churn the account if it leaks. Refuse live
  unless `ipRestrict` is true. The Bridge now does this (`guard.require_ip_restriction`).

## Low

- **B8. Environment-variable keys** (`OMEGA_BINANCE_*`) are inherited by every child process and show up in process
  listings and crash dumps. Prefer the vault; for live, warn when the key comes from the environment.
- **B9. No clock-drift handling.** There is no `-1021` resync (`/fapi/v1/time`). A PC clock drifting more than 5 s
  makes every signed call fail, including stop placement and kill. The Bridge now resyncs once and retries.
- **B10. A stale resting limit** with `timeInForce=GTC` (used when the window is under 11 minutes) survives if the bot is
  off. Its closePosition stop also rests, so it stays protected, but it can fill much later. Consider a minimum GTD of
  11 minutes, or always cancel on start-up.
- **B11. Stop at 0.5% inside liquidation.** At 3x, stop ≤ 1/3 − 1.0% against a liquidation distance of 1/3 − 0.5%. A
  fast mark-price move can pass both. Consider `liq_buffer` ≥ 2% for live.
- **B12. `kill_all` cancels orders only for symbols in state or positions.** Resting orders on other symbols survive.
  Call `GET /fapi/v1/openOrders` (all symbols) and `algoOpenOrders` and cancel the bot's `omg-` client IDs.
