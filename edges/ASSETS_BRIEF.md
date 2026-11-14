# Gold · Silver · Bitcoin program (from 14 Nov 2026) — binding brief for the research bots

Owner (Maro, Trinidad, UTC−4): focus only on **BTC, gold (XAU), silver (XAG)**. For each asset find a tested strategy for
**day trades** (minutes–hours, closed same day or within 24 h), **swing/long trades** (1–20 days) and **holding**
(weeks–months, long or cash). Implement what passes in OMEGA; a dedicated bot per asset calls trades from passed rules only.

## Data (already downloaded; see edges/data/fetch.py and edges/data/fetch_metals.py)
- BTC: /home/user/data/1h/BTCUSDT.parquet (2020→), /home/user/data/5m/BTCUSDT.parquet (2022→), funding/BTCUSDT.parquet;
  also ETH etc. for context. Load with edges/lib/bt.py.
- Gold: /home/user/data/metals/GC_1d.parquet (2000→), GC_1h.parquet (Jun 2024→, Yahoo futures, CME hours with the daily
  break), PAXG_1h.parquet (Binance PAXGUSDT spot 2020→Oct 2026: a 24/7 gold-backed token, a PROXY, not XAUUSD).
- Silver: /home/user/data/metals/SI_1d.parquet (2000→), SI_1h.parquet (Jun 2024→).
- Not available: Dukascopy minute bid/ask (server resets connections; do not try to bypass), Binance XAU/XAG perps only
  from Dec 2025/Jan 2026 (too short to test, fine for live). Do not fabricate missing data; say what is missing.

## Periods (fixed before looking)
| Data | DISCOVERY | VALIDATION | FINAL (judged once) |
|---|---|---|---|
| BTC 1h/daily | 2020–2023 | 2024 | 2025-01 → 2026-11 |
| BTC 5m | 2022–2023 | 2024 | 2025-01 → 2026-11 |
| Gold/silver daily | 2000–2015 | 2016–2020 | 2021 → 2026-11 |
| Gold/silver hourly (futures) | 2024-06 → 2025-06 | 2025-07 → 2025-12 | 2026-01 → 2026-11 |
| PAXG hourly | 2020–2023 | 2024 | 2025-01 → 2026-10 |
Hourly metals give little data: report it and do not lower the pass mark for it.

## Costs (per side, plus funding where it exists)
BTC perp: taker 0.05% + 0.02% slippage; maker 0.02% only when price trades THROUGH the limit; funding from the files.
Gold/silver as CFD (Exness-like): spread 0.02% gold / 0.04% silver per side + overnight financing 6.5%/yr ÷ 360 per
night held; stress = double. PAXG: 0.10% per side. Daily holding rules: 0.10% (BTC) / 0.05% (metals) of turnover.

## What must be re-run (the external handoff, OMEGA-HANDOFF 12–14 Nov, reconstructed: its files are lost)
Re-run on YOUR asset with the definitions stated in that handoff where they apply (the lead pasted it into the session;
its key definitions): 15m signal bars, entry one full bar later, stop 2×ATR14, target 6×ATR14, max hold 4 h, no overlap,
stop-first in ambiguous bars. Families: learned price-only direction model (3 classes, boundary max(12 bp, ½ ATR)),
magnitude/"movement timing" watch (|4h move| > max(40 bp, 2 ATR), threshold = 75th pct of validation predictions)
against a volatility-and-clock control, price breakout, compression (+confirmation), accepted retest, failed auction
(sweep of the prior 16 bars' extreme by ≥0.1 ATR, close back inside, range ≥1.5 ATR, close location favouring the
rejection), macro-event follow/fade (CPI, NFP, FOMC) where you can source dates honestly (official Fed/BLS calendars;
if a source is blocked, say so and skip — never type dates from memory), trend/volatility long-or-cash controller
(E85 already did BTC and gold: re-use, add silver). Report each against the handoff's numbers where it gave them.

## Then go further (your own ideas, all pre-registered, counted, luck-checked)
Day: session effects (Asia/London/NY opens, the CME gold fix windows 10:30/15:00 London, the 21–22 UTC break),
range breakouts by session, gap behaviour after the CME break, volatility-regime filters, BTC weekend/funding windows,
the panic-bounce idea adapted per asset, maker-only entries/exits to cut costs. Swing: multi-day momentum/reversal,
gold–silver ratio mean reversion (relative value: long one, short the other), BTC–gold relationships, post-shock
drift. Holding: trend/vol controllers, ratio rotation (gold vs silver vs BTC vs cash), seasonality with honest tests.

## Rules
edges/PROTOCOL.md applies (plan before data with bt.register_plan, bt.log_attempt for every variant, luck check, judge
FINAL once, report failures). Pass mark: FINAL mean > 0 after costs with t ≥ 2 (week-clustered for intraday, Newey–West
for daily), VALIDATION > 0 with t ≥ 1.5, positive in ≥ 60% of years (or halves for short samples), beats the relevant
simple control (buy-and-hold for holding; random-entry/vol-clock control for day/swing), leverage table for anything
that passes (2× already liquidated everything so far — state it plainly). Grades: A passes all; B passes with a
weak point; C = watch list (discovery + validation only).

## Outputs per research bot
- plans in edges/plans/ (E86–E99 BTC, E100–E119 gold, E120–E139 silver), results in edges/results/, a section in
  edges/RESULTS.md (append; others write there too).
- edges/assets/<asset>/FINDINGS.md: plain-language summary per horizon (day / swing / hold): what passed, what failed,
  the best-evidence rule even if it failed (labelled), and what the asset bot should watch.
- For every PASS: a strategy file edges/bots/strategies/<asset>_<name>.py (Strategy contract in edges/bots/README.md,
  with a parity test vs your research trades) and an entry in edges/approved.json with "asset": "BTC"|"XAU"|"XAG",
  "horizon": "day"|"swing"|"hold", grade, status "paper", max_leverage from the table.
