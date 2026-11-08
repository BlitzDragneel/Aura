# OMEGA Live API 1.0 — live crypto, forex/metals and options data (FastAPI)

One small local service that gives the OMEGA apps (and the trading bots) fresher, more reliable live data than calling
exchanges from the browser. **Read-only: it places no orders and holds no exchange keys.**

| Data | Source order (automatic fallback) | Key needed |
|---|---|---|
| Crypto perps: candles 1m–1d, bid/ask, funding, open interest, top coins by volume | Binance USDT-M futures → OKX → Gate.io | no |
| Crypto spot, Coinbase premium (info only) | Binance spot mirror → Coinbase | no |
| Forex & metals live bid/ask (EURUSD, GBPUSD, USDJPY, XAUUSD, XAGUSD…, Exness `…m` names accepted) | Swissquote public quotes → Twelve Data | no |
| Forex candles | Twelve Data, or candles the service builds itself from live quotes (`/fx/recorded`) | Twelve Data key optional |
| Options: BTC/ETH DVOL (30-day implied volatility) | Deribit | no |
| Live signals of the **tested rules only** (`edges/approved.json`) | same strategy code as the backtester | no |

Binance blocks US and many cloud addresses (HTTP 451). From your PC in Tobago Binance answers, so it is used first;
elsewhere the service falls back to OKX/Gate by itself and `/health` shows which source is down and why.

## Start (Windows, ~5 minutes)
1. Install Python 3.11+ from python.org (tick "Add to PATH").
2. Double-click `run_windows.bat` (first run creates `.venv` and installs 4 packages).
3. Open http://127.0.0.1:8787/docs — every endpoint can be tried there.
Optional forex candles: before step 2, `setx TWELVEDATA_API_KEY yourkey` (new key — see the security note), then reopen the window.

## Endpoints
`/health` · `/crypto/ticker?symbols=BTCUSDT,ETHUSDT` · `/crypto/klines?symbol=BTCUSDT&tf=1h&limit=200` ·
`/crypto/funding?symbol=` · `/crypto/oi?symbol=` · `/crypto/top?n=30` · `/crypto/spot?symbol=` · `/crypto/coinbase-premium?asset=BTC` ·
`/fx/quote?symbol=XAUUSD` · `/fx/klines?symbol=EURUSD&tf=1h` (key) · `/fx/recorded?symbol=EURUSD&tf=5m` · `/options/dvol?currency=BTC&hours=48` ·
`/signals` · `/scouts?speed=fast|hourly` (UpScout/DownScout reading from the latest closed 15m or 1h candle, any time; information only) · `/stream` (Server-Sent Events: crypto + forex prices every 5 s).
Candles: `{t (open, ms UTC), o, h, l, c, v, qv, closed}` — `closed:false` marks the bar still forming; rules only use closed bars.

## Phone access
The service listens on 127.0.0.1 only. To use it from the phone on the same Wi-Fi:
`set OMEGA_API_HOST=0.0.0.0` and `set OMEGA_API_TOKEN=<long random text>` (the service refuses to start on the network
without a token), then call `http://<PC-IP>:8787/...` with header `Authorization: Bearer <token>`. For outside the house use
Tailscale rather than opening a router port.

## Why not on Netlify
Netlify runs static sites and JavaScript/Go functions, not a Python FastAPI server, and its function hosts are US-based,
which Binance refuses. Run this on the Windows PC (next to the Bridge) or a small Europe/Asia VPS
(`omega/recorder/` has a Caddy + systemd example).

## Tests
`pip install -r requirements.txt pytest && python -m pytest -q tests` — 12 offline tests (providers mocked).
Verified live from the build sandbox on 5 Nov 2026: OKX candles/tickers/funding/OI, Binance spot mirror, Coinbase,
Swissquote EURUSD/XAUUSD, Deribit DVOL. Not verified here: Binance futures (451 from the sandbox) and Twelve Data with a real key.
