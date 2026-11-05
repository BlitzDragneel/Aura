# OMEGA v6.5.98 — the panic-bounce watch, and a full check of the build (delivered as `omega-v6_5-47.html`)

Build stamp: v6.5.98 · build 2026-10-26 00:02 UTC. Made with `python3 patch98.py <v6.5.97 build> <new build>`
(patch98.py reads panic98.js from its own folder).

## Which file this was built from
The file uploaded on 25 Oct (`omega-v6_5-47__3__1.html`, md5 bece6268…) is **v6.5.91 of 22 Oct, unchanged**: applying the
official patches 92 → 97 to it gives v6.5.97 exactly (apart from build stamps). So nothing of yours was lost by building
on v6.5.97, and v6.5.98 contains everything in your file plus six updates (Risk Guard and Growth Bot, Market Cockpit, Events
and Monthly Review, Data Check and Baselines, and the data-check fix) and the new watch.

## New: PANIC BOUNCE (v6.5.98)
- Plan E22's two passes, **H1** (a buy limit 2σ under a bottom-10% 24-hour fall, 3 hours to fill, sold 24 hours after the fill)
  and **H3** (the deepest 5% of falls while 20%+ of coins panic, bought at the close, sold 24 hours later), on the 40
  most-traded Binance USDT perpetuals. **Grade B:** passed fair tests, not yet confirmed forward.
- Evidence in the card: E22 (H1 +0.36%, t 4.34; H3 +0.22%, t 3.63) and E25, the survivorship test with the 143 delisted coins
  (H1 +0.32%, t 4.54; H3 +0.30%, t 4.08), with the tail caveats (without the best 5% each loses ~0.7% a trade; single trades
  lost 77–93%) and the sizing advice that follows: many small seats.
- Shows a gauge of the share of coins in panic, open orders and trades, and its own forward record (H1 and H3, 50 each).
- Placed under the climax reversal on the **Signals, Edge Lab and Watch** pages. Runs as Autopilot job `panic` (hourly),
  with its own on/off switch in the Operator table. Notifications when alerts are on. Stored as `omega_panic_v1`.
- The same code as OMEGA Prime's watch; the two apps keep separate records.
- A volume-0 candle counts as missing (trading halts; Binance keeps writing flat candles after a delisting).

## The check of the whole build
| Check | Result |
|---|---|
| Test suites | 28 of 32 pass in full (s49…s98, incl. the new s98: 8/8). s67, s69, s79 and one check of s77 compare against research files missing from the carry-over bundle (`partB_fresh.json`, `round12_final.json`, `round17.json`, `watch16.py`); not app faults, not runnable until those files are back |
| 28-page crawl, offline | 0 page errors, 0 console errors |
| Syntax, every script block | 116 blocks, 0 errors |
| Duplicate element ids | none (715 static ids) |
| Storage keys | one key written by two modules (`omega_perp_venue_v1`): both write the same values; not a bug |
| Phone-number guard | clean |
| 8-hour soak, fake clock | 0 page errors; console errors are only blocked network connections (88 in v6.5.97, 87 in v6.5.98); same job pattern as v6.5.97 |
| 4 minutes, real clock, Autopilot on | 22 jobs ran, none threw, none stuck (the soak's "never finished" `desk` job finished in 112 s) |

**Bugs found: none in the app.** One test-tool limit found: the soak's fake clock fires each waiting timer at most once per
10-minute jump, so jobs that pause between coins look stuck there; the real-clock run shows they are not.

## Worth knowing (not changed)
- **Your Twelve Data key is in the file** (module "TWELVE DATA KEY — installed on request"), in plain text, as you asked
  earlier. Backups never include it, but anyone you send the HTML to gets it. It is a free key; say if you want it out.
- **The charts library loads from the internet** (LightweightCharts, a CDN). Offline, Analysis/Simulation/Growth charts do not
  draw and the app says so; CREED does not need it.

## Not verified
Not run on a real phone, and not against the real Binance (the sandbox is refused by Binance's live API).
