# XAG — findings (from edges/RESULTS.md, research of 14 Nov 2026)

Source of truth: the matching section of edges/RESULTS.md; result files in edges/results/.

## Silver (XAG) bot — E120–E128: nothing passed on any horizon (day, swing, hold)
Common methods `plans/E120_common_xag.md` (8cb3848d). Code `edges/research_xag/`, numbers `results/E121–E128_result.json`.
197 logged attempts, about 170 distinct variants (E121 was run twice after a bug fix: FOMC window and in-sample model
selection; both runs are logged). Costs: CFD 0.04%/side for silver and 0.02% for gold + 6.5%/yr financing per night;
maker variants use perp costs. Hourly data is 1h only (no 15m) and is short, and the bar was not lowered for it.
BLS calendars returned 403, so CPI/NFP were skipped. FOMC dates are from federalreserve.gov.

| Plan | md5 | Var. | Discovery best | Luck (95th pct) | Validation | Final | Verdict |
|---|---|---|---|---|---|---|---|
| E121 handoff families 1h | 214c2b88 | 9 | failed auction −3.6 bp, t −0.4 (model's discovery = training, excluded) | grid t 0.97 | breakout −2.0; compr+conf +22.4 (t 1.1); model +1.6 (t 0.4) | info: breakout −16.6 (t −2.2), model −9.8 (n 393) | FAIL |
| E122 break gap / silver fix / ORB | 3528118b | 24 | ORB NY hi-vol +2.3, t 0.2 | grid t 1.15 | not promoted | info −25.7 | FAIL |
| E123A hourly shocks × vol gate | ead0af26 | 24 | z3 FADE high-vol h4 +19.3, t 1.2 (n 40) | grid t 1.70 | not promoted | — | FAIL |
| E123B maker dip limit (perp) | ead0af26 | 4 (+4 mirror) | k3 H4 +25.4 bp, t 3.47, n 254 | random −0.0 bp | **+44.9, t 2.82, n 108** | **−4.7, t −0.41, n 168 (ex-top5% −27.8)** | FAIL at FINAL → grade C watch |
| E124 gold/silver ratio MR + trend | 99ad36a4 | 18 | trend L20 silver +0.1 bp/day, t 0.03 | grid t 1.71 | −4.0 | info −1.9 | FAIL |
| E125 momentum/reversal + post-shock | 997a208b | 28 | MOM L10 long +2.4 bp/day, t 1.34 | grid t 2.43 | −2.3 | info +0.1 | FAIL |
| E126 hold: E85 / improvements / rotation | 13cd962b | 13 | E85: Sharpe 0.26/0.31 (val/final) vs B&H 0.63/0.46; best B 0.50; best rotation 0.47 | Sharpe 0.52 / 0.64 | — | — | FAIL |
| E127 residual reversal 1–5 d | cdd9350a | 12 | best t −0.37 | grid t 1.36 | −3.8 | info −3.1 | FAIL |
| E128 hold: MA gates (silver/gold/both) | 349a4ae4 | 12 | gold-MA200 + vol size Sharpe 0.44 | Sharpe 0.66 | — | — | FAIL |

- *Day:* the handoff's gold findings carry over to silver. Breakouts lose most, there is no direction edge, and the
  movement-timing model sees big moves (21–27% hit rate vs 14%) but has worse log loss than a vol-and-clock control.
  The cost share is the same as gold's (8 bp ≈ 10.6% of the average 4 h move), so the missing edge, not costs, is the
  problem. The maker dip limit (E123B) is the only rule that passed validation; it failed 2026.
- *Swing:* ratio mean reversion and ratio/residual trades are all negative. Silver momentum/shock rules fail the luck check.
- *Hold:* E85 as written fails (2%/yr, drawdown −15% vs −57%). Trend gates whipsaw on silver. The best-evidence risk
  tool is vol-only sizing (20% target: final Sharpe 0.48 vs 0.46, drawdown −31% vs −57%). Holding gold beat holding
  silver on Sharpe in every period.
- *Perp (info, too short to judge):* Binance XAGUSDT Jan–Oct 2026 saved to /home/user/data/metals/XAGUSDT_perp_*.parquet:
  about $790M per day, 0.993 hourly correlation with COMEX. **Longs paid about 20%/yr in funding** (4-hourly; 6.3% in
  Jan 2026). Weekends are quiet (11 vs 49 bp mean |hourly move|).
- *Leverage:* nothing passed, so there is no table. Silver fell −31% close-to-close on 30 Jan 2026. The watch rule's
  worst 2026 intrabar move was −16%, which liquidates 5× and above; 20×/40× die on ordinary days (2σ ≈ 4%).
