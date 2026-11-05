# OMEGA Bridge 1.1 — control Exness (MT5) and Binance futures from your PC, behind one guard

Runs **on your Windows PC**. Claude (in Claude Desktop) or you can use it to read prices and positions and to place,
close and cancel orders on **Binance USDT-M futures** and **MT5** (Exness or any MT5 broker).

## The guard (every order, both venues)
- **Demo / testnet only** until you switch live on yourself in `config.json` (`"live": true` per venue). A real MT5 account
  is refused while MT5's `live` is false.
- **A stop on every order.** **Risk cap:** money lost if the stop is hit ≤ `max_risk_usd` (1 USD). **Size cap** on Binance:
  `max_order_usd` (10 USD). **At most 3 open positions** per venue. **Daily loss limit:** 5 USD (realized + open), then
  no new orders that day.
- **Kill switch:** double-click `KILL_and_close_all.bat` (blocks new orders and closes everything), or put a file named `KILL`
  in the Bridge folder. `kill_switch_off.bat` lifts it.
- **Preview first:** every order can be previewed (exact rounded order + every check) without sending; sending needs
  `confirm=true`. Every sent, refused or failed order is written to `orders.jsonl`.
- **Since the Nov 2026 security review:** `place_order` needs the `preview_id` of a preview of exactly that order (valid
  120 s, single use). A **LIVE** order also needs **you to click Yes in a dialog on the PC** (Claude cannot click it; no
  answer within 60 s = no). A live Binance key is refused if it can **withdraw** or is **not IP-restricted**
  (`guard.require_ip_restriction`). One position or resting entry order per symbol (no adding past the size cap);
  resting entry orders count toward the 3. MT5 orders are capped at `max_mt5_lots` (0.1). If the stop cannot be placed after
  the entry, the Bridge undoes the entry; if it cannot, it turns the kill switch on and says so. The kill switch with
  flatten also cancels resting entry orders. **Claude can turn the kill switch on but never off** (`kill_switch_off.bat`).
  In Claude Desktop, never choose "always allow" for `place_order`, `close_position` or `kill_switch`.
- **Secrets never in files:** your Binance key/secret and MT5 password go into the **Windows Credential Manager**. The config
  file refuses to load if it contains a key, secret or password. Logs redact anything secret-like.

## Setup (Windows, about 15 minutes)
1. Install **Python 3.11+** (python.org, tick "Add to PATH") and the **MT5 terminal from Exness**; log in to your
   **Exness demo** account in MT5 and keep the terminal running.
2. Unzip this folder to `C:\OMEGA-Bridge`. Open a terminal there:  `pip install -r requirements.txt`
3. **Binance testnet keys:** log in at the Binance futures testnet site (`testnet.binancefuture.com`), create an API key.
   For a real Binance key later: enable **Futures** trading only, **never "Enable Withdrawals"**, and restrict it to your IP.
   Then:  `python -m omega_bridge setkey binance`  (paste key and secret; they go into the Windows vault).
4. **MT5:** if the terminal is already logged in, nothing else is needed. To let the Bridge log in itself, put `login` and
   `server` (no password) in `config.json`'s `mt5` section and run  `python -m omega_bridge setkey mt5`.
5. Double-click `bridge_status.bat`: both venues should say `testnet` / `demo` with a balance. If a venue says
   "not connected", the message says why (MT5 not running, no key, wrong address).
6. **Claude Desktop:** Settings → Developer → Edit Config, add the `omega-bridge` entry from `claude_desktop_config_snippet.json`
   (adjust the folder), restart Claude Desktop. Then ask: "status of my bridge", "preview a 10 USD BTCUSDT long with a stop
   at …", "show my Exness positions". Claude Desktop asks before every tool call; the Bridge previews before every order.
`config.json` is created in `%APPDATA%\OMEGA-Bridge` on first run (limits, venues; never secrets).

## Funding monitor (new in 1.1): information only
`python -m omega_bridge funding` (or ask Claude Desktop for the funding monitor) lists the highest and most negative funding
rates right now, annualized, with warnings for extreme or flipping funding. It **places nothing**: research E34 (Nov 2026)
found the delta-neutral funding harvest FAILED in 2025–26 (−17% a year), because one coin's funding flipped in a crash
(−20.8% in a day, −64.6% in a month) and erased years of small gains.

## What it does not do
- It does not decide trades. It executes what you (or Claude, with your OK) ask, within the guard. OMEGA Prime's tickets
  say what the tested rules suggest; the Bridge is how such an order reaches the exchange.
- It does not run when your PC is off or asleep.

## Tests: `python -m pytest -q tests` (37 incl. tests/test_security.py, with a simulated Binance and a fake MetaTrader5 module)
Signing (HMAC-SHA256; the secret never travels), rounding to the exchange's rules and minimums, stops on the wrong side,
preview never sends, confirm required, every guard refusal with reasons, bracket orders (stop-market and take-profit-market,
close-position), Exness symbol suffixes (XAUUSD → XAUUSDm), sizing by risk with MT5's profit calculator, minimum-lot refusals,
real accounts refused without the live switch, config refusing secrets, kill switch with flatten on both venues, the
connector's tools, the funding monitor (ranks, annualizes, warns, never sends an order).
**Not verified:** never run against the real MT5 terminal or Binance's servers (Claude's sandbox can reach neither). The
Binance testnet address can change; it is in `config.json` (`binance.testnet_url`). First run: demo/testnet, watching.
