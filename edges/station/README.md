# OMEGA Station — every bot on your laptop, 24/7

One program runs all the bots on time, starts when you log in, and keeps the laptop awake while it runs.
From Tobago, Binance answers directly, so the bots use Binance data (no OKX fallback) and can place **testnet** orders.

| Job | When (UTC) | What |
|---|---|---|
| Paper/testnet bot | :07 :22 :37 :52 | climax (A), panic H1/H3 (B) and the four watch-list rules (C, paper only) |
| Fast scouts | :02 :17 :32 :47 | up/down and trend-turn calls on 15-minute candles, scored 4 h later |
| Hourly scouts | :17 | the same on hourly candles, scored 24 h later |
| Live data API | always | http://127.0.0.1:8787 (crypto, gold/forex quotes, DVOL, /signals, /scouts) |
| Update | 06:41 daily | `git pull`, so new research and fixes arrive by themselves (paper/testnet only) |

## Install (about 10 minutes, once)
1. Install **Python 3.12** (python.org; on Windows tick "Add to PATH") and **Git** (git-scm.com).
2. Open a terminal and run:
   `git clone -b claude/trading-edge-research-bots-gpkvi1 https://github.com/BlitzDragneel/Aura`
3. **Windows:** double-click `Aura\edges\station\install_windows.bat`.
   **Mac:** in a terminal, `cd Aura && bash edges/station/install_mac.sh`.
4. Laptop settings: plugged in, **never sleep when plugged in**, lid-close action "do nothing" (Windows: Settings →
   System → Power; Mac: System Settings → Battery/Energy). The Station keeps it awake while it runs, but closing the
   lid can still sleep a laptop.

Records go to `%APPDATA%\OMEGA-Station` (Windows) or `~/OMEGA-Station` (Mac). Open **STATION.md** there for the latest
summary; `station.log` lists every job.

## Testnet (real exchange orders with fake money) — after a few days of paper
1. Log in at testnet.binancefuture.com, create an API key.
2. In the Aura folder: `.venv\Scripts\python -m edges.bots setkey testnet` (Mac: `.venv/bin/python …`). The key goes into
   the Windows Credential Manager / macOS Keychain, never into a file.
3. In `edges/approved.json` set `"status": "testnet"` for the grade A/B rule(s) you want (the watch-list rules stay paper).
4. In the Station folder edit `station.json`: `"mode": "testnet"`. The next cycle uses it; no restart needed.

**Live money is never started by the Station.** It needs the bot's own checklist in `edges/bots/README.md` (50+ testnet
trades that match the backtest, a futures-only key restricted to your IP, the rule set to live, and the live switches).

**Stop everything:** close the Station window (Mac: `launchctl unload ~/Library/LaunchAgents/com.omega.station.plist`).
**Kill switch for orders:** `edges\bots\KILL_all.bat` (cancels orders, closes positions, blocks new ones).
