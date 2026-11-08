# OMEGA v6.5.112 — all Forex through the OMEGA Live API, and the 24/7 bots feeding OMEGA
- **Live API token** (Settings > Data & Keys, next to the server address shared with the Academy; default
  https://omega-live-api.onrender.com). Stored only as `omega_live_token`: a `*_token` store, so patch107's `isSecretKey` keeps
  it out of every backup and a backup file can never set it (s112 checks both). "Test connection" calls /health and /fx/quote.
- **`window.OMEGA_LAPI`** (the name `OMEGA_LIVE` was already taken by Live Market Data): server client with
  `Authorization: Bearer`, plus a **fetch-level fallback**: with NO Twelve Data key in this browser and a token set, any
  `api.twelvedata.com/time_series` request is answered from `{server}/fx/klines` in Twelve Data's own shape (newest first, UTC).
  Intervals the server lacks (30min, 2h, 12h, 1week, 1month) are built from smaller candles. With a key nothing changes.
- Key checks that refused to fetch now accept the Live API: Charts/Analysis (no TD throttle/budget for server calls; the result
  names the source, e.g. "OMEGA Live API · Yahoo — futures GC=F as a proxy, not spot"), the **CREED desk** (one line in its
  `fetchTD`: data source only — `analyseSeries`, `walkExit` and the method untouched; s102 byte-identical, s109/s112 compare the
  whole module minus that line), the CREED Scanner and Market Intelligence. Gold without a key keeps its PAXG proxy.
- **Forex board** (`page-forex`; Charts tab "Forex board", menu, palette): Majors 7 / Minors 21 / Exotics 18 / Metals 4 from
  `/fx/board`, mid price, spread in pips (metals in $), "Market closed" for stale quotes, refresh every 20 s while open; a tap
  opens the pair on Charts and runs the analysis. Without a token it explains how to connect and still lists the pairs.
- **Bots feed** (`/bots/feed`) on Bots (top) and a compact card on Home: paper bot positions/resting orders per rule with grade
  A/B/C (C = watch list, paper only), idle rules on one line, recent actions (repeats folded), scouts' strongest up/down calls
  and forward hit rate vs base rate; marked PAPER · FORECASTS; refresh every 2 min while visible; "Last updated".
- CSP unchanged (connect-src open). Build `python3 patch112.py <v6.5.111> <out>`. Test `HARNESS=tools PREV=<v6.5.111> node
  s112_test.js <build>` (21/21; server mocked by `tools/livemock.js`, same shapes and token rule as omega/live_api).
