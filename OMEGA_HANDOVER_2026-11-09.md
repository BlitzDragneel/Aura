# OMEGA — handover, 9 Nov 2026 (read this first; it extends omega/OMEGA_HANDOVER_2026-11-02.md)

Repository: https://github.com/BlitzDragneel/Aura · working branch `claude/trading-edge-research-bots-gpkvi1`
(`main` holds only the GitHub Actions workflows; `bot-state` holds the cloud bots' records).

## 1. What is live
| What | Where | Notes |
|---|---|---|
| OMEGA app **v6.5.116** (installable PWA) | https://omega-board.onrender.com/omega-v6_5-47.html | Heaven theme, every forex pair, bots feed, Academy, one self-running Autopilot |
| Progress board | https://omega-board.onrender.com | every test and verdict, install instructions, links to all records |
| Live API (FastAPI) | https://omega-live-api.onrender.com | crypto (Binance→OKX→Gate), forex/metals (Swissquote quotes, Yahoo/Twelve Data candles), DVOL, /signals, /scouts, /bots/feed, /academy/*. Data endpoints need `Authorization: Bearer <token>` (token given to the owner in chat; Render env `OMEGA_API_TOKEN`) |
| Paper bot (cloud) | GitHub Actions every 15 min → `bot-state/STATUS.txt` | climax A, panic H1/H3 B, 4 watch-list rules C; paper only |
| Scouts (cloud) | hourly + every 15 min → `bot-state/scouts/`, `bot-state/fast_scouts/` | forecasts scored after their horizon; information only |
| Edge Hunter | claude.ai routine, daily 04:37 UTC | follows `edges/HUNTER.md` + `edges/IDEAS.md` |
| OMEGA Station (laptop) | `edges/station/` | runs all bots on time, Binance direct, testnet capable; live money never started by it |
Render services: `omega-live-api` (srv-dbnnbus9v7es73d8de4g), `omega-board` static (srv-dbnnllm7bikc73d2aoog). Both are
linked by public URL, so **pushes do not auto-deploy: trigger a deploy** after changes.

## 2. Research verdicts this round (edges/RESULTS.md has every number)
- **Nothing new passed.** E37–E46 (short timeframes, intraday timing), E50–E55 (trend, breakout, cross-section, ALT/BTC,
  funding, lead-lag), E63–E70 (F&G, DVOL, Coinbase/perp premium, taker flow, on-chain, regime), E80 (480 exits),
  E81/E82 (UpScout/DownScout 1h and 15m), E83 (US index overnight drift), E84 (volatility-managed holding).
- **Leverage:** 2× already liquidates on every rule; 20×/40× wipe the account. Highest safe leverage: 1×.
- **The two passed rules are fading:** H1 +127 → +33 → +19 bp/trade (2020–23 / 2024 / 2025–26, t 0.6); climax +136 → +126 → +109 bp (t 0.8).
- **Closest near-misses (now on the paper watch list):** 5m/15m panic bounce, 15m market-wide panic, UpScout top calls;
  also perp-premium dip (E66), panic+DVOL (E68), overnight drift with a zero-commission broker (+7.7%/yr, t 1.45).
- **Forward record decides:** ~50 closed paper trades per rule, a few hundred scored scout calls.

## 3. The app (omega/apps/omega-v6_5-47.html) — built only by patches in omega/kits/original
- v6.5.106–107 misinformation + security fixes · 108 Neon Glow · 109 research pages removed (−46% size) · 110 Academy +
  tutorial · 111 Brain slimmed · 112 forex board/fallback + bots feed · 113 Heaven theme + About page · 114/115 declutter,
  phone fixes, Install OMEGA · 116 one self-running Autopilot (25 jobs).
- CREED's engine is byte-identical (s102). One data-fetch line in the CREED module adds the forex fallback (owner to confirm).
- Run all suites: s102 s108–s113 s115 s116 s58 s78 s89 s91–s99 (`HARNESS=<kit>/tools node sNNN_test.js <build>`, s102 with `PREV=`).

## 4. Academy (omega/academy)
57 lessons / 10 modules (~7 h), 19 free; paid lessons served only by the Live API with a Gumroad license key.
Owner to do: Gumroad product with license keys → `ACADEMY_GUMROAD_PRODUCT_ID` on Render + `checkout_url` in pricing.json
(then re-run patch110 to refresh the app's embedded data); legal disclaimer check (TTSEC); refund policy.

## 5. Owner's open actions
1. cron-job.org pinger (`edges/PINGER_SETUP.md`) **or** the laptop Station (`edges/station/README.md`) — GitHub's own
   scheduler skips most runs.
2. Paste the API token in OMEGA → Settings → Data & Keys; install the app (board page has the steps).
3. Rotate the old Twelve Data key; optionally add a new one as GitHub secret `TWELVEDATA_API_KEY` for gold/forex research.
4. Consider making the repo private (then: Render needs GitHub access, Actions minutes are capped at 2,000/month).
5. Binance live key only after 50+ testnet trades: futures-only, no withdrawals, IP-restricted.

## 6. Standing rules (unchanged)
Never fabricate; plan before data; count every try; paper → testnet → live by the owner's hand; no secrets in files.
