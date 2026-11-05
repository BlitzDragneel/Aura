# OMEGA v6.5.88 — Research files card (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.88 · build 2026-10-21 00:15 UTC. Made with `python3 patch88.py <v6.5.87 build> <new build>` (uses `rdl.js`).

## Why
- **Plan E10** (the market-level capitulation bounce on BTC, ETH, SOL, BNB, XRP) needed the `creed15_1` 15-minute file. She could not find it, and its export was removed in an earlier build.
- **E10 uses daily closes only.** The app's wide data store already keeps daily bars from Jan 2020 for the 25 studied coins.
- **Addendum A to plan E10** (md5 `81652285baca5351b01a3f438221e8c7`), written before any data, switches the source to that store. Nothing else in the plan changes.

## Change
New card **"Research files to send (plan E10)"** at the bottom of the Breakout Desk (module `OMEGA_RDL`):
- **Status:** how many of the 25 studied coins are stored, BTC's first day, and which of the five E10 coins are missing.
- **Fetch missing coins:** runs the wide store's own fill for up to 6 minutes. The studied coins come first in its list.
- **Save daily history (25 coins):**
  - writes `omega-history-daily25-YYYY-MM-DD.json.gz`: omega-history v2, tf 1440, the usual encoding;
  - the store keeps no daily open, so opens equal closes;
  - `fs` and `fc` hold the day's funding sum (×1e7) and the payment count;
  - the file's own checks give each coin's days and date range, and missing coins are listed;
  - saving is refused if the file would contain a credential-like field.

## Verification
- **s88 (6 checks):**
  - the card wiring and the coin list;
  - the file format, ranges and missing-coin list;
  - the research loader's decoding matches the stored closes, highs and lows;
  - the credential refusal;
  - a browser run: status, Save, and the gzip file read back; no page errors.
- **All 22 suites pass** (s49…s88). s87's version check was widened.
- **Other checks:** 109 script blocks pass the syntax check; no duplicate ids; phone guard clean; 26-page crawl offline and with a fake exchange shows 0 errors.
- **Not run on a real phone.**
