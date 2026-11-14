# E120 — Silver (XAG) research bot: common methods for E120–E139 (written 14 Nov 2026, before any test statistic)

Binding: edges/ASSETS_BRIEF.md, edges/PROTOCOL.md, edges/assets/HANDOFF_REFERENCE.md. The handoff never studied silver;
its gold definitions are the template. Seen before writing the plans (data checks only, no rule tested): row counts,
hour-of-day coverage, missing hours (e.g. hourly gap 30 Jan 15:00 → 2 Feb 18:00 2026), year-end closes, and the
Jan 2026 blow-off (silver 70 → 121 → 76, −31% close-to-close on 30 Jan 2026).

## Data
- SI_1d (Yahoo SI=F continuous, 2000-08 → 2026-11-13), GC_1d for the gold/silver ratio. Daily **opens are unreliable**
  (timestamps vary, open ≠ previous close) → daily rules use **closes only**, signal at close t, position held close t →
  close t+1 (same-close execution, as E85); every daily rule also reports a 1-day-delay sensitivity (info).
- Continuous futures are spliced at rolls without back-adjustment (contango jumps of a few tenths of a % around rolls).
  Stated as a limitation; cannot be fixed without contract-level data.
- SI_1h (Jun 2024 → 13 Nov 2026, CME hours, daily 21–22/23 UTC break, missing hours left missing, volume-0 bars kept as
  prices but never used as signal bars if o=h=l=c). GC_1h for context. There are **no 15-minute bars**: the handoff's
  15m definitions are run on 1h bars (signal bar = 1h, "max hold 4 h" = 4 bars). Stated, not hidden.
- Macro dates: FOMC from the official Fed calendar (federalreserve.gov, fetched 14 Nov 2026; statement 14:00 New York).
  BLS (CPI, NFP) schedule pages answer 403 from this sandbox → CPI/NFP skipped, not typed from memory.

## Periods (fixed by the brief)
| | DISCOVERY | VALIDATION | FINAL (judged once) |
|---|---|---|---|
| daily | 2000-08 → 2015-12 | 2016 → 2020 | 2021-01 → 2026-11 |
| hourly | 2024-06-24 → 2025-06-30 | 2025-07 → 2025-12 | 2026-01 → 2026-11 |
Promotion: the discovery winner (highest t, minimum trades stated per plan) goes to validation only if discovery t ≥ 2
and it beats its luck check. FINAL is judged once, only for a variant that passed validation. When validation fails,
FINAL is computed and reported **for information only** (labelled), never judged or re-tuned.

## Costs (per side; stress = double)
- CFD (default venue): spread 0.04% per side silver, 0.02% gold; financing 6.5%/yr ÷ 360 per night held, charged on
  long AND short CFD positions (a night = position open across 21:00 UTC; Fri→Mon = 3 nights).
- Perp (maker-only variants): Binance XAGUSDT maker 0.02% (fills only if price trades THROUGH the limit), taker 0.05%
  + 0.02% slippage. Funding not charged (no history long enough) — stated.
- Daily holding rules: 0.05% of turnover (as E85); a CFD version also charges financing 6.5%/yr on |exposure| (info,
  and stated in the verdict).

## Statistics and pass mark (brief + protocol, unchanged)
- Intraday trades: mean net per trade, week-clustered t (bt.tstat_weekly). Daily trade/position rules: daily P&L series
  of the book, Newey–West t (lag 10) of the mean daily return; trade counts reported.
- PASS needs all: FINAL mean > 0, t ≥ 2; VALIDATION mean > 0, t ≥ 1.5; positive in ≥ 60% of calendar years (hourly:
  ≥ 60% of half-years); beats the simple control (day/swing: random-entry or vol-and-clock control at the 95th pct;
  holding: Sharpe above buy-and-hold and above volatility-only, drawdown ≤ 0.75× buy-and-hold); luck check (discovery
  best t vs the best t of the same grid on circularly time-shifted signals, ≥ 95th pct); enough trades (≥ 100 FINAL, or
  ≥ 50 with t ≥ 3 — hourly samples are small: reported, the bar is not lowered); FINAL without the best 5% of trades
  reported. Grades A/B/C as in the brief.
- Leverage table (bt.leverage_table with intrabar adverse excursion) for anything that passes.
- Every variant evaluated in any period → bt.log_attempt. Results → edges/results/E<nn>_result.json.
- Code: edges/research_xag/. Machine shared: single process, light jobs.
