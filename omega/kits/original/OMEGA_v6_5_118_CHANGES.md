# OMEGA v6.5.118 — gold and silver, first-class
- **Data:** XAUUSDT / XAGUSDT (Binance USDⓈ-M perpetuals, 24/7) are still read straight from Binance in the browser. New
  fallback layer right after the v6.5.40 metals rewrite: if Binance does not answer (blocked region, 451/403, outage) the
  same request is answered from OKX XAU/XAG-USDT-SWAP (browser, keyless), then from the OMEGA Live API (`/crypto/klines`,
  token needed; server: Binance → OKX → Gate). Answers keep Binance's shape, so every page that reads Binance works unchanged;
  if all three fail, one plain error names each failure.
- **Charts:** "Gold & silver (Binance perpetuals, no key)" is a group of the Crypto market list. Any gold/silver chart shows a
  strip: perpetual price and 24h change (and which source answered), spot XAU/USD or XAG/USD (Swissquote via the Live API,
  "Market closed" at weekends / CME break) and the perpetual's premium to spot (not compared while spot is closed).
- **Market lists (data-source layer):** CREED Scanner and Market Intelligence defaults include XAUUSDT/XAGUSDT; stored lists
  get them once (flag `omega_metals_added_v118`; a later removal is respected); Analysis scan catalog; CREED Desk crypto
  symbol list — one list line in the CREED module (s109 excludes that line like v6.5.112's data line; the method and
  `analyseSeries`/`walkExit` are byte-identical, s102).
- **Forex board → Metals:** a note on spot pauses vs the 24/7 perpetuals with "Gold/Silver 24/7 chart" buttons; tapping gold
  or silver opens the perpetual chart with spot beside it (platinum/palladium unchanged).
- **One scheduler:** Autopilot job `metals` (1 min while a gold/silver chart is open, else 15 min).
- Tests: new s118 (17/17). Harness `tools/livemock.js` gained `/crypto/klines`, `/crypto/ticker`, `/assets`, `/assets/{A}`.
  Build `python3 patch118.py <v6.5.117> <out>`.
