# OMEGA security audit, 5 Nov 2026 (security bot)

Scope: OMEGA Bridge 1.1, OMEGA Recorder 1.0.1, OMEGA Live API (`omega/live_api`), both HTML apps (review only:
`APP_FINDINGS.md`), `edges/bots` (review only: `BOTS_FINDINGS.md`), and secrets in the repo and its git history.
**Nothing here was run against real Binance, MT5, Caddy or systemd.** All tests use mocks. Run the first live checks on
testnet or demo, and watch them.

## Findings by severity (F = fixed in this review)

### Critical
- **C1 (F) Bridge: a failed stop left a naked position.** `send()` placed the entry and then the stop. If the stop POST
  failed, the position stayed open with no stop. This is likely on real Binance now: since Dec 2025, conditional orders
  on `/fapi/v1/order` are answered with `-4120` ("use the Algo Order API"); the bots' builder relies on the same change.
  Fixed: `-4120` falls back to `POST /fapi/v1/algoOrder` (`algoType=CONDITIONAL`). Any other stop failure undoes the
  entry (cancels it, closes the position). If the undo also fails, the kill switch is turned on and the reply says
  "close it in the Binance app now". (The algoOrder parameters follow Binance's announcement; verify on testnet first.)

### High
- **H1 (F) Bridge/MCP: `place_order(confirm=true)` could be called without any preview.** A prompt-injected assistant
  (text from a web page, email or another connector) needs only one tool call to send an order. Fixed: `place` needs the
  `preview_id` of a preview of exactly the same order, made within the last 120 s, usable once.
- **H2 (F) Bridge: no human gate for LIVE orders apart from Claude Desktop's tool prompt**, which "always allow" switches
  off. Fixed: on a LIVE account, the order goes out only after a Yes clicked in a Windows dialog on the PC (system-modal,
  default button No). An answer after 60 s counts as no; off Windows the answer is always no.
  `guard.live_confirm_dialog` can turn this off.
- **H3 (F) Bridge/MCP: the assistant could lift the kill switch** (`kill_switch(on=false)`). Fixed: the connector can only
  turn it on; lifting it is `kill_switch_off.bat` on the PC.
- **H4 (F) Bridge guard: unlimited adding to one symbol and unlimited resting LIMIT orders.** `open_positions` counted
  filled positions only, and the size cap applied per order. Repeated 10 USD orders could build any position size.
  Fixed: one position or resting entry order per symbol (`allow_add_to_position` false), and resting entry orders count
  toward `max_open_positions` on both venues.
- **H5 (F) Bridge: the live Binance key's permissions were never checked.** Fixed: live orders are refused if
  `/sapi/v1/account/apiRestrictions` shows `enableWithdrawals`, if it cannot be read, or if the key is not IP-restricted
  (`require_ip_restriction`, default on).
- **H6 (F) Bridge kill switch: one error stopped the flatten, and resting entries survived it.** An `httpx` error (not
  caught) aborted the kill for both venues. Pending LIMIT/MT5 pending orders were not cancelled, so they could fill
  after the kill. Fixed: every venue and position is tried separately, resting entry orders are cancelled first, and
  MT5 close retcodes are checked (`closed` is false if any close failed).
- **H7 (open, bots) edges/bots:** a naked position plus a forgotten state after a stop failure (B1), and a kill switch
  separate from the Bridge's on the same account (B2). See `BOTS_FINDINGS.md`.

### Medium
- **M1 (F) Bridge: input validation.** NaN, inf, negative, non-numeric, wrong side (`LONG`) and wrong type (`STOP`)
  reached `prepare`. Some went through guard comparisons, where NaN is always false. Fixed: `core.preview` validates
  everything, and the guard re-checks finite and positive values (fail-closed).
- **M2 (F) Bridge: network errors.** `httpx` exceptions escaped unlogged, and their text could carry the signed URL. A
  timed-out entry could be re-sent by the user, so it could fill twice. Fixed: errors are wrapped with no URL. Entries
  carry `newClientOrderId`, and a timeout is resolved by looking the order up.
- **M3 (F) Bridge: MT5 had no size cap.** Risk ≤ 1 USD with a 1-tick stop allowed huge lot sizes, and a gap or slippage
  can lose far more than the risk cap. Fixed: `max_mt5_lots` (0.1). If `order_calc_profit` returns None, the order is
  refused.
- **M4 (F) Bridge: clock drift.** Fixed: on `-1021`, it resyncs with `/fapi/v1/time` and retries once. That is safe
  because the first request was rejected.
- **M5 (F) Bridge: unpinned dependencies.** Fixed: exact pins (httpx 0.28.1, keyring 25.7.0, mcp 2.3.0, pytest, respx);
  MetaTrader5 has a range. Recorder: upper bounds added.
- **M6 (F) Recorder: unauthenticated heavy endpoints on a public server.** Exports could load years of rows into memory
  (DoS). Fixed: optional `OMEGA_READ_TOKEN` (everything except `/health`), date-range caps on exports (400 days of
  table rows, 3 years of history), `/jobs` limit ≤ 1000, one backfill at a time (409), and bad dates return 400 instead
  of 500.
- **M7 (F) Recorder: Caddyfile and systemd.** Caddy gets HSTS, nosniff, frame-deny, no-referrer and CSP headers, a
  64 KB body limit, `/docs` hidden, and tokens redacted in its log. systemd gets ProtectSystem=strict,
  NoNewPrivileges, an empty CapabilityBoundingSet, a SystemCallFilter, MemoryMax and UMask 0077. This was not tested
  with a real Caddy or systemd; `systemd-analyze verify` only reported the missing venv path, as expected.
- **M8 (F) Live API: DNS rebinding.** Bound to 127.0.0.1 without a token, any web page could read it through a
  rebinding domain. Fixed: `TrustedHostMiddleware` (loopback names only, plus `OMEGA_API_HOSTS`) when no token is set.
  Provider errors are scrubbed of the Twelve Data key; `/options/dvol` currency is validated.
- **M9 (open, apps)** A WhatsApp number and the webhook URL go into backups; a crafted backup can redirect alerts; no
  SRI on the CDN script (hash supplied); no CSP; prices via corsproxy.io can be faked. See `APP_FINDINGS.md` A1–A5.

### Low
- **L1 (F)** Recorder token compared in constant time (`hmac.compare_digest`). Event fields are length-limited, and
  `kind` is restricted to `[A-Za-z0-9_-]`.
- **L2 (F)** Bridge config secret check now covers every depth and every section (it was binance/mt5 top level only).
- **L3 (open)** Recorder CORS defaults to `*` (reads are public market data). Set `OMEGA_CORS` to the app's origin. The
  Live API allows Origin `null` (needed for file://), so any sandboxed or file page can read it. Low impact: public data
  and the Twelve Data quota.
- **L4 (open)** Bridge `close()` cancels `allOpenOrders` but not algo orders (`/fapi/v1/algoOpenOrders`). A stale
  closePosition algo stop could close a later position. Add `DELETE /fapi/v1/algoOpenOrders` once it is verified on
  testnet.
- **L5 (open)** Bridge risk for MT5 is in the account currency (labelled USD); `notional_usd` for non-USD-quoted pairs is
  in the quote currency.
- **L6 (info)** Git commit metadata contains the GitHub account's email address (`marksimon1996b@…`). Switch to the
  GitHub noreply address if that should be private.
- **L7 (open, apps)** Small escape gaps and a dormant unescaped renderer; see `APP_FINDINGS.md` A6–A11.

## Secrets scan (working tree, untracked files, both commits of git history)
- **Twelve Data key:** not present in HEAD or in history. The lead removed it before the import commit, and the only
  `omega_td_key` value in the repo is the test fixture `BROWSERKEY99887766`.
- **Other keys and tokens:** I searched for AWS, GitHub, Anthropic, Slack, Telegram and Google key formats, private
  keys, and `key|token|secret|password = "<16+ chars>"`. Nothing was found. The 64-character runs in the original HTML
  are base64 data (line 30694), and the hex strings are md5/sha256 fingerprints.
- **Phone numbers:** `nophone.js` over all 621 tracked and untracked files found none.
- **Private URLs:** only the `your-name.duckdns.org` placeholder.

## Files changed
- Bridge: `omega_bridge/binance.py`, `core.py`, `guard.py`, `config.py`, `mt5.py`, `mcp_server.py`, new
  `omega_bridge/human.py`, `requirements.txt`, `README.md`, `tests/conftest.py` (`orders_get`), `tests/test_bridge.py`
  (preview_id flow, openOrders mock), new `tests/test_security.py` (25 tests).
- Recorder: `omega_recorder/api.py`, `config.py`, `Caddyfile`, `omega-recorder.service`, `requirements.txt`,
  `README.md`, new `tests/test_security.py` (4 tests).
- Live API: `omega_live/app.py`, new `tests/conftest.py`, 2 tests added to `tests/test_api.py`.

## Test results (Linux, Python 3.13, MetaTrader5 faked, Binance mocked with respx)
- Bridge: **37 passed** (12 existing + 25 new).
- Recorder: **18 passed** (14 + 4).
- Live API: **14 passed** (12 + 2).

## Owner actions (Maro)
1. **Rotate the Twelve Data key.** It was inside copies of `omega-v6_5-47.html` that were shared, so treat it as public.
2. Binance live key: Futures only, **withdrawals and internal transfer OFF, IP-restricted**. The Bridge now refuses
   anything else.
3. In Claude Desktop, **never "Always allow"** `place_order`, `close_position` or `kill_switch`. Do not run the Bridge
   connector in the same Claude Desktop as web-browsing or email connectors while live is on.
4. Test on testnet first: an order with a stop (it should show `via: algoOrder` if Binance answers -4120), the LIVE dialog
   (switch live on with the smallest size), and `KILL_and_close_all.bat`.
5. Recorder on a public server: set `OMEGA_TOKEN` and `OMEGA_READ_TOKEN` in `/etc/omega-recorder.env` (chmod 600) and
   `OMEGA_CORS`.
6. Anthropic console: put a low monthly spend limit on the Claude key the app keeps in the browser.
7. If the GitHub email should be private, switch commits to the GitHub noreply address.
